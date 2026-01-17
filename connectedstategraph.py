
# connectedstategraph.py
import os
from typing import TypedDict, Dict, Any

from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langgraph.prebuilt import create_react_agent

# --------- Types ----------
class MyState(TypedDict):
    count: int

# --------- LLM Factory ----------
def get_llm():
    HF_TOKEN = os.getenv("HF_TOKEN")
    REPO_ID = os.getenv("HF_REPO_ID", "openai/gpt-oss-20b")
    endpoint = HuggingFaceEndpoint(
        repo_id=REPO_ID,
        huggingfacehub_api_token=HF_TOKEN
    )
    return ChatHuggingFace(llm=endpoint)

# --------- Counter nodes ----------
def increment(st: MyState) -> MyState:
    return {"count": st["count"] + 1}

def double(st: MyState) -> MyState:
    # FIX: actually double
    return {"count": st["count"] * 2}

# --------- Router nodes ----------
def manager_node_factory(llm):
    def manager_node(state: Dict[str, Any]) -> Dict[str, Any]:
        task_input = state.get("task", "")
        user_input = state.get("input", "")
        prompt = f"""
You are a task router. Based on the user request below, decide whether it is a:
- translate
- summarize
- calculate

Respond with only one word (translate, summarize, or calculate).

Task: {task_input}
"""
        decision = llm.invoke(prompt).content.strip().lower()
        # normalize
        if "trans" in decision:
            decision = "translate"
        elif "summ" in decision:
            decision = "summarize"
        elif "calc" in decision:
            decision = "calculate"
        else:
            decision = "default"
        return {"agent": decision, "input": user_input}
    return manager_node

def translator_node_factory(llm):
    def translator_node(state: Dict[str, Any]) -> Dict[str, Any]:
        text = state.get("input", "")
        prompt = f"Act like a translator. Only respond with the English translation of the text below:\n\n{text}"
        result = llm.invoke(prompt).content
        return {"result": result}
    return translator_node

def summarizer_node_factory(llm):
    def summarizer_node(state: Dict[str, Any]) -> Dict[str, Any]:
        text = state.get("input", "")
        prompt = f"Summarize the following in 1-2 lines:\n\n{text}"
        result = llm.invoke(prompt).content
        return {"result": result}
    return summarizer_node

def calculator_node_factory(llm):
    def calculator_node(state: Dict[str, Any]) -> Dict[str, Any]:
        expression = state.get("input", "")
        prompt = f"Please calculate and return the result of:\n{expression}"
        result = llm.invoke(prompt).content
        return {"result": result}
    return calculator_node

def default_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return {"result": "Sorry, I couldn't understand the task."}

def router_key(state: Dict[str, Any]) -> str:
    key = state.get("agent", "default").lower()
    mapping = {
        "translate": "Translator",
        "summarize": "Summarizer",
        "calculate": "Calculator",
        "default": "Default",
    }
    return mapping.get(key, "Default")

# --------- Graph builders ----------
def build_counter_graph():
    g = StateGraph(MyState)
    g.add_node("increment", increment)
    g.set_entry_point("increment")
    g.add_edge("increment", END)
    return g.compile()

def build_counter_graph_chain():
    g = StateGraph(MyState)
    g.add_node("increment", increment)
    g.add_node("double", double)
    g.set_entry_point("increment")
    g.add_edge("increment", "double")
    g.add_edge("double", END)
    return g.compile()

def build_router_graph(llm=None):
    if llm is None:
        llm = get_llm()

    g = StateGraph(dict)
    g.add_node("Manager", manager_node_factory(llm))
    g.add_node("Translator", translator_node_factory(llm))
    g.add_node("Summarizer", summarizer_node_factory(llm))
    g.add_node("Calculator", calculator_node_factory(llm))
    g.add_node("Default", default_node)

    g.set_entry_point("Manager")
    # explicit conditional routing
    g.add_conditional_edges(
        "Manager",
        router_key,
        {
            "Translator": "Translator",
            "Summarizer": "Summarizer",
            "Calculator": "Calculator",
            "Default": "Default",
        },
    )
    g.add_edge("Translator", END)
    g.add_edge("Summarizer", END)
    g.add_edge("Calculator", END)
    g.add_edge("Default", END)
    return g.compile()


# --------- ReAct Agent ----------
def add(a: int, b: int) -> int:
    """Addition: return the sum of two integers a and b."""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiplication: return the product of two integers a and b."""
    return a * b


def build_react_agent(llm=None):
    if llm is None:
        llm = get_llm()
    tools = [add, multiply]
    return create_react_agent(model=llm, tools=tools)

# --------- Optional: quick test when running directly ----------
if __name__ == "__main__":
    llm = get_llm()
    app1 = build_counter_graph()
    print("Counter result:", app1.invoke({"count": 3}))

    app2 = build_counter_graph_chain()
    print("Counter chain result:", app2.invoke({"count": 3}))

    router = build_router_graph(llm)
    print("Router translate:", router.invoke({"task": "please translate", "input": "Bonjour le monde"}))
