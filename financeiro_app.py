import streamlit as st
import pandas as pd
from datetime import datetime, date
from supabase import create_client

st.set_page_config(
    page_title="LANÇAMENTOS FINANCEIROS - SIGCF",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from sigcf_auth import exigir_acesso, logo_html

ITENS_FINANCEIRO = ["PECAS", "M.O.", "M.O. OPERADOR", "DIESEL", "OUTROS"]
TIPOS_MANUTENCAO = ["HIDRAULICO", "ELETRICO", "MOTOR", "TDP", "OUTROS"]

exigir_acesso("LANÇAMENTOS FINANCEIROS — OS Frota")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&display=swap');
[data-testid="stAppViewContainer"]{background:#0a1409;}
[data-testid="stSidebar"]{display:none;}
[data-testid="stHeader"]{background:#0a1409;}
h1,h2,h3,h4,p,span,label{color:#e8edd0;}
h1{font-family:'Barlow Condensed',sans-serif;letter-spacing:1px;}
.stCaption,[data-testid="stCaptionContainer"] p{color:#8aab80!important;}
.sec{font-family:'Barlow Condensed',sans-serif;font-size:12px;font-weight:700;
 letter-spacing:2px;text-transform:uppercase;color:#8aab80;
 border-left:4px solid #4a9e3f;padding-left:10px;margin:8px 0 12px;}
.logo-frame{background:linear-gradient(145deg,#0a1628,#0d2040);border:2px solid #c9a227;
 border-radius:12px;padding:5px;display:inline-block;box-shadow:0 4px 18px rgba(0,0,0,.45);}
.logo-frame img{display:block;border-radius:8px;}
.ctx-box{background:#0d180c;border:1px solid #1e2e1c;border-radius:12px;padding:14px 16px;margin-bottom:12px;}

.stTextInput input,.stNumberInput input,.stTextArea textarea,
[data-testid="stDateInput"] input{
 background:#dce6d2!important;color:#1a2818!important;
 border:1px solid #4a6644!important;border-radius:8px!important;}
.stTextInput input:focus,.stNumberInput input:focus,.stTextArea textarea:focus,
[data-testid="stDateInput"] input:focus{
 border-color:#6fcf60!important;box-shadow:0 0 0 1px #6fcf6044!important;}
div[data-baseweb="select"] > div{
 background:#dce6d2!important;border:1px solid #4a6644!important;
 color:#1a2818!important;border-radius:8px!important;}
div[data-baseweb="select"] div{color:#1a2818!important;}
div[data-baseweb="select"] svg{fill:#4a6644!important;}
ul[data-testid="stSelectboxVirtualDropdown"],
div[data-baseweb="popover"] ul{background:#e8edd0!important;}
div[data-baseweb="popover"] li{color:#1a2818!important;}
[data-testid="stNumberInput"] button{
 background:#cdd9c4!important;border-color:#4a6644!important;color:#1a2818!important;}
[data-testid="stForm"]{
 background:#0d180c!important;border:1px solid #1e2e1c!important;
 border-radius:12px;padding:12px 16px;}
[data-testid="stVerticalBlockBorderWrapper"]{
 background:#0d180c!important;border-color:#1e2e1c!important;}
div[data-testid="stMetric"]{background:#0d180c;border:1px solid #1e2e1c;border-radius:10px;padding:10px 14px;}
div[data-testid="stMetric"] label{color:#8aab80!important;}
div[data-testid="stMetricValue"]{color:#6fcf60!important;font-family:'Barlow Condensed',sans-serif;}
.stButton button,[data-testid="stFormSubmitButton"] button{
 background:#4a9e3f!important;color:#ffffff!important;border:1px solid #6fcf60!important;
 font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:1.5px;
 text-transform:uppercase;border-radius:8px;}
.stButton button:hover,[data-testid="stFormSubmitButton"] button:hover{background:#3d8534!important;}
.stButton button p,[data-testid="stFormSubmitButton"] button p{color:#ffffff!important;}
</style>
""", unsafe_allow_html=True)


def dark_table(df, height=320):
    if df.empty:
        st.info("Nenhum registro.")
        return
    rows = "".join(
        "<tr>" + "".join(
            f'<td style="padding:6px 10px;border-bottom:1px solid #1e2e1c;'
            f'color:#e8edd0;font-size:12px;white-space:nowrap;">{v}</td>'
            for v in row) + "</tr>"
        for _, row in df.iterrows())
    headers = "".join(
        f'<th style="padding:7px 10px;background:#111c10;color:#8aab80;font-size:10px;'
        f'font-weight:700;text-transform:uppercase;letter-spacing:1px;'
        f'border-bottom:2px solid #1e2e1c;white-space:nowrap;">{c}</th>'
        for c in df.columns)
    st.markdown(
        f'<div style="overflow-x:auto;border:1px solid #1e2e1c;border-radius:10px;">'
        f'<div style="max-height:{height}px;overflow-y:auto;">'
        f'<table style="width:100%;border-collapse:collapse;background:#0d180c;'
        f'font-family:Barlow Condensed,sans-serif;"><thead><tr>{headers}</tr></thead>'
        f'<tbody>{rows}</tbody></table></div></div>',
        unsafe_allow_html=True,
    )


def fmt_moeda(v):
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return "R$ 0,00"


try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as exc:
    st.error("Configure SUPABASE_URL e SUPABASE_KEY nos Secrets do Streamlit Cloud.")
    st.caption(str(exc))
    st.stop()


@st.cache_data(ttl=10)
def carregar_lancamentos():
    res = (
        supabase.table("financeiro_lancamento")
        .select("*")
        .order("data", desc=True)
        .order("criado_em", desc=True)
        .limit(500)
        .execute()
    )
    return res.data or []


@st.cache_data(ttl=60)
def carregar_frotas():
    res = (
        supabase.table("dim_frota")
        .select("id_frota, modelo, categoria")
        .eq("ativo", True)
        .order("id_frota")
        .execute()
    )
    return res.data or []


def lancamentos_do_dia(rows: list, data_ref: date) -> list:
    data_str = str(data_ref)
    return [l for l in rows if l.get("data") == data_str]


def df_lancamentos(rows: list) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
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
    cols = [c for c in rename if c in df.columns]
    out = df[cols].rename(columns=rename)
    if "Valor" in out.columns:
        out["Valor"] = out["Valor"].apply(fmt_moeda)
    return out


lancamentos = carregar_lancamentos()
frotas = carregar_frotas()
opcoes_frota = {"(sem frota)": None}
for f in frotas:
    opcoes_frota[f"{f['id_frota']} — {f.get('modelo', '')}"] = f["id_frota"]

col_logo, col_titulo, col_acao = st.columns([1.1, 5, 1])
with col_logo:
    st.markdown(logo_html(118), unsafe_allow_html=True)
with col_titulo:
    st.title("Lançamentos Financeiros — OS Frota")
    st.caption("SIGCF — CONTROLADORIA · GESTÃO E ANÁLISE DE DADOS")
with col_acao:
    if st.button("🔄 Atualizar"):
        st.cache_data.clear()
        st.rerun()

st.divider()

st.markdown('<div class="sec">Resumo do dia</div>', unsafe_allow_html=True)
fc1, fc2, fc3 = st.columns([2, 1, 1])
with fc1:
    filtro_data = st.date_input("Filtrar por data", value=date.today(), format="DD/MM/YYYY")
with fc2:
    lanc_dia = lancamentos_do_dia(lancamentos, filtro_data)
    total_dia = sum(float(l.get("valor") or 0) for l in lanc_dia)
    st.metric("Total do dia", fmt_moeda(total_dia))
with fc3:
    st.metric("Lançamentos", len(lanc_dia))

st.markdown('<div class="sec">Novo lançamento</div>', unsafe_allow_html=True)
st.markdown('<div class="ctx-box">', unsafe_allow_html=True)

with st.form("form_lancamento", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        data_lanc = st.date_input("📅 Data *", value=date.today(), format="DD/MM/YYYY")
    with col2:
        nfe = st.text_input("🧾 NFE")
    with col3:
        id_fornecedor = st.text_input("🏭 ID Fornecedor SAP")

    col4, col5, col6 = st.columns(3)
    with col4:
        item = st.selectbox("📦 Item *", options=ITENS_FINANCEIRO)
    with col5:
        tipo_manutencao = st.selectbox("🔧 Tipo de manutenção *", options=TIPOS_MANUTENCAO)
    with col6:
        valor = st.number_input("💰 Valor (R$) *", min_value=0.0, step=0.01, format="%.2f")

    col7, col8 = st.columns(2)
    with col7:
        frota_label = st.selectbox("🚜 Frota (opcional)", options=list(opcoes_frota.keys()))
    with col8:
        observacao = st.text_area("💬 Observação", height=68)

    enviar = st.form_submit_button("✅ Salvar lançamento", use_container_width=True, type="primary")

st.markdown('</div>', unsafe_allow_html=True)

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
            st.success(f"Lançamento salvo — {item} | {tipo_manutencao} | {fmt_moeda(valor)}")
            st.cache_data.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

st.markdown(
    f'<div class="sec">Lançamentos em {filtro_data.strftime("%d/%m/%Y")}</div>',
    unsafe_allow_html=True,
)

lanc_dia = lancamentos_do_dia(lancamentos, filtro_data)
if lanc_dia:
    df_dia = df_lancamentos(lanc_dia)
    dark_table(df_dia, height=280)

    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown('<div class="sec">Resumo por item</div>', unsafe_allow_html=True)
        resumo_item = (
            pd.DataFrame(lanc_dia)
            .groupby("item")["valor"]
            .sum()
            .reset_index()
        )
        resumo_item.columns = ["Item", "Total"]
        resumo_item["Total"] = resumo_item["Total"].apply(fmt_moeda)
        dark_table(resumo_item, height=180)
    with rc2:
        st.markdown('<div class="sec">Resumo por tipo de manutenção</div>', unsafe_allow_html=True)
        resumo_tipo = (
            pd.DataFrame(lanc_dia)
            .groupby("tipo_manutencao")["valor"]
            .sum()
            .reset_index()
        )
        resumo_tipo.columns = ["Tipo Manut.", "Total"]
        resumo_tipo["Total"] = resumo_tipo["Total"].apply(fmt_moeda)
        dark_table(resumo_tipo, height=180)
else:
    st.info("Nenhum lançamento nesta data.")

st.divider()
st.caption("SIGCF | Lançamentos Financeiros | Núcleo de Controladoria SV")
