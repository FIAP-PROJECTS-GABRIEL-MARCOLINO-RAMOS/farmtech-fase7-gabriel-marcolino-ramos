import json
from concurrent.futures import ThreadPoolExecutor
import pytest
from botocore.exceptions import ClientError
from farmtech import db,manejo,telemetria,alertas

@pytest.fixture
def database(tmp_path):
    p=tmp_path/'test.db';db.initialize(p);manejo.save_plot('Teste',1,10000,2,path=p);return p

def reading(**changes):
    value={'sensor_id':'s1','evento_id':'e1','observado_em':'2026-10-15T10:00:00-03:00',
           'umidade_solo':25,'umidade_ar':70,'temperatura':25,'ph':6,'ph_simulado':True,
           'fosforo':1,'potassio':1,'origem':'simulado'}
    return value|changes

def test_area_and_doses():
    assert manejo.calculate('retangulo',100,200,dose_l_ha=2)=={'area_m2':20000,'area_ha':2,'insumo_l':4}
    assert manejo.calculate('trapezio',200,100,100,2)['area_m2']==15000
    assert manejo.coffee_input(10,100,20)==20
    with pytest.raises(ValueError):manejo.calculate('trapezio',100,100,200)
    with pytest.raises(ValueError):manejo.coffee_input(1,1,1.5)

@pytest.mark.parametrize('value',[float('nan'),float('inf'),-1,101,True,'invalido'])
def test_invalid_values_are_atomic(database,value):
    with pytest.raises(ValueError):telemetria.ingest_many([reading(evento_id='good'),reading(evento_id='bad',umidade_solo=value)],1,path=database)
    assert db.query('SELECT COUNT(*) n FROM leitura',path=database)[0]['n']==0
    assert not db.query('SELECT * FROM sensor',path=database)

def test_ingestion_dedup_and_alert_transaction(database):
    assert telemetria.ingest_many([reading()],1,path=database)=={'inseridas':1,'duplicadas':0,'alertas':1}
    assert telemetria.ingest_many([reading()],1,path=database)=={'inseridas':0,'duplicadas':1,'alertas':0}
    assert len(alertas.listing(database))==1
    with pytest.raises(ValueError):telemetria.ingest_many([reading(umidade_solo=45)],1,path=database)
    assert len(telemetria.readings(database))==1

def test_unknown_or_archived_plot_rejected(database):
    with pytest.raises(ValueError):telemetria.ingest_many([reading()],999,path=database)
    manejo.archive_plot(1,database)
    with pytest.raises(ValueError):telemetria.ingest_many([reading()],1,path=database)

def test_air_humidity_is_not_soil_humidity(database):
    telemetria.ingest_many([reading(umidade_solo=None,umidade_ar=10)],1,path=database)
    assert not alertas.listing(database)

def test_conflicting_sensor_mapping_rolls_back(database):
    telemetria.ingest_many([reading()],1,path=database)
    manejo.save_plot('Outro',2,5000,1,path=database)
    with pytest.raises(ValueError):telemetria.ingest_many([reading(evento_id='e2')],2,path=database)
    assert len(telemetria.readings(database))==1

def test_invalid_date_requires_timezone(database):
    with pytest.raises(ValueError):telemetria.ingest_many([reading(observado_em='2026-10-15')],1,path=database)

def test_sns_acceptance_record_and_no_second_send(database):
    telemetria.ingest_many([reading()],1,path=database)
    class FakeSNS:
        calls=0
        def publish(self,**kwargs):
            assert kwargs['TopicArn']=='arn:aws:sns:us-east-1:123456789012:test'
            assert 'Ação sugerida:' in kwargs['Message']
            self.calls+=1;return {'MessageId':'test-message-id'}
    client=FakeSNS();arn='arn:aws:sns:us-east-1:123456789012:test'
    result=alertas.dispatch(1,client=client,topic_arn=arn,path=database)
    assert result['status']=='aceito_sns'
    with pytest.raises(ValueError):alertas.dispatch(1,client=client,topic_arn=arn,path=database)
    assert client.calls==1

def test_sns_network_ambiguity_retains_item(database):
    telemetria.ingest_many([reading()],1,path=database)
    class NetworkFailure:
        def publish(self,**kwargs):raise TimeoutError('simulated network timeout')
    with pytest.raises(RuntimeError):alertas.dispatch(1,client=NetworkFailure(),topic_arn='arn:aws:sns:us-east-1:123456789012:test',path=database)
    assert alertas.listing(database)[0]['notificacao']=='incerto'

def test_resolved_alert_cannot_be_sent(database):
    telemetria.ingest_many([reading()],1,path=database);alertas.resolve(1,database)
    with pytest.raises(ValueError):alertas.dispatch(1,topic_arn='arn:aws:sns:us-east-1:123456789012:test',path=database)

def test_foreign_keys_enforced(database):
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError):
        with db.connection(database) as c:c.execute('DELETE FROM cultura WHERE id=1')
