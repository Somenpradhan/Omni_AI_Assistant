import os
import sys
import streamlit as st
import requests
from dotenv import load_dotenv

# Include workspace root directory in sys.path to enable local imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

load_dotenv()

# Page configuration for a premium, clean layout
st.set_page_config(
    page_title="Aether - Multi-Agent Orchestrator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000"

# --- CUSTOM CSS FOR PREMIUM AESTHETICS ---
st.markdown("""
<style>
    /* Global styles and custom fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Main layout dark mode gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #020617 100%);
        color: #f8fafc;
    }
    
    /* Premium Title Header styling */
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.05rem;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    
    /* Pipeline component indicators */
    .pipeline-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(148, 163, 184, 0.1);
        backdrop-filter: blur(10px);
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    
    .pipeline-node {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        text-align: center;
        flex: 1;
        margin: 0 0.5rem;
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }
    
    .node-active {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
        border-color: #818cf8;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
        color: white;
    }
    
    .node-inactive {
        background: rgba(15, 23, 42, 0.6);
        border-color: rgba(148, 163, 184, 0.1);
        color: #64748b;
    }
    
    .node-router {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
        border-color: #38bdf8;
        color: white;
    }
    
    .node-response {
        background: linear-gradient(135deg, #d946ef 0%, #c026d3 100%);
        border-color: #f472b6;
        color: white;
    }
    
    .pipeline-arrow {
        color: #475569;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    /* Custom style for response block */
    .agent-header {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #818cf8;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .chat-bubble {
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    
    .chat-user {
        background-color: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.3);
        margin-left: 2rem;
        text-align: right;
    }
    
    .chat-assistant {
        background-color: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(71, 85, 105, 0.3);
        margin-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- BACKEND HEALTH / STATUS PING ---
@st.cache_data(ttl=5)
def check_backend_status():
    try:
        r = requests.get(f"{API_URL}/health", timeout=1.5)
        if r.status_code == 200:
            return True, r.json()
    except Exception:
        pass
    return False, {}

backend_online, health_data = check_backend_status()

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.markdown("<h2 style='margin-top:0;'>⚙️ Workspace settings</h2>", unsafe_allow_html=True)
    
    # Thread (Session) selector
    st.markdown("### 💬 Conversation Session")
    thread_id = st.text_input("Session ID (Conversational Memory)", value="session_01")
    st.caption("Change Session ID to start a new thread. History is stored locally.")
    
    if st.button("🧹 Clear Current Workspace"):
        st.session_state.chat_history = []
        st.toast("Local session cleared. (Server session remains in memory.db)")
        
    st.markdown("---")
    
    # System Telemetry & Configuration Status
    st.markdown("### 📊 System Status")
    if backend_online:
        st.markdown("🟢 **API Backend**: Running (`localhost:8000`) ")
        openai_status = "✅ Configured" if health_data.get("openai_configured") else "❌ Missing"
        tavily_status = "✅ Configured" if health_data.get("tavily_configured") else "⚠️ Missing (Falls back to DDG)"
        
        st.markdown(f"- OpenAI API Key: **{openai_status}**")
        st.markdown(f"- Tavily Search: **{tavily_status}**")
    else:
        st.markdown("🟡 **API Backend**: Offline. (Running inside local Streamlit fallback process)")
        has_openai = bool(os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your_openai_api_key_here")
        openai_status = "✅ Configured" if has_openai else "❌ Missing"
        st.markdown(f"- OpenAI API Key: **{openai_status}**")
        st.caption("Ensure your `.env` contains `OPENAI_API_KEY` to run queries.")
        
    st.markdown("---")
    st.markdown("### 🧪 Agents In Play")
    st.info("""
    - **Router Agent**: Routes inputs dynamically.
    - **RAG Agent**: Queries local files.
    - **Planner Agent**: Outlines step-by-step goals.
    - **Web Agent**: Searches live public indices.
    - **Response Agent**: Coordinates final answers.
    """)

# --- MAIN APP LAYOUT ---
st.markdown("<h1 class='main-title'>Aether Orchestrator</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>A premium LangGraph multi-agent orchestration hub integrating RAG, Planner, and live Search</p>", unsafe_allow_html=True)

# Helper function to submit query
def submit_query(query_text, session_id):
    if backend_online:
        # API request
        try:
            r = requests.post(
                f"{API_URL}/chat", 
                json={"query": query_text, "thread_id": session_id},
                timeout=120
            )
            if r.status_code == 200:
                return r.json()
            else:
                st.error(f"Error {r.status_code}: {r.text}")
                return None
        except Exception as e:
            st.error(f"Connection to API failed: {e}")
            return None
    else:
        # Fallback to local import invocation
        try:
            from app.orchestrator.graph import run_orchestrator
            res = run_orchestrator(query_text, thread_id=session_id)
            if res:
                res["task_output"] = res.get("planner_output", "")
            return res
        except Exception as e:
            st.error(f"Failed to run orchestrator locally: {e}")
            return None

# --- INITIALIZE CHAT STATE ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Fetch history from backend on startup or session ID change if not already fetched
if backend_online and not st.session_state.chat_history:
    try:
        r = requests.get(f"{API_URL}/history/{thread_id}")
        if r.status_code == 200:
            st.session_state.chat_history = r.json().get("history", [])
    except Exception:
        pass

# Display Conversation History
for chat in st.session_state.chat_history:
    role = chat.get("role")
    content = chat.get("content")
    
    if role == "user":
        st.markdown(f"""
        <div class="chat-bubble chat-user">
            <div class="agent-header">YOU</div>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-bubble chat-assistant">
            <div class="agent-header">AETHER ASSISTANT</div>
            {content}
        </div>
        """, unsafe_allow_html=True)

# --- CHAT INPUT ---
user_input = st.chat_input("Ask a question, request a task plan, or ask about internal documents...")

if user_input:
    # 1. Display User Message immediately
    st.markdown(f"""
    <div class="chat-bubble chat-user">
        <div class="agent-header">YOU</div>
        {user_input}
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Query Orchestrator
    with st.spinner("🧠 Orchestrating agents..."):
        result = submit_query(user_input, thread_id)
        
    if result:
        # 3. Add to chat history list
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": result["final_response"]})
        
        # 4. Draw Pipeline Flow
        active_route = result["route"]
        
        st.markdown("#### 🔗 Execution Routing Pipeline")
        st.markdown(f"""
        <div class="pipeline-container">
            <div class="pipeline-node node-router">Router Agent</div>
            <div class="pipeline-arrow">➔</div>
            <div class="pipeline-node {'node-active' if active_route == 'llm' else 'node-inactive'}">LLM Agent</div>
            <div class="pipeline-node {'node-active' if active_route == 'rag' else 'node-inactive'}">RAG Agent</div>
            <div class="pipeline-node {'node-active' if active_route == 'planner' else 'node-inactive'}">Planner Agent</div>
            <div class="pipeline-node {'node-active' if active_route == 'web_search' else 'node-inactive'}">Web Agent</div>
            <div class="pipeline-arrow">➔</div>
            <div class="pipeline-node node-response">Response Agent</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 5. Display Assistant Response
        st.markdown(f"""
        <div class="chat-bubble chat-assistant">
            <div class="agent-header">AETHER ASSISTANT</div>
            {result["final_response"]}
        </div>
        """, unsafe_allow_html=True)
        
        # 6. Display Collapsible Trace Logs
        with st.expander("🔍 Intermediate Agent Telemetry Logs", expanded=False):
            st.markdown(f"**Orchestrator Routing Decision:** `{active_route.upper()}`")
            st.markdown("---")
            
            if result.get("llm_output"):
                st.markdown("**LLM Node Output:**")
                st.code(result["llm_output"], language="markdown")
                
            if result.get("rag_context"):
                st.markdown("**RAG Node Context (Vector Search):**")
                st.code(result["rag_context"], language="markdown")
                
            if result.get("task_output"):
                st.markdown("**Planner Node Steps & Strategy:**")
                st.code(result["task_output"], language="markdown")
                
            if result.get("web_search_output"):
                st.markdown("**Web Search Node Snippets:**")
                st.code(result["web_search_output"], language="markdown")
                
        # Rerun to keep interface updated
        st.rerun()
