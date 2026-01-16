# import streamlit as st
# import requests

# API_URL = "http://127.0.0.1:8000/process"

# st.title("Streamlit to FastAPI")
# with st.form("text_form"):
#     text = st.text_input("Enter text")
#     submitted = st.form_submit_button("Send to API")
# if submitted:
#     response = requests.post(
#         API_URL,
#         json ={"text": text}
#     )
#     if response.status_code == 200:
#         data = response.json()
#         st.success("Response from API")
#         st.json(data)
#     else:
#         st.error("API calll failed")


# #######for first we ahve to run the first.py in Faster in one terminal using #(myenv) C:\Emphasis\FirstProject\Faster\myenv>uvicorn first:appn --reload --host 127.0.0.1 --port 8000 this has to be run in terminal
# # and then in StreamFasterApi.pu we havve to run in another terminal as --> streamlit run StreamFasterApi.py(file name )

##########PARSERS

# streamfsterapi.py
import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8000/process"

st.set_page_config(page_title="Streamlit → FastAPI (JSON Parsers)", page_icon="🧩")
st.title("Streamlit → FastAPI with JSON Parsers")

st.markdown("Paste request JSON below. **Expected:** `{ \"text\": \"your message\" }`")

with st.form("json_form"):
    default_json = '{\n  "text": "Hello from Streamlit"\n}'
    json_input = st.text_area("Request JSON", value=default_json, height=150)
    submitted = st.form_submit_button("Send to API")

if submitted:
    # 1) Parse the JSON locally (client-side parser)
    try:
        payload = json.loads(json_input)   # <-- JSON parser in action
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON: {e.msg}")
    else:
        # 2) Validate shape (optional but helpful)
        if not isinstance(payload, dict):
            st.error("JSON root must be an object")
        elif "text" not in payload:
            st.error("Missing field: 'text'")
        elif not isinstance(payload["text"], str):
            st.error("'text' must be a string")
        elif not payload["text"].strip():
            st.warning("'text' is empty. Please enter some content.")
        else:
            # 3) Send to API (send the raw JSON text with proper header)
            headers = {"Content-Type": "application/json"}
            with st.spinner("Calling API..."):
                try:
                    response = requests.post(
                        API_URL,
                        data=json_input,         # sending the raw JSON string
                        headers=headers,
                        timeout=10
                    )
                    st.write(f"HTTP Status: {response.status_code}")

                    # Parse response JSON for display
                    if "application/json" in response.headers.get("content-type", ""):
                        try:
                            st.subheader("JSON Response")
                            st.json(response.json())  # <-- parses response JSON
                        except ValueError:
                            st.subheader("Raw Response")
                            st.code(response.text)
                    else:
                        st.subheader("Raw Response")
                        st.code(response.text)

                    if response.status_code == 200:
                        st.success("Success ✅")
                    else:
                        st.error("API call failed. See details above.")

                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to FastAPI. Is it running on 127.0.0.1:8000?")
                except requests.exceptions.Timeout:
                    st.error("Request timed out.")
                except Exception as e:
                    st.exception(e)

st.caption("Tip: You can also send with requests.post(..., json=payload). That auto-serializes and sets headers.")
