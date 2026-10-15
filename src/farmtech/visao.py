"""Inferência real com o checkpoint customizado da Fase 6, sem retreinamento."""
from functools import lru_cache
import hashlib
import io
import json
import os
import time
import numpy as np
from PIL import Image,UnidentifiedImageError
from .config import ROOT
from .db import connection,now
from .alertas import queue_alert

WEIGHTS={'yolo60':'yolov5n_60ep_best.pt','yolo30':'yolov5n_30ep_best.pt','yolo_padrao':'yolov5n.pt'}
LABELS={'yolo60':'YOLOv5n Fase 6 — 60 épocas','yolo30':'YOLOv5n Fase 6 — 30 épocas','yolo_padrao':'YOLOv5n COCO padrão','cnn':'CNN Fase 6 — do zero'}

@lru_cache(maxsize=3)
def load_model(model_key='yolo60'):
    import torch
    folder=ROOT/'vendor/yolov5'
    if not (folder/'hubconf.py').exists():raise ValueError('Execute python scripts/bootstrap_vision.py primeiro.')
    os.environ['YOLOv5_AUTOINSTALL']='false'
    model=torch.hub.load(str(folder),'custom',path=str(ROOT/'models'/WEIGHTS[model_key]),source='local',device='cpu',verbose=False)
    model.conf=.25;model.iou=.45
    if model_key=='yolo_padrao':
        model.classes=[2,15];model.names[2]='carro';model.names[15]='gato'
    return model

def detect(image_bytes,filename,path=None,model_key='yolo60'):
    if model_key not in LABELS:raise ValueError('Modelo desconhecido.')
    if len(image_bytes)>10*1024*1024:raise ValueError('Imagem excede 10 MB.')
    try:
        image=Image.open(io.BytesIO(image_bytes))
        if image.width*image.height>20_000_000:raise ValueError('Imagem excede 20 megapixels.')
        image=image.convert('RGB')
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise ValueError('Não foi possível decodificar a imagem.') from None
    start=time.perf_counter()
    if model_key=='cnn':
        from .cnn import classify,load
        load();start=time.perf_counter()
        classification=classify(image)
        result={'deteccoes':[],'classificacao':classification,'tempo_ms':(time.perf_counter()-start)*1000,
                'modelo':LABELS[model_key],'classes':['gato','carro']}
        rendered=image
        boxes=[]
    else:
        model=load_model(model_key);start=time.perf_counter()
        predictions=model(np.array(image,copy=True),size=416);elapsed=(time.perf_counter()-start)*1000
        boxes=[]
        for x1,y1,x2,y2,confidence,class_id in predictions.xyxy[0].tolist():
            boxes.append({'classe':str(model.names[int(class_id)]),'confianca':round(confidence,5),
                          'caixa':[round(v,2) for v in (x1,y1,x2,y2)]})
        result={'deteccoes':boxes,'tempo_ms':elapsed,'modelo':LABELS[model_key],'classes':['gato','carro']}
        rendered=Image.fromarray(predictions.render()[0])
    elapsed=result['tempo_ms']
    with connection(path) as conn:
        run=conn.execute('INSERT INTO visao(criado_em,arquivo,sha256,modelo,resultado_json,tempo_ms) VALUES (?,?,?,?,?,?)',
                         (now(),str(filename)[:120],hashlib.sha256(image_bytes).hexdigest(),result['modelo'],json.dumps(result,ensure_ascii=False),elapsed)).lastrowid
        # Classes do projeto anterior: nenhum diagnóstico de praga ou doença é inferido.
        if any(b['classe']=='carro' for b in boxes):
            queue_alert(conn,'veiculo','Veículo identificado na imagem',
                        'Conferir a imagem e verificar se o acesso do veículo ao local é esperado. A detecção não identifica a placa nem autoriza acesso.',
                        f'visao:{run}:veiculo',vision_id=run)
    result['execucao_id']=run
    return result,rendered
