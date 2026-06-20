import streamlit as st
import requests
import urllib.parse
import urllib3

# Desativa o aviso de segurança no terminal devido ao verify=False nas APIs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuração da página
st.set_page_config(page_title="Simulador de Economia de Energia", layout="centered")

# ==========================================
# CONFIGURAÇÃO DOS LOGOTIPOS (TOPO DO APP)
# ==========================================
# SUBSTITUA OS LINKS ABAIXO PELOS LINKS REAIS DAS LOGOS (De preferência imagens com fundo transparente)
LOGO_ELUMIA = "https://via.placeholder.com/150x50?text=E-lumia" 
LOGO_PARCEIRO = "https://via.placeholder.com/150x50?text=Logo+Parceiro"

st.markdown(
    f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 30px; padding-bottom: 15px;">
        <img src="{LOGO_ELUMIA}" style="max-height: 55px; width: auto;">
        <img src="{LOGO_PARCEIRO}" style="max-height: 55px; width: auto;">
    </div>
    """,
    unsafe_allow_html=True
)

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
            
            # Tentativa 1: BrasilAPI
            response = requests.get(f"https://brasilapi.com.br/api/cep/v1/{cep_limpo}", headers=headers, timeout=5, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                endereco_completo = f"{data.get('street', '')}, {data.get('neighborhood', '')} - {data.get('city', '')}/{data.get('state', '')}"
                st.success(f"Endereço encontrado: **{endereco_completo}**")
            else:
                # Tentativa 2: ViaCEP
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
            st.error("Bloqueio de rede detectado. O firewall ou antivírus está impedindo o app de buscar o CEP.")
            
    elif len(cep_input) > 0 and len(cep_limpo) != 8:
        st.warning("Continue digitando... O CEP precisa ter 8 números.")
            
    valor_fatura = st.number_input("Valor médio da sua fatura de energia (R$)", min_value=0.0, format="%.2f")
    
    if st.button("Calcular Minha Economia"):
        if endereco_completo and valor_fatura > 0:
            st.session_state.valor_fatura = valor_fatura
            next_page()
            st.rerun()
        else:
            st.warning("Certifique-se de preencher um CEP válido e o valor da fatura.")

# ==========================================
# TELA 3: RESULTADOS E 3 BOTÕES DE WHATSAPP
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
    
    st.markdown("<h3 style='text-align: center; color: #2E86C1;'>Esta economia ajudaria no crescimento da sua empresa?</h3>", unsafe_allow_html=True)
    
    # ==========================================
    # CONFIGURAÇÃO DOS 3 ESPECIALISTAS
    # ==========================================
    # Troque os nomes e os números abaixo (Código do país 55 + DDD + Número)
    
    nome_esp1 = "Thaiz Magnino"
    num_esp1 = "5511937567788"
    
    nome_esp2 = "Peterson Rodrigues"
    num_esp2 = "5511980781012"
    
    nome_esp3 = "Roberto Moreira Filho"
    num_esp3 = "5511957714063"
    
    # Mensagem padronizada
    mensagem_padrao = f"Olá! Meu nome é {st.session_state.nome}. Acabei de usar o simulador e vi que posso economizar até {formata_moeda(economia_mensal)} por mês. Gostaria de saber como conseguir essa economia!"
    mensagem_codificada = urllib.parse.quote(mensagem_padrao)
    
    # Geração dos 3 links
    link_wpp1 = f"https://wa.me/{num_esp1}?text={mensagem_codificada}"
    link_wpp2 = f"https://wa.me/{num_esp2}?text={mensagem_codificada}"
    link_wpp3 = f"https://wa.me/{num_esp3}?text={mensagem_codificada}"
    
    # Criação dos botões na tela
    st.markdown(
        f"""
        <div style="display: flex; flex-direction: column; align-items: center; gap: 15px; margin-top: 25px;">
            <p style="font-size: 18px; font-weight: bold; margin-bottom: 5px;">Escolha com quem quer começar a economizar:</p>
            
            <a href="{link_wpp1}" target="_blank" style="background-color: #25D366; color: white; padding: 12px 20px; text-align: center; text-decoration: none; width: 100%; max-width: 320px; font-size: 16px; border-radius: 8px; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                📱 Falar com {nome_esp1}
            </a>
            
            <a href="{link_wpp2}" target="_blank" style="background-color: #25D366; color: white; padding: 12px 20px; text-align: center; text-decoration: none; width: 100%; max-width: 320px; font-size: 16px; border-radius: 8px; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                📱 Falar com {nome_esp2}
            </a>
            
            <a href="{link_wpp3}" target="_blank" style="background-color: #25D366; color: white; padding: 12px 20px; text-align: center; text-decoration: none; width: 100%; max-width: 320px; font-size: 16px; border-radius: 8px; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                📱 Falar com {nome_esp3}
            </a>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    if st.button("Fazer nova simulação"):
        reset()
        st.rerun()
