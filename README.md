# Agent Railway

Agente de monitoramento inteligente para aplicações hospedadas no [Railway](https://railway.com), construído com LangGraph e Google Gemini.

O agente recebe perguntas em linguagem natural, coleta métricas reais da Railway API e retorna uma análise consolidada para o usuário.

## Como funciona

```
Usuário
  │
  ▼
intention_node          → classifica a intenção (Railway ou fora do escopo)
  │
  ▼
intent_classification_node  → verifica se o contexto é suficiente (interrupt se vago)
  │
  ▼
verify_project_node     → busca projetos e serviços na Railway API
  │
  ▼
verify_project_route    → confirma o serviço (interrupt para seleção se necessário)
  │
  ▼ Send (paralelo, apenas métricas relevantes)
  ├── cpu_metrics → cpu_analysis
  ├── memory_metrics → memory_analysis
  ├── logs_metrics → logs_analysis
  ├── requests_metrics → requests_analysis
  └── status_metrics → status_analysis
                │ fan-in
                ▼
        final_analysis  → resposta consolidada para o usuário
```

## Tecnologias

| Tecnologia | Uso |
|---|---|
| [LangGraph](https://langchain-ai.github.io/langgraph/) | Orquestração do grafo de agentes |
| [Google Gemini 2.5 Flash](https://deepmind.google/technologies/gemini/) | LLM para classificação e análise |
| [Railway GraphQL API](https://docs.railway.com/reference/public-api) | Coleta de métricas, logs e status |
| Python 3.14 | Runtime |

## Funcionalidades

- **Classificação de intenção** — detecta automaticamente se a pergunta é sobre Railway
- **Validação de contexto** — pede esclarecimento quando a pergunta é vaga
- **Resolução de serviço** — encontra o serviço certo mesmo sem o nome exato
- **Coleta paralela de métricas** — CPU, memória, logs, tráfego de rede e status
- **Análise por LLM** — cada métrica é analisada individualmente com contexto da pergunta
- **Resposta consolidada** — análise final que responde diretamente ao usuário
- **Filtro por nível de log** — suporte a `error`, `warning` e `info`

## Exemplos de perguntas

```
"minha api está no ar?"
"tem erros acontecendo no projeto taaqi?"
"está consumindo muita CPU?"
"quero ver os logs de erro"
"o que está acontecendo com o serviço?"
```

## Instalação

```bash
# Clone o repositório
git clone https://github.com/giovaninogueira/agent-railway.git
cd agent-railway

# Instale as dependências
pip install -e .

# Configure as variáveis de ambiente
cp .env.example .env
```

### Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
RAILWAY_API_TOKEN=seu_token_aqui
GOOGLE_API_KEY=sua_chave_aqui
LANGSMITH_API_KEY=sua_chave_aqui      # opcional
LANGSMITH_TRACING=true                # opcional
LANGSMITH_PROJECT=agent-railway       # opcional
```

- **RAILWAY_API_TOKEN** — gere em [railway.com/account/tokens](https://railway.com/account/tokens)
- **GOOGLE_API_KEY** — gere em [Google AI Studio](https://aistudio.google.com/app/apikey)

## Executando

```bash
langgraph dev
```

O servidor sobe em `http://localhost:2024` com o LangGraph Studio para visualizar e interagir com o grafo.

## Estrutura do projeto

```
src/
├── graph/
│   ├── graph.py                  # Definição do grafo LangGraph
│   └── nodes/
│       ├── intention_node.py     # Classificação de intenção
│       ├── intent_classification_node.py  # Validação de contexto
│       ├── verify_project_node.py         # Resolução de projeto/serviço
│       ├── analysis_final_node.py         # Análise consolidada final
│       ├── metrics/
│       │   ├── cpu_node.py / cpu_analysis_node.py
│       │   ├── memory_node.py / memory_analysis_node.py
│       │   ├── logs_node.py / logs_analysis_node.py
│       │   ├── requests_node.py / requests_analysis_node.py
│       │   └── status_node.py / status_analysis_node.py
│       └── routes/
│           ├── out_of_scope_route.py
│           ├── verify_project_route.py
│           └── metrics_route.py
├── services/
│   └── railway_service.py        # Cliente da Railway GraphQL API
└── state.py                      # Definição do AgentState
```

## Conceitos de IA aplicados

- **Grafos de agentes** com LangGraph (nós, arestas condicionais, ciclos)
- **Human-in-the-loop** via `interrupt` para coleta de informações faltantes
- **Paralelismo dinâmico** com `Send` baseado na intenção classificada
- **Fan-in** para convergência de branches paralelas em análise única
- **Prompt engineering** para classificação, validação e análise de métricas
- **Pipeline de LLM em múltiplas camadas** (classificação → coleta → análise → síntese)
