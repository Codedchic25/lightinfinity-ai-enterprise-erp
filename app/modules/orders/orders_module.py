import os
from decimal import Decimal

import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.core.base import Client, Comanda, ComandaLumanare, Lumanare
from app.db.connection import SessionLocal


def generare_pdf_factura(id_comanda, data_v, nume_c, email_c, nume_p, cantitate, pret_u, total):
    folder_facturi = "autogen_facturi"
    if not os.path.exists(folder_facturi):
        os.makedirs(folder_facturi)

    cale_pdf = os.path.join(folder_facturi, f"factura_{id_comanda}.pdf")

    c = canvas.Canvas(cale_pdf, pagesize=letter)

    # 🌟 TEXT CURĂȚAT: Înlocuit FACTURĂ FISCALĂ cu FACTURA FISCALA
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, 750, "LIGHT INFINITY AI — FACTURA FISCALA")

    # 🌟 TEXT CURĂȚAT: Înlocuit Serie/Număr cu Serie/Numar
    c.setFont("Helvetica", 10)
    c.drawString(50, 730, f"Serie/Numar: LI-{id_comanda} | Data: {data_v}")
    c.line(50, 715, 550, 715)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 690, "Furnizor:")
    c.drawString(300, 690, "Client:")

    # 🌟 TEXT CURĂȚAT: Înlocuit România cu Romania
    c.setFont("Helvetica", 11)
    c.drawString(50, 670, "LIGHT INFINITY AI S.R.L.")
    c.drawString(50, 650, "Cluj-Napoca, Romania")

    c.drawString(300, 670, f"Nume: {nume_c}")
    c.drawString(300, 650, f"Email: {email_c}")
    c.line(50, 630, 550, 630)

    # 🌟 TEXT CURĂȚAT: Înlocuit Specificație cu Specificatie și Preț cu Pret
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 600, "Denumire Produs / Specificatie")
    c.drawString(300, 600, "Cantitate")
    c.drawString(400, 600, "Pret Unitar")
    c.drawString(490, 600, "Total")
    c.line(50, 590, 550, 590)

    c.setFont("Helvetica", 11)
    c.drawString(50, 560, str(nume_p))
    c.drawString(300, 560, f"{cantitate} buc")
    c.drawString(400, 560, f"{pret_u} RON")
    c.drawString(490, 560, f"{total} RON")

    c.line(50, 530, 550, 530)

    # 🌟 TEXT CURĂȚAT: Înlocuit TOTAL PLATĂ cu TOTAL PLATA
    c.setFont("Helvetica-Bold", 14)
    c.drawString(400, 500, "TOTAL PLATA:")
    c.drawString(500, 500, f"{total} RON")

    c.showPage()
    c.save()
    return cale_pdf


def render_orders_module():
    st.header("🛒 Checkout & Plasare Comenzi Directe")
    st.caption("Preluarea comenzilor de la clienți, procesare tranzacțională instantanee și decrementare stoc.")
    st.markdown("<br>", unsafe_allow_html=True)

    db = SessionLocal()
    try:
        lumanari = db.query(Lumanare).all()
        clienti_db = db.query(Client).all()
        comenzi_totale = db.query(Comanda).all()

        venit_total = sum(float(c.total) for c in comenzi_totale)
        clienti_unici = len(clienti_db)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Tranzacții Procesate", value=str(len(comenzi_totale)))
        with col2:
            st.metric(label="Volum Vânzări Total", value=f"{venit_total:,.2f} RON")
        with col3:
            st.metric(label="Portofoliu Clienți Activi", value=str(clienti_unici))

        st.markdown("<br>", unsafe_allow_html=True)
        tab_checkout, tab_clienti = st.tabs(["🛒 Checkout Nou", "📋 Registru Clienți & Istoric"])
        with tab_checkout:
            st.subheader("Nou Formular de Vânzare Rapidă")

            # Apelăm elementele direct, fără asignări inutile de variabile blocate (Elimină F841)
            st.text_input("Nume Complet Client:", key="vanzare_nume_client_p")
            st.text_input("Adresă Email Client:", key="vanzare_email_client_p")

            st.markdown("---")
            st.markdown("##### 🕯️ Configurație Produs Solicitat")

            if lumanari:
                produs_id_ales = st.selectbox(
                    "Selectează Produsul din Stoc:",
                    options=[p.id_lumanare for p in lumanari],
                    format_func=lambda x: next(
                        f"{p.nume} (Preț: {p.pret} RON | Stoc: {p.stoc} buc)" for p in lumanari if p.id_lumanare == x
                    ),
                    key="v_select_produs_direct",
                )
                produs_gasit = next(p for p in lumanari if p.id_lumanare == produs_id_ales)
            else:
                produs_gasit = None

            st.markdown("---")
            cantitate = st.number_input(
                "Cantitate solicitată (buc):", min_value=1, value=1, step=1, key="v_num_cantitate"
            )

            # Eliminat variabila fantomă 'Grid_curent'
            if produs_gasit:
                st.info(
                    f"📊 **Selectat:** {produs_gasit.nume} | **Stoc disponibil:** {produs_gasit.stoc} buc | **Preț unitar:** {produs_gasit.pret} RON"
                )
            else:
                st.warning("ℹ️ Nu există produse configurate în catalog.")

            st.markdown("<br>", unsafe_allow_html=True)
            buton_tranzactie = st.button(
                "💳 Finalizează Tranzacția Sincron", type="primary", width="stretch", key="v_btn_tranzactie"
            )

            if buton_tranzactie:
                # 🔒 CITIRE PERSISTENTĂ: Preluăm datele direct din starea salvată în sesiune
                nume_stabil = st.session_state.get("vanzare_nume_client_p", "").strip()
                email_stabil = st.session_state.get("vanzare_email_client_p", "").strip()

                if not nume_stabil or not email_stabil:
                    st.error("❌ Te rog completează datele clientului!")
                elif not produs_gasit:
                    st.error("❌ Nu există niciun produs selectat.")
                elif produs_gasit.stoc < cantitate:
                    st.error(f"❌ Stoc insuficient! Sunt disponibile doar {produs_gasit.stoc} bucăți.")
                else:
                    client = db.query(Client).filter(Client.email == email_stabil).first()
                    if not client:
                        client = Client(nume=nume_stabil, email=email_stabil)
                        db.add(client)
                        db.commit()
                        db.refresh(client)

                    total_plata = produs_gasit.pret * Decimal(str(cantitate))
                    noua_comanda = Comanda(id_client=client.id_client, total=total_plata)
                    db.add(noua_comanda)
                    db.commit()
                    db.refresh(noua_comanda)

                    pivot = ComandaLumanare(
                        id_comanda=noua_comanda.id_comanda,
                        id_lumanare=produs_gasit.id_lumanare,
                        cantitate=cantitate,
                        pret_unitar=produs_gasit.pret,
                    )
                    produs_gasit.stoc -= cantitate
                    db.add(pivot)
                    db.commit()

                    data_str = (
                        noua_comanda.data_comanda.strftime("%Y-%m-%d") if noua_comanda.data_comanda else "2026-09-17"
                    )
                    cale_generata = generare_pdf_factura(
                        id_comanda=noua_comanda.id_comanda,
                        data_v=data_str,
                        nume_c=client.nume,
                        email_c=client.email,
                        nume_p=produs_gasit.nume,
                        cantitate=cantitate,
                        pret_u=float(produs_gasit.pret),
                        total=float(total_plata),
                    )

                    st.session_state["factura_finala_cale"] = cale_generata
                    st.session_state["factura_finala_id"] = noua_comanda.id_comanda
                    st.success(f"🎉 Tranzacție procesată structural! Factură LI-{noua_comanda.id_comanda} generată.")

            if "factura_finala_cale" in st.session_state and st.session_state["factura_finala_cale"]:
                if os.path.exists(st.session_state["factura_finala_cale"]):
                    with open(st.session_state["factura_finala_cale"], "rb") as file:
                        st.download_button(
                            label="📥 Descarcă Factura PDF Securizată",
                            data=file,
                            file_name=f"factura_LI_{st.session_state['factura_finala_id']}.pdf",
                            mime="application/pdf",
                            width="stretch",
                            key="v_btn_download_factura",
                        )

        with tab_clienti:
            st.subheader("📋 Registrul Istoric de Tranzacții")
            if comenzi_totale:
                date_comenzi = []
                for c in comenzi_totale:
                    date_comenzi.append(
                        {
                            "ID Comandă": c.id_comanda,
                            "Client": c.client.nume if c.client else "Anonim",
                            "Email": c.client.email if c.client else "-",
                            "Data Tranzacției": str(c.data_comanda),
                            "Valoare Totală (RON)": float(c.total),
                        }
                    )
                st.dataframe(date_comenzi, width="stretch", hide_index=True, key="v_grid_istoric_comenzi")
            else:
                st.info("Nu există comenzi plasate în sistem.")

    except Exception as e:
        st.error(f"Eroare la procesarea modulului de checkout: {e}")
    finally:
        db.close()
