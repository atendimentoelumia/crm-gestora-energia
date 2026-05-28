import streamlit as st
import uuid

# Configuração da página para ocupar a tela toda (ideal para Kanban)
st.set_page_config(page_title="CRM Gestora de Energia", layout="wide")

# Forçando um estilo escuro (Dark Mode) nos cards via CSS
st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div {
        background-color: #1E1E1E;
        padding: 10px;
        border-radius: 8px;
    }
    .card-title { color: #4CAF50; font-weight: bold; margin-bottom: 5px; }
    .card-info { font-size: 14px; color: #E0E0E0; margin-bottom: 2px; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ CRM - Gestora de Energia")

# Definindo as fases do Kanban
FASES = [
    "Contato feito", "Fatura recebida", "Aguardando estudo", 
    "Aguardando reunião", "Proposta apresentada", 
    "Aguardando decisão", "Ganho", "Perdido"
]

# Inicializando o "banco de dados" temporário na memória do Streamlit
if 'leads' not in st.session_state:
    st.session_state.leads = []

# ==========================================
# BARRA LATERAL: FORMULÁRIO DE NOVO LEAD
# ==========================================
with st.sidebar:
    st.header("➕ Novo Card (Lead)")
    
    with st.form("form_novo_lead", clear_on_submit=True):
        contato = st.text_input("Contato (Nome da pessoa)")
        empresa = st.text_input("Nome da empresa")
        cnpj = st.text_input("CNPJ")
        executivo = st.selectbox("Executivo", ["Roberto", "Thaiz", "Peterson"])
        
        canal = st.radio("Canal", ["Direto", "Parceiro"])
        # Variável para o nome do parceiro (ficará vazia se for Direto)
        nome_parceiro = ""
        
        # Nota: O Streamlit form não suporta lógica condicional dinâmica *dentro* do submit sem recarregar.
        # Para simplificar no MVP, deixamos o campo de parceiro sempre visível, mas opcional.
        st.caption("Se o canal for 'Parceiro', digite o nome abaixo:")
        nome_parceiro = st.text_input("Nome do Parceiro (Opcional)")
        
        produto = st.selectbox("Produto", ["Mercado Livre (ML)", "Geração Distribuída (GD)"])
        consumo_kwh = st.number_input("Consumo Mês (kWh)", min_value=0.0, step=100.0)
        tempo_contrato = st.number_input("Tempo de Contrato (Meses)", min_value=0, step=12)
        migrado = st.radio("Cliente Migrado?", ["Sim", "Não"])
        observacoes = st.text_area("Observações Gerais")
        
        btn_salvar = st.form_submit_button("Salvar Lead")
        
        if btn_salvar and empresa:
            novo_lead = {
                "id": str(uuid.uuid4()), # Gera um ID único para o card
                "fase": "Contato feito", # Todo card nasce na primeira fase
                "contato": contato,
                "empresa": empresa,
                "cnpj": cnpj,
                "executivo": executivo,
                "canal": "Direto" if canal == "Direto" else f"Parceiro ({nome_parceiro})",
                "produto": produto,
                "consumo": consumo_kwh,
                "tempo": tempo_contrato,
                "migrado": migrado,
                "obs": observacoes
            }
            st.session_state.leads.append(novo_lead)
            st.success("Lead salvo com sucesso!")

# ==========================================
# PAINEL KANBAN (COLUNAS)
# ==========================================
st.write("---")

# Cria 8 colunas na tela
colunas_kanban = st.columns(len(FASES))

for index, fase in enumerate(FASES):
    with colunas_kanban[index]:
        st.markdown(f"### {fase}")
        st.write("---")
        
        # Filtra os leads que pertencem a esta fase
        leads_nesta_fase = [lead for lead in st.session_state.leads if lead["fase"] == fase]
        
        for lead in leads_nesta_fase:
            # Desenhando o Card
            st.markdown(f"<div class='card-title'>{lead['empresa']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-info'>👤 {lead['contato']} ({lead['executivo']})</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-info'>⚡ {lead['produto']} | {lead['consumo']} kWh</div>", unsafe_allow_html=True)
            
            # Selectbox para "Mover" o card de fase
            nova_fase = st.selectbox(
                "Mover para:", 
                FASES, 
                index=FASES.index(lead['fase']), 
                key=f"move_{lead['id']}",
                label_visibility="collapsed"
            )
            
            # Se a fase foi alterada no selectbox, atualiza o dado e recarrega a tela
            if nova_fase != lead['fase']:
                lead['fase'] = nova_fase
                st.rerun()
                
            st.write("") # Espaçamento entre os cards