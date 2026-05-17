from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState
import json

LOGS_ANALYSIS_PROMPT = """
Você é um especialista em análise de logs de aplicações em produção.

Você receberá logs brutos de uma aplicação rodando no Railway e deve
identificar padrões, erros e comportamentos anômalos.

Contexto da análise:
- Nível de log filtrado: {log_level}
- Pergunta original do usuário: {user_input}

Logs recebidos:
{logs_data}

Responda APENAS com um JSON:
{{
  "status": "NORMAL" | "ATENCAO" | "CRITICO",
  "errors_found": true | false,
  "error_types": ["lista de tipos de erro ou array vazio"],
  "error_frequency": "high" | "medium" | "low" | "none",
  "most_recent_error": "timestamp do erro mais recente ou null",
  "patterns": ["padrões identificados, ex: erro recorrente a cada X min"],
  "conclusion": "análise técnica em 2-3 frases focada na pergunta do usuário",
  "anomalies": ["lista de anomalias ou array vazio"]
}}

Regras importantes:
- Foque a análise na pergunta original do usuário
- Não invente dados que não estão nos logs
- Se os logs estiverem vazios, retorne status NORMAL e errors_found false
- Priorize erros que aparecem com alta frequência
- Se houver stack trace, identifique a origem do erro
- Considere CRITICO: crashes, exceptions não tratadas, erros 5xx em massa
- Considere ATENCAO: warnings recorrentes, erros 4xx em massa, timeouts
- Considere NORMAL: logs de info, poucos erros isolados

Não explique. Não cumprimente. Apenas o JSON.
"""


def logs_analysis_node(state: AgentState):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    logs_data = state.get("logs_data", [])

    if not logs_data:
        return {
            "logs_analysis": {
                "status": "NORMAL",
                "errors_found": False,
                "error_types": [],
                "error_frequency": "none",
                "most_recent_error": None,
                "patterns": [],
                "conclusion": "Nenhum log encontrado para análise.",
                "anomalies": [],
            }
        }

    prompt = LOGS_ANALYSIS_PROMPT.format(
        log_level=state.get("log_level") or "todos",
        user_input=state.get("user_input", ""),
        logs_data=json.dumps(logs_data, ensure_ascii=False),
    )

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content="Analise os logs acima."),
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

    return {"logs_analysis": analysis}
