import argparse
import json
from pathlib import Path
from .db import initialize, talhoes
from .telemetria import seed_demo, ingest_many
from .alertas import listing, dispatch

def main():
    parser=argparse.ArgumentParser(description='Serviços FarmTech Fase 7')
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('init');sub.add_parser('demo');sub.add_parser('talhoes');sub.add_parser('alertas');sub.add_parser('treinar')
    ingest=sub.add_parser('ingerir');ingest.add_argument('file',type=Path);ingest.add_argument('--talhao',type=int,required=True)
    send=sub.add_parser('notificar');send.add_argument('--id',type=int,required=True);send.add_argument('--aws',action='store_true',required=True,help='Publica uma notificação real no tópico configurado')
    args=parser.parse_args();initialize()
    if args.command=='init':result={'banco':'inicializado'}
    elif args.command=='demo':result={'demo_criada':seed_demo()}
    elif args.command=='talhoes':result=talhoes()
    elif args.command=='alertas':result=listing()
    elif args.command=='treinar':
        from .analise import train
        result=train()
    elif args.command=='ingerir':
        text=args.file.read_text();payload=json.loads(text) if args.file.suffix=='.json' else [json.loads(line) for line in text.splitlines() if line.strip()]
        result=ingest_many(payload if isinstance(payload,list) else [payload],args.talhao)
    else:result=dispatch(args.id)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
