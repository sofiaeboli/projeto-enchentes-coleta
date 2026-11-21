"""
Prepara os dados que o dashboard usa e salva em dados/processados/.
Rodar a partir da raiz do repositório:  python scripts/preparar_dados.py
"""
import os
import unicodedata

import geopandas as gpd
import pandas as pd

SAIDA = "dados/processados/"
os.makedirs(SAIDA, exist_ok=True)


def normalizar(nome):
    nome = unicodedata.normalize("NFKD", str(nome))
    nome = "".join(c for c in nome if not unicodedata.combining(c))
    nome = nome.replace("'", " ").replace("’", " ").replace("-", " ")
    return " ".join(nome.upper().split())


# nomes que a Prefeitura escreve diferente do INCT
AJUSTES = {
    "CEL. APARICIO BORGES": "CORONEL APARICIO BORGES",
    "MONTSERRAT": "MONT SERRAT",
    "PASSO DA AREIA": "PASSO D AREIA",
}

# 1) JSON do INCT: nome bonito de cada bairro (com acento) ligado à chave
inct = pd.read_json("dados/tratados/dados_inct_limpo.json")
inct["chave"] = inct["bairro"].apply(normalizar)
nomes = inct.drop_duplicates("chave").set_index("chave")["bairro"]

# 2) Limites dos bairros: junta os 128 polígonos em 94 e simplifica o desenho
bairros = gpd.read_file("dados/originais/bairros/bairros_poa.geojson")
bairros["chave"] = bairros["nome"].apply(normalizar).replace(AJUSTES)
bairros = bairros.dissolve(by="chave", as_index=False)[["chave", "geometry"]]
bairros = bairros.to_crs("EPSG:4326")
bairros["geometry"] = bairros.geometry.simplify(0.0002, preserve_topology=True)
bairros["bairro"] = bairros["chave"].map(nomes)
assert bairros["bairro"].notna().all(), "algum bairro não casou com o INCT"
bairros.to_file(SAIDA + "bairros_poa_94.geojson", driver="GeoJSON")

# 3) Serviços do OSM: descobre o bairro de cada ponto
serv = pd.read_csv("dados/originais/osm/servicos_poa.csv")
pontos = gpd.GeoDataFrame(
    serv, geometry=gpd.points_from_xy(serv["lon"], serv["lat"]), crs="EPSG:4326"
)
junto = gpd.sjoin(pontos, bairros[["chave", "geometry"]], how="left", predicate="within")
serv["chave"] = junto["chave"].values
serv["bairro"] = serv["chave"].map(nomes)
serv.to_csv(SAIDA + "servicos_bairro.csv", index=False)


# 4) Fontes e datas de coleta (o dashboard mostra isso)
def le(caminho):
    with open(caminho, encoding="utf-8") as f:
        return f.read().strip()


with open(SAIDA + "FONTES.txt", "w", encoding="utf-8") as f:
    f.write("INCT SiMAI: simulação de enchentes (JSON fornecido pelo instituto)\n\n")
    f.write(le("dados/originais/osm/COLETA.txt") + "\nLicença ODbL: © contribuidores do OpenStreetMap\n\n")
    f.write(le("dados/originais/bairros/COLETA.txt") + "\n")

print("Bairros:", len(bairros), "| serviços:", len(serv), "| sem bairro:", serv["chave"].isna().sum())
print("Arquivos salvos em", SAIDA)