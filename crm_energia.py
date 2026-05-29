import streamlit as st
import uuid

st.set_page_config(page_title="CRM E-lumia", layout="wide")

st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div {
        background-color: #1E1E1E; padding: 12px; border-radius: 8px; border-left: 4px solid #4CAF50;
    }
    .card-title { color: #4CAF50; font-weight: bold; font-size: 16px; margin-bottom: 5px; }
    .card-info { font-size: 13px; color: #E0E0E0; margin-bottom: 3px; }
    .card-money { font-size: 14px; color: #FFD700; font-weight: bold; margin-top: 5px; margin-bottom: 5px;}
    </style>
""", unsafe_allow_html=True)

st.title("⚡ CRM E-lumia")

# As duas esteiras separadas
FASES_LEADS = ["A Contatar", "Contatado", "Quente", "Stand by"]
FASES_CRM = ["Contato feito", "Fatura recebida", "Aguardando estudo", "Aguardando reunião", "Proposta apresentada", "Aguardando decisão", "Ganho", "Perdido"]

if 'leads' not in st.session_state:
    st.session_state.leads = []
if 'lead_em_edicao' not in st.session_state:
    st.session_state.lead_em_edicao = None
if 'lead_para_converter' not in st.session_state:
    st.session_state.lead_para_converter = None

# ==========================================
# BARRA LATERAL: INTELIGÊNCIA DOS FORMULÁRIOS
# ==========================================
with st.sidebar:
    if st.session_state.lead_para_converter:
        # --- FORMULÁRIO DE CONVERSÃO (QUENTE -> FATURA RECEBIDA) ---
        st.header("🔥 Converter Oportunidade")
        st.warning("Para mover para 'Fatura Recebida', preencha os dados técnicos.")
        lead_conv = st.session_state.lead_para_converter
        
        with st.form("form_conversao"):
            produto = st.selectbox("Produto", ["Mercado Livre", "GD"])
            consumo_kwh = st.number_input("Consumo médio (kWh)", min_value=0.0, step=100.0)
            fee_gestao = st.number_input("Fee Gestão (R$/MWh)", min_value=0.0, step=1.0)
            tempo_contrato = st.number_input("Tempo de contrato (Meses)", min_value=0, step=12)
            
            if st.form_submit_button("Confirmar Conversão"):
                for idx, l in enumerate(st.session_state.leads):
                    if l['id'] == lead_conv['id']:
                        gestao_mensal = (consumo_kwh / 1000) * fee_gestao
                        receita_gestao = gestao_mensal * tempo_contrato
                        st.session_state.leads[idx].update({
                            "fase": "Fatura recebida", # Move para o CRM!
                            "produto": produto, "consumo": consumo_kwh, "fee_gestao": fee_gestao,
                            "tempo_contrato": tempo_contrato, "gestao_mensal": gestao_mensal, "receita_gestao": receita_gestao
                        })
                        break
                st.session_state.lead_para_converter = None
                st.rerun()
                
        if st.button("Cancelar"):
            st.session_state.lead_para_converter = None
            st.rerun()

    elif st.session_state.lead_em_edicao:
        # --- FORMULÁRIO DE EDIÇÃO (Simplificado para o MVP) ---
        st.header("✏️ Editar")
        lead_atual = st.session_state.lead_em_edicao
        with st.form("form_edit"):
            empresa = st.text_input("Empresa", value=lead_atual.get('empresa', ''))
            contato = st.text_input("Contato", value=lead_atual.get('contato', ''))
            status = st.text_area("Status / Observações", value=lead_atual.get('status', ''))
            if st.form_submit_button("Atualizar"):
                for idx, l in enumerate(st.session_state.leads):
                    if l['id'] == lead_atual['id']:
                        st.session_state.leads[idx].update({"empresa": empresa, "contato": contato, "status": status})
                        break
                st.session_state.lead_em_edicao = None
                st.rerun()
        if st.button("Cancelar Edição"):
            st.session_state.lead_em_edicao = None
            st.rerun()

    else:
        # --- FORMULÁRIO DE CADASTRO SIMPLES (PROSPECÇÃO) ---
        st.header("➕ Cadastrar Novo Prospect")
        with st.form("form_novo_prospect", clear_on_submit=True):
            empresa = st.text_input("Nome da empresa *")
            executivo = st.selectbox("Executivo", ["Roberto", "Thaiz", "Peterson"])
            contato = st.text_input("Contato na empresa")
            canal = st.selectbox("Canal", ["Direto", "Parceiro"])
            
            if st.form_submit_button("Salvar Prospect"):
                if empresa:
                    novo_lead = {
                        "id": str(uuid.uuid4()),
                        "fase": "A Contatar", # Nasce sempre no primeiro funil
                        "empresa": empresa, "executivo": executivo, "contato": contato, "canal": canal,
                        "consumo": 0, "receita_gestao": 0 # Dados zerados por enquanto
                    }
                    st.session_state.leads.append(novo_lead)
                    st.success("Prospect adicionado!")
                    st.rerun()

# ==========================================
# FUNÇÃO PARA DESENHAR OS CARTÕES
# ==========================================
def desenhar_cartao(lead, lista_fases):
    st.markdown(f"<div class='card-title'>{lead.get('empresa')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card-info'>👤 {lead.get('contato', '')} ({lead.get('executivo', '')})</div>", unsafe_allow_html=True)
    
    if lead.get('receita_gestao', 0) > 0:
        st.markdown(f"<div class='card-info'>⚡ {lead.get('produto', '')} | {lead.get('consumo', 0):,.0f} kWh</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card-money'>💰 R$ {lead.get('receita_gestao', 0):,.2f}</div>", unsafe_allow_html=True)
    
    col_edit, col_del = st.columns(2)
    with col_edit:
        if st.button("✏️", key=f"edit_{lead['id']}", help="Editar"):
            st.session_state.lead_em_edicao = lead
            st.rerun()
    with col_del:
        if st.button("❌", key=f"del_{lead['id']}", help="Excluir"):
            st.session_state.leads.remove(lead)
            st.rerun()
            
    fase_atual = lead.get('fase')
    indice_fase = lista_fases.index(fase_atual)
    
    col_esq, col_dir = st.columns(2)
    with col_esq:
        if indice_fase > 0:
            if st.button("⬅️", key=f"esq_{lead['id']}"):
                lead['fase'] = lista_fases[indice_fase - 1]
                st.rerun()
    with col_dir:
        # AQUI ESTÁ A REGRA: Se for o último do funil de Leads, o botão muda para "Converter"
        if lista_fases == FASES_LEADS and indice_fase == len(FASES_LEADS) - 1:
            pass # Fica em Stand By, não avança direto
        elif lista_fases == FASES_LEADS and fase_atual == "Quente":
            if st.button("🚀 Converter", key=f"conv_{lead['id']}"):
                st.session_state.lead_para_converter = lead
                st.rerun()
        elif indice_fase < len(lista_fases) - 1:
            if st.button("➡️", key=f"dir_{lead['id']}"):
                lead['fase'] = lista_fases[indice_fase + 1]
                st.rerun()

# ==========================================
# PAINEL 1: ESTEIRA DE PROSPECÇÃO (LEADS)
# ==========================================
st.markdown("### 🎯 Esteira de Prospecção (SDR)")
colunas_leads = st.columns(len(FASES_LEADS))
for index, fase in enumerate(FASES_LEADS):
    with colunas_leads[index]:
        st.markdown(f"##### {fase}")
        leads_fase = [l for l in st.session_state.leads if l.get("fase") == fase]
        st.markdown(f"<span style='color:gray; font-size:12px;'>{len(leads_fase)} prospects</span>", unsafe_allow_html=True)
        st.write("---")
        for lead in leads_fase:
            desenhar_cartao(lead, FASES_LEADS)
            st.write("")

st.write("---")

# ==========================================
# PAINEL 2: PIPELINE DE VENDAS (CLOSER)
# ==========================================
st.markdown("### 💰 Pipeline de Vendas (Fechamento)")
colunas_crm = st.columns(len(FASES_CRM))
for index, fase in enumerate(FASES_CRM):
    with colunas_crm[index]:
        st.markdown(f"##### {fase}")
        leads_fase = [l for l in st.session_state.leads if l.get("fase") == fase]
        valor_fase = sum(l.get('receita_gestao', 0) for l in leads_fase)
        st.markdown(f"<span style='color:gray; font-size:12px;'>{len(leads_fase)} cards | R$ {valor_fase:,.2f}</span>", unsafe_allow_html=True)
        st.write("---")
        for lead in leads_fase:
            desenhar_cartao(lead, FASES_CRM)
            st.write("")