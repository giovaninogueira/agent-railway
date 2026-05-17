from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState
import json

STATUS_ANALYSIS_PROMPT = """
Você é um especialista em análise de disponibilidade de aplicações em produção.

Você receberá dados de status de uma aplicação rodando no Railway
e deve determinar se o serviço está saudável.

Contexto da análise:
- Pergunta original do usuário: {user_input}

Dados de status:
{status_data}

Responda APENAS com um JSON:
{{
  "status": "NORMAL" | "ATENCAO" | "CRITICO",
  "is_alive": true | false,
  "recent_errors": <número de erros recentes>,
  "conclusion": "análise técnica em 2-3 frases focada na pergunta do usuário",
  "anomalies": ["lista de anomalias ou array vazio"]
}}

Regras importantes:
- Foque a análise na pergunta original do usuário
- alive=false significa serviço offline ou sem dados de CPU nos últimos 5 minutos
- Considere CRITICO: serviço offline ou muitos erros recentes (>50)
- Considere ATENCAO: serviço online mas com erros moderados (10-50)
- Considere NORMAL: serviço online e poucos ou nenhum erro (<10)

Não explique. Não cumprimente. Apenas o JSON.
"""


def status_analysis_node(state: AgentState):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    status_data = state.get("status_data", {})

    if not status_data:
        return {
            "status_analysis": {
                "status": "NORMAL",
                "is_alive": None,
                "recent_errors": 0,
                "conclusion": "Nenhum dado de status encontrado para análise.",
                "anomalies": [],
            }
        }

    prompt = STATUS_ANALYSIS_PROMPT.format(
        user_input=state.get("user_input", ""),
        status_data=json.dumps(status_data, ensure_ascii=False),
    )

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content="Analise o status acima."),
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

    return {"status_analysis": json.loads(content)}
