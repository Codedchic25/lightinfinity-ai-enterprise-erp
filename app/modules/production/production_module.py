from datetime import UTC, datetime

import streamlit as st

from app.core.base import Ceara, Culoare, Forma, Lumanare, Parfum, Productie
from app.db.connection import SessionLocal


def render_production_module():
    st.header("🏭 Management Producție & Monitorizare Loturi")
    st.caption(
        "Planificarea șarjelor de turnare, monitorizarea istoricului și actualizarea automată a stocurilor comerciale Enterprise."
    )
    st.markdown("<br>", unsafe_allow_html=True)

    data_curenta_sigura = datetime.now(UTC).date()
    db = SessionLocal()

    try:
        # Preluăm loturile și nomenclatoarele din SQLite
        loturi = db.query(Productie).all()
        lumanari = db.query(Lumanare).all()
        f_db = db.query(Forma).all()
        c_db = db.query(Ceara).all()
        p_db = db.query(Parfum).all()
        cl_db = db.query(Culoare).all()

        # Listă statică completă pentru tipurile de fitil, în perfectă armonie cu Catalogul
        OPTIUNI_FITIL = ["Bumbac Organic", "Lemn Pocnitor Premium", "Fitil Dublu Textil", "Fără Fitil (Topitură)"]

        # =====================================================================
        # 1. METRICI / KPI-URI LIVE
        # =====================================================================
        col_m1, col_m2, col_m3 = st.columns(3)
        total_loturi = len(loturi)
        total_bucati = sum(l.cantitate for l in loturi)

        with col_m1:
            st.metric(label="Total Șarje / Loturi Turnate", value=str(total_loturi))
        with col_m2:
            st.metric(label="Volum Total Fabricat", value=f"{total_bucati} buc")
        with col_m3:
            st.metric(label="Status Eficiență Laborator", value="100% Optim")

        st.markdown("<br>", unsafe_allow_html=True)

        tab_istoric, tab_lansare = st.tabs(
            [
                "📋 Registru Loturi Fabricate",
                "⚡ Înregistrare Lot Nou (Turnare)",
            ]
        )

        # =====================================================================
        # TAB 1: ISTORIC JURNAL DE FABRICARE
        # =====================================================================
        with tab_istoric:
            st.subheader("Jurnalul Oficial de Fabricare")

            date_loturi = []
            for lot in loturi:
                if lot.lumanare:
                    nume_p = lot.lumanare.parfum.nume_parfum if lot.lumanare.parfum else "Nespecificat"
                    nume_f = lot.lumanare.forma.nume_forma if lot.lumanare.forma else "Nespecificat"
                    nume_cl = lot.lumanare.culoare.nume_culoare if lot.lumanare.culoare else "Nespecificat"
                    nume_model = lot.lumanare.nume
                else:
                    nume_p = nume_f = nume_cl = "Nespecificat"
                    nume_model = f"Model ID {lot.id_lumanare}"

                if lot.data_productie:
                    if hasattr(lot.data_productie, "strftime"):
                        data_afisare = lot.data_productie.strftime("%Y-%m-%d")
                    else:
                        data_afisare = str(lot.data_productie)
                else:
                    data_afisare = data_curenta_sigura.strftime("%Y-%m-%d")

                date_loturi.append(
                    {
                        "ID Lot": lot.id_productie,
                        "Denumire Comercială": nume_model,
                        "Formă Geometrică": nume_f,
                        "Culoare Turnată": nume_cl,
                        "Aromă / Parfum": nume_p,
                        "Dată Fabricare": data_afisare,
                        "Cantitate (buc)": lot.cantitate,
                    }
                )

            if date_loturi:
                st.dataframe(
                    date_loturi,
                    width="stretch",
                    hide_index=True,
                    key="df_jurnal_unic_direct_2026",
                )
            else:
                st.info("Nu există loturi înregistrate în istoricul fabricii.")

        # =====================================================================
        # TAB 2: LANSARE ȘARJĂ NOUĂ (MATRICE COMPLETĂ 5D)
        # =====================================================================
        with tab_lansare:
            st.subheader("Raportează o Șarjă Nouă Completată")

            if not lumanari:
                st.warning("⚠️ Adaugă mai întâi produse în catalog pentru a le putea introduce în producție.")
                return

            # Extragem opțiunile din nomenclatoarele corect inițializate
            toate_formele = sorted(list({f.nume_forma for f in f_db if f.nume_forma}))
            toate_ceurile = sorted(list({c.nume_ceara for c in c_db if c.nume_ceara}))
            toate_parfumurile = sorted(list({p.nume_parfum for p in p_db if p.nume_parfum}))
            toate_culorile = sorted(list({cl.nume_culoare for cl in cl_db if cl.nume_culoare}))

            with st.form("form_productie_real_bulk_unificat_v2", clear_on_submit=True):
                st.markdown("##### 🔍 Selectează criteriile de turnare pentru lot:")

                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    forma_selectata = st.multiselect(
                        "Filtrează după Formă (**Lasă gol pentru TOATE**):",
                        options=toate_formele,
                        placeholder="Alege formele geometrice...",
                    )
                    ceara_selectata = st.multiselect(
                        "Filtrează după Tip Ceară (**Lasă gol pentru TOATE**):",
                        options=toate_ceurile,
                        placeholder="Alege tipurile de ceară...",
                    )
                with col_p2:
                    parfum_selectat = st.multiselect(
                        "Filtrează după Esențe Parfum (**Lasă gol pentru TOATE**):",
                        options=toate_parfumurile,
                        placeholder="Alege aromele folosite...",
                    )
                    culoare_selectata = st.multiselect(
                        "Filtrează după Culoare (**Lasă gol pentru TOATE**):",
                        options=toate_culorile,
                        placeholder="Alege culorile intrate la turnare...",
                    )

                # 🔥 NOU: A cincea axă obligatorie - Selecția de fitil pentru turnare
                fitil_selectat = st.multiselect(
                    "Filtrează după Tip Fitil (**Lasă gol pentru TOATE**):",
                    options=OPTIUNI_FITIL,
                    placeholder="Alege fitilurile folosite la șarjă...",
                )

                st.markdown("---")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    cantitate_turnata = st.number_input(
                        "Cantitate realizată per model (buc):", min_value=1, value=25, step=5
                    )
                with col_c2:
                    data_sarjei = st.date_input("Data turnării lotului:", data_curenta_sigura)

                st.caption(
                    "💡 Sistemul va scana depozitul și va actualiza stocul pentru toate modelele care respectă simultan cele 5 criterii selectate."
                )
                buton_bulk_productie = st.form_submit_button("🏭 Înregistrează și Actualizează Stocurile Sincron")

            if buton_bulk_productie:
                # Regula implicită: dacă e gol, selectăm tot din nomenclatoare
                filtru_forma = forma_selectata if forma_selectata else toate_formele
                filtru_ceara = ceara_selectata if ceara_selectata else toate_ceurile
                filtru_parfum = parfum_selectat if parfum_selectat else toate_parfumurile
                filtru_culoare = culoare_selectata if culoare_selectata else toate_culorile
                filtru_fitil = fitil_selectat if fitil_selectat else OPTIUNI_FITIL

                # Căutăm lumânările din DB care se potrivesc cu TOATE cele 5 filtre
                modele_tinta = []
                for lum in lumanari:
                    nume_f = lum.forma.nume_forma if lum.forma else None
                    nume_c = lum.ceara.nume_ceara if lum.ceara else None
                    nume_p = lum.parfum.nume_parfum if lum.parfum else None
                    nume_cl = lum.culoare.nume_culoare if lum.culoare else None

                    # Extragem fitilul stocat text în denumire
                    fitil_produs = "Nespecificat"
                    for f in OPTIUNI_FITIL:
                        if f in lum.nume:
                            fitil_produs = f
                            break

                    if (
                        nume_f in filtru_forma
                        and nume_c in filtru_ceara
                        and nume_p in filtru_parfum
                        and nume_cl in filtru_culoare
                        and fitil_produs in filtru_fitil
                    ):
                        modele_tinta.append(lum)

                if not modele_tinta:
                    st.error(
                        "❌ Nu s-a găsit niciun model configurat în Catalog care să respecte această matrice de 5 criterii."
                    )
                else:
                    contor_loturi = 0
                    total_bucati_adaugate = 0

                    for lum in modele_tinta:
                        nou_lot = Productie(
                            id_lumanare=lum.id_lumanare,
                            cantitate=cantitate_turnata,
                            data_productie=data_sarjei,
                        )
                        db.add(nou_lot)
                        lum.stoc += cantitate_turnata

                        contor_loturi += 1
                        total_bucati_adaugate += cantitate_turnata

                    db.commit()
                    st.success(
                        f"🎉 Succes! S-au înregistrat {contor_loturi} șarje noi. "
                        f"Inventarul a crescut automat cu +{total_bucati_adaugate} bucăți."
                    )
                    st.balloons()
                    st.rerun()

    except Exception as e:
        db.rollback()
        st.error(f"Eroare la procesarea modulului de producție: {e}")
    finally:
        db.close()
