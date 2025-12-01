import os
import streamlit as st
import openai

# -----------------------------------------------
# CONFIGURAÇÕES DA PÁGINA
# -----------------------------------------------
st.set_page_config(
    page_title="Feature ROI Intelligence Agent",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Feature ROI Intelligence Agent")
st.markdown("""
Digite uma feature e o sistema irá gerar automaticamente:
- Justificativa de medição  
- Leading indicators (com definição, fórmula, como medir e ferramentas)  
- Lagging indicators (incluindo ROI direto)  
- Tabela ferramentas → métricas  
- Tempo recomendado por métrica  
- Plano de ação  
""")

# -----------------------------------------------
# SIDEBAR
# -----------------------------------------------
st.sidebar.header("⚙️ Configurações")

api_key_input = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    value=os.getenv("OPENAI_API_KEY", "")
)

model_input = st.sidebar.text_input(
    "Model",
    value="gpt-4o-mini",
    help="Ex.: gpt-4o-mini, gpt-4o, gpt-4.1"
)

language = st.sidebar.radio(
    "Idioma da resposta",
    ("Português", "English"),
    index=0
)

traffic_hint = st.sidebar.selectbox(
    "Nível de tráfego da feature",
    ["Não sei / depende", "Baixo tráfego", "Médio tráfego", "Alto tráfego"]
)

# Aplica API key
if api_key_input:
    openai.api_key = api_key_input


# -----------------------------------------------
# PROMPTS DO SISTEMA (PT e EN)
# -----------------------------------------------
SYSTEM_PROMPT_PT = """
Você é um Feature ROI Intelligence Agent especialista em UX, Product Analytics, 
métricas de negócio e medição de ROI.

Quando o usuário fornecer uma feature de produto, gere:

1. Justificativa da medição  
2. Leading Indicators (definição, fórmula, como medir, ferramentas)  
3. Lagging Indicators (definição, fórmula, como medir, ferramentas)  
4. Mapeamento de ferramentas → métricas  
5. Tempo recomendado de medição por métrica (e justificativa)  
6. Plano de ação em passos objetivos  

Sempre responda de maneira estruturada e clara para times de produto.
"""

SYSTEM_PROMPT_EN = """
You are a Feature ROI Intelligence Agent specialized in UX, Product Analytics,
business metrics, and ROI measurement.

When the user provides a product feature, generate:

1. Justification for measurement  
2. Leading Indicators (definition, formula, how to measure, tools)  
3. Lagging Indicators (definition, formula, how to measure, tools)  
4. Tool → metric mapping  
5. Recommended measurement time per metric (with justification)  
6. A practical action plan  

Respond in a clear, structured, and actionable format.
"""


# -----------------------------------------------
# INPUT DA FEATURE
# -----------------------------------------------
st.subheader("🧩 Descreva a feature que você quer lançar")

feature_text = st.text_area(
    "Qual é a feature?",
    placeholder="Ex.: Novo onboarding personalizado, checkout simplificado..."
)

generate_button = st.button("🚀 Gerar plano de ROI")


# -----------------------------------------------
# FUNÇÃO PARA CHAMAR O GPT (SDK ANTIGO)
# -----------------------------------------------
def call_gpt(system_prompt, user_prompt, model="gpt-4o-mini"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
    )
    return response["choices"][0]["message"]["content"]


# -----------------------------------------------
# LÓGICA DO BOTÃO
# -----------------------------------------------
if generate_button:

    if not api_key_input:
        st.error("Por favor, informe sua API Key.")
        st.stop()

    if not feature_text.strip():
        st.warning("Descreva a feature antes de gerar o plano.")
        st.stop()

    system_prompt = SYSTEM_PROMPT_PT if language == "Português" else SYSTEM_PROMPT_EN

    user_prompt = f"""
    Feature: {feature_text}

    Nível de tráfego informado: {traffic_hint}

    Gere o plano de medição completo.
    """

    with st.spinner("Gerando plano de medição com IA..."):
        try:
            output = call_gpt(system_prompt, user_prompt, model=model_input)
            st.subheader("📊 Plano de Medição de ROI Gerado")
            st.markdown(output)

        except Exception as e:
            st.error(f"Erro ao chamar o modelo: {e}")
            st.stop()
