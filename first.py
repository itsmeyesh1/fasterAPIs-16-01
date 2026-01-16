# from fastapi import FastAPI
# from pydantic import BaseModel, Field,EmailStr,AnyUrl,field_validator,model_validator
# appn = FastAPI()
# ############ pip install -"uvicorn[standard]"

# ##### uvicorn main:app --port 3000
# # 
# @appn.get("/hii")  ##We can also use the like 127.00.1.56900 atlastkeep /abcd (the one which is present in get) in browser url ..
# def read_root():
#    return {"first": "one", "second":"two"}
#    return "Hello"
# #uvicorn first:appn --reload #to run it

# @appn.get("/call/start")
# def start_call():
#     return{
#         "call_id": "CALL_123", "status": "starting.."
#     }

# ##Post Approach
# # @appn.post("/status")
# # def status():
# #    return {"status": "running"}

# #####Another way creating a baseclass and pydantic 

# class Item(BaseModel): #from pydantic import BaseModel
#    name:str
#    email:str

# @appn.post("/create_items/")
# def create_items(item: Item):
#    return item.name +  " and " + item.email


# #Another code
# class TextInput(BaseModel):
#    text: str   #(myenv) C:\Emphasis\FirstProject\Faster\myenv>uvicorn first:appn --reload --host 127.0.0.1 --port 8000 this has to be run in terminal
    
# @appn.post("/process")
# def process_text(data: TextInput):  
#    return {
#       "original" : data.text,
#       "length": len(data.text),
#       "upper" : data.text.upper()
#    }





# # 
# # uvicorn
# # fastapi
# # streamlit
# # langchain
# # langchain-core
# # langchain-community
# # langchain-huggingface
# # langgraph-supervisor  These are the necessary requirements.txt
# #rather than flask fastapi is better and faster
# # get and post apporach 2 

##############PARsers
#for custom manual parsing we have to use this
# first.py ##It is a server side actually 
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json

appn = FastAPI(title="FastAPI + Manual JSON Parsing")

# --- Your simple GETs (kept as-is) ---
@appn.get("/hii")
def read_root():
    return {"first": "one", "second": "two"}

@appn.get("/call/start")
def start_call():
    return {"call_id": "CALL_123", "status": "starting.."}

# --- Pydantic example (optional) ---
class Item(BaseModel):
    name: str
    email: str

@appn.post("/create_items/")
def create_items(item: Item):
    return {"message": f"{item.name} and {item.email}"}

# --- Manual JSON parsing endpoint ---
@appn.post("/process")
async def process_text(request: Request):
    """
    Manually parse incoming JSON.
    Expected body: { "text": "some string" }
    """
    try:
        raw = await request.body()
        if not raw:
            raise HTTPException(status_code=400, detail="Empty request body")

        # Explicit JSON parsing (JSON parser usage)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {e.msg}")

        # Schema checks
        if not isinstance(payload, dict):
            raise HTTPException(status_code=422, detail="JSON root must be an object")
        if "text" not in payload:
            raise HTTPException(status_code=422, detail="Missing field: 'text'")
        if not isinstance(payload["text"], str):
            raise HTTPException(status_code=422, detail="'text' must be a string")

        text = payload["text"]
        result = {
            "original": text,
            "length": len(text),
            "upper": text.upper()
        }
        return JSONResponse(result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@appn.get("/health")
def health():
    return {"status": "ok"}
