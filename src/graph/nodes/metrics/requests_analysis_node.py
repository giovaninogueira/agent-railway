from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState
import json

REQUESTS_ANALYSIS_PROMPT = """
Você é um especialista em análise de tráfego de rede de aplicações em produção.

Você receberá dados de tráfego de rede (TX e RX em GB) de uma aplicação rodando no Railway
e deve identificar padrões de uso, picos e comportamentos anômalos.

Contexto da análise:
- Pergunta original do usuário: {user_input}

Dados de rede recebidos (séries temporais em GB):
TX (saída): {tx_data}
RX (entrada): {rx_data}

Responda APENAS com um JSON:
{{
  "status": "NORMAL" | "ATENCAO" | "CRITICO",
  "total_tx_gb": <soma total TX no período ou null>,
  "total_rx_gb": <soma total RX no período ou null>,
  "peak_tx_gb": <pico de TX ou null>,
  "peak_rx_gb": <pico de RX ou null>,
  "trend": "stable" | "increasing" | "decreasing" | "spike",
  "conclusion": "análise técnica em 2-3 frases focada na pergunta do usuário",
  "anomalies": ["lista de anomalias ou array vazio"]
}}

Regras importantes:
- Foque a análise na pergunta original do usuário
- Se TX e RX estiverem zerados, pode indicar serviço sem tráfego ou offline
- Não invente dados que não estão na série temporal
- Se os dados estiverem vazios, retorne status NORMAL com valores null
- Considere CRITICO: picos abruptos de tráfego (possível ataque ou bug)
- Considere ATENCAO: crescimento constante de tráfego fora do padrão
- Considere NORMAL: tráfego estável ou dentro do padrão esperado

Não explique. Não cumprimente. Apenas o JSON.
"""


def requests_analysis_node(state: AgentState):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    requests_data = state.get("requests_data", {})
    tx_data = requests_data.get("tx", [])
    rx_data = requests_data.get("rx", [])

    if not tx_data and not rx_data:
        return {
            "requests_analysis": {
                "status": "NORMAL",
                "total_tx_gb": None,
                "total_rx_gb": None,
                "peak_tx_gb": None,
                "peak_rx_gb": None,
                "trend": "stable",
                "conclusion": "Nenhum dado de tráfego encontrado para análise.",
                "anomalies": [],
            }
        }

    prompt = REQUESTS_ANALYSIS_PROMPT.format(
        user_input=state.get("user_input", ""),
        tx_data=json.dumps(tx_data, ensure_ascii=False),
        rx_data=json.dumps(rx_data, ensure_ascii=False),
    )

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content="Analise os dados de tráfego acima."),
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

    return {"requests_analysis": json.loads(content)}
