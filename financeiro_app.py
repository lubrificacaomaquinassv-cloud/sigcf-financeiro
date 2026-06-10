import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

st.set_page_config(page_title="Financeiro OS - SIGCF", layout="wide")

# ─────────────────────────────────────────────
# TEMA ESCURO
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background-color: #161b22; }
    [data-testid="stMetric"] {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 8px; padding: 12px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: #161b22; border-radius: 8px 8px 0 0;
        color: #8b949e; border: 1px solid #30363d;
    }
    .stTabs [aria-selected="true"] {
        background: #1f6feb !important; color: #fff !important;
    }
    div[data-testid="stForm"] {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 10px; padding: 16px;
    }
    h1, h2, h3, label, p { color: #e6edf3 !important; }
    .stCaption { color: #8b949e !important; }
</style>
""", unsafe_allow_html=True)

col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    st.image("https://i.postimg.cc/Y9X7ddnb/LOGO-BP.jpg", width=110)
with col_titulo:
    st.title("Lancamento Financeiro de OS")
    st.caption("SIGCF - Sistema Integrado de Gestao de Custos de Frota")

st.divider()

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ITENS_FINANCEIRO = ["PECAS", "M.O.", "M.O. OPERADOR", "DIESEL", "OUTROS"]
TIPOS_MANUTENCAO = ["HIDRAULICO", "ELETRICO", "MOTOR", "TDP", "OUTROS"]

# ─────────────────────────────────────────────
# CARREGAMENTO DE DADOS
# ─────────────────────────────────────────────
@st.cache_data(ttl=30)
def carregar_os_oficina():
    res = supabase.table("ordem_servico") \
        .select("numero_os, id_frota, mecanico, tempo_min, status") \
        .order("created_at", desc=True).limit(100).execute()
    return res.data or []

@st.cache_data(ttl=60)
def carregar_colaboradores():
    res = supabase.table("dim_colaborador") \
        .select("nome, custo_hora").eq("ativo", True).execute()
    return res.data or []

@st.cache_data(ttl=10)
def carregar_lancamentos_oficina():
    res = supabase.table("financeiro_os") \
        .select("*").eq("tipo_os", "OFICINA") \
        .order("criado_em", desc=True).limit(20).execute()
    return res.data or []

@st.cache_data(ttl=30)
def carregar_os_lubrificacao():
    res = supabase.table("lubrificacao") \
        .select("id, order_number, vehicle, location, created_at, actions") \
        .order("created_at", desc=True).limit(200).execute()
    return res.data or []

@st.cache_data(ttl=60)
def carregar_dim_insumo():
    res = supabase.table("dim_insumo") \
        .select("id_insumo, nome, unidade, categoria") \
        .order("categoria").execute()
    return res.data or []

@st.cache_data(ttl=60)
def carregar_preco_insumo():
    res = supabase.table("preco_insumo") \
        .select("id_insumo, valor_unitario").eq("ativo", True).execute()
    return res.data or []

@st.cache_data(ttl=10)
def carregar_lancamentos_lubrificacao():
    res = supabase.table("financeiro_lubrificacao") \
        .select("*").order("criado_em", desc=True).limit(20).execute()
    return res.data or []

@st.cache_data(ttl=10)
def carregar_lancamentos_direto():
    res = supabase.table("financeiro_lancamento") \
        .select("*") \
        .order("data", desc=True) \
        .order("criado_em", desc=True) \
        .limit(200).execute()
    return res.data or []

@st.cache_data(ttl=60)
def carregar_frotas():
    res = supabase.table("dim_frota") \
        .select("id_frota, modelo, categoria") \
        .eq("ativo", True) \
        .order("id_frota").execute()
    return res.data or []

os_oficina          = carregar_os_oficina()
colaboradores       = carregar_colaboradores()
lancamentos_oficina = carregar_lancamentos_oficina()
os_lubrificacao     = carregar_os_lubrificacao()
dim_insumo          = carregar_dim_insumo()
preco_insumo        = carregar_preco_insumo()
lancamentos_direto  = carregar_lancamentos_direto()
frotas              = carregar_frotas()

custo_map = {c["nome"]: float(c["custo_hora"] or 0) for c in colaboradores}
preco_map = {p["id_insumo"]: float(p["valor_unitario"] or 0) for p in preco_insumo}

opcoes_frota = {"(sem frota)": None}
for f in frotas:
    opcoes_frota[f"{f['id_frota']} — {f.get('modelo', '')}"] = f["id_frota"]

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://i.postimg.cc/Y9X7ddnb/LOGO-BP.jpg", width=140)
    st.divider()
    st.header("Ultimos Lancamentos")
    pagina_sidebar = st.radio("Modulo", ["Oficina", "Lubrificacao", "Lancamento Direto"])
    st.divider()

    if pagina_sidebar == "Oficina" and lancamentos_oficina:
        df = pd.DataFrame(lancamentos_oficina)
        cols = [c for c in ["numero_os", "id_frota", "peca_descricao", "custo_total_os"] if c in df.columns]
        st.table(df[cols].head(10))

    elif pagina_sidebar == "Lubrificacao":
        try:
            lanc_lub = carregar_lancamentos_lubrificacao()
            if lanc_lub:
                df2 = pd.DataFrame(lanc_lub)
                cols = [c for c in ["order_number", "id_frota", "insumo_nome", "custo_total"] if c in df2.columns]
                st.table(df2[cols].head(10))
            else:
                st.info("Nenhum lancamento ainda.")
        except Exception as e:
            st.info(f"Aguardando dados: {e}")

    elif pagina_sidebar == "Lancamento Direto" and lancamentos_direto:
        df_ld = pd.DataFrame(lancamentos_direto)
        cols = [c for c in ["data", "nfe", "item", "tipo_manutencao", "valor"] if c in df_ld.columns]
        st.table(df_ld[cols].head(10))

    else:
        st.info("Nenhum lancamento ainda.")

# ─────────────────────────────────────────────
# ABAS PRINCIPAIS
# ─────────────────────────────────────────────
aba = st.tabs(["🔧 Oficina", "🛢️ Lubrificacao", "💰 Lancamento Direto"])

# ... (resto igual ao arquivo gerado acima - Oficina, Lubrificacao, Lancamento Direto)
