st.markdown("""
<style>
    /* ── Fundo geral (estrutura do painel) ── */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    section.main,
    .main .block-container {
        background-color: #0d1117 !important;
        color: #e6edf3;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {
        background-color: #0d1117 !important;
        border-right: 1px solid #30363d;
    }

    /* ── Cards de metrica ── */
    [data-testid="stMetric"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 14px 16px;
    }
    [data-testid="stMetricLabel"] { color: #8b949e !important; }
    [data-testid="stMetricValue"] { color: #e6edf3 !important; }

    /* ── Painel do formulario ── */
    div[data-testid="stForm"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px;
        padding: 24px !important;
    }

    /* ── Campos de entrada (escuros) ── */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    div[data-testid="stDateInput"] input {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
    }

    /* ── Selectbox / dropdown ── */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] {
        background-color: #0d1117 !important;
        border-color: #30363d !important;
        color: #e6edf3 !important;
    }

    /* ── Labels e titulos ── */
    h1, h2, h3, label, p { color: #e6edf3 !important; }
    .stCaption, small { color: #8b949e !important; }

    /* ── Divisores ── */
    hr { border-color: #30363d !important; margin: 1rem 0; }

    /* ── Tabelas ── */
    [data-testid="stDataFrame"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d;
        border-radius: 8px;
    }

    /* ── Botao salvar ── */
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
