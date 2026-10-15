"""ESP32 USB → JSON Lines → banco e regras; nenhum envio AWS implícito."""
import argparse
import json
import uuid
from datetime import datetime,timezone
import serial
from farmtech.db import initialize
from farmtech.telemetria import ingest_many

p=argparse.ArgumentParser();p.add_argument('--port',required=True);p.add_argument('--talhao',type=int,required=True)
a=p.parse_args();initialize();session=uuid.uuid4().hex
with serial.Serial(a.port,115200,timeout=3) as board:
    while True:
        line=board.readline().decode('utf-8',errors='replace').strip()
        if not line:continue
        try:
            payload=json.loads(line)
            payload['evento_id']=session+':'+str(payload.pop('sequencia'))
            payload['observado_em']=datetime.now(timezone.utc).isoformat()
            payload['origem']='ESP32'
            print(json.dumps(ingest_many([payload],a.talhao),ensure_ascii=False),flush=True)
        except (ValueError,KeyError,TypeError) as exc:
            print(f'Linha descartada: {exc}',flush=True)
