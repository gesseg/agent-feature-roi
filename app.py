import os
import streamlit as st
from openai import OpenAI

# ----------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ----------------------------------------------------
st.set_page_config(
    page_title="Feature ROI Intelligence Agent",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Feature ROI Intelligence Agent")
st.markdown(
    """
    Digite a **feature** que você pretende criar ou lançar e o agente irá gerar automaticamente:
    
    - Uma **justificativa** de por que medir essa feature é importante  
    - **Leading indicators** (com definição, fórmula, como medir e ferramentas)  
    - **Lagging indicators / ROI direto** (com definição, fórmula, como medir e ferramentas)  
    - Um **mapeamento de ferramentas → métricas**  
    - **Tempo recomendado de medição por métrica**, com justificativa  
    - Um **plano de ação** para começar a medir hoje  
    """
)

# ----------------------------------------------------
# SIDEBAR – CONFIGURAÇÕES
# ----------------------------------------------------
st.sidebar.header("⚙️ Configurações")

# API Key: pega do ambiente se existir, mas pode ser sobrescrita no campo
default_api_key = os.getenv("OPENAI_API_KEY", "")
api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    value=default_api_key,
    help="Sua chave da API do OpenAI (env: OPENAI_API_KEY)."
)

model_name = st.sidebar.text_input(
    "Model name",
    value="gpt-4o-mini",
    help="Nome do modelo a ser usado (ex.: gpt-4o, gpt-4o-mini, gpt-4.1 etc.)."
)

language = st.sidebar.radio(
    "Language / Idioma da resposta",
    ("Português", "English"),
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("Desenvolvido para apoiar medição de ROI em UX/Product. 🤖")

# ----------------------------------------------------
# INPUT DA FEATURE
# ----------------------------------------------------
st.subheader("🧩 Descreva a feature que você quer lançar")

feature_text = st.text_area(
    "Qual é a feature (ou melhoria de produto) que você pretende criar ou lançar?",
    placeholder="Exemplos:\n- Novo fluxo simplificado de checkout\n- Onboarding personalizado com recomendações\n- Nova tela de relatório para times internos\n- Sistema de recomendação de produtos baseado em histórico\n...",
    height=150
)

traffic_hint = st.selectbox(
    "Qual é o nível de tráfego esperado para essa feature?",
    (
        "Não sei / depende",
        "Baixo tráfego",
        "Médio tráfego",
        "Alto tráfego"
    ),
    index=0
)

generate_button = st.button("🚀 Gerar plano de medição de ROI")

# ----------------------------------------------------
# FUNÇÃO DE CHAMADA AO MODELO
# ----------------------------------------------------
SYSTEM_PROMPT_PT = """
Você é um Feature ROI Intelligence Agent especialista em UX, Product Analytics, métricas de negócio e medição de ROI.

Sua tarefa: quando o usuário informar uma feature de produto que será criada ou lançada, você deve gerar um plano COMPLETO de medição, sempre em português e em formato estruturado.

O output DEVE conter, nesta ordem:

1. **Justificativa da medição da feature**
   - Explique em 1–2 parágrafos por que medir essa feature é importante para negócio, UX e ROI.
   - Aponte riscos de não medir.

2. **Leading Indicators (indicadores antecedentes)**
   Para cada métrica que você recomendar:
   - Nome da métrica
   - Definição
   - Fórmula / cálculo exato (em notação simples, tipo: conversão = compras / sessões * 100)
   - Como medir (quais eventos rastrear ou dados coletar)
   - Quais ferramentas podem medir ESSA métrica (ex.: GA4, Amplitude, Mixpanel, Hotjar, FullStory, SQL, CRM etc.)

   Utilize, quando fizer sentido, métricas como:
   - Task success rate
   - Task time
   - Error rate
   - User engagement
   - Retention rate
   - User satisfaction
   - Conversion rate (pode ser leading/lagging)
   - Cart abandonment rate
   - Time to first click
   - Operational efficiency
   - Learning time
   - NPS

3. **Lagging Indicators (indicadores tardios, de resultado de negócio / ROI)**
   Para cada métrica recomendada:
   - Nome da métrica
   - Definição
   - Fórmula / cálculo exato
   - Como medir (fonte de dados)
   - Ferramentas recomendadas (SQL, DW, CRM, BI, GA4 etc.)

   Inclua sempre que fizer sentido:
   - Conversão final
   - Receita incremental
   - Redução de churn
   - Redução de custo operacional
   - Aumento de LTV
   - ROI direto = (Ganho – Custo) / Custo

4. **Mapeamento Ferramentas → Métricas**
   Uma tabela ou lista clara, por exemplo:
   - GA4: quais métricas mede, e como (eventos, funis etc.)
   - Amplitude: quais métricas mede, e como (cohorts, funnels etc.)
   - Mixpanel
   - Hotjar / FullStory
   - SQL / Data Warehouse
   - CRM
   - BI (Power BI, Looker, etc.)

5. **Tempo ideal de medição POR MÉTRICA**
   Não apenas por tráfego, mas também pela natureza da métrica:
   - Métricas comportamentais rápidas (task success, error rate, task time etc.) → janelas menores (em dias/semanas)
   - Métricas de adoção/engajamento/retensão → janelas médias
   - Métricas de negócio/ROI/LTV → janelas mais longas

   Para cada métrica ou grupo de métricas:
   - Informe um tempo recomendado de medição (ex.: 7–14 dias, 3–4 semanas, 30–60 dias)
   - Dê uma breve justificativa (ex.: “depende de ciclo de compra”, “precisa de volume para significância estatística” etc.)

   Leve em conta a dica de tráfego fornecida pelo usuário, se houver (baixo/médio/alto).

6. **Plano de Ação**
   Um checklist em passos numerados, mostrando:
   - o que instrumentar (eventos, tags)
   - como criar baseline
   - como acompanhar leading indicators
   - como acompanhar lagging indicators
   - como calcular ROI ao final
   - próximos passos (iterar na feature, desligar se não performar, etc.)

Use sempre linguagem clara, objetiva e prática, focada em times de produto e UX.
"""

SYSTEM_PROMPT_EN = """
You are a Feature ROI Intelligence Agent specialized in UX, Product Analytics, business metrics, and ROI measurement.

Your task: when the user provides a product feature they plan to create or launch, you must generate a COMPLETE measurement plan, in English, in a structured format.

The output MUST contain, in this order:

1. Justification for measuring the feature
   - Explain in 1–2 paragraphs why measuring this feature matters for business, UX, and ROI.
   - Highlight the risks of not measuring it.

2. Leading Indicators
   For each recommended metric:
   - Name of the metric
   - Definition
   - Exact formula / calculation (e.g., conversion = purchases / sessions * 100)
   - How to measure it (which events or data to track)
   - Which tools can measure THIS metric (e.g., GA4, Amplitude, Mixpanel, Hotjar, FullStory, SQL, CRM, etc.)

   Use, when appropriate:
   - Task success rate
   - Task time
   - Error rate
   - User engagement
   - Retention rate
   - User satisfaction
   - Conversion rate (can be leading/lagging)
   - Cart abandonment rate
   - Time to first click
   - Operational efficiency
   - Learning time
   - NPS

3. Lagging Indicators (business / ROI outcomes)
   For each recommended metric:
   - Name
   - Definition
   - Exact formula
   - How to measure it (data source)
   - Recommended tools (SQL, DW, CRM, BI, GA4, etc.)

   Include when appropriate:
   - Final conversion
   - Incremental revenue
   - Churn reduction
   - Operational cost reduction
   - LTV increase
   - Direct ROI = (Gain – Cost) / Cost

4. Tool → Metrics Mapping
   A clear list or table, e.g.:
   - GA4: which metrics it measures and how (events, funnels, etc.)
   - Amplitude
   - Mixpanel
   - Hotjar / FullStory
   - SQL / Data Warehouse
   - CRM
   - BI tools (Power BI, Looker, etc.)

5. Recommended measurement time PER METRIC
   Consider both traffic level and metric nature:
   - Fast behavioral metrics (task success, error rate, task time) → shorter windows
   - Adoption/engagement/retention → mid-term windows
   - Business/ROI/LTV metrics → longer windows

   For each metric or group:
   - Provide a recommended measurement window (e.g., 7–14 days, 3–4 weeks, 30–60 days)
   - Add a brief justification.

   Use the user's traffic hint (low/medium/high) if provided.

6. Action Plan
   A numbered checklist covering:
   - instrumentation (events, tags)
   - how to create a baseline
   - how to monitor leading indicators
   - how to monitor lagging indicators
   - how to compute ROI at the end
   - next steps (iterate on the feature, roll-back if underperforming, etc.)

Use clear, concise, and practical language for product and UX teams.
"""

def get_client(api_key_value: str) -> OpenAI:
    # Se api_key_value estiver vazio, o SDK vai tentar usar OPENAI_API_KEY do ambiente
    if api_key_value:
        return OpenAI(api_key=api_key_value)
    return OpenAI()


def build_messages(feature: str, traffic_level: str, lang: str):
    if lang == "Português":
        system_prompt = SYSTEM_PROMPT_PT
        user_prompt = f"""
Feature de produto a ser analisada: {feature}

Nível de tráfego informado: {traffic_level}.

Gere o plano completo de medição conforme as instruções do sistema.
"""
    else:
        system_prompt = SYSTEM_PROMPT_EN
        user_prompt = f"""
Product feature to be analyzed: {feature}

Traffic level provided: {traffic_level}.

Generate the full measurement plan according to the system instructions.
"""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

# ----------------------------------------------------
# LÓGICA PRINCIPAL
# ----------------------------------------------------
if generate_button:
    if not feature_text.strip():
        st.warning("Por favor, descreva a feature antes de gerar o plano.")
    else:
        try:
            client = get_client(api_key)

            messages = build_messages(feature_text.strip(), traffic_hint, language)

            with st.spinner("Gerando plano de medição de ROI com IA..."):
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.3,
                )

            content = response.choices[0].message.content
            st.markdown("---")
            st.subheader("📊 Plano de Medição de ROI Gerado")
            st.markdown(content)

        except Exception as e:
            st.error(f"Ocorreu um erro ao chamar a API: {e}")
            st.stop()
