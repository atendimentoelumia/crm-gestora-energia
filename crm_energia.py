import streamlit as st
import requests
import urllib.parse

# Configuração da página para ficar amigável em celulares
st.set_page_config(page_title="Simulador de Economia de Energia", layout="centered")

# Controle das telas (páginas) do app
if 'page' not in st.session_state:
    st.session_state.page = 1

def next_page():
    st.session_state.page += 1

def reset():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.page = 1

# ==========================================
# TELA 1: DADOS DE CONTATO
# ==========================================
if st.session_state.page == 1:
    st.title("⚡ Simulador de Economia de Energia")
    st.write("Preencha seus dados abaixo para descobrirmos o quanto você pode economizar.")
    
    with st.form("form_contato"):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        telefone = st.text_input("Telefone de contato (WhatsApp)")
        
        submit = st.form_submit_button("Próximo passo")
        
        if submit:
            if nome and email and telefone:
                # Salva os dados na sessão
                st.session_state.nome = nome
                st.session_state.email = email
                st.session_state.telefone = telefone
                next_page()
                st.rerun()
            else:
                st.error("Por favor, preencha todos os campos para continuar.")

# ==========================================
# TELA 2: DADOS DA FATURA E CEP
# ==========================================
elif st.session_state.page == 2:
    st.title("📍 Dados da Instalação")
    st.write("Agora, informe o local e o valor médio da sua conta de luz.")
    
    # Campo de CEP
    cep = st.text_input("CEP (Apenas números)", max_chars=8)
    endereco_completo = ""
    
    # API do ViaCEP para busca automática
    if len(cep) == 8:
        try:
            response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
            data = response.json()
            if "erro" not in data:
                endereco_completo = f"{data['logradouro']}, {data['bairro']} - {data['localidade']}/{data['uf']}"
                st.success(f"Endereço encontrado: **{endereco_completo}**")
            else:
                st.error("CEP não encontrado. Verifique os números.")
        except:
            st.error("Erro ao buscar o CEP na base de dados.")
            
    # Campo de Valor da Fatura
    valor_fatura = st.number_input("Valor médio da sua fatura de energia (R$)", min_value=0.0, format="%.2f")
    
    # Botão para calcular
    if st.button("Calcular Minha Economia"):
        if endereco_completo and valor_fatura > 0:
            st.session_state.valor_fatura = valor_fatura
            next_page()
            st.rerun()
        else:
            st.warning("Certifique-se de que o CEP é válido e de preencher o valor da fatura.")

# ==========================================
# TELA 3: RESULTADOS E WHATSAPP
# ==========================================
elif st.session_state.page == 3:
    st.title("💰 Sua Economia Estimada")
    
    # Cálculos
    valor_fatura = st.session_state.valor_fatura
    desconto = 0.12 # 12%
    
    economia_mensal = valor_fatura * desconto
    economia_anual = economia_mensal * 12
    economia_contrato = economia_anual * 5
    
    # Função auxiliar para formatar moeda no padrão brasileiro
    def formata_moeda(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # Exibição dos dados
    st.info(f"Analisamos sua fatura média de {formata_moeda(valor_fatura)} e aplicamos 12% de desconto.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Economia Mensal", formata_moeda(economia_mensal))
    col2.metric("Economia Anual", formata_moeda(economia_anual))
    col3.metric("Contrato (5 Anos)", formata_moeda(economia_contrato))
    
    st.markdown("---")
    
    # Frase de impacto
    st.markdown("<h3 style='text-align: center; color: #2E86C1;'>Esta economia ajudaria no crescimento da sua empresa?</h3>", unsafe_allow_html=True)
    
    # Geração do link do WhatsApp
    # COLOQUE O NÚMERO DA SUA EMPRESA AQUI (com código do país 55 e DDD)
    numero_empresa = "5511999999999" 
    
    mensagem_padrao = f"Olá! Meu nome é {st.session_state.nome}. Acabei de usar o simulador e vi que posso economizar até {formata_moeda(economia_mensal)} por mês. Gostaria de saber mais!"
    mensagem_codificada = urllib.parse.quote(mensagem_padrao)
    link_whatsapp = f"https://wa.me/{numero_empresa}?text={mensagem_codificada}"
    
    # Botão visual para o WhatsApp
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 20px;">
            <a href="{link_whatsapp}" target="_blank" style="background-color: #25D366; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 18px; border-radius: 8px; font-weight: bold;">
                Falar com um Especialista no WhatsApp
            </a>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    if st.button("Fazer nova simulação"):
        reset()
        st.rerun()
