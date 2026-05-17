from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState
import json

CPU_ANALYSIS_PROMPT = """
Você é um especialista em análise de performance de aplicações em produção.

Você receberá dados de uso de CPU de uma aplicação rodando no Railway
e deve identificar tendências, picos e comportamentos anômalos.

Contexto da análise:
- Pergunta original do usuário: {user_input}

Dados de CPU recebidos (séries temporais, valor entre 0 e 1 = 0% a 100%):
{cpu_data}

Responda APENAS com um JSON:
{{
  "status": "NORMAL" | "ATENCAO" | "CRITICO",
  "current_usage_pct": <último valor em % ou null>,
  "peak_usage_pct": <valor máximo em % no período ou null>,
  "average_usage_pct": <média em % do período ou null>,
  "trend": "stable" | "increasing" | "decreasing" | "spike",
  "conclusion": "análise técnica em 2-3 frases focada na pergunta do usuário",
  "anomalies": ["lista de anomalias ou array vazio"]
}}

Regras importantes:
- Foque a análise na pergunta original do usuário
- Multiplique os valores por 100 para converter para porcentagem
- Não invente dados que não estão na série temporal
- Se os dados estiverem vazios, retorne status NORMAL com valores null
- Considere CRITICO: uso médio acima de 90% ou picos frequentes acima de 95%
- Considere ATENCAO: uso médio entre 70-90% ou picos isolados acima de 85%
- Considere NORMAL: uso abaixo de 70% com comportamento estável

Não explique. Não cumprimente. Apenas o JSON.
"""


def cpu_analysis_node(state: AgentState):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    cpu_data = state.get("cpu_data", [])

    if not cpu_data:
        return {
            "cpu_analysis": {
                "status": "NORMAL",
                "current_usage_pct": None,
                "peak_usage_pct": None,
                "average_usage_pct": None,
                "trend": "stable",
                "conclusion": "Nenhum dado de CPU encontrado para análise.",
                "anomalies": [],
            }
        }

    prompt = CPU_ANALYSIS_PROMPT.format(
        user_input=state.get("user_input", ""),
        cpu_data=json.dumps(cpu_data, ensure_ascii=False),
    )

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content="Analise os dados de CPU acima."),
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

    return {"cpu_analysis": json.loads(content)}
