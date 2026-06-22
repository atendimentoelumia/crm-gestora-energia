import streamlit as st
import requests
import urllib.parse
import urllib3
from datetime import datetime

# Desativa o aviso de segurança no terminal
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuração da página
st.set_page_config(page_title="Simulador de Economia de Energia", layout="centered")

# ==========================================
# NOVA FUNÇÃO: SALVAR NO FORMSPREE
# ==========================================
def enviar_para_formspree(nome, email, telefone, cep, endereco, valor_fatura, mensal, anual, contrato):
    # COLOQUE O SEU LINK DO FORMSPREE NA LINHA ABAIXO:
    LINK_FORMSPREE = "https://formspree.io/f/mnjkqwbq"
    
    try:
        # Empacota os dados de forma limpa
        dados = {
            "Data e Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Nome": nome,
            "E-mail": email,
            "WhatsApp": telefone,
            "CEP": cep,
            "Endereço": endereco,
            "Valor da Fatura (R$)": f"{valor_fatura:.2f}",
            "Economia Mensal (R$)": f"{mensal:.2f}",
            "Economia Anual (R$)": f"{anual:.2f}",
            "Economia Contrato (R$)": f"{contrato:.2f}"
        }
        
        # Envia os dados para o Formspree
        resposta = requests.post(LINK_FORMSPREE, json=dados)
        
        # O código 200 significa que o Formspree recebeu com sucesso!
        if resposta.status_code == 200:
            return True
        else:
            st.error(f"Erro ao enviar: O Formspree retornou o código {resposta.status_code}")
            return False
            
    except Exception as e:
        st.error(f"Erro de conexão com o Formspree: {e}")
        return False

# ==========================================
# CONFIGURAÇÃO DOS LOGOTIPOS (TOPO DO APP)
# ==========================================
LOGO_ELUMIA = "https://via.placeholder.com/150x50.png?text=E-lumia" 
LOGO_PARCEIRO = "https://via.placeholder.com/150x50.png?text=Logo+Parceiro"

col_logo1, espaco, col_logo2 = st.columns([1, 2, 1])
with col_logo1:
    st.image(LOGO_ELUMIA, use_container_width=True)
with col_logo2:
    st.image(LOGO_PARCEIRO, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

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
    st.write("Preencha os seus dados abaixo para descobrirmos o quanto pode economizar.")
    
    with st.form("form_contato"):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        telefone = st.text_input("Telefone de contato (WhatsApp)")
        
        submit = st.form_submit_button("Próximo passo")
        
        if submit:
            if nome and email and telefone:
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
    
    cep_input = st.text_input("CEP", max_chars=9)
    cep_limpo = cep_input.replace("-", "").replace(".", "").strip()
    endereco_completo = ""
    
    if len(cep_limpo) == 8 and cep_limpo.isdigit():
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
            response = requests.get(f"https://brasilapi.com.br/api/cep/v1/{cep_limpo}", headers=headers, timeout=5, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                endereco_completo = f"{data.get('street', '')}, {data.get('neighborhood', '')} - {data.get('city', '')}/{data.get('state', '')}"
                st.success(f"Endereço encontrado: **{endereco_completo}**")
            else:
                response_via = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", headers=headers, timeout=5, verify=False)
                if response_via.status_code == 200:
                    data = response_via.json()
                    if "erro" not in data:
                        endereco_completo = f"{data.get('logradouro', '')}, {data.get('bairro', '')} - {data.get('localidade', '')}/{data.get('uf', '')}"
                        st.success(f"Endereço encontrado: **{endereco_completo}**")
                    else:
                        st.error("CEP não encontrado na base dos Correios.")
                else:
                    st.error("Serviços de CEP indisponíveis no momento.")
        except requests.exceptions.RequestException:
            st.error("Erro de conexão ao buscar o CEP.")
            
    elif len(cep_input) > 0 and len(cep_limpo) != 8:
        st.warning("Continue digitando... O CEP precisa ter 8 números.")
            
    valor_fatura = st.number_input("Valor médio da sua fatura de energia (R$)", min_value=0.0, format="%.2f")
    
    if st.button("Calcular Minha Economia"):
        if endereco_completo and valor_fatura > 0:
            st.session_state.valor_fatura = valor_fatura
            st.session_state.endereco_completo = endereco_completo
            st.session_state.cep_limpo = cep_limpo
            
            desconto = 0.12
            economia_mensal = valor_fatura * desconto
            economia_anual = economia_mensal * 12
            economia_contrato = economia_anual * 5
            
            with st.spinner("Processando simulação..."):
                sucesso = enviar_para_formspree(
                    st.session_state.nome,
                    st.session_state.email,
                    st.session_state.telefone,
                    st.session_state.cep_limpo,
                    st.session_state.endereco_completo,
                    valor_fatura,
                    economia_mensal,
                    economia_anual,
                    economia_contrato
                )
            
            if sucesso:
                next_page()
                st.rerun()
            else:
                st.error("Falha ao se conectar com o banco de dados. Tente novamente.")
        else:
            st.warning("Certifique-se de preencher um CEP válido e o valor da fatura.")

# ==========================================
# TELA 3: RESULTADOS E WHATSAPP
# ==========================================
elif st.session_state.page == 3:
    st.title("💰 Sua Economia Estimada")
    
    valor_fatura = st.session_state.valor_fatura
    desconto = 0.12 
    
    economia_mensal = valor_fatura * desconto
    economia_anual = economia_mensal * 12
    economia_contrato = economia_anual * 5
    
    def formata_moeda(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    st.info(f"Com base na sua fatura média de {formata_moeda(valor_fatura)}, projetamos a seguinte economia para a sua empresa:")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Economia Mensal", formata_moeda(economia_mensal))
    col2.metric("Economia Anual", formata_moeda(economia_anual))
    col3.metric("Contrato (5 Anos)", formata_moeda(economia_contrato))
    
    st.markdown("---")
    
    st.markdown("<h3 style='text-align: center; color: #2E86C1; margin-bottom: 30px;'>Esta economia ajudaria no crescimento da sua empresa?</h3>", unsafe_allow_html=True)
    
    # CONFIGURAÇÃO DOS 3 ESPECIALISTAS
    nome_esp1 = "João Paulo"
    num_esp1 = "5511999999991"
    
    nome_esp2 = "Maria Silva"
    num_esp2 = "5511999999992"
    
    nome_esp3 = "Carlos Eduardo"
    num_esp3 = "5511999999993"
    
    mensagem_padrao = f"Olá! Meu nome é {st.session_state.nome}. Acabei de usar o simulador e vi que posso economizar até {formata_moeda(economia_mensal)} por mês. Gostaria de saber como conseguir essa economia!"
    mensagem_codificada = urllib.parse.quote(mensagem_padrao)
    
    link_wpp1 = f"https://wa.me/{num_esp1}?text={mensagem_codificada}"
    link_wpp2 = f"https://wa.me/{num_esp2}?text={mensagem_codificada}"
    link_wpp3 = f"https://wa.me/{num_esp3}?text={mensagem_codificada}"
    
    st.markdown("<p style='text-align: center; font-size: 18px; font-weight: bold;'>Escolha com quem quer falar agora:</p>", unsafe_allow_html=True)
    
    st.link_button(f"📱 Falar com {nome_esp1}", link_wpp1, use_container_width=True)
    st.link_button(f"📱 Falar com {nome_esp2}", link_wpp2, use_container_width=True)
    st.link_button(f"📱 Falar com {nome_esp3}", link_wpp3, use_container_width=True)
    
    st.markdown("---")
    
    if st.button("Fazer nova simulação", use_container_width=True):
        reset()
        st.rerun()
