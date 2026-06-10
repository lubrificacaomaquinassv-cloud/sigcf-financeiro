import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

st.set_page_config(page_title="SIGCF - Lancamentos Financeiros", layout="wide")

st.markdown("""
<style>
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    section.main,
    .main .block-container {
        background-color: #0d1117 !important;
        color: #e6edf3;
    }
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {
        background-color: #0d1117 !important;
        border-right: 1px solid #30363d;
    }
    [data-testid="stMetric"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 14px 16px;
    }
    [data-testid="stMetricLabel"] { color: #8b949e !important; }
    [data-testid="stMetricValue"] { color: #e6edf3 !important; }
    div[data-testid="stForm"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px;
        padding: 24px !important;
    }
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    div[data-testid="stDateInput"] input {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] {
        background-color: #0d1117 !important;
        border-color: #30363d !important;
        color: #e6edf3 !important;
    }
    h1, h2, h3, label, p { color: #e6edf3 !important; }
    .stCaption, small { color: #8b949e !important; }
    hr { border-color: #30363d !important; margin: 1rem 0; }
    [data-testid="stDataFrame"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    .stFormSubmitButton button {
        background-color: #238636 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stFormSubmitButton button:hover {
        background-color: #2ea043 !important;
    }
</style>
""", unsafe_allow_html=True)

col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    st.image("https://i.postimg.cc/Y9X7ddnb/LOGO-BP.jpg", width=110)
with col_titulo:
    st.title("Lancamentos Financeiros")
    st.caption("SIGCF - Sistema Integrado de Gestao de Custos de Frota")

st.divider()

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ITENS_FINANCEIRO = ["PECAS", "M.O.", "M.O. OPERADOR", "DIESEL", "OUTROS"]
TIPOS_MANUTENCAO = ["HIDRAULICO", "ELETRICO", "MOTOR", "TDP", "OUTROS"]

@st.cache_data(ttl=10)
def carregar_lancamentos():
    res = supabase.table("financeiro_lancamento") \
        .select("*") \
        .order("data", desc=True) \
        .order("criado_em", desc=True) \
        .limit(500).execute()
    return res.data or []

@st.cache_data(ttl=60)
def carregar_frotas():
    res = supabase.table("dim_frota") \
        .select("id_frota, modelo, categoria") \
        .eq("ativo", True) \
        .order("id_frota").execute()
    return res.data or []

lancamentos = carregar_lancamentos()
frotas = carregar_frotas()

opcoes_frota = {"(sem frota)": None}
for f in frotas:
    opcoes_frota[f"{f['id_frota']} — {f.get('modelo', '')}"] = f["id_frota"]

with st.sidebar:
    st.image("https://i.postimg.cc/Y9X7ddnb/LOGO-BP.jpg", width=140)
    st.divider()
    st.header("Ultimos Lancamentos")
    if lancamentos:
        df_side = pd.DataFrame(lancamentos)
        cols = [c for c in ["data", "nfe", "item", "tipo_manutencao", "valor"] if c in df_side.columns]
        st.dataframe(df_side[cols].head(15), use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum lancamento ainda.")

fc1, fc2, fc3 = st.columns([2, 1, 1])
with fc1:
    filtro_data = st.date_input("Filtrar por data", value=datetime.now().date())
with fc2:
    slot_total = st.empty()
with fc3:
    slot_qtd = st.empty()

data_str = str(filtro_data)
lanc_dia = [l for l in lancamentos if l.get("data") == data_str]
total_dia = sum(float(l.get("valor") or 0) for l in lanc_dia)
slot_total.metric("Total do dia", f"R$ {total_dia:,.2f}")
slot_qtd.metric("Lancamentos", len(lanc_dia))

st.divider()
st.subheader("Novo Lancamento")

with st.form("form_lancamento", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        data_lanc = st.date_input("Data *", value=datetime.now().date())
    with col2:
        nfe = st.text_input("NFE")
    with col3:
        id_fornecedor = st.text_input("ID Fornecedor SAP")

    col4, col5, col6 = st.columns(3)
    with col4:
        item = st.selectbox("Item *", options=ITENS_FINANCEIRO)
    with col5:
        tipo_manutencao = st.selectbox("Tipo de Manutencao *", options=TIPOS_MANUTENCAO)
    with col6:
        valor = st.number_input("Valor (R$) *", min_value=0.0, step=0.01, format="%.2f")

    col7, col8 = st.columns(2)
    with col7:
        frota_label = st.selectbox("Frota (opcional)", options=list(opcoes_frota.keys()))
    with col8:
        observacao = st.text_area("Observacao", height=68)

    enviar = st.form_submit_button("SALVAR LANCAMENTO", use_container_width=True, type="primary")

if enviar:
    if valor <= 0:
        st.warning("Informe um valor maior que zero.")
    else:
        novo = {
            "data": str(data_lanc),
            "nfe": nfe.strip() or None,
            "id_fornecedor_sap": id_fornecedor.strip() or None,
            "item": item,
            "tipo_manutencao": tipo_manutencao,
            "valor": round(valor, 2),
            "id_frota": opcoes_frota.get(frota_label),
            "observacao": observacao.strip() or None,
        }
        try:
            supabase.table("financeiro_lancamento").insert(novo).execute()
            st.success(f"Lancamento salvo — {item} | {tipo_manutencao} | R$ {valor:,.2f}")
            st.cache_data.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

st.divider()
st.subheader(f"Lancamentos em {filtro_data.strftime('%d/%m/%Y')}")

if lanc_dia:
    df_dia = pd.DataFrame(lanc_dia)
    rename = {
        "data": "Data",
        "nfe": "NFE",
        "id_fornecedor_sap": "Fornecedor SAP",
        "item": "Item",
        "tipo_manutencao": "Tipo Manut.",
        "valor": "Valor",
        "id_frota": "Frota",
        "observacao": "Obs",
    }
    cols_show = [c for c in rename if c in df_dia.columns]
    st.dataframe(df_dia[cols_show].rename(columns=rename), use_container_width=True, hide_index=True)

    rc1, rc2 = st.columns(2)
    with rc1:
        st.subheader("Resumo por item")
        resumo_item = df_dia.groupby("item")["valor"].sum().reset_index()
        resumo_item.columns = ["Item", "Total R$"]
        st.dataframe(resumo_item, use_container_width=True, hide_index=True)
    with rc2:
        st.subheader("Resumo por tipo de manutencao")
        resumo_tipo = df_dia.groupby("tipo_manutencao")["valor"].sum().reset_index()
        resumo_tipo.columns = ["Tipo Manut.", "Total R$"]
        st.dataframe(resumo_tipo, use_container_width=True, hide_index=True)
else:
    st.info("Nenhum lancamento nesta data.")

st.divider()
st.caption("SIGCF | Lancamentos Financeiros | Nucleo de Controladoria SV")
