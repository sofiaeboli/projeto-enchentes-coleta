"""Coleta serviços essenciais de Porto Alegre no OpenStreetMap (Overpass API).
Uma única consulta, sem paralelismo, com espera em caso de 429/504."""
import json
import os
import time
from datetime import date

import pandas as pd
import requests

URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "projeto-enchentes-pucrs (trabalho academico)"}
SAIDA = "dados/originais/osm/"
os.makedirs(SAIDA, exist_ok=True)

CONSULTA = """
[out:json][timeout:120];
area["name"="Porto Alegre"]["boundary"="administrative"]["admin_level"="8"]->.a;
(
  nwr["amenity"~"^(hospital|clinic|school|fire_station|police|pharmacy)$"](area.a);
);
out center tags;
"""

dados = None
for tentativa in range(3):
    print(f"Consultando a Overpass API (tentativa {tentativa + 1} de 3)...")
    r = requests.post(URL, data={"data": CONSULTA}, headers=HEADERS, timeout=180)
    if r.status_code == 200:
        dados = r.json()
        break
    print(f"Status {r.status_code}, esperando 30 s...")
    time.sleep(30)

if dados is None:
    raise SystemExit("Overpass não respondeu. Tente de novo mais tarde.")

# Guarda a resposta crua, pra não precisar consultar de novo
with open(SAIDA + "servicos_poa.json", "w", encoding="utf-8") as f:
    json.dump(dados, f, ensure_ascii=False)
print("Resposta salva em", SAIDA + "servicos_poa.json")

linhas = []
for e in dados["elements"]:
    lat = e.get("lat") or e.get("center", {}).get("lat")
    lon = e.get("lon") or e.get("center", {}).get("lon")
    tags = e.get("tags", {})
    linhas.append({"osm_id": e["id"], "tipo": tags.get("amenity"),
                   "nome": tags.get("name"), "lat": lat, "lon": lon})

df = pd.DataFrame(linhas)
df.to_csv(SAIDA + "servicos_poa.csv", index=False)
with open(SAIDA + "COLETA.txt", "w") as f:
    f.write(f"Fonte: OpenStreetMap via Overpass API ({URL})\nData da coleta: {date.today()}\n")

print(len(df), "serviços")
print(df["tipo"].value_counts())