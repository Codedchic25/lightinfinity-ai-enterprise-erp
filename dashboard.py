import hashlib
import os
import sys
import time

import streamlit as st
from sqlalchemy import func, inspect

# ==========================================
# 1. ASIGURARE CĂI PYTHON & CONFIGURARE PAGINĂ
# ==========================================
cale_proiect = os.path.abspath(os.path.dirname(__file__))
if cale_proiect not in sys.path:
    sys.path.insert(0, cale_proiect)

st.set_page_config(page_title="Light Infinity AI ERP", layout="wide")

from app.core.base import Base, Client
from app.db.connection import SessionLocal, engine


# ==========================================
# 2. FUNCȚIE CRIPTARE PAROLE
# ==========================================
def genereaza_hash_parola(password: str, email: str) -> str:
    """Creează un hash securizat SHA-256 folosind email-ul ca salt."""
    salt = email.lower().strip()
    text_de_criptat = password + salt
    return hashlib.sha256(text_de_criptat.encode("utf-8")).hexdigest()


# ==========================================
# 3. AUTO-INIȚIALIZARE BAZĂ DE DATE (CLOUD READY)
# ==========================================
@st.cache_resource
def initializeaza_baza_date():
    inspector = inspect(engine)
    if not inspector.has_table("clienti"):
        Base.metadata.create_all(bind=engine)
        try:
            import seed
            for fn_name in ("seed_database", "seed_all", "run_seed", "main"):
                if hasattr(seed, fn_name) and callable(getattr(seed, fn_name)):
                    getattr(seed, fn_name)()
                    break
        except Exception:
            pass

    # Asigurăm existența contului demo pentru acces imediat pe Streamlit Cloud
    db = SessionLocal()
    try:
        admin_email = "admin@lightinfinity.ai"
        exista = db.query(Client).filter(func.lower(Client.email) == admin_email).first()
        if not exista:
            client_demo = Client(
                nume="Administrator",
                email=admin_email,
                parola_hash=genereaza_hash_parola("light2026", admin_email),
            )
            db.add(client_demo)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
    return True


initializeaza_baza_date()

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


# ==========================================
# 4. MANAGEMENT SESIUNE IMUN LA RESETARE & RERUN
# ==========================================
if "login_status" in st.query_params and st.query_params["login_status"] == "autentificat":
    st.session_state["global_autentificat"] = True
    if "global_user_email" not in st.session_state or not st.session_state["global_user_email"]:
        st.session_state["global_user_email"] = st.query_params.get("user_email", "admin@lightinfinity.ai")

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
                    "Adresă Email Utilizator:", placeholder="admin@lightinfinity.ai", key="login_email_main"
                )
                password = st.text_input(
                    "Parolă:", type="password", placeholder="Introduceți parola...", key="login_pass_main"
                )

                btn_login = st.button("🔓 Conectare Securizată", key="login_btn_main", type="primary", use_container_width=True)

                if btn_login:
                    email_curat = email_input.strip().lower()
                    if email_curat and password:
                        db = SessionLocal()
                        try:
                            client = db.query(Client).filter(func.lower(Client.email) == email_curat).first()
                            hash_introdus = genereaza_hash_parola(password, email_input.strip())

                            if client and (getattr(client, "parola_hash", None) == hash_introdus):
                                st.session_state["global_autentificat"] = True
                                st.session_state["global_user_email"] = client.email
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
                    "💾 Salvează Noua Parolă", key="global_reset_submit_btn", type="primary", use_container_width=True
                )

                if btn_aplica_resetare:
                    email_r_curat = email_reset.strip().lower()
                    if email_r_curat and noua_parola and pin_siguranta:
                        if pin_siguranta == "1234":
                            db = SessionLocal()
                            try:
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


# ==========================================
# 5. INJECTARE DIRECTĂ ULTRA-DARK & LIZIBILITATE TOTALĂ (CSS)
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


# ==========================================
# 6. ZONA PRINCIPALĂ & MENIU OPERAȚIONAL
# ==========================================
st.markdown('<div class="candle-header">🕯️</div>', unsafe_allow_html=True)
st.title("⚡ LIGHT INFINITY AI - ENTERPRISE")
st.caption("Management tranzactional sincron conectat la SQLite Local")
st.markdown("---")

st.sidebar.title("🕹️ Panou Control")
st.sidebar.markdown(f"👤 Utilizator conectat: `{st.session_state.global_user_email}`")
st.sidebar.markdown("<br>", unsafe_allow_html=True)

opțiuni_module = [
    "🛍️ Magazin Online E-Shop",
    "📦 Catalog Dynamic",
    "🏭 Management Production",
    "🛒 Checkout & Plasare Comenzi",
    "📈 Interogari BI & Analize",
    "🧪 Rețete & Laborator AI",
]

index_implicit = 0
pagina_salvata_url = st.query_params.get("pagina_activa", "")
if pagina_salvata_url in opțiuni_module:
    index_implicit = opțiuni_module.index(pagina_salvata_url)

app_mode = st.sidebar.selectbox(
    "Navighează prin modulele ERP:",
    options=opțiuni_module,
    index=index_implicit,
    key="navigation_select_box",
)

if st.query_params.get("pagina_activa", "") != app_mode:
    st.query_params["pagina_activa"] = app_mode

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
if st.sidebar.button("🚪 Deconectare Securizată", type="secondary", use_container_width=True):
    st.session_state["global_autentificat"] = False
    st.session_state["global_user_email"] = ""
    st.query_params.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Status Conexiune: **Bază Date Sincronizată**")


# ==========================================
# 7. RUTARE CĂTRE MODULE CURENTE
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
