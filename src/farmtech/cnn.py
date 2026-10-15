"""A mesma arquitetura e checkpoint CNN da Fase 6."""
from functools import lru_cache
import io
import torch
from torch import nn
from torchvision import transforms
from PIL import Image
from .config import ROOT

class SmallCNN(nn.Module):
    def __init__(self):
        super().__init__();layers=[];channels=3
        for out in (16,32,64):
            layers.extend([nn.Conv2d(channels,out,3,padding=1),nn.ReLU(),nn.MaxPool2d(2)]);channels=out
        self.features=nn.Sequential(*layers)
        self.classifier=nn.Sequential(nn.AdaptiveAvgPool2d((4,4)),nn.Flatten(),nn.Linear(64*4*4,64),nn.ReLU(),nn.Dropout(.3),nn.Linear(64,2))
    def forward(self,x):return self.classifier(self.features(x))

@lru_cache(maxsize=1)
def load():
    checkpoint=torch.load(ROOT/'models/cnn_best.pt',map_location='cpu',weights_only=True)
    model=SmallCNN();model.load_state_dict(checkpoint['state_dict']);model.eval()
    return model,{idx:name for name,idx in checkpoint['class_to_idx'].items()}

def classify(image):
    model,names=load()
    transform=transforms.Compose([transforms.Resize((128,128)),transforms.ToTensor(),transforms.Normalize((.5,)*3,(.5,)*3)])
    with torch.inference_mode():probabilities=model(transform(image).unsqueeze(0)).softmax(dim=1)[0]
    return {'classe':names[int(probabilities.argmax())],'probabilidade_softmax':float(probabilities.max()),
            'nota':'Classificação da imagem inteira; probabilidade não calibrada. Não localiza objetos.'}
