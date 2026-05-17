from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import json

SYSTEM_PROMPT = """
Você é um classificador de intenções para um assistente de monitoramento Railway.

Sua função é:
1. Classificar se a pergunta é relacionada ao Railway
2. Extrair o nome do projeto caso tenha sido mencionado
3. Identificar quais métricas são relevantes para a pergunta

Responda APENAS com um JSON:
{
  "intention": "RAILWAY" | "OUT_OF_SCOPE",
  "project": "nome do projeto ou null",
  "metrics": ["cpu", "memory", "logs", "status", "requests"],
  "reason": "breve explicação"
}

Regras para o campo metrics:
- Inclua APENAS as métricas relevantes para a pergunta
- Se não for possível determinar, retorne todas: ["cpu", "memory", "logs", "status", "requests"]
- Se a pergunta for sobre "está no ar", inclua apenas: ["status", "logs"]
- Se a pergunta for sobre lentidão, inclua: ["cpu", "memory", "requests"]

Exemplos:
"minha api está no ar?" → metrics: ["status", "logs"]
"está lenta" → metrics: ["cpu", "memory", "requests"]
"tem erros?" → metrics: ["logs"]
"como está o consumo?" → metrics: ["cpu", "memory"]
"o que está acontecendo?" → metrics: ["cpu", "memory", "logs", "status", "requests"]

Exemplos OUT_OF_SCOPE: perguntas gerais, clima, matemática,
assuntos não relacionados à aplicação.

Não explique. Não cumprimente. Apenas o JSON.
"""


def intention_node(state):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    topic = state.get('user_input', '')
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Classifique a seguinte pergunta: '{topic}'")
    ]
    
    response = llm.invoke(messages)
    content = response.content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(content)
    
    if data.get("intention", "") == "OUT_OF_SCOPE":
        return {
            **state,
            "is_out_of_scope": True,
            "reason": data.get("reason", ""),
            "project": data.get("project", None),
            "intention": data.get("intention", ""),
            "metrics": [],
            "messages": [state.get("user_input")] + state.get("messages", []),
        }
    
    return {
        **state,
        "is_out_of_scope": False,
        "reason": data.get("reason", ""),
        "project": data.get("project", None),
        "intention": data.get("intention", ""),
        "metrics": data.get("metrics", []),
        "messages": [state.get("user_input")] + state.get("messages", []),
    }