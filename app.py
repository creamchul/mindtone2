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
    page_icon="��",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 추가
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    * {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .stApp {
        background-color: #f8f9fa;
    }
    
    h1, h2, h3 {
        font-weight: 600 !important;
        color: #333;
    }
    
    .main-title {
        font-size: 2.5rem;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #6b7afc, #9c7af7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }
    
    .emotion-title {
        font-size: 1.8rem;
        margin: 2rem 0 1.5rem;
        text-align: center;
    }
    
    .emotion-container {
        display: flex;
        justify-content: center;
        gap: 12px;
        flex-wrap: wrap;
        margin: 2rem 0;
    }
    
    .emotion-button {
        background-color: white;
        border: none;
        border-radius: 18px;
        padding: 20px 25px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 120px;
    }
    
    .emotion-button:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .emotion-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .emotion-label {
        font-size: 1rem;
        font-weight: 500;
        color: #333;
    }
    
    .card {
        background-color: white;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 24px;
    }
    
    .chat-container {
        height: 450px;
        overflow-y: auto;
        padding: 20px;
        background-color: #f9f9f9;
        border-radius: 18px;
        margin: 20px 0;
        scrollbar-width: thin;
        scrollbar-color: #d1d5db transparent;
    }
    
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: transparent;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background-color: #d1d5db;
        border-radius: 10px;
    }
    
    .message-row {
        display: flex;
        margin-bottom: 15px;
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message-container {
        justify-content: flex-end;
    }
    
    .ai-message-container {
        justify-content: flex-start;
    }
    
    .user-avatar, .ai-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 8px;
        flex-shrink: 0;
    }
    
    .user-avatar {
        background-color: #6b7afc;
        color: white;
        font-size: 16px;
    }
    
    .ai-avatar {
        background-color: #9c7af7;
        color: white;
        font-size: 16px;
    }
    
    .user-bubble {
        background-color: #6b7afc;
        color: white;
        padding: 12px 18px;
        border-radius: 20px 4px 20px 20px;
        max-width: 70%;
        position: relative;
        line-height: 1.5;
        font-size: 1rem;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    
    .ai-bubble {
        background-color: white;
        color: #333;
        padding: 12px 18px;
        border-radius: 4px 20px 20px 20px;
        max-width: 70%;
        position: relative;
        line-height: 1.5;
        font-size: 1rem;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    
    .message-time {
        font-size: 0.7rem;
        color: #999;
        margin-top: 4px;
        text-align: right;
    }
    
    .input-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 20px;
    }
    
    .input-box {
        padding: 16px;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        font-size: 1rem;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        transition: border-color 0.3s;
    }
    
    .input-box:focus {
        border-color: #6b7afc;
        outline: none;
    }
    
    .send-button {
        background-color: #6b7afc;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 18px;
        font-size: 1rem;
        font-weight: 500;
        cursor: pointer;
        transition: background-color 0.3s, transform 0.2s;
        width: 100%;
    }
    
    .send-button:hover {
        background-color: #5868e0;
        transform: translateY(-2px);
    }
    
    .sidebar-content {
        padding: 20px 10px;
    }
    
    .sidebar-title {
        font-weight: 600;
        margin-bottom: 1rem;
        color: #333;
        font-size: 1.2rem;
        padding-bottom: 10px;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .reset-button {
        background-color: #f8f9fa;
        color: #333;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 10px;
        width: 100%;
        margin: 1rem 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .reset-button:hover {
        background-color: #e9ecef;
    }
    
    .tips-card {
        background-color: #f5f7ff;
        border-radius: 16px;
        padding: 20px;
        margin-top: 20px;
        border-left: 4px solid #6b7afc;
    }
    
    .tips-title {
        font-weight: 600;
        color: #333;
        margin-bottom: 10px;
        font-size: 1.2rem;
    }
    
    .tips-item {
        margin: 10px 0;
        padding-left: 10px;
    }
    
    .current-emotion {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 20px 0;
        padding: 10px 15px;
        background-color: #f0f2ff;
        border-radius: 12px;
        width: fit-content;
    }
    
    .current-emotion-icon {
        font-size: 1.5rem;
    }
    
    .current-emotion-text {
        font-weight: 500;
        color: #555;
    }
    
    /* 감정별 색상 */
    .emotion-행복 { color: #FFDE7D; }
    .emotion-슬픔 { color: #9DB4FF; }
    .emotion-화남 { color: #FF9F9F; }
    .emotion-불안 { color: #B69CFF; }
    .emotion-지침 { color: #A0E4B0; }
    
    /* 요소 숨기기 */
    #MainMenu, footer {
        visibility: hidden;
    }

    /* Plotly 그래프 스타일링 */
    .js-plotly-plot .plotly {
        padding: 10px;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        background-color: white;
    }
    
    /* 새로운 스타일 추가 */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #d1d5db;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #9ca3af;
    }
    
    @media (max-width: 768px) {
        .emotion-button {
            width: 100px;
            padding: 15px;
        }
        
        .user-bubble, .ai-bubble {
            max-width: 85%;
        }
    }
</style>
""", unsafe_allow_html=True)

# 감정 이모지 매핑
emotion_emojis = {
    "행복": "😊",
    "슬픔": "😢",
    "화남": "😠",
    "불안": "😰",
    "지침": "😩"
}

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
        # 현재 시간 가져오기
        current_time = datetime.now().strftime("%H:%M")
        
        # 사용자 메시지 추가
        st.session_state.messages.append({
            "role": "user", 
            "content": message,
            "time": current_time
        })
        
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
            st.session_state.messages.append({
                "role": "assistant", 
                "content": ai_response,
                "time": datetime.now().strftime("%H:%M")
            })
        
        except Exception as e:
            st.error(f"OpenAI API 호출 중 오류가 발생했습니다: {e}")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "죄송합니다. 응답을 생성하는 동안 오류가 발생했습니다.",
                "time": datetime.now().strftime("%H:%M")
            })

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
            "content": f"안녕하세요! 오늘 {emotion} 감정을 느끼고 계시는군요. 어떤 일이 있으셨나요?",
            "time": datetime.now().strftime("%H:%M")
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
        
        # 그래프 스타일 업데이트
        fig.update_layout(
            font_family="Noto Sans KR",
            title_font_size=18,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=40, b=10),
            title_x=0.5,
            xaxis=dict(tickfont=dict(size=12)),
            yaxis=dict(tickfont=dict(size=12)),
            height=300
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
        with st.container():
            st.markdown(f"""
            <div class="tips-card">
                <div class="tips-title">💡 도움이 될 만한 팁</div>
            """, unsafe_allow_html=True)
            
            for tip in tips[emotion]:
                st.markdown(f"""
                <div class="tips-item">• {tip}</div>
                """, unsafe_allow_html=True)
                
            st.markdown("""
            </div>
            """, unsafe_allow_html=True)

# 메인 UI
def main():
    # 메인 타이틀
    st.markdown('<h1 class="main-title">🧠 Mindtone - 감정 지원 챗봇</h1>', unsafe_allow_html=True)
    
    # 사이드바
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">📊 내 감정 통계</div>', unsafe_allow_html=True)
        
        # 감정 통계 표시
        show_emotion_stats()
        
        # 대화 초기화 버튼
        if st.button("💫 새 대화 시작", key="reset_btn", help="모든 대화 기록을 초기화합니다"):
            st.session_state.messages = []
            st.session_state.current_emotion = None
            st.experimental_rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 감정 선택 부분
    if st.session_state.current_emotion is None:
        st.markdown('<h2 class="emotion-title">오늘 어떤 기분이신가요?</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="emotion-container">', unsafe_allow_html=True)
        
        # 감정 버튼 생성
        for emotion, emoji in emotion_emojis.items():
            button_html = f"""
            <button class="emotion-button" onclick="parent.postMessage({{msg: '{emotion}'}}, '*')">
                <div class="emotion-icon emotion-{emotion}">{emoji}</div>
                <div class="emotion-label">{emotion}</div>
            </button>
            """
            st.markdown(button_html, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # JavaScript로 버튼 클릭 처리
        st.markdown("""
        <script>
        window.addEventListener('message', function(e) {
            if (e.data.msg) {
                const data = {
                    emotion: e.data.msg
                };
                fetch('', {
                    method: 'POST',
                    body: JSON.stringify(data),
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }).then(response => location.reload());
            }
        });
        </script>
        """, unsafe_allow_html=True)
        
        # 버튼 클릭을 위한 스트림릿 버튼 (대체용)
        cols = st.columns(5)
        with cols[0]:
            if st.button("행복", key="btn_행복", help="행복하고 기쁜 감정", use_container_width=True):
                select_emotion("행복")
                st.experimental_rerun()
        with cols[1]:
            if st.button("슬픔", key="btn_슬픔", help="슬프고 우울한 감정", use_container_width=True):
                select_emotion("슬픔")
                st.experimental_rerun()
        with cols[2]:
            if st.button("화남", key="btn_화남", help="화나고 짜증나는 감정", use_container_width=True):
                select_emotion("화남")
                st.experimental_rerun()
        with cols[3]:
            if st.button("불안", key="btn_불안", help="불안하고 걱정되는 감정", use_container_width=True):
                select_emotion("불안")
                st.experimental_rerun()
        with cols[4]:
            if st.button("지침", key="btn_지침", help="지치고 피곤한 감정", use_container_width=True):
                select_emotion("지침")
                st.experimental_rerun()
                
        # 버튼을 숨김
        st.markdown("""
        <style>
        [data-testid="stButton"] {
            visibility: hidden;
            height: 0px;
            position: absolute;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # 대화 인터페이스
    else:
        # 현재 감정 표시
        emoji = emotion_emojis.get(st.session_state.current_emotion, "")
        st.markdown(f"""
        <div class="current-emotion">
            <span class="current-emotion-icon emotion-{st.session_state.current_emotion}">{emoji}</span>
            <span class="current-emotion-text">현재 감정: {st.session_state.current_emotion}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 팁 표시
        show_emotion_tips(st.session_state.current_emotion)
        
        # 채팅 컨테이너
        st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)
        
        # 메시지 표시
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="message-row user-message-container">
                    <div class="user-bubble">{message["content"]}</div>
                    <div class="user-avatar">나</div>
                </div>
                <div class="message-time" style="text-align: right;">{message.get("time", "")}</div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message-row ai-message-container">
                    <div class="ai-avatar">AI</div>
                    <div class="ai-bubble">{message["content"]}</div>
                </div>
                <div class="message-time" style="text-align: left; margin-left: 50px;">{message.get("time", "")}</div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 자동 스크롤 스크립트
        st.markdown("""
        <script>
            function scrollToBottom() {
                const chatContainer = document.getElementById('chat-container');
                if (chatContainer) {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            }
            
            // 페이지 로드 시 스크롤
            window.addEventListener('load', scrollToBottom);
            
            // 1초 후 다시 스크롤 (컨텐츠가 늦게 로드되는 경우를 위해)
            setTimeout(scrollToBottom, 1000);
        </script>
        """, unsafe_allow_html=True)
        
        # 메시지 입력 폼
        with st.form(key="message_form", clear_on_submit=True):
            user_input = st.text_area("메시지 입력:", height=120, key="user_input", placeholder="메시지를 입력하세요...")
            submit_button = st.form_submit_button("전송")
            
            if submit_button and user_input:
                send_message(user_input, st.session_state.current_emotion)
                st.experimental_rerun()

if __name__ == "__main__":
    main() 