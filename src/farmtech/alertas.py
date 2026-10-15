"""Regras demonstrativas e fila transacional. Nenhum envio externo implícito."""
import os
import re
from .db import connection, now, query

def rules(reading):
    actions=[]
    soil=reading.get('umidade_solo')
    if soil is not None and soil < 30:
        actions.append(('solo_seco','Umidade do solo abaixo de 30%',
                        'Verificar a leitura e a calibração do sensor; inspecionar o sistema de irrigação antes de decidir o acionamento.'))
    ph=reading.get('ph')
    if ph is not None and not 5.5 <= ph <= 7.5:
        label='pH simulado' if reading.get('ph_simulado',True) else 'pH'
        actions.append(('ph_faixa',f'{label} fora da faixa demonstrativa 5,5–7,5',
                        'Conferir a origem e a calibração da medição; solicitar avaliação do solo antes de alterar o manejo.'))
    if not reading.get('fosforo',1) or not reading.get('potassio',1):
        actions.append(('nutrientes','Indicador de nutrientes requer conferência',
                        'Inspecionar os indicadores simulados de fósforo/potássio e confirmar a condição por análise antes de aplicar insumos.'))
    return actions

def queue_alert(conn, rule, title, action, key, reading_id=None, vision_id=None):
    conn.execute('INSERT OR IGNORE INTO alerta(leitura_id,visao_id,regra,chave,titulo,acao,criado_em) VALUES (?,?,?,?,?,?,?)',
                 (reading_id,vision_id,rule,key,title,action,now()))
    alert_id=conn.execute('SELECT id FROM alerta WHERE chave=?',(key,)).fetchone()[0]
    conn.execute('INSERT OR IGNORE INTO notificacao(alerta_id,atualizado_em) VALUES (?,?)',(alert_id,now()))
    return alert_id

def listing(path=None):
    return query('SELECT a.*,n.id notificacao_id,n.estado notificacao,n.tentativas,n.message_id,n.erro, '
                 'l.origem,s.talhao_id,t.nome talhao FROM alerta a JOIN notificacao n ON n.alerta_id=a.id '
                 'LEFT JOIN leitura l ON l.id=a.leitura_id LEFT JOIN sensor s ON s.id=l.sensor_id '
                 'LEFT JOIN talhao t ON t.id=s.talhao_id ORDER BY a.id DESC',path=path)

def resolve(alert_id,path=None):
    with connection(path) as conn:
        if not conn.execute("UPDATE alerta SET estado='resolvido' WHERE id=?",(alert_id,)).rowcount:
            raise ValueError('Alerta inexistente.')

def dispatch(notification_id, *, client=None, topic_arn=None, path=None):
    """Entrega um item pendente ao SNS. Retorno do SNS não comprova leitura do e-mail."""
    arn=topic_arn or os.getenv('FARMTECH_SNS_TOPIC_ARN','')
    if not re.fullmatch(r'arn:aws:sns:[a-z0-9-]+:\d{12}:[A-Za-z0-9_-]+',arn):
        raise ValueError('Configure um ARN de tópico SNS Standard válido antes de enviar.')
    with connection(path) as conn:
        conn.execute('BEGIN IMMEDIATE')
        row=conn.execute('SELECT n.*,a.titulo,a.acao,a.estado alerta_estado,a.chave FROM notificacao n '
                         'JOIN alerta a ON a.id=n.alerta_id WHERE n.id=?',(notification_id,)).fetchone()
        if not row:raise ValueError('Notificação inexistente.')
        if row['alerta_estado']=='resolvido':raise ValueError('Alerta já resolvido; envio cancelado.')
        if row['estado'] not in ('pendente','falha'):
            raise ValueError('Item já processado ou com resultado incerto; revisar antes de reenviar.')
        conn.execute("UPDATE notificacao SET estado='enviando',tentativas=tentativas+1,atualizado_em=? WHERE id=?",(now(),notification_id))
        message=f"FARMTECH | Demonstração acadêmica\nOcorrência: {row['titulo']}\nAção sugerida: {row['acao']}\nReferência: {row['chave']}\nAs regras são demonstrativas. Confirme a leitura antes de intervir."
    try:
        if client is None:
            import boto3
            from botocore.config import Config
            client=boto3.client('sns',region_name=arn.split(':')[3],config=Config(retries={'max_attempts':0},connect_timeout=5,read_timeout=10))
        response=client.publish(TopicArn=arn,Subject='FarmTech | Alerta operacional',Message=message)
        message_id=response['MessageId']
    except Exception as exc:
        # Falhas de rede podem ocorrer depois da aceitação: não reenviar automaticamente.
        from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
        status='falha' if isinstance(exc,(ClientError,NoCredentialsError,PartialCredentialsError)) else 'incerto'
        safe_error=type(exc).__name__
        if isinstance(exc,ClientError):safe_error += ': '+exc.response.get('Error',{}).get('Code','ErroAWS')
        with connection(path) as conn:
            conn.execute('UPDATE notificacao SET estado=?,erro=?,atualizado_em=? WHERE id=?',(status,safe_error,now(),notification_id))
        raise RuntimeError(f'Envio não confirmado ({safe_error}). Estado: {status}.') from None
    with connection(path) as conn:
        conn.execute("UPDATE notificacao SET estado='aceito_sns',message_id=?,erro=NULL,atualizado_em=? WHERE id=?",(message_id,now(),notification_id))
    return {'notification_id':notification_id,'status':'aceito_sns','message_id':message_id}
