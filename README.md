# Análise de Dados de Enchentes – INCT SiMAI

Projeto extensionista da disciplina Coleta, Preparação e Análise de Dados (PUCRS),
Profª Katherine Bianchini Esper de Vargas.

Dashboard com duas telas: (1) impacto da simulação do INCT SiMAI por nível do Guaíba
e (2) bases externas sobre enchentes no RS que complementam essa resposta.

## Equipe
- Sofia Eboli
- Aline Acevedo
- Joao Dallanora

## Dashboard
Link: https://enchentes-poa-inct.streamlit.app

- **Tela 1 – Simulação do INCT:** se o Guaíba chegar a X metros, quais bairros e quantas pessoas são afetados.
- **Tela 2 – Serviços essenciais:** quantas escolas, farmácias, clínicas, hospitais, delegacias e
  quartéis de bombeiros (OpenStreetMap) ficam em bairros atingidos a cada nível.

Os números são **estimativas de uma simulação**, não previsões nem contagens oficiais.
Relatório do dashboard: `relatorios/dashboard.pdf`.

## Como rodar

Requisitos: Python 3.12 e as bibliotecas do `requirements.txt`.

```bash
# 1. Clonar o repositório e entrar na pasta
git clone https://github.com/sofiaeboli/projeto-enchentes-coleta.git
cd projeto-enchentes-coleta

# 2. (Opcional) criar um ambiente virtual
python -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Abrir o dashboard (os dados que ele usa já estão no repositório)
streamlit run app/app.py         # abre em http://localhost:8501
```

### Refazer os dados do zero (opcional)

```bash
python scripts/coletar_osm.py      # serviços essenciais (OpenStreetMap) -> dados/originais/osm/
python scripts/coletar_bairros.py  # limites dos bairros (Prefeitura)   -> dados/originais/bairros/
python scripts/preparar_dados.py   # gera os arquivos de dados/processados/
```

- Limpeza do JSON do INCT: `notebooks/analise_inical_json.ipynb`
  (lê `dados/originais/dados_inct.json` e gera `dados/tratados/dados_inct_limpo.json`).
- Análise exploratória: `notebooks/EDA.ipynb`.

Os dados **brutos** das bases externas não ficam no GitHub (tamanho e licenças de cada fonte);
os scripts de coleta registram a data da coleta em um `COLETA.txt` dentro de cada pasta.
Os dados **processados** que o dashboard usa ficam no GitHub, para o link público funcionar.

## Estrutura
- `dados/originais/` – dados como vieram (JSON do INCT; `osm/` e `bairros/` são gerados pelos scripts)
- `dados/tratados/` – JSON do INCT limpo, em formato longo (`dados_inct_limpo.json`)
- `dados/processados/` – dados usados pelo dashboard (limites dos 94 bairros, serviços por bairro, fontes)
- `scripts/` – coleta das bases externas e preparação dos dados do dashboard
- `notebooks/` – limpeza do JSON do INCT e análise exploratória (EDA)
- `relatorios/` – `base_dados.pdf`, `limpeza_dados.pdf`, `dashboard.pdf` e registro de uso de IA
- `app/` – código do dashboard (Streamlit), `app/app.py`

## Fontes
- INCT SiMAI – simulação de inundação por nível do Guaíba: http://vhlab.com.br/INCT/floods/
- OpenStreetMap via Overpass API (licença ODbL): https://www.openstreetmap.org/copyright
- Limites dos bairros – Prefeitura de Porto Alegre (camada bairros_2016):
  https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/01_PUBLICACOES/bairros_2016/MapServer

## Uso de IA
Registro dos momentos em que ferramentas de IA foram usadas: ver `relatorios/uso_ia.md`.
