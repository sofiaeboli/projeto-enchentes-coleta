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
Link: (em construção)

## Como rodar

Requisitos: Python 3 e as bibliotecas do `requirements.txt`.

```bash
# 1. Clonar o repositório e entrar na pasta
git clone <url-do-repositorio>
cd projeto-enchentes-coleta

# 2. (Opcional) criar um ambiente virtual
python -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Baixar as bases externas (rodar a partir da raiz do repositório)
python scripts/coletar_osm.py      # serviços essenciais (OpenStreetMap) -> dados/originais/osm/
python scripts/coletar_bairros.py  # limites dos bairros (Prefeitura)   -> dados/originais/bairros/
```

5. Limpeza do JSON do INCT: `notebooks/analise_inical_json.ipynb`
   (lê `dados/originais/dados_inct.json` e gera `dados/tratados/dados_inct_limpo.json`).
6. Análise exploratória: `notebooks/EDA.ipynb` (usa o JSON limpo e as bases externas).

Os dados das bases externas não ficam no GitHub (tamanho e licenças de cada fonte);
os scripts registram a data da coleta em um arquivo `COLETA.txt` dentro de cada pasta.

## Estrutura
- `dados/originais/` – dados como vieram (JSON do INCT; `osm/` e `bairros/` são gerados pelos scripts)
- `dados/tratados/` – JSON do INCT limpo, em formato longo (`dados_inct_limpo.json`)
- `dados/processados/` – dados preparados para o dashboard (Fase 3)
- `scripts/` – scripts de coleta das bases externas
- `notebooks/` – limpeza do JSON do INCT e análise exploratória (EDA)
- `relatorios/` – relatórios em PDF (`base_dados.pdf`, `limpeza_dados.pdf`) e registro de uso de IA
- `app/` – código do dashboard

## Uso de IA
Registro dos momentos em que ferramentas de IA foram usadas: ver `relatorios/uso_ia.md`.
