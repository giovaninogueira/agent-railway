def out_of_scope_route(state):
    reason = state.get("reason", "")
    message = f"Desculpe, essa pergunta está fora do escopo do assistente Railway. {reason}".strip()
    
    return {
        **state,
        "answer": message,
        "messages": state.get("messages", []) + [message],
    }
