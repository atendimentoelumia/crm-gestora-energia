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

# Inicializa as variáveis de estado
if 'leads' not in st.session_state:
    st.session_state.leads = []

if 'lead_em_edicao' not in st.session_state:
    st.session_state.lead_em_edicao = None

# ==========================================
# BARRA LATERAL: FORMULÁRIO DINÂMICO (CRIAR / EDITAR)
# ==========================================
with st.sidebar:
    # Se houver um lead selecionado para edição, preenche com os dados dele
    if st.session_state.lead_em_edicao:
        st.header("✏️ Editar Lead")
        lead_atual = st.session_state.lead_em_edicao
        
        # Botão para cancelar a edição e voltar a criar um novo
        if st.button("Cancelar Edição"):
            st.session_state.lead_em_edicao = None
            st.rerun()
    else:
        st.header("➕ Cadastrar Lead")
        lead_atual = {}

    # Formulário principal
    with st.form("form_lead", clear_on_submit=False):
        empresa = st.text_input("Nome da empresa *", value=lead_atual.get('empresa', ''))
        executivo = st.selectbox("Executivo", ["Roberto", "Thaiz", "Peterson"], index=["Roberto", "Thaiz", "Peterson"].index(lead_atual.get('executivo', 'Roberto')))
        contato = st.text_input("Contato na empresa", value=lead_atual.get('contato', ''))
        
        canal = st.selectbox("Canal", ["Direto", "Parceiro"], index=["Direto", "Parceiro"].index(lead_atual.get('canal', 'Direto')))
        produto = st.selectbox("Produto", ["Mercado Livre", "GD"], index=["Mercado Livre", "GD"].index(lead_atual.get('produto', 'Mercado Livre')))
        
        st.markdown("---")
        st.markdown("**Dados Técnicos e Financeiros**")
        consumo_kwh = st.number_input("Consumo médio (kWh)", min_value=0.0, step=100.0, value=float(lead_atual.get('consumo', 0.0)))
        fee_gestao = st.number_input("Fee Gestão (R$/MWh)", min_value=0.0, step=1.0, value=float(lead_atual.get('fee_gestao', 0.0)))
        tempo_contrato = st.number_input("Tempo de contrato (Meses)", min_value=0, step=12, value=int(lead_atual.get('tempo_contrato', 0)))
        
        st.markdown("---")
        migrado = st.selectbox("Cliente Migrado?", ["Sim", "Não"], index=["Sim", "Não"].index(lead_atual.get('migrado', 'Não')))
        proposta = st.selectbox("Proposta apresentada?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(lead_atual.get('proposta', '')))
        
        lista_prob = ["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"]
        probabilidade = st.selectbox("Probabilidade de fechamento", lista_prob, index=lista_prob.index(lead_atual.get('probabilidade', '10%')))
        status = st.text_area("Status / Observações", value=lead_atual.get('status', ''))
        
        # O texto do botão muda dependendo do modo
        texto_botao = "Atualizar Lead" if st.session_state.lead_em_edicao else "Salvar Lead"
        btn_salvar = st.form_submit_button(texto_botao)
        
        if btn_salvar and empresa:
            # Recalcula a matemática financeira
            gestao_mensal = (consumo_kwh / 1000) * fee_gestao
            receita_gestao = gestao_mensal * tempo_contrato
            
            if st.session_state.lead_em_edicao:
                # MODO EDIÇÃO: Atualiza o lead existente na lista
                for idx, lead in enumerate(st.session_state.leads):
                    if lead['id'] == lead_atual['id']:
                        st.session_state.leads[idx].update({
                            "empresa": empresa,
                            "executivo": executivo,
                            "contato": contato,
                            "canal": canal,
                            "produto": produto,
                            "consumo": consumo_kwh,
                            "fee_gestao": fee_gestao,
                            "tempo_contrato": tempo_contrato,
                            "migrado": migrado,
                            "proposta": proposta,
                            "probabilidade": probabilidade,
                            "status": status,
                            "gestao_mensal": gestao_mensal,
                            "receita_gestao": receita_gestao
                        })
                        break
                st.session_state.lead_em_edicao = None # Limpa o modo edição
                st.success("Lead atualizado com sucesso!")
            else:
                # MODO CRIAÇÃO: Adiciona um novo lead à lista
                novo_lead = {
                    "id": str(uuid.uuid4()),
                    "fase": "Contato feito",
                    "empresa": empresa,
                    "executivo": executivo,
                    "contato": contato,
                    "canal": canal,
                    "produto": produto,
                    "consumo": consumo_kwh,
                    "fee_gestao": fee_gestao,
                    "tempo_contrato": tempo_contrato,
                    "migrado": migrado,
                    "proposta": proposta,
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
colunas_kanban = st.columns(len(FASES))

for index, fase in enumerate(FASES):
    with colunas_kanban[index]:
        st.markdown(f"#### {fase}")
        
        leads_nesta_fase = [lead for lead in st.session_state.leads if lead.get("fase") == fase]
        valor_fase = sum(lead.get('receita_gestao', 0) for lead in leads_nesta_fase)
        
        st.markdown(f"<span style='color:gray; font-size:12px;'>{len(leads_nesta_fase)} cartões | R$ {valor_fase:,.2f}</span>", unsafe_allow_html=True)
        st.write("---")
        
        for lead in leads_nesta_fase:
            # Desenhando o Cartão
            st.markdown(f"<div class='card-title'>{lead.get('empresa')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-info'>👤 {lead.get('contato', '')} ({lead.get('executivo', '')})</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-info'>⚡ {lead.get('produto', '')} | {lead.get('consumo', 0):,.0f} kWh</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-money'>💰 R$ {lead.get('receita_gestao', 0):,.2f}</div>", unsafe_allow_html=True)
            
            # Pequenos botões de ação para Editar e Excluir
            col_edit, col_del = st.columns(2)
            with col_edit:
                if st.button("✏️ Editar", key=f"edit_{lead['id']}", use_container_width=True):
                    st.session_state.lead_em_edicao = lead
                    st.rerun()
            with col_del:
                if st.button("❌ Excluir", key=f"del_{lead['id']}", use_container_width=True):
                    st.session_state.leads.remove(lead)
                    st.rerun()
            
            # Caixa de seleção para "Mover" o cartão de fase de forma rápida
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