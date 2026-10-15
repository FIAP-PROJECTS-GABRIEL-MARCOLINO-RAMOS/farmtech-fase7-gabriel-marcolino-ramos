"""Previsão meteorológica pública; não é uma leitura de sensor da fazenda."""
from datetime import datetime, timezone
import json
from pathlib import Path
import requests
from .manejo import number
from .config import ROOT

def forecast(latitude=-21.17,longitude=-47.81):
    lat=number(latitude,'Latitude',-90,90);lon=number(longitude,'Longitude',-180,180)
    response=requests.get('https://api.open-meteo.com/v1/forecast',
        params={'latitude':lat,'longitude':lon,'daily':'temperature_2m_max,temperature_2m_min,precipitation_sum',
                'forecast_days':7,'timezone':'America/Sao_Paulo'},timeout=15)
    response.raise_for_status();data=response.json()
    data['_proveniencia']={'fonte':'Open-Meteo','tipo':'previsão meteorológica modelada',
                          'consultado_em':datetime.now(timezone.utc).isoformat(),
                          'latitude_consulta':lat,'longitude_consulta':lon,
                          'documentacao':'https://open-meteo.com/en/docs'}
    folder=ROOT/'runtime';folder.mkdir(exist_ok=True)
    (folder/'ultima-previsao.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    return data
