import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

st.set_page_config(
    page_title="SIGCF - Lancamentos Financeiros",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MESES = [
    "", "janeiro", "fevereiro", "marco", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]
hoje = datetime.now()
mes_ano = f"{MESES[hoje.month]} de {hoje.year}"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {{
        --bg:        #0a0e0a;
        --panel:     #121a12;
        --border:    #2a3d2a;
        --accent:    #b8e986;
        --accent2:   #8fd44f;
        --text:      #d4e4c8;
        --text-dim:  #7d9170;
        --white:     #f0f4ec;
    }}

    #MainMenu, footer, header {{ visibility: hidden; }}

    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {{
        display: none !important;
    }}

    .stApp,
    [data-testid="stAppViewContainer"],
    section.main,
    .main .block-container {{
        background-color: var(--bg) !important;
        color: var(--text);
        font-family: 'Inter', sans-serif !important;
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }}

    .sv-header {{
        display: flex;
        align-items: center;
        gap: 18px;
        padding: 8px 0 20px 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 20px;
    }}
    .sv-logo-wrap {{
        background: #ffffff;
        border-radius: 10px;
        padding: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 72px;
        height: 72px;
        flex-shrink: 0;
    }}
    .sv-logo-wrap img {{ width: 56px; height: auto; }}
    .sv-title {{
        font-size: 1.55rem;
        font-weight: 700;
        color: var(--accent) !important;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin: 0;
        line-height: 1.2;
    }}
    .sv-subtitle {{
        font-size: 0.82rem;
        color: var(--text-dim) !important;
        margin-top: 4px;
        letter-spacing: 0.02em;
    }}
    .sv-badge {{
        display: inline-block;
        background: #1a2e1a;
        border: 1px solid var(--border);
        color: var(--accent2);
        font-size: 0.72rem;
        padding: 4px 12px;
        border-radius: 20px;
        margin-left: auto;
        white-space: nowrap;
    }}

    .sv-section {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 20px 0 14px 0;
    }}
    .sv-section-bar {{
        width: 4px;
        height: 22px;
        background: var(--accent2);
        border-radius: 2px;
        flex-shrink: 0;
    }}
    .sv-section-text {{
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--text) !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 0;
    }}

    [data-testid="stMetric"] {{
        background-color: var(--panel) !important;
        border: 1px solid var(--border) !important;
        border-top: 3px solid var(--accent2) !important;
        border-radius: 10px !important;
        padding: 14px 16px !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: var(--text-dim) !important;
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}
    [data-testid="stMetricValue"] {{
        color: var(--white) !important;
        font-weight: 700 !important;
    }}

    div[data-testid="stForm"] {{
        background-color: var(--panel) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 24px !important;
    }}

    label, .stSelectbox label, .stTextInput label,
    .stNumberInput label, .stDateInput label {{
        color: var(--text-dim) !important;
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        font-weight: 500 !important;
    }}
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    div[data-testid="stDateInput"] input {{
        background-color: var(--bg) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
    }}
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] {{
        background-color: var(--bg) !important;
        border-color: var(--border) !important;
        color: var(--text) !important;
    }}

    h1, h2, h3, p {{ color: var(--text) !important; }}
    .stCaption, small {{ color: var(--text-dim) !important; }}
    hr {{ border-color: var(--border) !important; }}

    [data-testid="stDataFrame"] {{
        background-color: var(--panel) !important;
        border: 1px solid var(--border);
        border-radius: 10px;
    }}

    .stFormSubmitButton button {{
        background-color: var(--accent2) !important;
        color: #0a0e0a !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.85rem !important;
    }}
    .stFormSubmitButton button:hover {{
        background-color: var(--accent) !important;
    }}
</style>

<div class="sv-header">
    <div class="sv-logo-wrap">
        <img src="https://raw.githubusercontent.com/lubrificacaomaquinassv-cloud/sigcf-financeiro/main/logo_sv.png" alt="SV">
    </div>
    <div>
        <p class="sv-title">Lancamentos Financeiros — OS Frota</p>
        <p class="sv-subtitle">Controladoria &bull; Financeiro &bull; {mes_ano}</p>
    </div>
    <span class="sv-badge">SIGCF &bull; v1.0</span>
</div>
""", unsafe_allow_html=True)

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

st.markdown(
    '<div class="sv-section"><div class="sv-section-bar"></div>'
    '<p class="sv-section-text">Resumo do dia</p></div>',
    unsafe_allow_html=True,
)

fc1, fc2, fc3 = st.columns([2, 1, 1])
with fc1:
    filtro_data = st.date_input(
        "Filtrar por data",
        value=datetime.now().date(),
        label_visibility="collapsed",
    )
with fc2:
    slot_total = st.empty()
with fc3:
    slot_qtd = st.empty()

data_str = str(filtro_data)
lanc_dia = [l for l in lancamentos if l.get("data") == data_str]
total_dia = sum(float(l.get("valor") or 0) for l in lanc_dia)
slot_total.metric("Total do dia", f"R$ {total_dia:,.2f}")
slot_qtd.metric("Lancamentos", len(lanc_dia))

st.markdown(
    '<div class="sv-section"><div class="sv-section-bar"></div>'
    '<p class="sv-section-text">Novo lancamento</p></div>',
    unsafe_allow_html=True,
)

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

    enviar = st.form_submit_button("Salvar Lancamento", use_container_width=True, type="primary")

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

st.markdown(
    f'<div class="sv-section"><div class="sv-section-bar"></div>'
    f'<p class="sv-section-text">Lancamentos em {filtro_data.strftime("%d/%m/%Y")}</p></div>',
    unsafe_allow_html=True,
)

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
    st.dataframe(
        df_dia[cols_show].rename(columns=rename),
        use_container_width=True,
        hide_index=True,
    )

    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown(
            '<div class="sv-section"><div class="sv-section-bar"></div>'
            '<p class="sv-section-text">Resumo por item</p></div>',
            unsafe_allow_html=True,
        )
        resumo_item = df_dia.groupby("item")["valor"].sum().reset_index()
        resumo_item.columns = ["Item", "Total R$"]
        st.dataframe(resumo_item, use_container_width=True, hide_index=True)
    with rc2:
        st.markdown(
            '<div class="sv-section"><div class="sv-section-bar"></div>'
            '<p class="sv-section-text">Resumo por tipo de manutencao</p></div>',
            unsafe_allow_html=True,
        )
        resumo_tipo = df_dia.groupby("tipo_manutencao")["valor"].sum().reset_index()
        resumo_tipo.columns = ["Tipo Manut.", "Total R$"]
        st.dataframe(resumo_tipo, use_container_width=True, hide_index=True)
else:
    st.info("Nenhum lancamento nesta data.")

st.markdown(
    '<p style="color:#7d9170;font-size:0.75rem;text-align:center;margin-top:24px;">'
    'SIGCF | Lancamentos Financeiros | Nucleo de Controladoria SV</p>',
    unsafe_allow_html=True,
)
