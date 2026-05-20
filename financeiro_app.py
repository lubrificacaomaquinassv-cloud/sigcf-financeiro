import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

st.set_page_config(page_title="Financeiro OS - SIGCF", layout="wide")

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

# ─────────────────────────────────────────────
# CARREGAMENTO DE DADOS
# ─────────────────────────────────────────────
@st.cache_data(ttl=30)
def carregar_os_oficina():
    res = supabase.table("ordem_servico")\
        .select("numero_os, id_frota, mecanico, tempo_min, status")\
        .order("created_at", desc=True).limit(100).execute()
    return res.data or []

@st.cache_data(ttl=60)
def carregar_colaboradores():
    res = supabase.table("dim_colaborador")\
        .select("nome, custo_hora").eq("ativo", True).execute()
    return res.data or []

@st.cache_data(ttl=10)
def carregar_lancamentos_oficina():
    res = supabase.table("financeiro_os")\
        .select("*").eq("tipo_os", "OFICINA")\
        .order("criado_em", desc=True).limit(20).execute()
    return res.data or []

@st.cache_data(ttl=30)
def carregar_os_lubrificacao():
    res = supabase.table("lubrificacao")\
        .select("id, order_number, vehicle, location, created_at, actions")\
        .order("created_at", desc=True).limit(100).execute()
    return res.data or []

@st.cache_data(ttl=60)
def carregar_dim_insumo():
    res = supabase.table("dim_insumo")\
        .select("id_insumo, nome, unidade, categoria")\
        .order("categoria").execute()
    return res.data or []

@st.cache_data(ttl=60)
def carregar_preco_insumo():
    res = supabase.table("preco_insumo")\
        .select("id_insumo, valor_unitario").eq("ativo", True).execute()
    return res.data or []

@st.cache_data(ttl=10)
def carregar_lancamentos_lubrificacao():
    res = supabase.table("financeiro_lubrificacao")\
        .select("*").order("criado_em", desc=True).limit(20).execute()
    return res.data or []

os_oficina           = carregar_os_oficina()
colaboradores        = carregar_colaboradores()
lancamentos_oficina  = carregar_lancamentos_oficina()
os_lubrificacao      = carregar_os_lubrificacao()
dim_insumo           = carregar_dim_insumo()
preco_insumo         = carregar_preco_insumo()

# mapas
custo_map  = {c['nome']: float(c['custo_hora'] or 0) for c in colaboradores}
preco_map  = {p['id_insumo']: float(p['valor_unitario'] or 0) for p in preco_insumo}
insumo_map = {i['nome']: i['id_insumo'] for i in dim_insumo}

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://i.postimg.cc/Y9X7ddnb/LOGO-BP.jpg", width=140)
    st.divider()
    st.header("Ultimos Lancamentos")
    pagina_sidebar = st.radio("Modulo", ["Oficina", "Lubrificacao"])
    st.divider()
    if pagina_sidebar == "Oficina" and lancamentos_oficina:
        df = pd.DataFrame(lancamentos_oficina)[
            ['numero_os', 'id_frota', 'peca_descricao', 'custo_total_os']].head(10)
        st.table(df)
    elif pagina_sidebar == "Lubrificacao":
        try:
            lanc_lub = carregar_lancamentos_lubrificacao()
            if lanc_lub:
                df2 = pd.DataFrame(lanc_lub)[
                    ['order_number', 'id_frota', 'insumo_nome', 'custo_total']].head(10)
                st.table(df2)
            else:
                st.info("Nenhum lancamento ainda.")
        except:
            st.info("Tabela ainda nao criada.")
    else:
        st.info("Nenhum lancamento ainda.")

# ─────────────────────────────────────────────
# NAVEGAÇÃO PRINCIPAL
# ─────────────────────────────────────────────
aba = st.tabs(["🔧 Oficina", "🛢️ Lubrificacao"])

# ═══════════════════════════════════════════
# ABA OFICINA
# ═══════════════════════════════════════════
with aba[0]:
    lista_os = [
        f"{o['numero_os']} | {o['id_frota']} | {o['mecanico']} | {o['status']}"
        for o in os_oficina
    ]

    if not lista_os:
        st.warning("Nenhuma OS de oficina encontrada.")
    else:
        os_sel        = st.selectbox("Selecione a OS", options=lista_os)
        numero_os_sel = os_sel.split("|")[0].strip()
        id_frota_sel  = os_sel.split("|")[1].strip()
        responsavel   = os_sel.split("|")[2].strip()

        tempo_min_os = 0
        for o in os_oficina:
            if o['numero_os'] == numero_os_sel:
                tempo_min_os = int(o.get('tempo_min') or 0)
                break

        custo_hora_resp = custo_map.get(responsavel.strip(), 0.0)
        custo_mo_calc   = round((tempo_min_os / 60) * custo_hora_resp, 2)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("OS",        numero_os_sel)
        c2.metric("Frota",     id_frota_sel)
        c3.metric("Tempo",     f"{tempo_min_os} min")
        c4.metric("Custo M.O.", f"R$ {custo_mo_calc:.2f}")

        st.divider()

        with st.form("form_oficina", clear_on_submit=True):
            st.subheader("Lançamento de Peca")
            col1, col2, col3 = st.columns(3)
            with col1:
                peca_desc  = st.text_input("Descricao da Peca")
            with col2:
                peca_valor = st.number_input("Valor Unitario (R$)", min_value=0.0,
                                             step=0.01, format="%.2f")
            with col3:
                quantidade = st.number_input("Quantidade", min_value=1.0,
                                             step=1.0, format="%.0f")

            valor_total_pecas = round(peca_valor * quantidade, 2)
            custo_total_os    = round(valor_total_pecas + custo_mo_calc, 2)

            ca, cb, cc = st.columns(3)
            ca.metric("Total Pecas",    f"R$ {valor_total_pecas:.2f}")
            cb.metric("Custo M.O.",     f"R$ {custo_mo_calc:.2f}")
            cc.metric("CUSTO TOTAL OS", f"R$ {custo_total_os:.2f}")

            enviar = st.form_submit_button("SALVAR LANCAMENTO", use_container_width=True,
                                           type="primary")

        if enviar:
            if not peca_desc.strip():
                st.warning("Informe a descricao da peca.")
            elif peca_valor == 0:
                st.warning("Informe o valor da peca.")
            else:
                novo = {
                    "numero_os":         numero_os_sel,
                    "tipo_os":           "OFICINA",
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
                    st.success(f"✅ Lancamento salvo! Custo total OS {numero_os_sel}: R$ {custo_total_os:.2f}")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

# ═══════════════════════════════════════════
# ABA LUBRIFICAÇÃO
# ═══════════════════════════════════════════
with aba[1]:

    lista_lub = [
        f"{o['order_number']} | {o['vehicle']} | {o.get('location','') or ''} | {str(o['created_at'])[:10]}"
        for o in os_lubrificacao
        if o.get('order_number')
    ]

    if not lista_lub:
        st.warning("Nenhuma OS de lubrificacao encontrada.")
    else:
        os_lub_sel    = st.selectbox("Selecione a OS do Comboio", options=lista_lub)
        order_number  = os_lub_sel.split("|")[0].strip()
        frota_lub     = os_lub_sel.split("|")[1].strip()
        local_lub     = os_lub_sel.split("|")[2].strip()

        c1, c2, c3 = st.columns(3)
        c1.metric("OS Comboio", order_number)
        c2.metric("Frota",      frota_lub)
        c3.metric("Local",      local_lub or "—")

        st.divider()

        # Monta lista de insumos agrupada por categoria
        categorias = sorted(set(i['categoria'] for i in dim_insumo))
        opcoes_insumo = {}
        for cat in categorias:
            for i in dim_insumo:
                if i['categoria'] == cat:
                    label = f"{i['nome']} ({i['unidade']})"
                    opcoes_insumo[label] = i['id_insumo']

        with st.form("form_lubrificacao", clear_on_submit=True):
            st.subheader("Lançamento de Insumo")

            col1, col2, col3 = st.columns(3)
            with col1:
                insumo_label = st.selectbox("Insumo", options=list(opcoes_insumo.keys()))
            with col2:
                qtd_lub = st.number_input("Quantidade", min_value=0.01,
                                          step=0.01, format="%.2f")
            with col3:
                id_insumo_sel  = opcoes_insumo[insumo_label]
                preco_unitario = preco_map.get(id_insumo_sel, 0.0)
                st.metric("Preço Unitário", f"R$ {preco_unitario:.2f}")

            custo_total_lub = round(qtd_lub * preco_unitario, 2)
            st.metric("💰 Custo Total do Insumo", f"R$ {custo_total_lub:.2f}")

            obs_lub = st.text_area("Observação", height=60)

            enviar_lub = st.form_submit_button("SALVAR LANÇAMENTO",
                                               use_container_width=True, type="primary")

        if enviar_lub:
            if qtd_lub <= 0:
                st.warning("Informe a quantidade.")
            else:
                novo_lub = {
                    "order_number":  order_number,
                    "id_frota":      frota_lub,
                    "local":         local_lub,
                    "id_insumo":     id_insumo_sel,
                    "insumo_nome":   insumo_label.split(" (")[0],
                    "quantidade":    qtd_lub,
                    "preco_unit":    preco_unitario,
                    "custo_total":   custo_total_lub,
                    "observacao":    obs_lub.strip() or None,
                    "criado_em":     datetime.now().isoformat()
                }
                try:
                    supabase.table("financeiro_lubrificacao").insert(novo_lub).execute()
                    st.success(f"✅ Insumo salvo! {insumo_label} — R$ {custo_total_lub:.2f}")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

        # Lançamentos da OS selecionada
        st.divider()
        st.subheader(f"Insumos lançados — {order_number}")
        try:
            res_lub = supabase.table("financeiro_lubrificacao")\
                .select("*").eq("order_number", order_number)\
                .order("criado_em", desc=True).execute()
            dados_lub = res_lub.data or []
            if dados_lub:
                df_lub = pd.DataFrame(dados_lub)
                total_lub = df_lub["custo_total"].sum()
                st.metric("Total de Insumos da OS", f"R$ {total_lub:.2f}")
                st.dataframe(
                    df_lub[["insumo_nome", "quantidade", "preco_unit", "custo_total", "observacao"]]\
                    .rename(columns={
                        "insumo_nome": "Insumo", "quantidade": "Qtd",
                        "preco_unit": "R$/Unit", "custo_total": "Total",
                        "observacao": "Obs"
                    }),
                    use_container_width=True, hide_index=True
                )
            else:
                st.info("Nenhum insumo lançado para esta OS ainda.")
        except:
            st.info("Aguardando criação da tabela no banco.")

st.divider()
st.caption("SIGCF | Financeiro OS | Nucleo de Controladoria SV")
