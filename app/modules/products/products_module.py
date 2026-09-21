import itertools
from decimal import Decimal

import streamlit as st

from app.core.base import Ceara, Culoare, Forma, Lumanare, Parfum, Sezon
from app.db.connection import SessionLocal


def render_products_module():
    st.header("📦 Catalog Dynamic de Produse Finisate")
    st.caption(
        "Centrul de control pentru nomenclatorul de produse, prețuri de listă, fitiluri și stocuri comerciale Enterprise."
    )
    st.markdown("<br>", unsafe_allow_html=True)

    db = SessionLocal()
    try:
        produse = db.query(Lumanare).all()
        ceara_list = db.query(Ceara).all()
        parfum_list = db.query(Parfum).all()
        forme_list = db.query(Forma).all()
        culori_list = db.query(Culoare).all()
        sezoane_list = db.query(Sezon).all()

        OPTIUNI_FITIL = ["Bumbac Organic", "Lemn Pocnitor Premium", "Fitil Dublu Textil", "Fără Fitil (Topitură)"]

        # KPI-uri Live
        col_m1, col_m2, col_m3 = st.columns(3)
        total_modele = len(produse)
        valoare_stoc = sum(float(p.pret) * p.stoc for p in produse)
        stocuri_critice = sum(1 for p in produse if p.stoc <= 5)

        with col_m1:
            st.metric(label="Total Modele Active", value=str(total_modele))
        with col_m2:
            st.metric(label="Valoare Estimata Stoc (RON)", value=f"{valoare_stoc:,.2f}")
        with col_m3:
            st.metric(label="Alerte Stoc Critic (<=5 buc)", value=str(stocuri_critice))

        st.markdown("<br>", unsafe_allow_html=True)

        tab_registru, tab_unic, tab_bulk = st.tabs(
            ["📋 Registru Central", "⚡ Adăugare Model Unic", "🚀 Generare Matriceală (Bulk)"]
        )

        # =====================================================================
        # TAB 1: REGISTRU CENTRAL (TABEL LIVE)
        # =====================================================================
        with tab_registru:
            st.subheader("🔍 Filtre Matriceale Avansate")
            r1_c1, r1_c2, r1_c3 = st.columns(3)
            with r1_c1:
                ceara_unice = sorted(list(set(c.nume_ceara for c in ceara_list if c.nume_ceara)))
                f_ceara = st.selectbox("1. Filtru Tip Ceară:", ["Toate tipurile"] + ceara_unice, key="f_cx_matrice")
            with r1_c2:
                parfumuri_unice = sorted(list(set(p.nume_parfum for p in parfum_list if p.nume_parfum)))
                f_parfum = st.selectbox(
                    "2. Filtru Esență Parfum:", ["Toate esențele"] + parfumuri_unice, key="f_pf_matrice"
                )
            with r1_c3:
                forme_unice = sorted(list(set(f.nume_forma for f in forme_list if f.nume_forma)))
                f_forma = st.selectbox(
                    "3. Filtru Formă Geometrică:", ["Toate formele"] + forme_unice, key="f_fr_matrice"
                )

            r2_c1, r2_c2, r2_c3 = st.columns(3)
            with r2_c1:
                culori_unice = sorted(list(set(cl.nume_culoare for cl in culori_list if cl.nume_culoare)))
                f_culoare = st.selectbox(
                    "4. Filtru Culoare Alocată:", ["Toate culorile"] + culori_unice, key="f_cl_matrice"
                )
            with r2_c2:
                f_fitil = st.selectbox("5. Filtru Tip Fitil:", ["Toate fitilurile"] + OPTIUNI_FITIL, key="f_ft_matrice")
            with r2_c3:
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

            st.markdown("---")
            st.subheader("📊 Date Live din Inventarul Gestiunii")

            date_produse = []
            for p in produse:
                nume_c = p.ceara.nume_ceara.strip() if p.ceara else "Nespecificat"
                nume_p = p.parfum.nume_parfum.strip() if p.parfum else "Nespecificat"
                nume_f = p.forma.nume_forma.strip() if p.forma else "Nespecificat"
                nume_cl = p.culoare.nume_culoare.strip() if p.culoare else "Nespecificat"

                fitil_curent = "Bumbac Organic"
                for f in OPTIUNI_FITIL:
                    if f.lower() in p.nume.lower():
                        fitil_curent = f
                        break

                if f_ceara != "Toate tipurile" and nume_c.lower() != f_ceara.strip().lower():
                    continue
                if f_parfum != "Toate esențele" and nume_p.lower() != f_parfum.strip().lower():
                    continue
                if f_forma != "Toate formele" and nume_f.lower() != f_forma.strip().lower():
                    continue
                if f_culoare != "Toate culorile" and nume_cl.lower() != f_culoare.strip().lower():
                    continue
                if f_fitil != "Toate fitilurile" and fitil_curent.lower() != f_fitil.strip().lower():
                    continue

                date_produse.append(
                    {
                        "ID": p.id_lumanare,
                        "Denumire Model Comercial": p.nume,
                        "Formă Geometrică": nume_f,
                        "Culoare Alocată": nume_cl,
                        "Tip Ceară": nume_c,
                        "Esență Parfum": nume_p,
                        "Fitil Utilizat": fitil_curent,
                        "Preț de Listă (RON)": float(p.pret),
                        "Stoc Disponibil (buc)": p.stoc,
                    }
                )

            if date_produse:
                st.dataframe(date_produse, width="stretch", hide_index=True, key="grid_central_produse_2026")

                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("⚠️ Zonă Securizată: Elimină Produse din Catalog"):
                    lista_id_stergere = [p["ID"] for p in date_produse]
                    id_ales = st.selectbox("Alege ID-ul modelului:", lista_id_stergere, key="sb_del_matriceal_final")
                    nume_prod_ales = next(p["Denumire Model Comercial"] for p in date_produse if p["ID"] == id_ales)

                    if st.button(f"🗑️ Elimină definitiv modelul: {nume_prod_ales}", type="primary", width="stretch"):
                        prod_db = db.query(Lumanare).filter(Lumanare.id_lumanare == id_ales).first()
                        if prod_db:
                            db.delete(prod_db)
                            db.commit()
                            st.success("🗑️ Modelul a fost eliminat!")
                            st.rerun()
        # =====================================================================
        # TAB 2: ADĂUGARE MODEL UNIC
        # =====================================================================
        with tab_unic:
            st.subheader("⚡ Înregistrare Model Unic în Nomenclator")
            with st.form("form_adauga_lumanare_unica", clear_on_submit=True):
                nume_nou = st.text_input("Denumire Comercială Produs:", placeholder="Ex: Lumânare Elegantă de Sezon...")

                c1, c2, c3 = st.columns(3)
                with c1:
                    id_cx = st.selectbox(
                        "Tip Ceară:",
                        [c.id_ceara for c in ceara_list],
                        format_func=lambda x: next(c.nume_ceara for c in ceara_list if c.id_ceara == x),
                    )
                    id_sz = st.selectbox(
                        "Sezon Alocat:",
                        [s.id_sezon for s in sezoane_list],
                        format_func=lambda x: next(s.nume_sezon for s in sezoane_list if s.id_sezon == x),
                    )
                with c2:
                    id_fr = st.selectbox(
                        "Formă Geometrică:",
                        [f.id_forma for f in forme_list],
                        format_func=lambda x: next(f.nume_forma for f in forme_list if f.id_forma == x),
                    )
                    id_pf = st.selectbox(
                        "Esență Parfum:",
                        [p.id_parfum for p in parfum_list],
                        format_func=lambda x: next(p.nume_parfum for p in parfum_list if p.id_parfum == x),
                    )
                with c3:
                    id_cl = st.selectbox(
                        "Culoare Alocată:",
                        [cl.id_culoare for cl in culori_list],
                        format_func=lambda x: next(cl.nume_culoare for cl in culori_list if cl.id_culoare == x),
                    )
                    fitil_nou = st.selectbox("Tip Fitil Adăugat în Nume:", OPTIUNI_FITIL)

                st.markdown("---")
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    pret_nou = st.number_input("Preț de Listă (RON):", min_value=1.0, value=30.0, step=5.0)
                with col_p2:
                    stoc_nou = st.number_input("Stoc Inițial Disponibil (buc):", min_value=0, value=10, step=5)

                btn_salveaza_unic = st.form_submit_button(
                    "⚡ Înregistrează Modelul Sincron", type="primary", width="stretch"
                )

                if btn_salveaza_unic:
                    if nume_nou.strip():
                        nume_complet = f"{nume_nou.strip()} ({fitil_nou})"
                        lumanare_noua = Lumanare(
                            nume=nume_complet,
                            id_ceara=id_cx,
                            id_sezon=id_sz,
                            id_forma=id_fr,
                            id_parfum=id_pf,
                            id_culoare=id_cl,
                            pret=Decimal(str(pret_nou)),
                            stoc=stoc_nou,
                        )
                        db.add(lumanare_noua)
                        db.commit()
                        st.success(f"✅ Modelul '{nume_complet}' a fost înregistrat nativ!")
                        st.rerun()
                    else:
                        st.error("❌ Introdu o denumire validă pentru produs.")

        # =====================================================================
        # TAB 3: GENERARE MATRICEALĂ (BULK MULTIPLIER)
        # =====================================================================
        with tab_bulk:
            st.subheader("🚀 Generator Matriceal de Înaltă Productivitate (Bulk)")
            st.caption(
                "Selectează multipli parametri. Sistemul va rula produsul cartezian (itertools.product) și va genera automat toate combinațiile unice lipsă."
            )

            with st.form("form_bulk_matrix_generator"):
                bulk_forme = st.multiselect(
                    "Selectează Forme:",
                    [f.id_forma for f in forme_list],
                    format_func=lambda x: next(f.nume_forma for f in forme_list if f.id_forma == x),
                )
                bulk_ceari = st.multiselect(
                    "Selectează Ceară:",
                    [c.id_ceara for c in ceara_list],
                    format_func=lambda x: next(c.nume_ceara for c in ceara_list if c.id_ceara == x),
                )
                bulk_parfumuri = st.multiselect(
                    "Selectează Parfumuri:",
                    [p.id_parfum for p in parfum_list],
                    format_func=lambda x: next(p.nume_parfum for p in parfum_list if p.id_parfum == x),
                )
                bulk_culori = st.multiselect(
                    "Selectează Culori:",
                    [cl.id_culoare for cl in culori_list],
                    format_func=lambda x: next(cl.nume_culoare for cl in culori_list if cl.id_culoare == x),
                )
                bulk_fitiluri = st.multiselect("Selectează Fitiluri:", OPTIUNI_FITIL)

                st.markdown("---")
                b_c1, b_c2 = st.columns(2)
                with b_c1:
                    bulk_pret = st.number_input("Preț Standard Combinat (RON):", min_value=5.0, value=25.0)
                with b_c2:
                    bulk_stoc = st.number_input("Stoc Standard per Combinație (buc):", min_value=0, value=20)

                btn_genereaza_bulk = st.form_submit_button(
                    "🚀 Lansează Generarea Matriceală", type="primary", width="stretch"
                )

                if btn_genereaza_bulk:
                    if bulk_forme and bulk_ceari and bulk_parfumuri and bulk_culori and bulk_fitiluri:
                        produse_generate = 0
                        for f_id, cx_id, pf_id, cl_id, fitil_n in itertools.product(
                            bulk_forme, bulk_ceari, bulk_parfumuri, bulk_culori, bulk_fitiluri
                        ):
                            f_nume = next(f.nume_forma for f in forme_list if f.id_forma == f_id)
                            cl_nume = next(cl.nume_culoare for cl in culori_list if cl.id_culoare == cl_id)

                            nume_matriceal = f"{f_nume} {cl_nume} Matrix ({fitil_n})"

                            # Evităm duplicarea dacă modelul există deja în nomenclator
                            exista = db.query(Lumanare).filter(Lumanare.nume == nume_matriceal).first()
                            if not exista:
                                m_lumanare = Lumanare(
                                    nume=nume_matriceal,
                                    id_ceara=cx_id,
                                    id_sezon=1,  # Sezon implicit implicit
                                    id_forma=f_id,
                                    id_parfum=pf_id,
                                    id_culoare=cl_id,
                                    pret=Decimal(str(bulk_pret)),
                                    stoc=bulk_stoc,
                                )
                                db.add(m_lumanare)
                                produse_generate += 1

                        db.commit()
                        st.success(
                            f"🚀 Matrice activată! S-au generat automat {produse_generate} combinații noi în baza de date."
                        )
                        st.rerun()
                    else:
                        st.error(
                            "❌ Te rog selectează cel puțin o opțiune din fiecare categorie pentru a rula matricea."
                        )

    except Exception as e:
        st.error(f"Eroare structurală la procesarea catalogului: {e}")
    finally:
        db.close()
