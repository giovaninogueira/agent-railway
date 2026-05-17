from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState
import json

FINAL_ANALYSIS_PROMPT = """
Você é um assistente de monitoramento Railway especializado em sintetizar análises técnicas
em respostas claras e objetivas para o usuário.

Você receberá análises individuais de diferentes métricas e deve consolidar tudo
em uma resposta direta à pergunta original do usuário.

Pergunta original do usuário: {user_input}

Análises disponíveis:
{analyses}

Responda APENAS com um JSON:
{{
  "overall_status": "NORMAL" | "ATENCAO" | "CRITICO",
  "answer": "resposta direta e clara para o usuário em 3-5 frases, sem jargão técnico excessivo",
  "highlights": ["pontos mais importantes encontrados, máximo 3 itens"],
  "action_needed": true | false
}}

Regras:
- Foque 100% na pergunta original do usuário — ignore métricas irrelevantes para ela
- overall_status deve refletir o pior status entre as análises disponíveis
- answer deve ser em português, direto ao ponto e útil para quem fez a pergunta
- Se tudo estiver normal, diga isso claramente
- Se houver problema, explique o que está errado e qual métrica indica isso
- action_needed: true se houver algo que exige atenção imediata

Não explique. Não cumprimente. Apenas o JSON.
"""


def analysis_final_node(state: AgentState):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    analyses = {}
    for key in ["cpu_analysis", "memory_analysis", "logs_analysis", "requests_analysis", "status_analysis"]:
        value = state.get(key)
        if value:
            analyses[key] = value

    if not analyses:
        return {
            "answer": "Não foi possível coletar dados suficientes para análise.",
            "messages": state.get("messages", []) + ["Não foi possível coletar dados suficientes para análise."],
        }

    prompt = FINAL_ANALYSIS_PROMPT.format(
        user_input=state.get("user_input", ""),
        analyses=json.dumps(analyses, ensure_ascii=False, indent=2),
    )

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content="Consolide as análises e responda ao usuário."),
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
    result = json.loads(content)
    answer = result.get("answer", "")

    return {
        "answer": answer,
        "messages": state.get("messages", []) + [answer],
    }
