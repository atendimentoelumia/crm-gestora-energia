import streamlit as st
import uuid

# Configuração da página
st.set_page_config(page_title="CRM E-lumia", layout="wide")

# Estilo visual dos cartões (cards)
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
            # Cálculos automáticos de Gestão Mensal e Receita
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
        
        # Filtra as leads e garante que não há erros caso a chave 'fase' não exista
        leads_nesta_fase = [lead for lead in st.session_state.leads if lead.get("fase") == fase]
        
        # Utiliza o .get() para somar o valor da fase com segurança (0 se não houver)
        valor_fase = sum(lead.get('receita_gestao', 0) for lead in leads_nesta_fase)
        
        st.markdown(f"<span style='color:gray; font-size:12px;'>{len(leads_nesta_fase)} cartões | R$ {valor_fase:,.2f}</span>", unsafe_allow_html=True)
        st.write("---")
        
        for lead in leads_nesta_fase:
            # Captura os dados de forma segura
            empresa_nome = lead.get('empresa', 'Empresa Indefinida')
            contato_nome = lead.get('contato', '')
            exec_nome = lead.get('executivo', '')
            prod_nome = lead.get('produto', '')
            cons = lead.get('consumo', 0)
            receita = lead.get('receita_gestao', 0)

            # Desenhando o Cartão (Card)
            st.markdown(f"<div class='card-title'>{empresa_nome}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-info'>👤 {contato_nome} ({exec_nome})</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-info'>⚡ {prod_nome} | {cons:,.0f} kWh</div>", unsafe_allow_html=True)
            
            # Mostra o valor projetado no cartão de forma segura
            st.markdown(f"<div class='card-money'>💰 R$ {receita:,.2f}</div>", unsafe_allow_html=True)
            
            # Caixa de seleção para "Mover" o cartão de fase
            nova_fase = st.selectbox(
                "Mover para:", 
                FASES, 
                index=FASES.index(lead.get('fase', fase)), 
                key=f"move_{lead['id']}",
                label_visibility="collapsed"
            )
            
            if nova_fase != lead.get('fase'):
                lead['fase'] = nova_fase
                st.rerun()
                
            st.write("") # Espaçamento entre os cartões