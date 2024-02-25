import streamlit as st
import pandas as pd
from generate import generate_image, generate_plan, bedrock_chat
from data_df import create_dataframe

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
    duration = st.slider('원하는 여행 기간을 알려주세요.', 1, 15, 3)
    purpose = st.selectbox(
        '원하는 여행 목적을 알려주세요.', 
        ("자연경관을 보며 휴양", "맛있는 음식 먹기", "역사적인 건축물 관람", "예술 작품 관람"), 
        placeholder="여행에서 뭘 하고 싶어요?",
    )
    st.divider()
    if st.button("이미지 생성", type="primary"):
        with st.spinner("이미지를 생성하는 중입니다..."):
            st.session_state.result_image = generate_image(place)
    st.image(st.session_state.result_image, caption="AI 생성 이미지", use_column_width=True)
with col2:
    st.write(f"당신의 선택은 : {purpose}을(를) 주 목적으로 {place}에서 {duration-1}박 {duration}일 동안 여행하기")
    if st.button("여행 계획 만들기", type="primary"):
        with st.spinner("여행 계획을 생성하는 중입니다..."):
            st.session_state.messages = [{"role": "assistant", "content": "생성된 당신의 여행 계획에 대해서 물어보세요!"}]
            st.session_state.result_plan = generate_plan(place, duration, purpose)
    st.text_area(st.session_state.result_plan, label_visibility="hidden")
st.divider()
df = create_dataframe()
st.header("다른 사람들의 :blue[선택]은? :", divider="rainbow")
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("어디가?")
    place_counts = df['Place'].value_counts()
    st.bar_chart(place_counts)
with col2:
    st.subheader("몇일가?")
    duration_counts = df['Duration'].value_counts()
    st.bar_chart(duration_counts, color="#fdf0d5")
with col3:
    st.subheader("뭐하러가?")
    purpose_counts = df['Purpose'].value_counts()
    st.bar_chart(purpose_counts, color="#c1121f")
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
