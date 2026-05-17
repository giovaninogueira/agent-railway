from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState
import json

MEMORY_ANALYSIS_PROMPT = """
Você é um especialista em análise de performance de aplicações em produção.

Você receberá dados de uso de memória de uma aplicação rodando no Railway
e deve identificar tendências, picos e comportamentos anômalos.

Contexto da análise:
- Pergunta original do usuário: {user_input}

Dados de memória recebidos (séries temporais em GB):
{memory_data}

Responda APENAS com um JSON:
{{
  "status": "NORMAL" | "ATENCAO" | "CRITICO",
  "current_usage_gb": <último valor ou null>,
  "peak_usage_gb": <valor máximo no período ou null>,
  "average_usage_gb": <média do período ou null>,
  "trend": "stable" | "increasing" | "decreasing" | "spike",
  "possible_leak": true | false,
  "conclusion": "análise técnica em 2-3 frases focada na pergunta do usuário",
  "anomalies": ["lista de anomalias ou array vazio"]
}}

Regras importantes:
- Foque a análise na pergunta original do usuário
- Não invente dados que não estão na série temporal
- Se os dados estiverem vazios, retorne status NORMAL com valores null
- Considere CRITICO: uso acima de 90% do limite ou crescimento constante sem queda (possível leak)
- Considere ATENCAO: picos isolados acima de 80%, tendência de crescimento moderada
- Considere NORMAL: uso estável, picos ocasionais com recuperação
- possible_leak: true se houver crescimento contínuo sem queda ao longo do período

Não explique. Não cumprimente. Apenas o JSON.
"""


def memory_analysis_node(state: AgentState):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    memory_data = state.get("memory_data", [])

    if not memory_data:
        return {
            "memory_analysis": {
                "status": "NORMAL",
                "current_usage_gb": None,
                "peak_usage_gb": None,
                "average_usage_gb": None,
                "trend": "stable",
                "possible_leak": False,
                "conclusion": "Nenhum dado de memória encontrado para análise.",
                "anomalies": [],
            }
        }

    prompt = MEMORY_ANALYSIS_PROMPT.format(
        user_input=state.get("user_input", ""),
        memory_data=json.dumps(memory_data, ensure_ascii=False),
    )

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content="Analise os dados de memória acima."),
    ]

    response = llm.invoke(messages)
    content = (
        response.content
        .strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )
    analysis = json.loads(content)

    return {"memory_analysis": analysis}
