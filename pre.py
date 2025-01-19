import streamlit as st
import requests
import json
import random

# 페이지 기본 설정
st.set_page_config(
    page_title="키즈 영어 선생님",
    page_icon="🌈",
    layout="wide"
)

# 기본 주제와 단어 설정
TOPICS = {
    "animals": ["dog", "cat", "elephant", "lion", "rabbit"],
    "colors": ["red", "blue", "yellow", "green", "pink"],
    "numbers": ["one", "two", "three", "four", "five"],
    "greetings": ["hello", "goodbye", "thank you", "please"],
    "daily_activities": ["eat", "play", "sleep", "walk", "run"]
}

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_topic" not in st.session_state:
    st.session_state.current_topic = "animals"
if "points" not in st.session_state:
    st.session_state.points = 0

def initialize_chat_history():
    return [
        {
            "role": "system",
            "content": """당신은 5세 유치원생을 위한 친근하고 재미있는 영어 선생님입니다. 다음 지침을 따라주세요:
            1. 항상 긍정적이고 격려하는 톤을 유지하세요 ("잘했어요!", "멋져요!", "정말 훌륭해요!")
            2. 한국어를 주로 사용하고, 영어 단어나 문장을 가르칠 때는 천천히 설명하세요
            3. 답변은 짧고 이해하기 쉽게 해주세요
            4. 동물 소리나 이모지를 활용해 재미있게 가르쳐주세요
            5. 한 번에 하나의 개념만 가르치고, 많은 반복을 활용하세요"""
        }
    ]

def chat_with_deepseek(messages, api_key):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"오류가 발생했어요: {str(e)}"

# 사이드바 구성
with st.sidebar:
    st.title("🎨 설정")
    api_key = st.text_input("Deepseek API 키를 입력하세요", type="password")
    
    # 주제 선택
    selected_topic = st.selectbox(
        "오늘의 주제를 선택해주세요",
        ["동물(Animals)", "색깔(Colors)", "숫자(Numbers)", "인사(Greetings)", "일상활동(Daily Activities)"]
    )
    
    # 학습 진행도
    st.markdown("### 🌟 나의 점수")
    st.progress(min(st.session_state.points / 100.0, 1.0))
    st.write(f"현재 점수: {st.session_state.points}")
    
    if st.button("새로운 대화 시작하기"):
        st.session_state.messages = initialize_chat_history()
        st.session_state.points = 0

# 메인 화면
st.title("🌈 키즈 영어 선생님")
st.write("안녕하세요! 오늘은 재미있는 영어 공부를 해볼까요? 😊")

# 게임 섹션
st.markdown("### 🎮 미니 게임")
if st.button("단어 맞추기 게임 시작!"):
    topic_key = selected_topic.split("(")[0]
    if topic_key == "동물":
        word = random.choice(TOPICS["animals"])
        st.session_state.current_word = word
        st.write(f"이 동물은 무엇일까요? 🤔")
        if topic_key == "동물" and word == "dog":
            st.write("멍멍! 🐕")
        elif word == "cat":
            st.write("야옹! 🐱")

# 채팅 인터페이스
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 사용자 입력
if user_input := st.chat_input("메시지를 입력하세요..."):
    if not api_key:
        st.error("API 키를 입력해주세요!")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # AI 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("선생님이 생각중이에요..."):
                response = chat_with_deepseek(st.session_state.messages, api_key)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # 정답을 맞췄을 때 점수 부여
                if hasattr(st.session_state, 'current_word') and \
                   st.session_state.current_word.lower() in user_input.lower():
                    st.balloons()
                    st.session_state.points += 10
                    st.write("🎉 정답이에요! 10점을 획득했어요!")
