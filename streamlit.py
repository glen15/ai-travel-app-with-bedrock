import streamlit as st
import requests
import json
import boto3

ENDPOINT_LAMBDA_URL = "<<YOUR-LAMBDA-URL>>"

def bedrock_chat(user_message):
    bedrock_runtime = boto3.client(
            service_name="bedrock-runtime", region_name="us-east-1"
        )

    request_body = json.loads(event.get("body"))
    prompt = (
        request_body.get("prompt")
        if "prompt" in request_body
        else "Amazon Bedrock이 뭐야? 3문장 이내로 답변해"
    )
    print(f">>>>>>>>>>>> prompt: {prompt}")
    # Anthropic의 Claude 모델 사용
    # 한국어를 비교적 잘 지원
    # https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-claude.html
    body = json.dumps(
        {
            "prompt": f"\n\nHuman:{prompt}\n\nAssistant:",
            "temperature": 0,
            "top_p": 0.01,
            "max_tokens_to_sample": 1000,
        }
    )
    # buffered
    response = bedrock_runtime.invoke_model(
        body=body, modelId="anthropic.claude-v2"
    )
    response_body = json.loads(response.get("body").read())
    model_response = response_body["completion"]
    print(f">>>>>>>>>>>> model output: {model_response}")
    return done(None, {"output": model_response})

def done(err, res):
    if err:
        print(f"!!!!!!!!!!!!{err}")

    return {
        "statusCode": "400" if err else "200",
        # 한글 깨짐을 방지하기 위해 ensure_ascii 옵션 추가
        "body": json.dumps(res, ensure_ascii=False),
        "headers": {"Content-Type": "application/json"},
    }

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
            ai_response = bedrock_chat(prompt)
            print(f"AI 응답: {ai_response}")
        st.write(ai_response)

    st.session_state.messages.append({"role": "assistant", "content": ai_response})