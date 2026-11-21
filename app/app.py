

"""
Dashboard de enchentes em Porto Alegre (INCT SiMAI).
Rodar a partir da raiz do repositório:  streamlit run app/app.py
"""
import json
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from shapely.geometry import shape

RAIZ = Path(__file__).resolve().parents[1]
PICO_2024 = 5.35

st.set_page_config(page_title="Enchentes em Porto Alegre", layout="wide")


# ---------- aparência dos gráficos ----------
# Sem cores de texto fixas: o Streamlit ajusta o texto dos gráficos ao tema (claro/escuro).
def base_grafico():
    return dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="IBM Plex Sans, sans-serif", size=13))


def cores():
    # tons de azul que funcionam nos dois temas
    return dict(linha="#4A90D9", barra="#4A90D9", pico="#D9962B", cinza="#E5E7EB")


# ---------- utilidades ----------
def normalizar(nome):
    nome = unicodedata.normalize("NFKD", str(nome))
    nome = "".join(c for c in nome if not unicodedata.combining(c))
    nome = nome.replace("'", " ").replace("’", " ").replace("-", " ")
    return " ".join(nome.upper().split())


def n(x):
    """Número com ponto de milhar (padrão brasileiro)."""
    return f"{x:,.0f}".replace(",", ".")


def dec(x, casas=1):
    return f"{x:.{casas}f}".replace(".", ",")


@st.cache_data
def carregar():
    df = pd.read_json(RAIZ / "dados/tratados/dados_inct_limpo.json")
    df["chave"] = df["bairro"].apply(normalizar)
    df["nivel_m"] = df["nivel_m"].round(1)
    df["pct"] = np.where(
        df["total_buildings"] > 0, df["affected_buildings"] / df["total_buildings"] * 100, 0
    )
    with open(RAIZ / "dados/processados/bairros_poa_94.geojson", encoding="utf-8") as f:
        geo = json.load(f)
    pontos = {}
    for feat in geo["features"]:
        p = shape(feat["geometry"]).representative_point()
        pontos[feat["properties"]["chave"]] = (p.x, p.y)
    fontes = (RAIZ / "dados/processados/FONTES.txt").read_text(encoding="utf-8")
    datas = re.findall(r"Data da coleta: (\d{4})-(\d{2})-(\d{2})", fontes)
    data_coleta = f"{datas[0][2]}/{datas[0][1]}/{datas[0][0]}" if datas else "ver FONTES.txt"
    return df, geo, pontos, data_coleta


df, geo, pontos, DATA_COLETA = carregar()

ESCALA = [
    [0.0, "#EAF2FA"], [0.05, "#C6DBEF"], [0.15, "#9ECAE1"],
    [0.35, "#4292C6"], [0.65, "#08519C"], [1.0, "#08306B"],
]


def rodape():
    st.divider()
    st.caption(
        "**Fontes:** INCT SiMAI (simulação, arquivo JSON fornecido pelo instituto) · "
        "[OpenStreetMap](https://www.openstreetmap.org/copyright) via "
        "[Overpass API](https://overpass-api.de), licença ODbL · "
        "[Limites dos bairros, Prefeitura de Porto Alegre (UMDU/SMUrb)]"
        "(https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/01_PUBLICACOES/bairros_2016/MapServer). "
        f"Bases externas coletadas em {DATA_COLETA}."
    )


def cartao(rotulo, valor, nota):
    """Número grande com rótulo em cima e nota embaixo."""
    st.markdown(
        f'<div style="line-height:1.25">'
        f'<div style="font-size:1rem;opacity:.8">{rotulo}</div>'
        f'<div style="font-size:3.2rem;font-weight:600;line-height:1.15;margin:.15rem 0">{valor}</div>'
        f'<div style="font-size:.9rem;opacity:.65">{nota}</div></div>',
        unsafe_allow_html=True)


# ---------- mapa ----------
def mapa(dn, mostrar_nomes, mostrar_pct, limite, fundo, altura=700):
    dn = dn.copy()
    dn["hover"] = (
        "<b>" + dn["bairro"] + "</b><br>" + dn["pct"].map(lambda v: dec(v)) + "% dos prédios afetados<br>"
        + dn["affected_buildings"].map(n) + " de " + dn["total_buildings"].map(n) + " prédios<br>"
        + dn["affected_population"].map(n) + " pessoas afetadas (estimativa)"
    )   + dn["affected_buildings"].map(n) + " prédios · " + dn["affected_population"].map(n) + " pessoas"
    acima = dn[dn["pct"] >= limite]
    abaixo = dn[dn["pct"] < limite]

    fig = go.Figure()
    comum = dict(geojson=geo, featureidkey="properties.chave", marker_line_width=0.6,
                 marker_line_color="white", hoverinfo="text", below="")
    if len(abaixo):
        fig.add_trace(go.Choroplethmap(
            locations=abaixo["chave"], z=[0] * len(abaixo), hovertext=abaixo["hover"],
            colorscale=[[0, cores()["cinza"]], [1, cores()["cinza"]]], showscale=False, **comum))
    if len(acima):
        fig.add_trace(go.Choroplethmap(
            locations=acima["chave"], z=acima["pct"], hovertext=acima["hover"],
            colorscale=ESCALA, zmin=0, zmax=100,
            colorbar=dict(title="% de prédios<br>afetados", thickness=12, len=0.6), **comum))

    if mostrar_nomes or mostrar_pct:
        for escuro, parte in ((False, dn[dn["pct"] < 40]), (True, dn[dn["pct"] >= 40])):
            if parte.empty:
                continue
            textos = []
            for _, r in parte.iterrows():
                linhas = []
                if mostrar_nomes:
                    linhas.append(r["bairro"])
                if mostrar_pct and r["pct"] >= 0.5:
                    linhas.append(f"{dec(r['pct'], 0)}%")
                textos.append("<br>".join(linhas))
            fig.add_trace(go.Scattermap(
                lon=[pontos[c][0] for c in parte["chave"]], lat=[pontos[c][1] for c in parte["chave"]],
                mode="text", text=textos, hoverinfo="skip", showlegend=False,
                textfont=dict(family="IBM Plex Sans, sans-serif", size=11, color="#FFFFFF" if escuro else "#1F2937")))

    fig.update_layout(
        map=dict(style=fundo, center=dict(lat=-30.10, lon=-51.16), zoom=10.6),
        margin=dict(l=0, r=0, t=0, b=0), height=altura, showlegend=False, **base_grafico(),
    )
    return fig


# ---------- Tela 1 ----------
def tela1(nivel, topn, mostrar_nomes, mostrar_pct, limite, fundo):
    st.title("Enchentes em Porto Alegre: o que acontece em cada nível do Guaíba?")
    st.info("A população afetada supõe pessoas distribuídas igualmente entre as construções de cada bairro.")

    dn = df[df["nivel_m"] == round(nivel, 1)].copy()
    atingidos = dn[dn["affected_buildings"] > 0]

    st.subheader(f"Nível do Guaíba: {dec(nivel)} m")
    if abs(nivel - PICO_2024) <= 0.05:
        st.caption("Perto do pico da enchente de maio de 2024 (5,35 m).")

    c1, c2, c3 = st.columns(3)
    with c1:
        cartao("Pessoas afetadas (estimativa)", n(dn["affected_population"].sum()),
               f"de {n(dn['population'].sum())} moradores (Censo 2022)")
    with c2:
        cartao("Prédios afetados (estimativa)", n(dn["affected_buildings"].sum()),
               f"de {n(dn['total_buildings'].sum())} prédios (OpenStreetMap)")
    with c3:
        cartao("Bairros com algum prédio afetado", f"{len(atingidos)} de {dn['bairro'].nunique()}",
               "neste nível do Guaíba")

    st.markdown("#### Mapa dos bairros, coloridos pelo % de prédios afetados")
    st.plotly_chart(mapa(dn, mostrar_nomes, mostrar_pct, limite, fundo), width="stretch",
                    config={"scrollZoom": True, "displaylogo": False})
    st.caption("Use a roda do mouse (ou os dois dedos) para dar zoom e arraste para mover o mapa. "
               "Os controles dos nomes, do % e do destaque ficam na barra lateral.")

    esq, dir_ = st.columns(2)

    with esq:
        st.markdown(f"#### % de prédios afetados: {topn} bairros com maior percentual")
        top = atingidos.sort_values("pct", ascending=False).head(topn).sort_values("pct")
        if top.empty:
            st.write("Nenhum bairro com prédio afetado neste nível.")
        else:
            fig = go.Figure(go.Bar(
                x=top["pct"], y=top["bairro"], orientation="h", marker_color=cores()["barra"],
                text=top["pct"].map(lambda v: dec(v) + "%"), textposition="outside",
                hovertemplate="%{y}: %{x:.1f}%<extra></extra>"))
            fig.update_layout(**base_grafico(), height=max(300, 28 * len(top) + 80),
                              xaxis_title="% de prédios afetados", xaxis_range=[0, 120],
                              margin=dict(l=0, r=10, t=10, b=0))
            st.plotly_chart(fig, width="stretch")

    with dir_:
        st.markdown("#### População afetada na cidade, por nível do Guaíba")
        curva = df.groupby("nivel_m", as_index=False)["affected_population"].sum()
        fig = go.Figure(go.Scatter(x=curva["nivel_m"], y=curva["affected_population"], mode="lines",
                                   line=dict(color=cores()["linha"], width=3),
                                   hovertemplate="%{x:.1f} m: %{y:,.0f} pessoas<extra></extra>"))
        atual = curva[curva["nivel_m"] == round(nivel, 1)]
        fig.add_trace(go.Scatter(x=atual["nivel_m"], y=atual["affected_population"], mode="markers",
                                 marker=dict(size=12, color="white", line=dict(color=cores()["linha"], width=3)),
                                 hoverinfo="skip", showlegend=False))
        fig.add_vline(x=PICO_2024, line_dash="dash", line_color=cores()["pico"],
                      annotation_text="5,35 m · pico de maio de 2024", annotation_position="top left")
        fig.update_layout(**base_grafico(), height=max(300, 28 * topn + 80), showlegend=False,
                          xaxis_title="Nível do Guaíba (m)", yaxis_title="Pessoas afetadas (estimativa)",
                          yaxis_rangemode="tozero", margin=dict(l=0, r=10, t=10, b=0))
        st.plotly_chart(fig, width="stretch")

    st.markdown(f"#### Ranking dos {topn} bairros mais afetados")
    ordem = st.radio("Ordenar por", ["Pessoas afetadas", "% de prédios afetados"], horizontal=True)
    chave_ordem = "affected_population" if ordem == "Pessoas afetadas" else "pct"
    rank = atingidos.sort_values(chave_ordem, ascending=False).head(topn)
    tabela = pd.DataFrame({
        "#": range(1, len(rank) + 1),
        "Bairro": rank["bairro"].values,
        "Pessoas afetadas": rank["affected_population"].map(n).values,
        "% de prédios": rank["pct"].map(lambda v: dec(v) + "%").values,
        "Prédios afetados": rank["affected_buildings"].map(n).values,
    })
    st.dataframe(tabela, hide_index=True, width="stretch")
    rodape()


# ---------- Tela 2 (em construção) ----------
def tela2(nivel, topn, mostrar_nomes, mostrar_pct, limite, fundo):
    st.title("Que serviços essenciais ficam em bairros atingidos?")
    st.info("Tela 2 em construção.")
    rodape()


# ---------- barra lateral ----------
st.sidebar.title("Enchentes em Porto Alegre")
tela = st.sidebar.radio("Tela", ["Tela 1: Simulação (INCT)", "Tela 2: Serviços essenciais"])
nivel = st.sidebar.slider("Nível do Guaíba (m)", 3.0, 10.0, 5.3, 0.1, format="%.1f",
                          help="O pico da enchente de maio de 2024 foi de 5,35 m.")
st.sidebar.markdown("**Mapa**")
fundo_nome = st.sidebar.selectbox("Fundo do mapa", ["Com ruas", "Sem fundo"])
fundo = "carto-positron-nolabels" if fundo_nome == "Com ruas" else "white-bg"
mostrar_nomes = st.sidebar.checkbox("Mostrar nomes dos bairros", value=False)
mostrar_pct = st.sidebar.checkbox("Mostrar % de prédios afetados no bairro", value=False)
limite = st.sidebar.slider("Destacar bairros com mais de (% de prédios afetados)", 0, 100, 0, 1,
                           help="Os bairros abaixo desse valor ficam cinza. Em 0, todos ficam coloridos.")
topn = st.sidebar.slider("Quantos bairros mostrar nos gráficos", 5, 30, 10, 1)

if tela.startswith("Tela 1"):
    tela1(nivel, topn, mostrar_nomes, mostrar_pct, limite, fundo)
else:
    tela2(nivel, topn, mostrar_nomes, mostrar_pct, limite, fundo)