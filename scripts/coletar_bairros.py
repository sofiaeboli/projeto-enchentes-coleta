"""Baixa os limites dos bairros de Porto Alegre (Prefeitura, camada bairros_2016)."""
import json
import os
from datetime import date

import requests

URL = ("https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/"
       "01_PUBLICACOES/bairros_2016/MapServer/0/query")
PARAMS = {"where": "1=1", "outFields": "nome", "f": "geojson"}
HEADERS = {"User-Agent": "projeto-enchentes-pucrs (trabalho academico)"}
SAIDA = "dados/originais/bairros/"
os.makedirs(SAIDA, exist_ok=True)

print("Baixando os limites dos bairros...")
r = requests.get(URL, params=PARAMS, headers=HEADERS, timeout=180)
r.raise_for_status()
dados = r.json()

with open(SAIDA + "bairros_poa.geojson", "w", encoding="utf-8") as f:
    json.dump(dados, f, ensure_ascii=False)

with open(SAIDA + "COLETA.txt", "w") as f:
    f.write(f"Fonte: Prefeitura de Porto Alegre (UMDU/SMUrb), camada bairros_2016\n{URL}\n"
            f"Data da coleta: {date.today()}\n")

nomes = {feat["properties"]["nome"] for feat in dados["features"]}
print(len(dados["features"]), "polígonos")
print(len(nomes), "bairros diferentes")