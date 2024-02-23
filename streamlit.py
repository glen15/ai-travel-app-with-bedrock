import streamlit as st
import requests
import json

ENDPOINT_LAMBDA_URL = "<<YOUR-LAMBDA-URL>>"

st.title("Chatbot powered by Bedrock")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message Bedrock..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # buffered
        with st.spinner("Thinking..."):
            response_raw = requests.post(ENDPOINT_LAMBDA_URL, json={"prompt": prompt})
            print(f"raw: {response_raw}")
            response_json = response_raw.json()
            print(f"json: {response_json}")
            model_output = response_json.get("output")
            print(model_output)

        st.write(model_output)

    st.session_state.messages.append({"role": "assistant", "content": model_output})