
# connected_graph.py
from typing import TypedDict
from langgraph.graph import StateGraph, END
import math

class AppState(TypedDict, total=False):
    count: int
    task: str
    input: str
    agent: str
    result: str

def a_increment(st: AppState) -> AppState:
    return {**st, "count": st.get("count", 0) + 1}

def b_increment(st: AppState) -> AppState:
    return {**st, "count": st.get("count", 0) + 1}

def b_double(st: AppState) -> AppState:
    return {**st, "count": st.get("count", 0) * 2}

def manager_node(state: AppState) -> AppState:
    t = (state.get("task") or "").lower()
    if "translate" in t:
        agent = "translate"
    elif "summarize" in t or "summary" in t:
        agent = "summarize"
    elif any(x in t for x in ("calc", "calculate", "math", "+", "-", "*", "/")):
        agent = "calculate"
    else:
        agent = "default"
    return {**state, "agent": agent}

def translator_node(state: AppState) -> AppState:
    text = state.get("input", "")
    if text.strip().lower() == "bonjour le monde":
        result = "Hello world"
    else:
        result = f"(translated) {text}"
    return {**state, "result": result}

def summarizer_node(state: AppState) -> AppState:
    text = state.get("input", "")
    short = (text[:120] + "...") if len(text) > 120 else text
    return {**state, "result": f"(summary) {short}"}

def calculator_node(state: AppState) -> AppState:
    expr = state.get("input", "")
    try:
        val = eval(expr, {"__builtins__": {}}, {"math": math})
        result = str(val)
    except Exception as e:
        result = f"Error: {e}"
    return {**state, "result": result}

def default_node(state: AppState) -> AppState:
    return {**state, "result": "Sorry, I couldn't understand the task."}

def route_by_agent(state: AppState) -> str:
    agent = (state.get("agent") or "").strip().lower()
    if agent in ("translate", "translator"):
        return "Translator"
    if agent in ("summarize", "summariser", "summarizer", "summary"):
        return "Summarizer"
    if agent in ("calculate", "calculator", "math"):
        return "Calculator"
    return "Default"

def build_connected_app():
    g = StateGraph(AppState)

    # A → B → C (connected)
    g.add_node("A_Increment", a_increment)
    g.add_node("B_Increment", b_increment)
    g.add_node("B_Double", b_double)

    g.add_node("Manager", manager_node)
    g.add_node("Translator", translator_node)
    g.add_node("Summarizer", summarizer_node)
    g.add_node("Calculator", calculator_node)
    g.add_node("Default", default_node)

    g.set_entry_point("A_Increment")
    g.add_edge("A_Increment", "B_Increment")
    g.add_edge("B_Increment", "B_Double")
    g.add_edge("B_Double", "Manager")

    g.add_conditional_edges("Manager", route_by_agent)
    g.add_edge("Translator", END)
    g.add_edge("Summarizer", END)
    g.add_edge("Calculator", END)
    g.add_edge("Default", END)

    return g.compile()
