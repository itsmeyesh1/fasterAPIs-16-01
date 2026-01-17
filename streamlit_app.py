
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from connectedstategraph import (
    get_llm,
    build_counter_graph,
    build_counter_graph_chain,
    build_router_graph,
    build_react_agent,
)

st.set_page_config(page_title="LangGraph + Streamlit", page_icon="🧭", layout="wide")
st.title("🧭 LangGraph + Streamlit")

load_dotenv()

def read_secret_or_env(key: str, default: str = "") -> str:
    try:
        return st.secrets[key]  # Will raise if secrets.toml doesn't exist
    except Exception:
        return os.getenv(key, default) or default

HF_TOKEN_DEFAULT = read_secret_or_env("HF_TOKEN", "")
HF_REPO_DEFAULT = read_secret_or_env("HF_REPO_ID", "openai/gpt-oss-20b")

with st.sidebar:
    st.header("🔧 Settings")
    HF_TOKEN = st.text_input("Hugging Face Token (HF_TOKEN)", value=HF_TOKEN_DEFAULT, type="password")
    REPO_ID = st.text_input("Hugging Face repo_id", value=HF_REPO_DEFAULT)
    st.caption("Tip: Use `.streamlit/secrets.toml` or `.env` for local runs.")

if not HF_TOKEN:
    st.warning("Please provide a **Hugging Face token** to proceed.")
    st.stop()

# Make token/model visible to connectedstategraph.get_llm()
os.environ["HF_TOKEN"] = HF_TOKEN
os.environ["HF_REPO_ID"] = REPO_ID


# ---------- Build shared LLM and graphs (cached) ----------
@st.cache_resource(show_spinner=False)
def _init_llm_and_graphs_cached(token: str, repo_id: str):
    # ensure env is set inside cache scope too
    os.environ["HF_TOKEN"] = token
    os.environ["HF_REPO_ID"] = repo_id
    llm = get_llm()
    counter_app = build_counter_graph()
    counter_chain_app = build_counter_graph_chain()
    router_app = build_router_graph(llm)
    react_agent = build_react_agent(llm)
    return llm, counter_app, counter_chain_app, router_app, react_agent

llm, counter_app, counter_chain_app, router_app, react_agent = _init_llm_and_graphs_cached(HF_TOKEN, REPO_ID)

# ---------- Helper: diagram ----------

def show_graph_diagram(app, title: str):
    st.subheader(title)
    try:
        image_data = app.get_graph().draw_mermaid_png()
        st.image(image_data, caption="Graph diagram", width=450)   # 👈 Smaller size
    except Exception as e:
        st.info(f"Diagram rendering not available: {e}")




# ---------- Tabs ----------
tab1, tab2, tab3, tab4 = st.tabs([
    "Counter (increment → END)",
    "Counter (increment → double → END)",
    "Router (translate / summarize / calculate)",
    "ReAct Agent (tools)"
])

with tab1:
    show_graph_diagram(counter_app, "Counter Graph (increment → END)")
    st.markdown("**Run**")
    init_count = st.number_input("Initial count", min_value=0, max_value=10**9, value=3, step=1)
    if st.button("Run increment"):
        out = counter_app.invoke({"count": int(init_count)})
        st.success(f"Result: {out['count']}")

with tab2:
    show_graph_diagram(counter_chain_app, "Counter Graph (increment → double → END)")
    st.markdown("**Run**")
    init_count2 = st.number_input("Initial count", min_value=0, max_value=10**9, value=3, step=1, key="init2")
    if st.button("Run increment → double"):
        out = counter_chain_app.invoke({"count": int(init_count2)})
        st.success(f"Result: {out['count']}")

with tab3:
    show_graph_diagram(router_app, "Router Graph")
    st.markdown("**Run**")
    task = st.text_input("Task instruction (e.g., 'Please translate this')")
    user_input = st.text_area("Text / expression to process", height=120, value="Bonjour le monde")
    if st.button("Route & Execute"):
        with st.spinner("Routing and executing..."):
            result = router_app.invoke({"task": task, "input": user_input})
        st.success("Done")
        st.json(result)

with tab4:
    st.subheader("ReAct Agent with tools (add, multiply)")
    if "chat" not in st.session_state:
        st.session_state.chat = []

    # render chat history
    for role, content in st.session_state.chat:
        with st.chat_message(role):
            st.write(content)

    prompt = st.chat_input("Ask something (e.g., 'What is 12 + 30? Use tool.')")
    if prompt:
        st.session_state.chat.append(("user", prompt))
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    res = react_agent.invoke({"messages": [HumanMessage(content=prompt)]})
                    # best-effort extraction
                    content = None
                    if isinstance(res, dict):
                        if "messages" in res and res["messages"]:
                            last = res["messages"][-1]
                            content = getattr(last, "content", str(res))
                        else:
                            content = str(res)
                    else:
                        content = str(res)
                    st.write(content)
                    st.session_state.chat.append(("assistant", content))
                except Exception as e:
                    st.error(f"Agent error: {e}")
#parsers ,aiagents  pydantic ,fasterapi,streamlit and docker and kuberneteous format -yml format to connect to thr tool 
#docker 4 to 5 commands
