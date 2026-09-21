import os
from decimal import Decimal

import pandas as pd
import streamlit as st

from app.core.base import Ceara, Client, Comanda, ComandaLumanare, Culoare, Forma, Lumanare, Parfum
from app.db.connection import SessionLocal


def render_storefront_module():
    st.header("🛍️ Light Infinity — E-Shop Online")
    st.caption("Configurator comercial matriceal. Selectează dinamic orice formă, parfum sau culoare din catalog.")
    st.markdown("<br>", unsafe_allow_html=True)

    # Inițializăm coșul de cumpărături în sesiune dacă nu există
    if "cos_cumparaturi" not in st.session_state:
        st.session_state.cos_cumparaturi = []

    FOLDER_POZE = "autogen_assets"
    if not os.path.exists(FOLDER_POZE):
        os.makedirs(FOLDER_POZE)

    # Citim direct utilizatorul autentificat global din dashboard.py
    user_email_curent = st.session_state.get("global_user_email", "utilizator@erp.local")

    # Bară superioară simplă de informare, perfect simetrică
    col_client_info, col_spatiu = st.columns([3, 1])
    with col_client_info:
        st.markdown(f"👤 Cont Client Activ în Magazin: `{user_email_curent}`")

    st.markdown("<br>", unsafe_allow_html=True)

    db = SessionLocal()
    try:
        lumanari_db = db.query(Lumanare).all()
        toate_ceurile = sorted(list(set(c.nume_ceara for c in db.query(Ceara).all() if c.nume_ceara)))
        toate_parfumurile = sorted(list(set(p.nume_parfum for p in db.query(Parfum).all() if p.nume_parfum)))
        toate_culorile = sorted(list(set(cl.nume_culoare for cl in db.query(Culoare).all() if cl.nume_culoare)))
        toate_formele_db = db.query(Forma).all()

        titlu_cos = f"🛒 Coș ({len(st.session_state.cos_cumparaturi)})"
        tab_magazin, tab_cos, tab_incarcare = st.tabs(
            ["🕯️ Catalog Produse Disponibile", titlu_cos, "📸 Încarcă Poze Produse"]
        )

        # =====================================================================
        # 2. CATALOG CONFIGURATOR MATRICEAL
        # =====================================================================
        with tab_magazin:
            st.subheader("✨ Configurează-ți Lumânarea Personalizată")
            st.markdown("<br>", unsafe_allow_html=True)

            if not toate_formele_db:
                st.info("Nomenclatorul de forme este gol. Rulează scriptul seed.py!")
            else:
                cols = st.columns(3)
                for idx, f_obj in enumerate(toate_formele_db):
                    col_curenta = cols[idx % 3]
                    gama_nume = f_obj.nume_forma

                    with col_curenta:
                        with st.container(border=True):
                            st.markdown(
                                f"<h4 style='text-align:center; color:#00FFA3;'>🕯️ Model: {gama_nume}</h4>",
                                unsafe_allow_html=True,
                            )
                            st.markdown("---")

                            sel_ceara = st.selectbox("Alege Tip Ceară:", toate_ceurile, key=f"shop_c_{idx}")
                            sel_parfum = st.selectbox("Alege Esență Parfum:", toate_parfumurile, key=f"shop_p_{idx}")
                            sel_culoare = st.selectbox("Alege Culoarea Alocată:", toate_culorile, key=f"shop_cl_{idx}")

                            potrivire_model = None
                            for l in lumanari_db:
                                cx_l = l.ceara.nume_ceara if l.ceara else ""
                                p_l = l.parfum.nume_parfum if l.parfum else ""
                                c_l = l.culoare.nume_culoare if l.culoare else ""
                                f_l = l.forma.nume_forma if l.forma else ""

                                if f_l == gama_nume and cx_l == sel_ceara and p_l == sel_parfum and c_l == sel_culoare:
                                    potrivire_model = l
                                    break

                            st.markdown("<br>", unsafe_allow_html=True)
                            # Afișare imagine dinamică pe baza selecției
                            nume_imagine = f"img_{gama_nume.replace(' ', '_')}_{sel_parfum.replace(' ', '_')}_{sel_culoare.replace(' ', '_')}.png"
                            cale_poza = os.path.join(FOLDER_POZE, nume_imagine)

                            if os.path.exists(cale_poza):
                                st.image(cale_poza, use_container_width=True)
                            else:
                                st.markdown(
                                    f"<div style='background-color:#111622; height:110px; border-radius:6px; "
                                    f"display:flex; align-items:center; justify-content:center; color:#7F8C8D; "
                                    f"font-size:0.82rem; border:1px dashed #00FFA3; margin-bottom:15px; text-align:center; padding:5px;'>"
                                    f"📷 Fără fotografie specifică pentru:<br>{sel_parfum} - {sel_culoare}</div>",
                                    unsafe_allow_html=True,
                                )

                            col_info_p, col_info_s = st.columns(2)
                            if potrivire_model:
                                with col_info_p:
                                    st.markdown(
                                        f"<div style='color:#FFFFFF; font-size:0.95rem;'>💰 Preț: <b style='color:#00FFA3;'>{potrivire_model.pret} RON</b></div>",
                                        unsafe_allow_html=True,
                                    )
                                with col_info_s:
                                    if potrivire_model.stoc > 0:
                                        st.markdown(
                                            f"<div style='color:#FFFFFF; font-size:0.95rem;'>📦 Stoc: <b style='color:#00FFA3;'>{potrivire_model.stoc} buc</b></div>",
                                            unsafe_allow_html=True,
                                        )
                                    else:
                                        st.markdown(
                                            "<div style='color:#FF4B4B; font-size:0.95rem;'>📦 Stoc: <b>🔴 Epuizat</b></div>",
                                            unsafe_allow_html=True,
                                        )

                                st.markdown("<br>", unsafe_allow_html=True)

                                if potrivire_model.stoc > 0:
                                    cantitate_deja_in_cos = sum(
                                        item["cantitate"]
                                        for item in st.session_state.cos_cumparaturi
                                        if item["id_lumanare"] == potrivire_model.id_lumanare
                                    )
                                    stoc_disponibil_real = int(potrivire_model.stoc) - cantitate_deja_in_cos

                                    if stoc_disponibil_real > 0:
                                        cantitate_dorita = st.number_input(
                                            "Cantitate (buc):",
                                            min_value=1,
                                            max_value=stoc_disponibil_real,
                                            value=1,
                                            step=1,
                                            key=f"num_{idx}",
                                        )
                                        btn_click = st.button(
                                            "🛒 Pune în Coș", key=f"btn_buy_{idx}", use_container_width=True
                                        )
                                        if btn_click:
                                            st.session_state.cos_cumparaturi.append(
                                                {
                                                    "id_lumanare": potrivire_model.id_lumanare,
                                                    "nume": potrivire_model.nume,
                                                    "cantitate": cantitate_dorita,
                                                    "pret_unitar": potrivire_model.pret,
                                                }
                                            )
                                            st.success("➕ Adăugat în coș!")
                                            st.rerun()
                                    else:
                                        st.button(
                                            "🛒 Toate bucățile sunt în coș",
                                            key=f"btn_buy_{idx}",
                                            disabled=True,
                                            use_container_width=True,
                                        )
                                else:
                                    st.button(
                                        "❌ Stoc Epuizat", key=f"btn_buy_{idx}", disabled=True, use_container_width=True
                                    )
                            else:
                                with col_info_p:
                                    st.markdown(
                                        "<div style='color:#7F8C8D; font-size:0.95rem;'>💰 Preț: <b>--</b></div>",
                                        unsafe_allow_html=True,
                                    )
                                with col_info_s:
                                    st.markdown(
                                        "<div style='color:#FF4B4B; font-size:0.95rem;'>📦 Stoc: <b>🔴 Lipsă</b></div>",
                                        unsafe_allow_html=True,
                                    )
                                st.markdown("<br>", unsafe_allow_html=True)
                                st.button(
                                    "⚠️ Combinație Nefabricată",
                                    key=f"btn_buy_{idx}",
                                    disabled=True,
                                    use_container_width=True,
                                )

        # =====================================================================
        # 3. INTERFAȚA COȘULUI DE CUMPĂRĂTURI UNIFICAT
        # =====================================================================
        with tab_cos:
            st.subheader("🛒 Coșul tău de Cumpărături")
            if not st.session_state.cos_cumparaturi:
                st.info("Coșul tău este gol. Mergi la catalog și adaugă lumânări!")
            else:
                date_tabel_cos = []
                total_general_plata = Decimal("0.00")

                for item in st.session_state.cos_cumparaturi:
                    subtotal = item["pret_unitar"] * Decimal(str(item["cantitate"]))
                    total_general_plata += subtotal
                    date_tabel_cos.append(
                        {
                            "Produs": item["nume"],
                            "Preț Unitar": f"{item['pret_unitar']} RON",
                            "Cantitate": f"{item['cantitate']} buc",
                            "Subtotal": f"{subtotal} RON",
                        }
                    )

                st.table(pd.DataFrame(date_tabel_cos))
                st.markdown(
                    f"### 💵 Total de plată: <span style='color:#00FFA3;'>{total_general_plata:,.2f} RON</span>",
                    unsafe_allow_html=True,
                )

                col_goleste, col_trimite = st.columns(2)
                with col_goleste:
                    if st.button("🗑️ Golește Coșul", use_container_width=True):
                        st.session_state.cos_cumparaturi = []
                        st.rerun()
                with col_trimite:
                    if st.button("💳 Finalizează și Trimite Comanda Unică", type="primary", use_container_width=True):
                        client = db.query(Client).filter(Client.email == st.session_state.user_email).first()
                        noua_comanda = Comanda(id_client=client.id_client, total=total_general_plata)
                        db.add(noua_comanda)
                        db.commit()
                        db.refresh(noua_comanda)

                        for item in st.session_state.cos_cumparaturi:
                            produs_db = db.query(Lumanare).filter(Lumanare.id_lumanare == item["id_lumanare"]).first()
                            produs_db.stoc -= item["cantitate"]
                            pivot = ComandaLumanare(
                                id_comanda=noua_comanda.id_comanda,
                                id_lumanare=item["id_lumanare"],
                                cantitate=item["cantitate"],
                                pret_unitar=item["pret_unitar"],
                            )
                            db.add(pivot)

                        db.commit()
                        st.session_state.cos_cumparaturi = []
                        st.success(f"🎉 Excelent! Comanda unificată cu ID #{noua_comanda.id_comanda} a fost salvată!")
                        st.balloons()
                        st.rerun()

        # =====================================================================
        # 4. PANOU ADMINISTRATIV: ÎNCĂRCARE IMAGINE
        # =====================================================================
        with tab_incarcare:
            st.subheader("📸 Încarcă Imagini pentru Variante Combinatorice")
            st.caption("Asociază o poză pentru o rețetă tehnică exactă.")

            toate_formele_nume = sorted(list(set(f.nume_forma for f in toate_formele_db if f.nume_forma)))

            with st.form("form_upload_media_matrix", clear_on_submit=True):
                select_gama_media = st.selectbox("1. Alege Formă / Model de bază:", toate_formele_nume, key="up_gama")
                select_parfum_media = st.selectbox("2. Alege Esența de Parfum:", toate_parfumurile, key="up_parf")
                select_culoare_media = st.selectbox("3. Alege Culoarea Alocată:", toate_culorile, key="up_cul")
                fisier_incarcat = st.file_uploader(
                    "4. Selectează fișierul imagine (.png/.jpg):", type=["png", "jpg", "jpeg"], key="upload_store"
                )
                btn_submit_media = st.form_submit_button("💾 Salvează Imaginea în Depozitul Media")

            if btn_submit_media and fisier_incarcat is not None:
                nume_matrice_imagine = f"img_{select_gama_media.replace(' ', '_')}_{select_parfum_media.replace(' ', '_')}_{select_culoare_media.replace(' ', '_')}.png"
                cale_salvare = os.path.join(FOLDER_POZE, nume_matrice_imagine)

                with open(cale_salvare, "wb") as f:
                    f.write(fisier_incarcat.getbuffer())

                st.success("✅ Imaginea a fost salvată în sistem!")
                st.rerun()

    except Exception as e:
        db.rollback()
        st.error(f"Eroare la procesarea magazinului matriceal: {e}")
    finally:
        db.close()
