# Dify Wrapper🤖

> Production-ready platform for agentic workflow development — now available as a Python library.

## What is Dify?

**Dify** is an open-source LLM app development platform. Its intuitive visual interface combines AI workflow, RAG pipeline, agent capabilities, model management, and observability — letting you quickly go from prototype to production.

This wrapper provides a Pythonic interface for programmatically creating, managing, and deploying Dify applications.

##⭐ Key Features

- **Workflow** — Visual canvas for building and testing AI workflows
- **Comprehensive Model Support** — GPT, Mistral, Llama3, 100+ providers
- **Prompt IDE** — Intuitive interface for crafting and comparing prompts
- **RAG Pipeline** — Document ingestion to retrieval
- **Agent Capabilities** — ReAct / Function Calling with 50+ built-in tools
- **LLMOps** — Monitor logs and improve prompts/datasets over time
- **Backend-as-a-Service** — REST APIs for any framework
- **Enterprise-ready** — Security and scalability features

## 📦 Installation

```bash
pip install dify-wrap
```

Or from source:

```bash
git clone https://github.com/q15004040209-creator/dify-wrap.git
cd dify-wrap
pip install -e .
```

## 🚀 Quick Start

```python
from dify import DifyClient, App, Workflow

# Connect to Dify (self-hosted or cloud)
client = DifyClient(
    base_url="http://localhost/install",  # or "https://cloud.dify.ai"
    api_key="your-dify-api-key"
)

# List apps
apps = client.apps.list()
for app in apps:
    print(f"- {app.name} ({app.id}) [{app.type}]")

# Chat with an app
app = client.apps.load("my-chat-app")
response = app.chat("What is the capital of France?")
print(response.message)
print(f"Tokens: {response.usage}")

# Run a workflow
workflow = client.workflows.load("data-processing-flow")
result = workflow.run(
    input={"documents": ["./data/*.pdf"]},
    config={"precision": "high"}
)
print(result.output)
```

## 🔧 Configuration

```python
from dify import DifyClient

client = DifyClient(
    base_url="http://localhost/install",
    api_key="app-xxxxxxxxxxxxxxxx",
    timeout=120,
    verify_ssl=True
)
```

## 📚 API Reference

### Apps

```python
# List all apps
apps = client.apps.list(tags=["production"])

# Chat with a chat app
app = client.apps.load("support-bot")
response = app.chat(
    "I need help with my order",
    conversation_id="conv_xxx",  # Continue conversation
    user="user_123" # User identifier
)
print(response.message)
print(f"Conversation: {response.conversation_id}")

# Chat with streaming
for chunk in app.chat_stream("Tell me a story"):
    print(chunk.message, end="", flush=True)
```

### Workflows

```python
# Load and run a workflow
workflow = client.workflows.load("email-processing")

result = workflow.run(
    input={
        "email_text": "Please process this order for customer #12345",
        "priority": "high"
    },
    config={
        "llm_model": "gpt-4o",
        "temperature": 0.3
    }
)

print(f"Status: {result.status}")
print(f"Output: {result.output}")
print(f"Duration: {result.duration_ms}ms")
```

### Datasets (RAG)

```python
# Create a dataset
dataset = client.datasets.create(
    name="Product Documentation",
    description="All product docs and manuals",
    index_engine="pgvector"
)

# Upload documents
dataset.upload(
    files=["./docs/*.pdf", "./docs/*.md"],
    batch_size=100,
    process_settings={"chunk_size": 500}
)

# Query the dataset
results = dataset.query(
    "How do I set up the product?",
    top_k=5
)
for r in results:
    print(f"[{r.score:.2f}] {r.content[:100]}...")
```

### Agents

```python
# Create an agent with tools
agent = client.agents.create(
    name="Research Agent",
    model="gpt-4o",
    prompt="You are a helpful research assistant.",
    tools=["web_search", "wikipedia", "ddg-search"]
)

# Run agent
response = agent.run("What are the latest developments in AI?")
print(response.message)
```

### LLMOps

```python
# List logs
logs = client.llmops.list_logs(
    app_id="app_xxx",
    limit=100,
    status="error"
)
for log in logs:
    print(f"{log.timestamp}: {log.input[:50]}... -> {log.status}")

# Improve prompt based on logs
suggestions = client.llmops.suggest_improvements(app_id="app_xxx")
for s in suggestions:
   print(f"💡 {s.suggestion}")
```

## 🌐 Deployment

### Docker (Recommended)

```bash
git clone https://github.com/langgenius/dify.git
cd dify/docker
cp .env.example .env
docker compose up -d
# Open http://localhost/install
```

### Self-hosting from Source

See [Dify Documentation](https://docs.dify.ai/getting-started/install-self-hosted/local-source-code).

## 📄 License

- **This wrapper**: MIT License
- **Dify**: Dify Open Source License (based on Apache 2.0) — [langgenius/dify](https://github.com/langgenius/dify)

## 🔗 Links

- 🌐 [Dify Official](https://dify.ai)
- 📖 [Documentation](https://docs.dify.ai)
- 💬 [Discord](https://discord.gg/FngNHpbcY7)
- 🐛 [Report Issues](https://github.com/langgenius/dify/issues)