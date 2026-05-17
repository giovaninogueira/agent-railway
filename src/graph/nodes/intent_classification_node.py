from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.types import interrupt
import json

SYSTEM_PROMPT = """
Você é um validador de contexto para um assistente de monitoramento Railway.

Você receberá a intenção classificada do usuário e deve verificar
se há contexto suficiente para executar a análise.

Intenção recebida:
{intention_output}

Responda APENAS com um JSON:
{
  "sufficient_context": true | false,
  "clarification_needed": "pergunta para o usuário ou null"
}

Considere insuficiente quando:
- A pergunta for vaga demais: "quero logs", "me mostra tudo", "o que tem?"
- Não der pra entender o que o usuário quer saber com as métricas
- A métrica foi identificada mas sem nenhum objetivo claro

Considere suficiente quando:
- Tiver um objetivo claro: "está no ar?", "tem erros?", "está lenta?"
- Mesmo que vaga, a intenção for clara o suficiente para agir

Exemplos insuficiente:
"quero logs" → "O que você quer verificar nos logs? Erros, warnings, ou comportamento geral?"
"me mostra tudo" → "O que especificamente você quer analisar? Status, erros, consumo de recursos?"
"quero ver memória" → "O que você quer saber sobre memória? Se está alta, se tem leak, uso geral?"

Exemplos suficiente:
"minha app está no ar?" → sufficient: true
"tem erros acontecendo?" → sufficient: true
"está consumindo muita CPU?" → sufficient: true

Não explique. Não cumprimente. Apenas o JSON.
"""


def intent_classification_node(state):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    topic = state.get('user_input', '')

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Classifique a seguinte pergunta: '{topic}'")
    ]

    response = llm.invoke(messages)
    content = response.content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(content)

    if not data.get("sufficient_context", False):
        new_input = interrupt({
            "mensagem": data.get("clarification_needed"),
        })
        original = state.get("user_input", "")
        combined = f"{original}. {new_input}"
        return {
            **state,
            "user_input": combined,
            "is_vague": True,
            "sufficient_context": False,
            "clarification_needed": data.get("clarification_needed"),
        }

    return {
        **state,
        "is_vague": False,
        "sufficient_context": True,
        "clarification_needed": None,
    }
