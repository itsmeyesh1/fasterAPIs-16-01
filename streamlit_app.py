
# streamlit_app.py
from connected_graph import build_connected_app
import streamlit as st


st.set_page_config(page_title="Connected LangGraph (A→B→C)", page_icon="🕸️")
st.title("🕸️ Connected Graph — shown only after Invoke")

# Inputs
st.subheader("Inputs")
col1, col2 = st.columns(2)
with col1:
    count0 = st.number_input("Initial count", min_value=0, value=3, step=1)
with col2:
    preset = st.selectbox("Manager task preset", ["Translate", "Summarize", "Calculate", "Custom"])

if preset == "Translate":
    task = "translate this to English"
    user_input = st.text_input("Text to translate", "Bonjour le monde")
elif preset == "Summarize":
    task = "summarize this"
    user_input = st.text_area("Text to summarize", "LangGraph helps you build flexible multi-agent workflows in Python...", height=120)
elif preset == "Calculate":
    task = "calculate this"
    user_input = st.text_input("Expression", "12 * 8 + 5")
else:
    task = st.text_input("Task (e.g., 'translate', 'summarize', 'calculate')", "")
    user_input = st.text_area("Input", "", height=100)

run = st.button("Run")

# Build app (cache so it’s not rebuilt every click)
@st.cache_resource(show_spinner=False)
def _get_app():
    return build_connected_app()

app = _get_app()

if run:
    with st.spinner("Invoking..."):
        state_in = {"count": count0, "task": task, "input": user_input}
        final_state = app.invoke(state_in)

    st.success("Done ✅")

    # Show result values
    st.write("**Final state:**")
    st.json(final_state)

    # IMPORTANT: Show the connected picture ONLY AFTER invoke
    st.subheader("Connected Graph (Mermaid)")
    try:
        # Local, no-network render (text-based)
        mermaid = app.get_graph().draw_mermaid()
        st.code(mermaid, language="mermaid")
    except Exception as e:
        st.error(f"Could not render mermaid: {e}")
else:
    st.info("Click **Run** to invoke. The connected graph picture will appear here after the run.")

#parsers ,aiagents  pydantic ,fasterapi,streamlit and docker and kuberneteous format -yml format to connect to thr tool 
#docker 4 to 5 commands in docker