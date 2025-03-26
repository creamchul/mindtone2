import streamlit as st
import openai
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# 페이지 설정
st.set_page_config(
    page_title="Mindtone - 감정 지원 챗봇",
    page_icon="🧠",
    layout="wide"
)

# CSS 스타일 추가
st.markdown("""
<style>
    .user-bubble {
        background-color: #E0E0FE;
        padding: 10px 15px;
        border-radius: 20px 20px 5px 20px;
        margin: 5px 0;
        display: inline-block;
        max-width: 80%;
        float: right;
        clear: both;
    }
    
    .ai-bubble {
        background-color: #F0F0F0;
        padding: 10px 15px;
        border-radius: 20px 20px 20px 5px;
        margin: 5px 0;
        display: inline-block;
        max-width: 80%;
        float: left;
        clear: both;
    }
    
    .emotion-button {
        border-radius: 15px;
        padding: 15px 20px;
        margin: 5px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .emotion-button:hover {
        transform: scale(1.05);
    }
    
    .chat-container {
        overflow-y: auto;
        height: 400px;
        padding: 10px;
        background-color: #FFFFFF;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    
    .clearfix::after {
        content: "";
        clear: both;
        display: table;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_emotion' not in st.session_state:
    st.session_state.current_emotion = None

if 'emotion_history' not in st.session_state:
    st.session_state.emotion_history = []

# 사용자 메시지 전송 함수
def send_message(message, emotion):
    if message:
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": message})
        
        # OpenAI API를 통해 응답 생성
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"당신은 사용자의 {emotion} 감정을 공감하고 지원하는 상담사입니다. 사용자의 감정에 맞게 공감적이고 도움이 되는 대화를 나누세요. 답변은 간결하게 1-2문장으로 작성하세요."},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ]
            )
            
            # AI 응답 추가
            ai_response = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        except Exception as e:
            st.error(f"OpenAI API 호출 중 오류가 발생했습니다: {e}")
            st.session_state.messages.append({"role": "assistant", "content": "죄송합니다. 응답을 생성하는 동안 오류가 발생했습니다."})

# 감정 선택 함수
def select_emotion(emotion):
    st.session_state.current_emotion = emotion
    
    # 감정 기록에 현재 감정과 시간 저장
    st.session_state.emotion_history.append({
        "emotion": emotion,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    
    # 새 대화 시작 메시지
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"안녕하세요! 오늘 {emotion} 감정을 느끼고 계시는군요. 어떤 일이 있으셨나요?"
        })

# 감정 통계 표시 함수
def show_emotion_stats():
    if st.session_state.emotion_history:
        # 데이터프레임 생성
        df = pd.DataFrame(st.session_state.emotion_history)
        
        # 감정별 빈도수 계산
        emotion_counts = df['emotion'].value_counts().reset_index()
        emotion_counts.columns = ['감정', '횟수']
        
        # 그래프 생성
        fig = px.bar(
            emotion_counts, 
            x='감정', 
            y='횟수',
            title='나의 감정 통계',
            color='감정',
            color_discrete_map={
                "행복": "#FFDE7D",
                "슬픔": "#9DB4FF",
                "화남": "#FF9F9F",
                "불안": "#B69CFF",
                "지침": "#A0E4B0"
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("아직 감정 기록이 없습니다.")

# 감정별 팁 제공 함수
def show_emotion_tips(emotion):
    tips = {
        "행복": [
            "행복한 순간을 일기에 기록해보세요.",
            "주변 사람들과 기쁨을 나누어 보세요.",
            "감사한 일 3가지를 생각해보세요."
        ],
        "슬픔": [
            "자신의 감정을 부정하지 말고 충분히 느껴보세요.",
            "믿을 수 있는 사람에게 감정을 표현해보세요.",
            "명상을 통해 마음을 진정시켜보세요."
        ],
        "화남": [
            "깊게 심호흡을 10번 해보세요.",
            "잠시 자리를 떠나 산책해보세요.",
            "감정을 글로 표현해보세요."
        ],
        "불안": [
            "5-4-3-2-1 기법: 보이는 것 5가지, 들리는 것 4가지, 느껴지는 것 3가지, 냄새 2가지, 맛 1가지를 의식해보세요.",
            "규칙적인 호흡으로 마음을 안정시켜보세요.",
            "불안한 생각을 객관적으로 바라보세요."
        ],
        "지침": [
            "짧은 낮잠(20-30분)이 도움이 될 수 있어요.",
            "가벼운 스트레칭을 해보세요.",
            "충분한 물을 마시고 건강한 간식을 드세요."
        ]
    }
    
    if emotion in tips:
        st.markdown("### 도움이 될 만한 팁")
        for tip in tips[emotion]:
            st.markdown(f"- {tip}")

# 메인 UI
def main():
    st.title("🧠 Mindtone - 감정 지원 챗봇")
    
    # 사이드바
    with st.sidebar:
        st.header("내 감정 기록")
        
        # 감정 통계 표시
        show_emotion_stats()
        
        # 대화 초기화 버튼
        if st.button("새 대화 시작"):
            st.session_state.messages = []
            st.session_state.current_emotion = None
            st.experimental_rerun()
    
    # 감정 선택 부분
    if st.session_state.current_emotion is None:
        st.markdown("### 지금 기분이 어떠신가요?")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("😊 행복", key="happy", help="행복하고 기쁜 감정", 
                        use_container_width=True):
                select_emotion("행복")
        
        with col2:
            if st.button("😢 슬픔", key="sad", help="슬프고 우울한 감정", 
                        use_container_width=True):
                select_emotion("슬픔")
        
        with col3:
            if st.button("😠 화남", key="angry", help="화나고 짜증나는 감정", 
                        use_container_width=True):
                select_emotion("화남")
        
        with col4:
            if st.button("😰 불안", key="anxious", help="불안하고 걱정되는 감정", 
                        use_container_width=True):
                select_emotion("불안")
        
        with col5:
            if st.button("😩 지침", key="tired", help="지치고 피곤한 감정", 
                        use_container_width=True):
                select_emotion("지침")
    
    # 대화 인터페이스
    else:
        st.markdown(f"### 현재 감정: {st.session_state.current_emotion}")
        
        # 팁 표시
        show_emotion_tips(st.session_state.current_emotion)
        
        # 채팅 컨테이너
        chat_container = st.container()
        
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # 메시지 표시
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f'<div class="clearfix"><div class="user-bubble">{message["content"]}</div></div>', 
                                unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="clearfix"><div class="ai-bubble">{message["content"]}</div></div>', 
                                unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 메시지 입력
        with st.form(key="message_form", clear_on_submit=True):
            user_input = st.text_area("메시지 입력:", height=100)
            submit_button = st.form_submit_button("전송")
            
            if submit_button and user_input:
                send_message(user_input, st.session_state.current_emotion)
                st.experimental_rerun()

if __name__ == "__main__":
    main() 