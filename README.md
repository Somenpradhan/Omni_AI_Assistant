# Aether Enterprise Multi-Agent AI Assistant

A production-grade, modular, and containerized Multi-Agent AI Assistant architecture built with **FastAPI**, **LangGraph**, and **Streamlit**. It integrates Retrieval-Augmented Generation (RAG) with local vector store files, memory profiling, and dynamic tool orchestration.

---

## 🏗️ Architecture Layout

The project complies with the clean enterprise layout below:

```bash
enterprise-ai-assistant/
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   └── v1/
│   │       └── endpoints/
│   │            ├── chat.py
│   │            ├── upload.py
│   │            ├── memory.py
│   │            ├── health.py
│   │            └── sessions.py
│   │
│   ├── agents/
│   │   ├── router_agent.py
│   │   ├── planner_agent.py
│   │   ├── rag_agent.py
│   │   ├── llm_agent.py
│   │   ├── web_agent.py
│   │   ├── memory_agent.py
│   │   ├── tool_agent.py
│   │   ├── response_agent.py
│   │   ├── reflection_agent.py
│   │   └── executor_agent.py
│   │
│   ├── orchestrator/
│   │   ├── workflow.py
│   │   ├── state.py
│   │   ├── router.py
│   │   └── graph.py
│   │
│   ├── rag/
│   │   ├── chunker.py
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   ├── vector_store.py
│   │   ├── reranker.py
│   │   └── document_loader.py
│   │
│   ├── memory/
│   │   ├── conversation_memory.py
│   │   ├── long_term_memory.py
│   │   ├── summary_memory.py
│   │   └── session_manager.py
│   │
│   ├── tools/
│   │   ├── tavily_search.py
│   │   ├── calculator.py
│   │   ├── python_executor.py
│   │   ├── sql_tool.py
│   │   ├── datetime_tool.py
│   │   ├── file_reader.py
│   │   └── tool_selector.py
│   │
│   ├── llm/
│   │   ├── provider.py
│   │   ├── prompts.py
│   │   ├── models.py
│   │   └── output_parser.py
│   │
│   ├── services/
│   │   ├── llm_service.py
│   │   ├── rag_service.py
│   │   ├── memory_service.py
│   │   ├── search_service.py
│   │   ├── citation_service.py
│   │   └── upload_service.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── crud.py
│   │   └── migrations/
│   │
│   ├── schemas/
│   │   ├── chat.py
│   │   ├── upload.py
│   │   ├── memory.py
│   │   └── session.py
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── logging.py
│   │   └── security.py
│   │
│   ├── frontend/
│   │   ├── templates/
│   │   ├── static/
│   │   └── chat_ui.html
│   │
│   ├── tests/
│   │
│   └── main.py
│
├── uploaded_documents/
├── vector_db/
├── logs/
├── .env
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🧠 Core Features

1. **LangGraph-driven Orchestration**: Incorporates an intelligent routing agent, step-by-step planners, tool selectors, execution wrappers, response synthesizers, and self-reflection layers.
2. **Local Vector Search with API Fallback**: Performs high-speed similarity search on pre-populated embeddings and automatically switches to keyword-based token evaluation during OpenAI API limit errors.
3. **Conversational SQL & Code Execution**: Provides tools to read and write database structures or run custom python scripts dynamically.
4. **Memory Profiling**: Stores message timelines and dynamically extracts user characteristics or conversational summaries to memory logs.
5. **Interactive UI Dashboards**: Integrates both a standalone vanilla HTML client page (`/chat-ui`) and a telemetry dashboard powered by Streamlit.

---

## 🚀 Execution Guide

### Local Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure your keys inside `.env`:
   ```env
   OPENAI_API_KEY=your_openai_key
   GROQ_API_KEY=your_groq_key
   TAVILY_API_KEY=your_tavily_key
   ```
3. Run the FastAPI Backend:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
4. Run the Streamlit Dashboard:
   ```bash
   streamlit run app/frontend/streamlit_app.py
   ```

### Docker Compose Deployment

Build and spin up the complete backend and frontend services in one command:
```bash
docker-compose up --build
```
- FastAPI Backend: `http://localhost:8000`
- FastAPI Chat HTML UI: `http://localhost:8000/chat-ui`
- Streamlit Dashboard: `http://localhost:8501`

---

## 🧪 Testing Suite

Execute the built-in python unittest verification suite:
```bash
python -m unittest discover -s app/tests
```
