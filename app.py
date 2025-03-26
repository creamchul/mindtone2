import streamlit as st
import openai
import os
from datetime import datetime
from dotenv import load_dotenv
from database import init_db, get_db, hash_password, verify_password
from models import User, Conversation, Message, Feedback
from sqlalchemy.orm import Session
import pandas as pd
import plotly.express as px

# .env 파일 로드
load_dotenv()

# 데이터베이스 초기화
init_db()

# 페이지 설정
st.set_page_config(
    page_title="Mindtone - 감정 지원 챗봇",
    page_icon="💭",
    layout="centered"
)

# OpenAI API 키 설정
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    st.error("OpenAI API 키가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY를 설정해주세요.")
    st.stop()

# 세션 상태 초기화
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_emotion' not in st.session_state:
    st.session_state.current_emotion = None
if 'current_conversation_id' not in st.session_state:
    st.session_state.current_conversation_id = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'show_stats' not in st.session_state:
    st.session_state.show_stats = False

# 감정 버튼 스타일 설정
emotion_button_style = """
<style>
    div.emotion-button > button {
        background-color: #f0f2f6;
        border-radius: 12px;
        padding: 15px 15px;
        font-size: 16px;
        margin: 5px;
        transition: all 0.3s;
    }
    div.emotion-button > button:hover {
        background-color: #e0e2e6;
        transform: translateY(-2px);
    }
    div.emotion-active > button {
        background-color: #6c7ac9;
        color: white;
    }
</style>
"""
st.markdown(emotion_button_style, unsafe_allow_html=True)

# 전역 변수로 감정 버튼 정의
emotions = {
    "기쁨": "😊",
    "슬픔": "😢",
    "화남": "😠",
    "불안": "😰",
    "지침": "😩",
    "혼란": "😕",
    "희망": "🌈",
    "감사": "🙏"
}

# 로그인 페이지
def show_login_page():
    st.title("Mindtone")
    st.subheader("감정 지원 AI 챗봇")
    st.write("계속하려면 로그인하거나 회원가입하세요.")
    
    login_tab, register_tab = st.tabs(["로그인", "회원가입"])
    
    with login_tab:
        login_username = st.text_input("사용자 이름", key="login_username")
        login_password = st.text_input("비밀번호", type="password", key="login_password")
        if st.button("로그인", key="login_button"):
            db = next(get_db())
            user = db.query(User).filter(User.username == login_username).first()
            if user and verify_password(login_password, user.password_hash):
                st.session_state.user_id = user.id
                st.session_state.username = user.username
                st.session_state.page = 'emotion_select'
                st.success("로그인 성공!")
                st.rerun()
            else:
                st.error("잘못된 사용자 이름 또는 비밀번호입니다.")
    
    with register_tab:
        register_username = st.text_input("새 사용자 이름", key="register_username")
        register_password = st.text_input("새 비밀번호", type="password", key="register_password")
        if st.button("회원가입", key="register_button"):
            db = next(get_db())
            if db.query(User).filter(User.username == register_username).first():
                st.error("이미 존재하는 사용자 이름입니다.")
            else:
                new_user = User(
                    username=register_username,
                    password_hash=hash_password(register_password)
                )
                db.add(new_user)
                db.commit()
                st.success("회원가입 성공! 로그인해주세요.")

# 감정 선택 페이지
def show_emotion_select_page():
    global emotions  # 전역 변수 emotions 사용
    
    st.title("Mindtone")
    st.write(f"안녕하세요, {st.session_state.username}님! 지금 어떤 감정이 드시나요?")
    
    # 로그아웃 버튼
    if st.button("로그아웃", key="emotion_page_logout"):
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.messages = []
        st.session_state.current_emotion = None
        st.session_state.current_conversation_id = None
        st.session_state.page = 'login'
        st.session_state.show_stats = False
        st.rerun()
    
    # 감정 통계 버튼
    if st.button("감정 분포 보기" if not st.session_state.show_stats else "감정 분포 숨기기"):
        st.session_state.show_stats = not st.session_state.show_stats
        st.rerun()
    
    # 감정 통계 표시
    if st.session_state.show_stats:
        st.subheader("감정 통계")
        db = next(get_db())
        conversations = db.query(Conversation).filter(Conversation.user_id == st.session_state.user_id).all()
        if conversations:
            emotions_list = [conv.emotion for conv in conversations]
            emotion_counts = pd.Series(emotions_list).value_counts()
            fig = px.pie(values=emotion_counts.values, names=emotion_counts.index, title="감정 분포")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("아직 감정 데이터가 없습니다.")
    
    # 감정 버튼 행 생성
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]

    for idx, (emotion, emoji) in enumerate(emotions.items()):
        col_idx = idx % 4
        button_text = f"{emoji} {emotion}"
        
        button_class = "emotion-button"
        
        with cols[col_idx]:
            st.markdown(f'<div class="{button_class}">', unsafe_allow_html=True)
            if st.button(button_text, key=f"emotion_{emotion}"):
                # 새로운 대화 시작
                db = next(get_db())
                new_conversation = Conversation(
                    user_id=st.session_state.user_id,
                    emotion=emotion
                )
                db.add(new_conversation)
                db.commit()
                
                # 세션 상태 업데이트
                st.session_state.current_emotion = emotion
                st.session_state.current_conversation_id = new_conversation.id
                st.session_state.messages = []
                
                # AI의 첫 응답 추가
                ai_first_msg = f"안녕하세요! 오늘 {emotion} 감정을 느끼고 계시는군요. 어떤 일이 있으신가요?"
                st.session_state.messages.append({"role": "assistant", "content": ai_first_msg})
                
                # 메시지 저장
                new_message = Message(
                    conversation_id=st.session_state.current_conversation_id,
                    role="assistant",
                    content=ai_first_msg
                )
                db.add(new_message)
                db.commit()
                
                # 채팅 페이지로 이동
                st.session_state.page = 'chat'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# 채팅 페이지
def show_chat_page():
    global emotions  # 전역 변수 emotions 사용
    
    st.title("Mindtone")
    
    # 탐색 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 감정 선택으로 돌아가기"):
            st.session_state.messages = []
            st.session_state.current_emotion = None
            st.session_state.page = 'emotion_select'
            st.rerun()
    with col2:
        if st.button("로그아웃", key="chat_page_logout"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.messages = []
            st.session_state.current_emotion = None
            st.session_state.current_conversation_id = None
            st.session_state.page = 'login'
            st.session_state.show_stats = False
            st.rerun()
            
    # 현재 선택된 감정 표시
    st.write(f"현재 감정: {emotions[st.session_state.current_emotion]} {st.session_state.current_emotion}")
    
    # 채팅 인터페이스 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input("메시지를 입력하세요"):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        # 메시지 저장
        db = next(get_db())
        new_message = Message(
            conversation_id=st.session_state.current_conversation_id,
            role="user",
            content=prompt
        )
        db.add(new_message)
        
        # AI 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("생각 중..."):
                messages = [
                    {"role": "system", "content": f"""당신은 공감 능력이 뛰어난 정신건강 상담사입니다. 
                    사용자가 '{st.session_state.current_emotion}' 감정을 느끼고 있습니다.
                    
                    상담 지침:
                    1. 사용자의 감정을 먼저 인정하고 공감해주세요.
                    2. 전문적인 용어는 자제하고, 친근하고 부드러운 말투를 사용하세요.
                    3. 사용자의 이야기를 경청하고, 판단하지 않으세요.
                    4. 필요할 때 적절한 위로와 격려를 해주세요.
                    5. 사용자가 스스로 해결책을 찾을 수 있도록 도와주세요.
                    6. 긍정적인 방향으로 대화를 이끌어가되, 무리한 긍정은 피하세요.
                    7. 위험한 상황이 감지되면 전문가 상담을 권유하세요.
                    
                    항상 따뜻하고 이해심 있는 태도로 대화해주세요."""}
                ]
                
                for msg in st.session_state.messages:
                    messages.append(msg)
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                
                ai_response = response.choices[0].message.content
                st.write(ai_response)
                
                # AI 응답 저장
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                new_message = Message(
                    conversation_id=st.session_state.current_conversation_id,
                    role="assistant",
                    content=ai_response
                )
                db.add(new_message)
                db.commit()

# 페이지 라우팅
if st.session_state.user_id is None:
    show_login_page()
elif st.session_state.page == 'emotion_select':
    show_emotion_select_page()
elif st.session_state.page == 'chat':
    show_chat_page() 