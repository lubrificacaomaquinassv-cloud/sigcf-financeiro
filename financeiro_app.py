import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

st.set_page_config(page_title="Financeiro OS - SIGCF", layout="wide")

col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    st.image("https://i.postimg.cc/Y9X7ddnb/LOGO-BP.jpg", width=110)
with col_titulo:
    st.title("Lançamentos Financeiros de OS")
    st.caption("SIGCF - Sistema Integrado de Gestao de Custos de Frota")

st.divider()

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Carregar OS abertas
@st.cache_data(ttl=30)
def carregar_os_oficina():
    res = supabase.table("ordem_servico")\
        .select("numero_os, id_frota, mecanico, tempo_min, status")\
        .order("created_at", desc=True).limit(100).execute()
    return res.data or []

@st.cache_data(ttl=30)
def carregar_os_borracharia():
    res = supabase.table("os_borracharia")\
        .select("numero_os, id_frota, borracheiro, tempo_minutos, status")\
        .order("criado_em", desc=True).limit(100).execute()
    return res.data or []

@st.cache_data(ttl=60)
def carregar_colaboradores():
    res = supabase.table("dim_colaborador")\
        .select("nome, custo_hora").eq("ativo", True).execute()
    return res.data or []

@st.cache_data(ttl=10)
def carregar_lancamentos():
    res = supabase.table("financeiro_os")\
        .select("*").order("criado_em", desc=True).limit(20).execute()
    return res.data or []

os_oficina     = carregar_os_oficina()
os_borracharia = carregar_os_borracharia()
colaboradores  = carregar_colaboradores()
lancamentos    = carregar_lancamentos()

# mapa custo_hora por nome
custo_map = {c['nome']: float(c['custo_hora'] or 0) for c in colaboradores}

# ── Sidebar lancamentos recentes
with st.sidebar:
    st.image("https://i.postimg.cc/Y9X7ddnb/LOGO-BP.jpg", width=140)
    st.divider()
    st.header("Ultimos Lancamentos")
    if lancamentos:
        df = pd.DataFrame(lancamentos)[['numero_os','id_frota','peca_descricao','custo_total_os']].head(10)
        st.table(df)
    else:
        st.info("Nenhum lancamento ainda.")

# ── Selecao do tipo de OS
tipo_os = st.radio("Tipo de OS", ["OFICINA", "BORRACHARIA"], horizontal=True)

if tipo_os == "OFICINA":
    lista_os = [f"{o['numero_os']} | {o['id_frota']} | {o['mecanico']} | {o['status']}" for o in os_oficina]
else:
    lista_os = [f"{o['numero_os']} | {o['id_frota']} | {o['borracheiro']} | {o['status']}" for o in os_borracharia]

if not lista_os:
    st.warning("Nenhuma OS encontrada.")
    st.stop()

os_sel = st.selectbox("Selecione a OS", options=lista_os)
numero_os_sel = os_sel.split("|")[0].strip()
id_frota_sel  = os_sel.split("|")[1].strip()
responsavel   = os_sel.split("|")[2].strip()

# Busca tempo da OS selecionada
tempo_min_os = 0
if tipo_os == "OFICINA":
    for o in os_oficina:
        if o['numero_os'] == numero_os_sel:
            tempo_min_os = int(o.get('tempo_min') or 0)
            break
else:
    for o in os_borracharia:
        if o['numero_os'] == numero_os_sel:
            tempo_min_os = int(o.get('tempo_minutos') or 0)
            break

custo_hora_resp = custo_map.get(responsavel.strip(), 0.0)
custo_mo_calc   = round((tempo_min_os / 60) * custo_hora_resp, 2)

# ── Painel info OS
c1, c2, c3, c4 = st.columns(4)
c1.metric("OS", numero_os_sel)
c2.metric("Frota", id_frota_sel)
c3.metric("Tempo", f"{tempo_min_os} min")
c4.metric("Custo M.O.", f"R$ {custo_mo_calc:.2f}")

st.divider()

# ── Formulario de pecas
with st.form("form_financeiro", clear_on_submit=True):
    st.subheader("Lançamento de Peca")

    col1, col2, col3 = st.columns(3)
    with col1:
        peca_desc  = st.text_input("Descricao da Peca")
    with col2:
        peca_valor = st.number_input("Valor Unitario (R$)", min_value=0.0, step=0.01, format="%.2f")
    with col3:
        quantidade = st.number_input("Quantidade", min_value=1.0, step=1.0, format="%.0f")

    valor_total_pecas = round(peca_valor * quantidade, 2)
    custo_total_os    = round(valor_total_pecas + custo_mo_calc, 2)

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Pecas", f"R$ {valor_total_pecas:.2f}")
    col_b.metric("Custo M.O.", f"R$ {custo_mo_calc:.2f}")
    col_c.metric("CUSTO TOTAL OS", f"R$ {custo_total_os:.2f}")

    enviar = st.form_submit_button("SALVAR LANCAMENTO")

    if enviar:
        if not peca_desc.strip():
            st.warning("Informe a descricao da peca.")
        elif peca_valor == 0:
            st.warning("Informe o valor da peca.")
        else:
            novo = {
                "numero_os":         numero_os_sel,
                "tipo_os":           tipo_os,
                "id_frota":          id_frota_sel,
                "mecanico":          responsavel,
                "peca_descricao":    peca_desc,
                "peca_valor":        peca_valor,
                "quantidade":        quantidade,
                "valor_total_pecas": valor_total_pecas,
                "tempo_min":         tempo_min_os,
                "custo_hora_mo":     custo_hora_resp,
                "custo_mo":          custo_mo_calc,
                "custo_total_os":    custo_total_os,
                "criado_em":         datetime.now().isoformat()
            }
            try:
                supabase.table("financeiro_os").insert(novo).execute()
                st.success(f"Lancamento salvo! Custo total OS {numero_os_sel}: R$ {custo_total_os:.2f}")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

st.divider()
st.caption("SIGCF | Financeiro OS | Nucleo de Controladoria SV")
