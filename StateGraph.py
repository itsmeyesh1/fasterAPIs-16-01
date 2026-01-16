import os
from dotenv import load_dotenv
load_dotenv()
import langgraph
import importlib.metadata
from IPython.display import display
from langchain_core.messages import HumanMessage
from langgraph_supervisor import create_supervisor
#############pip install langgraph langchain-core langchain-huggingface huggingface_hub
############# pip install pip-system-certs

# print(importlib.metadata.version)
from typing import TypedDict
# ######pydantic basemodel here in typing typedDict .
class MyState(TypedDict):           
    count: int
ms = MyState()
ms["count"] = 3
print(ms["count"])
# 
def increment(st: MyState) -> MyState:
    return {"count": st["count"] + 1}
        #stategraph -> state is memory
increment(ms)
def double(st: MyState) -> MyState:
    return {"count": st["count"] + 1}
double(ms)
def abcd(cnt: int) ->int:
    return cnt+1
print(abcd(3))

from langgraph.graph import StateGraph, END
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

HF_TOKEN = os.getenv("HF_TOKEN")
REPO_ID = os.getenv("HF_REPO_ID", "openai/gpt-oss-20b")

endpoint = HuggingFaceEndpoint(
    repo_id=REPO_ID,
    huggingfacehub_api_token=HF_TOKEN
)
llm = ChatHuggingFace(llm=endpoint)
graph = StateGraph(MyState) ##### nodes,entrypoint,edges
graph.add_node("increment",increment)  #it can have multiple noddes
graph.set_entry_point("increment")
graph.add_edge("increment",END)

from langgraph.prebuilt import create_react_agent

def add(a:int ,b:int):
    """Addition"""
    return a + b
def multiply(a:int ,b:int):
    """Multiplication"""
    return a * b
tools = [add,multiply]
react_agent_auto = create_react_agent(
    model=llm,
    tools=tools
)
result_auto = react_agent_auto.invoke(
{
    "messages": [HumanMessage(content="What is 12 + 30? Use tool.")]
}
)
#(display(react_agent_auto.get_graph().draw_mermaid_png()))

app = graph.compile()           ##APP1
from PIL import Image
import io
image_data = app.get_graph().draw_mermaid_png()
img = Image.open(io.BytesIO(image_data))
img.show()

graph = StateGraph(MyState)
graph.add_node("increment",increment)
graph.add_node("double",double)

graph.set_entry_point("increment")
graph.add_edge("increment", "double")
graph.add_edge("double", END)

app2 = graph.compile()
from PIL import Image
import io
image_data=app2.get_graph().draw_mermaid_png()
img = Image.open(io.BytesIO(image_data))
img.show()

#######Conditional Edges -- manager nodes
def manager_node(state):
    task_input = state.get("task", "")
    input  =state.get("input","")
    prompt=f"""
    You are a task router. Based on the user request below, decide whether it is a:
    - translate
    - summarize
    - calculate

    Respond with only one word (translate, summarizze, or calculate).

    Task: {task_input}
    """
    decision = llm.invoke(prompt).content.strip().lower()
    return {"agent": decision, "input":input}

def translator_node(state):
    text = state.get("input", "")
    prompt = f"Act like You are a translator. Only respond with the English translation of the text below:\n\n{text}"
    result = llm.invoke(prompt).content
    return {"result": result}
def summarizer_node(state):
    text = state.get("input", "")
    prompt = f"Summarize the following in 1-2 lines:\n\n{text}"
    result = llm.invoke(prompt).content
    return {"result": result}
def calculator_node(state):
    expression = state.get("input", "")
    prompt =f"Please calculate and return the result of:\n{expression}"
    result = llm.invoke(prompt).content
    return{"result": result}

def route_by_agent(state):
    return {
        "translate": "Translator",
        "summarize": "summarizer",
        "calculate": "Calculator",
        "input": state.get("input", "")
    }.get(state.get("agent",""),"Default")
def default_node(state):
    return {"result": "Sorry, I couldn't understand the task."}

g= StateGraph(dict)
g.add_node("Manager", manager_node)
g.add_node("Translator", translator_node)
g.add_node("Summarizer", summarizer_node)
g.add_node("Calculator", calculator_node)
g.add_node("Default", default_node)

g.set_entry_point("Manager")
g.add_conditional_edges("Manager",route_by_agent)

g.set_finish_point("Translator")
g.set_finish_point("Summarizer")
g.set_finish_point("Calculator")
g.set_finish_point("Default")

app3 = g.compile()
from PIL import Image
import io
image_data=app3.get_graph().draw_mermaid_png()
img = Image.open(io.BytesIO(image_data))
img.show()

print(app3.invoke({
    "task":"can you translate this?",
    "input": "Bonjur le monde"
}))
print(app3.invoke({
    "task": "Please summarize the following",
    "input": "LangGraph helps you build flexible multi-agent workflows in python..."
}))

respcal = app3.invoke({
    "task": "What is 12 * 8 + 5?",
    "input": "12 * 8 + 5"
})
print(respcal['result'])

print(app3.invoke({
    "task": "can you dance?",
    "input": "foo"
}))