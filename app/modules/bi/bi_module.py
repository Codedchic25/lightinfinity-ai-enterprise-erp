import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from app.core.base import Ceara, Comanda, Culoare, Lumanare, Parfum, Productie
from app.db.connection import SessionLocal


def render_bi_module():
    st.header("📈 Interogări BI & Analize Financiare")
    st.caption(
        "Sistem Business Intelligence conectat sincron la baza de date pentru calcularea indicatorilor de performanță (KPIs)."
    )
    st.markdown("<br>", unsafe_allow_html=True)

    db = SessionLocal()
    try:
        comenzi = db.query(Comanda).all()
        loturi = db.query(Productie).all()
        produse = db.query(Lumanare).all()

        # Încărcăm nomenclatoarele complete pentru a afișa TOATE elementele existente
        toate_ceurile_db = db.query(Ceara).all()
        toate_parfumurile_db = db.query(Parfum).all()
        toate_culorile_db = db.query(Culoare).all()

        OPTIUNI_FITIL = ["Bumbac Organic", "Lemn Pocnitor Premium", "Fitil Dublu Textil", "Fără Fitil (Topitură)"]

        # Calcul indicatori de performanță superiori
        total_venituri = sum(float(c.total) for c in comenzi)
        numar_tranzactii = len(comenzi)
        stoc_total = sum(p.stoc for p in produse)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="Venituri Totale (RON)", value=f"{total_venituri:,.2f} RON", delta=f"{numar_tranzactii} comenzi"
            )
        with col2:
            st.metric(label="Volum Total Producție", value=f"{sum(p.cantitate for p in loturi)} unități")
        with col3:
            st.metric(label="Volum Curent Depozit", value=f"{stoc_total} buc")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📊 Matrice Analitică BI: Inventar Total Nomenclatoare (Inclusiv Stoc 0)")

        # Agregăm volumele de stoc din depozit
        stoc_parfumuri = {}
        stoc_culori = {}
        stoc_ceara = {}
        stoc_fitiluri = {}

        for p in produse:
            nume_p = p.parfum.nume_parfum if p.parfum else "Nespecificat"
            nume_c = p.culoare.nume_culoare if p.culoare else "Nespecificat"
            nume_cx = p.ceara.nume_ceara if p.ceara else "Nespecificat"

            fitil_curent = "Nespecificat"
            for f in OPTIUNI_FITIL:
                if f in p.nume:
                    fitil_curent = f
                    break

            stoc_parfumuri[nume_p] = stoc_parfumuri.get(nume_p, 0) + p.stoc
            stoc_culori[nume_c] = stoc_culori.get(nume_c, 0) + p.stoc
            stoc_ceara[nume_cx] = stoc_ceara.get(nume_cx, 0) + p.stoc
            stoc_fitiluri[fitil_curent] = stoc_fitiluri.get(fitil_curent, 0) + p.stoc

        # Mapăm listele integrale - dacă stocul nu există, va rezulta automat valoarea 0
        date_ceara = [
            {"Ceara": c.nume_ceara, "Stoc": stoc_ceara.get(c.nume_ceara, 0)} for c in toate_ceurile_db if c.nume_ceara
        ]
        date_parfumuri = [
            {"Parfum": p.nume_parfum, "Stoc": stoc_parfumuri.get(p.nume_parfum, 0)}
            for p in toate_parfumurile_db
            if p.nume_parfum
        ]
        date_culori = [
            {"Culoare": c.nume_culoare, "Stoc": stoc_culori.get(c.nume_culoare, 0)}
            for c in toate_culorile_db
            if c.nume_culoare
        ]
        date_fitil = [{"Fitil": f, "Stoc": stoc_fitiluri.get(f, 0)} for f in OPTIUNI_FITIL]

        df_ceara = pd.DataFrame(date_ceara, columns=["Ceara", "Stoc"])
        df_parfumuri = pd.DataFrame(date_parfumuri, columns=["Parfum", "Stoc"])
        df_culori = pd.DataFrame(date_culori, columns=["Culoare", "Stoc"])
        df_fitil = pd.DataFrame(date_fitil, columns=["Fitil", "Stoc"])

        # Generăm structura finală de 4 coloane analitice paralele
        fig = make_subplots(
            rows=1,
            cols=4,
            subplot_titles=(
                "🪵 Toate Tipurile de Ceară",
                "🧪 Toate Esențele de Parfum",
                "🎨 Toate Culorile în Catalog",
                "🧵 Toate Fitilurile Enterprise",
            ),
            horizontal_spacing=0.06,
        )

        # --- SUBPLOT 1: CEARĂ ---
        fig.add_trace(
            go.Bar(
                x=df_ceara["Ceara"],
                y=df_ceara["Stoc"],
                name="Stoc Curent (buc)",
                marker_color="#00FFA3",
                showlegend=True,
            ),
            row=1,
            col=1,
        )

        # --- SUBPLOT 2: PARFUMURI ---
        fig.add_trace(
            go.Bar(
                x=df_parfumuri["Parfum"],
                y=df_parfumuri["Stoc"],
                name="Stoc Curent (buc)",
                marker_color="#00FFA3",
                showlegend=False,
            ),
            row=1,
            col=2,
        )

        # --- SUBPLOT 3: CULORI ---
        fig.add_trace(
            go.Bar(
                x=df_culori["Culoare"],
                y=df_culori["Stoc"],
                name="Stoc Curent (buc)",
                marker_color="#00FFA3",
                showlegend=False,
            ),
            row=1,
            col=3,
        )

        # --- SUBPLOT 4: FITILURI ---
        fig.add_trace(
            go.Bar(
                x=df_fitil["Fitil"],
                y=df_fitil["Stoc"],
                name="Stoc Curent (buc)",
                marker_color="#00FFA3",
                showlegend=False,
            ),
            row=1,
            col=4,
        )

        # Configurare layout premium fluid
        fig.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=480,
            margin=dict(l=15, r=15, t=60, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5, font=dict(color="#FFFFFF")),
        )

        for annot in fig["layout"]["annotations"]:
            annot["font"] = dict(color="#00FFA3", size=13, family="Courier New")

        fig.update_xaxes(tickfont=dict(color="#FFFFFF", size=9), gridcolor="#1E232E")
        fig.update_yaxes(tickfont=dict(color="#FFFFFF", size=9), gridcolor="#1E232E")

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    except Exception as e:
        st.error(f"Eroare agregare BI: {e}")
    finally:
        db.close()
