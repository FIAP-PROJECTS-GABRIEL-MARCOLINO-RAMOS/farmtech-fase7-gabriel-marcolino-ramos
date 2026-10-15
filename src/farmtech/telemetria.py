from datetime import datetime, timezone, timedelta
import hashlib
import json
import math
import random
from .db import connection, now, talhoes, query
from .manejo import number, save_plot
from .alertas import rules, queue_alert
from .config import SEED

def validate(payload):
    if not isinstance(payload,dict):raise ValueError('Cada leitura deve ser um objeto JSON.')
    source=payload.get('origem','manual')
    if source not in ('simulado','manual','ESP32'):raise ValueError('Origem inválida.')
    sensor=str(payload.get('sensor_id','')).strip()
    if not sensor or len(sensor)>60:raise ValueError('Informe sensor_id com até 60 caracteres.')
    event=str(payload.get('evento_id','')).strip()
    if not event or len(event)>120:raise ValueError('Informe evento_id com até 120 caracteres para evitar duplicação.')
    try:
        dt=datetime.fromisoformat(str(payload['observado_em']).replace('Z','+00:00'))
        if dt.tzinfo is None:raise ValueError()
        if dt > datetime.now(timezone.utc)+timedelta(minutes=5):raise ValueError()
    except (ValueError,KeyError,TypeError):
        raise ValueError('observado_em deve ser ISO 8601 com fuso e não estar no futuro.') from None
    out={'sensor_id':sensor,'evento_id':event,'origem':source,'observado_em':dt.astimezone(timezone.utc).isoformat(timespec='seconds')}
    for key,low,high in [('umidade_solo',0,100),('umidade_ar',0,100),('temperatura',-40,85),('ph',0,14)]:
        out[key]=None if payload.get(key) in (None,'') else number(payload[key],key,low,high)
    if not any(out[k] is not None for k in ('umidade_solo','umidade_ar','temperatura','ph')):
        raise ValueError('Inclua ao menos uma medição.')
    for key in ('fosforo','potassio'):
        value=payload.get(key,1)
        if value not in (0,1) or isinstance(value,str):raise ValueError(f'{key} deve ser 0 ou 1.')
        out[key]=int(value)
    simulated=payload.get('ph_simulado',True)
    if simulated not in (False,True,0,1):raise ValueError('ph_simulado deve ser booleano.')
    out['ph_simulado']=int(simulated)
    return out

def ingest_many(payloads, plot_id, *, path=None, emit_alerts=True):
    if not 0<len(payloads)<=1000:raise ValueError('Importe entre 1 e 1.000 leituras por lote.')
    values=[validate(p) for p in payloads] # Validação completa antes de escrever qualquer linha.
    inserted=0;alerts=0;duplicates=0
    with connection(path) as conn:
        if not conn.execute('SELECT 1 FROM talhao WHERE id=? AND ativo=1',(plot_id,)).fetchone():
            raise ValueError('Talhão inexistente ou arquivado.')
        for p in values:
            existing=conn.execute('SELECT talhao_id,origem FROM sensor WHERE id=?',(p['sensor_id'],)).fetchone()
            if existing and (existing['talhao_id']!=plot_id or existing['origem']!=p['origem']):
                raise ValueError('Sensor já registrado em outro talhão ou com outra origem.')
            conn.execute('INSERT OR IGNORE INTO sensor VALUES (?,?,?,?)',(p['sensor_id'],plot_id,'multissensor',p['origem']))
            keys=('sensor_id','evento_id','observado_em','umidade_solo','umidade_ar','temperatura','ph','ph_simulado','fosforo','potassio','origem')
            existing_reading=conn.execute('SELECT * FROM leitura WHERE sensor_id=? AND evento_id=?',(p['sensor_id'],p['evento_id'])).fetchone()
            if existing_reading:
                if any(existing_reading[k]!=p[k] for k in keys):
                    raise ValueError('evento_id repetido com conteúdo diferente; lote cancelado.')
                duplicates+=1;continue
            cur=conn.execute('INSERT INTO leitura('+','.join(keys)+',recebido_em) VALUES ('+','.join('?' for _ in range(12))+')',tuple(p[k] for k in keys)+(now(),))
            inserted+=1
            if emit_alerts:
                for rule,title,action in rules(p):
                    queue_alert(conn,rule,title,action,f'leitura:{cur.lastrowid}:{rule}',reading_id=cur.lastrowid);alerts+=1
    return {'inseridas':inserted,'duplicadas':duplicates,'alertas':alerts}

def readings(path=None, plot_id=None):
    return query('SELECT l.*,s.talhao_id,t.nome talhao FROM leitura l JOIN sensor s ON s.id=l.sensor_id '
                 'JOIN talhao t ON t.id=s.talhao_id '+('WHERE t.id=? ' if plot_id else '')+
                 'ORDER BY l.observado_em,l.id', (plot_id,) if plot_id else (),path)

def seed_demo(path=None):
    if talhoes(path,active=False):return False
    plots=[save_plot('Café · Norte',1,80000,2,path=path), save_plot('Cana · Sul',2,120000,1.5,path=path)]
    rng=random.Random(SEED);end=datetime.now(timezone.utc).replace(microsecond=0)
    for j,plot in enumerate(plots):
        payloads=[]
        for i in range(72):
            soil=round(48+13*math.sin(i/8+j)+rng.uniform(-3,3),2)
            payloads.append({'sensor_id':f'demo-{j+1}','evento_id':f'demo-{i}',
                             'observado_em':(end-timedelta(hours=71-i)).isoformat(),
                             'umidade_solo':soil,'umidade_ar':round(rng.uniform(55,85),2),
                             'temperatura':round(rng.uniform(19,32),2),'ph':round(rng.uniform(5.7,7),2),
                             'ph_simulado':True,'fosforo':1,'potassio':1,'origem':'simulado'})
        ingest_many(payloads,plot,path=path,emit_alerts=False)
    # Ocorrência explícita para demonstrar a trilha de alerta sem disparar mensagens.
    ingest_many([{'sensor_id':'demo-1','evento_id':'demo-alerta','observado_em':end.isoformat(),
                  'umidade_solo':24.5,'umidade_ar':65,'temperatura':29,'ph':6.3,
                  'ph_simulado':True,'fosforo':1,'potassio':1,'origem':'simulado'}],plots[0],path=path)
    return True
