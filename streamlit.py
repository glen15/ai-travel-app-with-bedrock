import streamlit as st
import json
import boto3
import os
import base64
import random

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime", region_name="us-east-1"
)

def invoke_model(prompt, model_id, max_tokens=1000):
    body = json.dumps({
        "prompt": prompt,
        "temperature": 0,
        "top_p": 0.01,
        "max_tokens_to_sample": max_tokens,
    })
    response = bedrock_runtime.invoke_model(body=body, modelId=model_id)
    return json.loads(response.get("body").read())["completion"]

def kor_to_eng(text):
    prompt = f"\n\nHuman:Translate '{text}' into English\n\nAssistant:"
    return invoke_model(prompt, model_id="anthropic.claude-v2", max_tokens=100)

def generate_plan(place, duration, purpose):
    prompt = f"\n\nSystem:You are an expert in creating travel plans\n\nHuman:Create a travel plan for {purpose} during {duration} in {place} Make sure to speak in Korean\n\nAssistant:"
    return invoke_model(prompt, model_id="anthropic.claude-v2")

def generate_image(place):
    seed = random.randint(0, 2147483647)
    text = kor_to_eng(f"{place}을 여행하는 포스터를 생성해라")
    prompt = {
        "taskType": "TEXT_IMAGE", 
        "textToImageParams": {"text": text},
        "imageGenerationConfig": {
            "numberOfImages": 1, "quality": "standard", "cfgScale": 7.5,
            "height": 512, "width": 512, "seed": seed,
        }
    }
    response = bedrock_runtime.invoke_model(
        modelId="amazon.titan-image-generator-v1", body=json.dumps(prompt)
    )
    base64_image_data = json.loads(response["body"].read())["images"][0]
    output_folder = 'generated_images'
    os.makedirs(output_folder, exist_ok=True)
    file_path = os.path.join(output_folder, f"image.png")
    with open(file_path, 'wb') as file:
        file.write(base64.b64decode(base64_image_data))
    return file_path

def bedrock_chat(ai_result, prompt):
    prompt = f"System:{ai_result}에 기반해서 질문에 대답해라\n\nHuman:{prompt}\n\nAssistant:"
    return invoke_model(prompt, model_id="anthropic.claude-v2")

### 화면 구성 ###
st.title("Chatbot powered by Bedrock")

if "result_plan" not in st.session_state:
    st.session_state.result_plan = "멋진 계획을 만들어드릴게요!"

if "result_image" not in st.session_state:
    st.session_state.result_image = "generated_images/sample.png"

st.header(":blue[GEN-AI] 텍스트 & 이미지 :sunglasses:", divider="rainbow")
col1, col2 = st.columns(2)
with col1:
    place = st.text_input('원하는 여행 장소를 알려주세요.', '프랑스 파리')
    duration = st.text_input('원하는 여행 기간을 알려주세요.', '2박 3일')
    purpose = st.text_input('원하는 여행 목적을 알려주세요.', '예술품 관람')
    st.divider()
    if st.button("이미지 생성", type="primary"):
        with st.spinner("이미지를 생성하는 중입니다..."):
            st.session_state.result_image = generate_image(place)
    st.image(st.session_state.result_image, caption="AI 생성 이미지", use_column_width=True)
with col2:
    if st.button("여행 계획 만들기", type="primary"):
        with st.spinner("여행 계획을 생성하는 중입니다..."):
            st.session_state.result_plan = generate_plan(place, duration, purpose)
    st.text_area("", st.session_state.result_plan)
st.divider()

st.header(":blue[GEN-AI] 챗봇 :sunglasses:", divider="rainbow")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "생성된 당신의 여행 계획에 대해서 물어보세요!"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message Bedrock..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = bedrock_chat(st.session_state.result_plan, prompt)
        st.write(result)

    st.session_state.messages.append({"role": "assistant", "content": result})
