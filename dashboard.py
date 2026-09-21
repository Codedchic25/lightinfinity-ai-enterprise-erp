import hashlib
import os
import sys
import time

import streamlit as st

from app.core.base import Client
from app.db.connection import SessionLocal

# 1. Configurare inițială obligatorie
st.set_page_config(page_title="Light Infinity AI ERP", layout="wide")


# ==========================================
# 2. FUNCȚIE CRIPTARE PAROLE
# ==========================================
def genereaza_hash_parola(password: str, email: str) -> str:
    salt = email.lower().strip()
    text_de_criptat = password + salt
    return hashlib.sha256(text_de_criptat.encode("utf-8")).hexdigest()


# ==========================================
# 3. MANAGEMENT SESIUNE IMUN LA RESETARE & RERUN
# ==========================================
# Citim și blocăm starea direct din URL-ul browserului pentru persistență totală
# Citim și blocăm starea direct din URL-ul browserului pentru persistență totală
if "login_status" in st.query_params and st.query_params["login_status"] == "autentificat":
    st.session_state["global_autentificat"] = True
    if "global_user_email" not in st.session_state or not st.session_state["global_user_email"]:
        st.session_state["global_user_email"] = st.query_params.get("user_email", "admin@erp.local")

    # 🌟 REPARARE PERSISTENȚĂ PAGINĂ: Dacă există pagină salvată în URL, o păstrăm în sesiune
    if "pagina_activa" in st.query_params and "pagina_curenta" not in st.session_state:
        st.session_state["pagina_curenta"] = st.query_params["pagina_activa"]
else:
    if "global_autentificat" not in st.session_state:
        st.session_state["global_autentificat"] = False
    if "global_user_email" not in st.session_state:
        st.session_state["global_user_email"] = ""

# Scut de Securitate Global
if not st.session_state["global_autentificat"]:
    st.markdown("<style>[data-testid='stSidebar'] {display: none !important;}</style>", unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(
                "<h3 style='text-align:center; color:#00FFA3; font-family:Courier New;'>🔑 Sistem ERP</h3>",
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)

            vrea_resetare = st.checkbox("🔄 Am uitat parola / Resetare cont", key="global_reset_toggle")

            if not vrea_resetare:
                st.markdown("<h5 style='color:#00FFA3;'>🔓 Autentificare</h5>", unsafe_allow_html=True)
                email_input = st.text_input(
                    "Adresă Email Utilizator:", placeholder="nume@exemplu.com...", key="login_email_main"
                )
                password = st.text_input(
                    "Parolă:", type="password", placeholder="Introduceți parola...", key="login_pass_main"
                )

                btn_login = st.button("🔓 Conectare Securizată", key="login_btn_main", type="primary", width="stretch")

                if btn_login:
                    email_curat = email_input.strip().lower()
                    if email_curat and password:
                        db = SessionLocal()
                        try:
                            from sqlalchemy import func

                            client = db.query(Client).filter(func.lower(Client.email) == email_curat).first()
                            hash_introdus = genereaza_hash_parola(password, email_input.strip())

                            if client and (getattr(client, "parola_hash", None) == hash_introdus):
                                # Fixăm datele în sesiune
                                st.session_state["global_autentificat"] = True
                                st.session_state["global_user_email"] = client.email

                                # Ancorăm starea direct în URL-ul browserului pentru imunitate la rerun
                                st.query_params["login_status"] = "autentificat"
                                st.query_params["user_email"] = client.email

                                st.success("🔓 Conectare reușită!")
                                st.rerun()
                            else:
                                time.sleep(0.5)
                                st.error("❌ Email sau parolă incorectă.")
                        except Exception as e:
                            st.error(f"Eroare: {e}")
                        finally:
                            db.close()
                    else:
                        st.error("❌ Completează email-ul și parola.")
            else:
                st.markdown("<h5 style='color:#FF4B4B;'>🔄 Recuperare Parolă</h5>", unsafe_allow_html=True)
                email_reset = st.text_input(
                    "Confirmă Email-ul contului:", placeholder="email@exemplu.com...", key="global_reset_email"
                )
                noua_parola = st.text_input(
                    "Noua Parolă Dorită:",
                    type="password",
                    placeholder="Introduceți noua parolă...",
                    key="global_reset_pass",
                )
                pin_siguranta = st.text_input(
                    "Cod Master PIN Admin:", type="password", placeholder="Codul din 4 cifre...", key="global_reset_pin"
                )

                btn_aplica_resetare = st.button(
                    "💾 Salvează Noua Parolă", key="global_reset_submit_btn", type="primary", width="stretch"
                )

                if btn_aplica_resetare:
                    email_r_curat = email_reset.strip().lower()
                    if email_r_curat and noua_parola and pin_siguranta:
                        if pin_siguranta == "1234":
                            db = SessionLocal()
                            try:
                                from sqlalchemy import func

                                client = db.query(Client).filter(func.lower(Client.email) == email_r_curat).first()
                                hash_nou = genereaza_hash_parola(noua_parola, email_reset.strip())

                                if client:
                                    client.parola_hash = hash_nou
                                    db.commit()
                                    st.success("✅ Parolă actualizată! Debifează căsuța de sus pentru conectare.")
                                else:
                                    client_nou = Client(
                                        nume="Administrator", email=email_reset.strip(), parola_hash=hash_nou
                                    )
                                    db.add(client_nou)
                                    db.commit()
                                    st.success("✅ Cont activat! Debifează căsuța de sus pentru conectare.")
                            except Exception as e:
                                st.error(f"Eroare la salvare: {e}")
                            finally:
                                db.close()
                        else:
                            st.error("❌ Codul Master PIN este incorect!")
                    else:
                        st.error("❌ Completează toate câmpurile.")
    st.stop()

# 4. Injectare CSS Ultra-Dark fără blocaje pe tabele
st.markdown(
    """
    <style>
        .stApp, [data-testid="stAppViewContainer"], .main, .block-container {
            background-color: #06090F !important;
        }
        [data-testid="stSidebar"], section[data-testid="stSidebar"] {
            background-color: #0D131F !important;
            min-width: 400px !important;
            max-width: 400px !important;
            border-right: 2px solid #00FFA3 !important;
        }
        h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #00FFA3 !important;
            font-family: 'Courier New', monospace !important;
        }
        p, span, label, .stMarkdown p, li, [data-testid="stMetricLabel"] {
            color: #FFFFFF !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 2. ASIGURARE CĂI PYTHON & IMPORTURI
# ==========================================
cale_proiect = os.path.abspath(os.path.dirname(__file__))
if cale_proiect not in sys.path:
    sys.path.insert(0, cale_proiect)

# Importăm modulele oficiale din arhitectură
try:
    from app.modules.storefront.storefront_module import render_storefront_module
except ImportError:

    def render_storefront_module():
        st.warning("Modulul Magazin Online E-Shop nu este complet disponibil.")


try:
    from app.modules.bi.bi_module import render_bi_module
except ImportError:

    def render_bi_module():
        st.warning("Modulul BI nu este complet.")


try:
    from app.modules.orders.orders_module import render_orders_module
except ImportError:

    def render_orders_module():
        st.warning("Modulul Orders nu este complet.")


try:
    from app.modules.production.production_module import render_production_module
except ImportError:

    def render_production_module():
        st.warning("Modulul Production nu este disponibil.")


try:
    from app.modules.products.products_module import render_products_module
except ImportError:

    def render_products_module():
        st.warning("Modulul Products nu este disponibil.")


try:
    from app.modules.laborator.laborator_module import render_laborator_module
except ImportError:

    def render_laborator_module():
        st.warning("Modulul Laborator AI nu este disponibil.")


# IMPORTANT: Aceasta trebuie să fie prima instrucțiune Streamlit apelată!
st.set_page_config(page_title="Light Infinity AI ERP", layout="wide")


# ==========================================
# FUNCȚII AJUTĂTOARE PENTRU CRIPTARE PAROLE
# ==========================================
def genereaza_hash_parola(password: str, email: str) -> str:
    """Creează un hash securizat SHA-256 folosinc email-ul ca salt."""
    salt = email.lower().strip()
    text_de_criptat = password + salt
    return hashlib.sha256(text_de_criptat.encode("utf-8")).hexdigest()


# ==========================================
# 3. SCUT DE SECURITATE GLOBAL ERP (BLOCARE TOTALĂ)
# ==========================================
if "global_autentificat" not in st.session_state:
    st.session_state.global_autentificat = False
if "global_user_email" not in st.session_state:
    st.session_state.global_user_email = ""
if not st.session_state.global_autentificat:
    # Ascundem sidebar-ul când nu suntem conectați
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {display: none !important;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(
                "<h3 style='text-align:center; color:#00FFA3; font-family:Courier New;'>🔑 Sistem ERP</h3>",
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)

            # Căsuța care activează sau ascunde formularul de resetare
            vrea_resetare = st.checkbox("🔄 Am uitat parola / Resetare cont", key="global_reset_toggle")

            if vrea_resetare:
                # ==========================================
                # FORMULAR INDEPENDENT DE RESETARE
                # ==========================================
                st.markdown("<h5 style='color:#FF4B4B;'>🔄 Recuperare Parolă</h5>", unsafe_allow_html=True)
                email_reset = st.text_input(
                    "Confirmă Email-ul contului:", placeholder="email@exemplu.com...", key="global_reset_email"
                )
                noua_parola = st.text_input(
                    "Noua Parolă Dorită:",
                    type="password",
                    placeholder="Introduceți noua parolă...",
                    key="global_reset_pass",
                )
                pin_siguranta = st.text_input(
                    "Cod Master PIN Admin:", type="password", placeholder="Codul din 4 cifre...", key="global_reset_pin"
                )

                st.markdown("<br>", unsafe_allow_html=True)
                btn_aplica_resetare = st.button(
                    "💾 Salvează Noua Parolă", key="global_reset_submit_btn", type="primary", width="stretch"
                )

                if btn_aplica_resetare:
                    email_r_curat = email_reset.strip().lower()
                    if email_r_curat and noua_parola and pin_siguranta:
                        if pin_siguranta == "1234":
                            db = SessionLocal()
                            try:
                                from sqlalchemy import func

                                client = db.query(Client).filter(func.lower(Client.email) == email_r_curat).first()
                                hash_nou = genereaza_hash_parola(noua_parola, email_reset.strip())

                                if client:
                                    client.parola_hash = hash_nou
                                    db.commit()
                                    st.success("✅ Parolă actualizată! Debifează căsuța de sus pentru a te conecta.")
                                else:
                                    # Creăm contul pe loc dacă nu exista în baza de date
                                    client_nou = Client(
                                        nume="Administrator", email=email_reset.strip(), parola_hash=hash_nou
                                    )
                                    db.add(client_nou)
                                    db.commit()
                                    st.success(
                                        "✅ Cont administrator activat! Debifează căsuța de sus pentru a te conecta."
                                    )
                            except Exception as e:
                                st.error(f"Eroare la salvare: {e}")
                            finally:
                                db.close()
                        else:
                            st.error("❌ Codul Master PIN este incorect!")
                    else:
                        st.error("❌ Completează toate câmpurile pentru resetare.")

            else:
                # ==========================================
                # FORMULAR DE CONECTARE NORMALĂ
                # ==========================================
                st.markdown("<h5 style='color:#00FFA3;'>🔓 Autentificare</h5>", unsafe_allow_html=True)
                email_input = st.text_input(
                    "Adresă Email Utilizator:", placeholder="nume@exemplu.com...", key="global_login_email"
                )
                password = st.text_input(
                    "Parolă:", type="password", placeholder="Introduceți parola...", key="global_login_pass"
                )

                st.checkbox("💾 Ține-mă minte pe acest dispozitiv", key="global_remember")
                st.markdown("<br>", unsafe_allow_html=True)

                btn_login = st.button(
                    "🔓 Conectare Securizată", key="global_login_btn", type="primary", width="stretch"
                )

                if btn_login:
                    email_curat = email_input.strip().lower()
                    if email_curat and "@" in email_curat and password:
                        db = SessionLocal()
                        try:
                            from sqlalchemy import func

                            client = db.query(Client).filter(func.lower(Client.email) == email_curat).first()
                            hash_introdus = genereaza_hash_parola(password, email_input.strip())

                            if client:
                                hash_salvat = getattr(client, "parola_hash", None)
                                if hash_salvat == hash_introdus:
                                    # 🔒 BLOCARE SESIUNE - Stabilă la orice rerun
                                    st.session_state["global_autentificat"] = True
                                    st.session_state["global_user_email"] = client.email
                                    st.success("🔓 Conectare reușită! Se încarcă...")
                                    st.rerun()
                                else:
                                    time.sleep(0.5)
                                    st.error("❌ Email sau parolă incorectă.")
                            else:
                                time.sleep(0.5)
                                st.error("❌ Acest cont nu există în baza de date.")
                        except Exception as e:
                            st.error(f"Eroare la conectare: {e}")
                        finally:
                            db.close()
                    else:
                        st.error("❌ Introdu o adresă de email validă și parola.")

    st.stop()

# ==========================================
# 4. INJECTARE DIRECTĂ ULTRA-DARK & LIZIBILITATE TOTALĂ (CSS)
# ==========================================
st.markdown(
    """
    <style>
        .stApp, [data-testid="stAppViewContainer"], .main, .block-container {
            background-color: #06090F !important;
        }

        [data-testid="stSidebar"],
        [data-testid="stSidebarUserContent"],
        [data-testid="stSidebarNav"],
        section[data-testid="stSidebar"] {
            background-color: #0D131F !important;
            background: #0D131F !important;
            box-shadow: none !important;
        }

        [data-testid="stSidebar"] {
            min-width: 400px !important;
            max-width: 400px !important;
            border-right: 2px solid #00FFA3 !important;
        }

        [data-testid="stSidebarUserContent"] {
            padding-top: 2rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }

        h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #00FFA3 !important;
            font-family: 'Courier New', monospace !important;
            text-shadow: 0 0 10px rgba(0, 255, 163, 0.5) !important;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h1 {
            color: #FFFFFF !important;
            font-weight: bold !important;
        }

        .stSelectbox div[data-baseweb="select"] {
            background-color: #161F30 !important;
            border: 2px solid #00FFA3 !important;
            border-radius: 8px !important;
            padding: 2px 6px !important;
        }

        .stSelectbox div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
        .stSelectbox div[data-baseweb="select"] span,
        .stSelectbox div[data-baseweb="select"] div {
            color: #00FFA3 !important;
            font-weight: bold !important;
            font-size: 1.05rem !important;
        }

        div[data-baseweb="popover"],
        div[role="listbox"],
        ul[role="listbox"],
        div[data-baseweb="menu"] {
            background-color: #0D131F !important;
            background: #0D131F !important;
            border: 2px solid #00FFA3 !important;
            border-radius: 8px !important;
        }

        li[role="option"],
        li[role="option"] div,
        li[role="option"] span,
        [data-baseweb="menu"] li,
        [role="option"] * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            font-weight: 600 !important;
            font-size: 1.05rem !important;
        }

        li[role="option"], [data-baseweb="menu"] li {
            background-color: #0D131F !important;
            background: #0D131F !important;
        }

        li[role="option"]:hover,
        li[role="option"]:hover div,
        li[role="option"]:hover span,
        li[role="option"]:hover *,
        [data-baseweb="menu"] li:hover {
            background-color: #161F30 !important;
            background: #161F30 !important;
            color: #00FFA3 !important;
            -webkit-text-fill-color: #00FFA3 !important;
            cursor: pointer;
        }

        p, span, label, .stMarkdown p, li, [data-testid="stMetricLabel"] {
            color: #FFFFFF !important;
            font-weight: 500 !important;
        }

        .stDataFrame, [data-testid="stDataFrameDataViewController"], div[data-testid="stDataFrame"] {
            background-color: #0D131F !important;
            border: 2px solid #00FFA3 !important;
            border-radius: 8px !important;
        }

        div[data-testid="stDataFrame"] table, div[data-testid="stDataFrame"] div {
            color: #FFFFFF !important;
        }

        [data-testid="stTable"] td, [data-testid="stTable"] th {
            color: #FFFFFF !important;
            background-color: #0D131F !important;
        }

        div[data-testid="stAlert"] p, div[data-testid="stAlert"] span, div[data-testid="stAlert"] label {
            color: #000000 !important;
            font-weight: bold !important;
        }

        .stMetric {
            background-color: #0D131F !important;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #00FFA3 !important;
            box-shadow: 0 0 15px rgba(0, 255, 163, 0.2) !important;
        }

        [data-testid="stMetricValue"] div {
            color: #00FFA3 !important;
            font-family: 'Courier New', monospace !important;
        }

        .candle-header {
            font-size: 4rem;
            text-align: left;
            margin-bottom: -20px;
        }
    </style>
""",
    unsafe_allow_html=True,
)


# Zona din Dreapta (Conținut principal)
st.markdown('<div class="candle-header">🕯️</div>', unsafe_allow_html=True)
st.title("⚡ LIGHT INFINITY AI - ENTERPRISE")
st.caption("Management tranzactional sincron conectat la SQLite Local")
st.markdown("---")

# ==========================================
# 5. MENIU OPERAȚIONAL CONSTRUIT ÎN STÂNGA (PERSISTENȚĂ 100%)
# ==========================================
st.sidebar.title("🕹️ Panou Control")
st.sidebar.markdown(f"👤 Utilizator conectat: `{st.session_state.global_user_email}`")
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Definim lista oficială de module ERP
opțiuni_module = [
    "🛍️ Magazin Online E-Shop",
    "📦 Catalog Dynamic",
    "🏭 Management Production",
    "🛒 Checkout & Plasare Comenzi",
    "📈 Interogari BI & Analize",
    "🧪 Rețete & Laborator AI",
]

# Calculăm indexul implicit bazat pe ce avem deja ancorat în URL-ul browserului
index_implicit = 0
pagina_salvata_url = st.query_params.get("pagina_activa", "")
if pagina_salvata_url in opțiuni_module:
    index_implicit = opțiuni_module.index(pagina_salvata_url)

# Renderiță dropdown-ul inteligent cu indexul persistent
app_mode = st.sidebar.selectbox(
    "Navighează prin modulele ERP:",
    options=opțiuni_module,
    index=index_implicit,
    key="navigation_select_box",
)

# Sincronizăm instant URL-ul când operatorul schimbă manual modulul din meniu
if st.query_params.get("pagina_activa", "") != app_mode:
    st.query_params["pagina_activa"] = app_mode

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
if st.sidebar.button("🚪 Deconectare Securizată", type="secondary", width="stretch"):
    st.session_state["global_autentificat"] = False
    st.session_state["global_user_email"] = ""
    st.query_params.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Status Conexiune: **Bază Date Sincronizată**")

# ==========================================
# 6. RUTARE CĂTRE MODULE CURENTE
# ==========================================
if app_mode == "🛍️ Magazin Online E-Shop":
    render_storefront_module()

elif app_mode == "📦 Catalog Dynamic":
    render_products_module()

elif app_mode == "🏭 Management Production":
    render_production_module()

elif app_mode == "🛒 Checkout & Plasare Comenzi":
    render_orders_module()

elif app_mode == "📈 Interogari BI & Analize":
    render_bi_module()

elif app_mode == "🧪 Rețete & Laborator AI":
    render_laborator_module()
