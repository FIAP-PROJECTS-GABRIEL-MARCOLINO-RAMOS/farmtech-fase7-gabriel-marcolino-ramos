"""Obtém a mesma revisão oficial YOLOv5 da Fase 6; não treina novos pesos."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
COMMIT='915bbf294bb74c859f0b41f1c23bc395014ea679'
path=ROOT/'vendor/yolov5'
if not path.exists():
    path.parent.mkdir(exist_ok=True)
    subprocess.run(['git','clone','--branch','v7.0','--depth','1','https://github.com/ultralytics/yolov5.git',str(path)],check=True)
actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=path,text=True).strip()
if actual!=COMMIT:raise RuntimeError('Revisão YOLOv5 diferente da fixada.')
print('YOLOv5 v7.0 verificado:',actual)
