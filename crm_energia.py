import streamlit as st
import uuid

# Configuração da página
st.set_page_config(page_title="CRM E-lumia", layout="wide")

# Estilo visual dos cards
st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div {
        background-color: #1E1E1E;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
    }
    .card-title { color: #4CAF50; font-weight: bold; font-size: 16px; margin-bottom: 5px; }
    .card-info { font-size: 13px; color: #E0E0E0; margin-bottom: 3px; }
    .card-money { font-size: 14px; color: #FFD700; font-weight: bold; margin-top: 5px; margin-bottom: 5px;}
    </style>
""", unsafe_allow_html=True)

st.title("⚡ CRM E-lumia")

FASES = [
    "Contato feito", "Fatura recebida", "Aguardando estudo", 
    "Aguardando reunião", "Proposta apresentada", 
    "Aguardando decisão", "Ganho", "Perdido"
]

if 'leads' not in st.session_state:
    st.session_state.leads = []

# ==========================================
# BARRA LATERAL: FORMULÁRIO BASEADO NA SUA PLANILHA
# ==========================================
with st.sidebar:
    st.header("➕ Cadastrar Lead")
    
    with st.form("form_novo_lead", clear_on_submit=True):
        empresa = st.text_input("Nome da empresa *")
        executivo = st.selectbox("Executivo", ["Roberto", "Thaiz", "Peterson"])
        contato = st.text_input("Contato na empresa")
        
        canal = st.selectbox("Canal", ["Direto", "Parceiro"])
        produto = st.selectbox("Produto", ["Mercado Livre", "GD"])
        
        st.markdown("---")
        st.markdown("**Dados Técnicos e Financeiros**")
        consumo_kwh = st.number_input("Consumo médio (kWh)", min_value=0.0, step=100.0)
        fee_gestao = st.number_input("Fee Gestão (R$/MWh)", min_value=0.0, step=1.0)
        tempo_contrato = st.number_input("Tempo de contrato (Meses)", min_value=0, step=12)
        
        st.markdown("---")
        migrado = st.selectbox("Cliente Migrado?", ["Sim", "Não"])
        proposta = st.selectbox("Proposta apresentada?", ["", "Sim", "Não"])
        probabilidade = st.selectbox("Probabilidade de fechamento", ["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"])
        status = st.text_area("Status / Observações")
        
        btn_salvar = st.form_submit_button("Salvar Lead")
        
        if btn_salvar and empresa:
            # A MÁGICA ACONTECE AQUI: Cálculos automáticos de Gestão Mensal e Receita!
            gestao_mensal = (consumo_kwh / 1000) * fee_gestao
            receita_gestao = gestao_mensal * tempo_contrato
            
            novo_lead = {
                "id": str(uuid.uuid4()),
                "fase": "Contato feito",
                "empresa": empresa,
                "executivo": executivo,
                "contato": contato,
                "produto": produto,
                "consumo": consumo_kwh,
                "probabilidade": probabilidade,
                "status": status,
                "gestao_mensal": gestao_mensal,
                "receita_gestao": receita_gestao
            }
            st.session_state.leads.append(novo_lead)
            st.success("Lead salvo com sucesso!")
            st.rerun()

# ==========================================
# PAINEL KANBAN (COLUNAS)
# ==========================================
# Cria o layout de colunas para o Kanban
colunas_kanban = st.columns(len(FASES))

for index, fase in enumerate(FASES):
    with colunas_kanban[index]:
        st.markdown(f"#### {fase}")
        
        # Conta quantos cards e o valor total em negociação nesta fase
        leads_nesta_fase = [lead for lead in st.session_state.leads if lead["fase"] == fase]
        valor_fase = sum(lead['receita_gestao'] for lead in leads_nesta_fase)
        
        st.markdown(f"<span style='color:gray; font-size:12px;'>{len(leads_nesta_fase)} cards | R$ {valor_fase:,.2f}</span>", unsafe_allow_html=True)
        st.write("---")
        
        for lead in leads_nesta_fase:
            # Desenhando o Card
            st.markdown(f"<div class='card-title'>{lead['empresa']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-info'>👤 {lead['contato']} ({lead['executivo']})</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-info'>⚡ {lead['produto']} | {lead['consumo']:,.0f} kWh</div>", unsafe_allow_html=True)
            
            # Mostra o dinheiro projetado no card (Receita de Gestão Total)
            st.markdown(f"<div class='card-money'>💰 R$ {lead['receita_gestao']:,.2f}</div>", unsafe_allow_html=True)
            
            # Selectbox para "Mover" o card de fase
            nova_fase = st.selectbox(
                "Mover para:", 
                FASES, 
                index=FASES.index(lead['fase']), 
                key=f"move_{lead['id']}",
                label_visibility="collapsed"
            )
            
            if nova_fase != lead['fase']:
                lead['fase'] = nova_fase
                st.rerun()
                
            st.write("") # Espaçamento entre os cards