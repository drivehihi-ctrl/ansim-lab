import streamlit as st
import google.generativeai as genai
import requests
import re

# 1. 화면 설정
st.set_page_config(page_title="안심이 심리 기획 비서", page_icon="🎯")
st.title("🧪 안심이의 구매 트리거 연구소")
st.subheader("논문의 심리 전략을 녹여 이탈 없는 상세페이지를 만듭니다 👓✨")

# 2. 비밀 정보 설정
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
WP_URL = st.secrets["WP_URL"]
WP_USER = st.secrets["WP_USER"]
WP_APP_PW = st.secrets["WP_APP_PW"]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

if "plan_content" not in st.session_state:
    st.session_state.plan_content = ""

# 4. 입력부
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/dachshund.png")
    st.info("💡 상품 정보와 적용할 심리 트리거(논문 내용)를 넣어주세요.")
    source_type = st.selectbox("공급처 선택", ["도매매", "오너클랜"])
    original_link = st.text_input("원본 상품 링크")

product_name = st.text_input("분석할 상품명")
# 🎯 논문의 핵심 트리거 전략 입력 (예: 희소성, 사회적 증거, 시각적 주목도 등)
paper_strategy = st.text_area("🎯 적용할 논문 속 트리거 전략", placeholder="예: 첫 3초 안에 시선을 끄는 법, 이탈을 막는 보상 체계 등 논문의 핵심 전략을 적어주세요.", height=150)

if st.button("🚀 심리 트리거 기획 시작!"):
    if not product_name:
        st.warning("상품명을 입력해주세요!")
    else:
        with st.spinner("수석 연구원 안심이가 고객의 마음을 훔칠 기획서를 작성 중입니다..."):
            
            # 💡 "논문에 따르면" 금지령을 내린 프롬프트
            plan_prompt = f"""
            너는 Magentalab 연구소의 수석 연구원, 닥스훈트 '안심이'야.
            이번 과제는 상품 '{product_name}'에 논문의 심리 트리거 전략 '{paper_strategy}'을 녹여낸 8P 기획이야.

            [지상 과제]
            - 절대로 "논문에 따르면", "연구 결과에 의하면" 같은 딱딱한 표현을 쓰지 마.
            - 대신 논문의 전략({paper_strategy})을 고객의 '구매 본능'을 자극하는 카피와 구성으로 치환해.
            - 예: '시각적 주목도 전략' -> '눈을 뗄 수 없는 화려한 연출', '손실 회피 전략' -> '지금 놓치면 후회할 구성'

            [절대 규칙]
            1. 이미지는 실사(Hyper-realistic)이며, 주인공은 안심이(브라운 닥스훈트 연구원)야.
            2. 기획서는 [1페이지]부터 [8페이지]까지 작성해.
            3. **메인카피와 서브카피는 무조건 한글로만 작성해.** (영어가 섞이지 않게 주의)
            4. 각 페이지는 고객이 다음 페이지를 보지 않고는 못 배기게 만드는 '트리거'를 하나씩 배치해.
            
            [페이지 구성 필수 양식]
            - 안심이의 행동: 
            - 배경: 
            - 메인카피(한글): 
            - 서브카피(한글): 
            - 영문 프롬프트: (Flow 생성용. Fujifilm style, 8k 포함)

            결과 형식:
            ---PLAN---
            (1~8페이지 내용)
            ---TITLE_TOSS---
            ---TITLE_ALWAYZ---
            """
            
            try:
                response = model.generate_content(plan_prompt)
                st.session_state.plan_content = response.text
                st.success("심리 기획 완료! 워드프레스로 보낼 준비가 됐습니다.")
            except Exception as e:
                st.error(f"오류 발생: {e}")

# 5. 결과 확인 및 워드프레스 전송
if st.session_state.plan_content:
    st.markdown("### 🎯 고객의 마음을 훔치는 8P 기획서")
    st.text_area("기획 데이터", st.session_state.plan_content, height=400)

    if st.button("📦 워드프레스 작업대로 전송"):
        auth = (WP_USER, WP_APP_PW)
        wp_body = f"""
        <h2>🎯 심리 트리거 기반 전략 기획</h2>
        <p><b>상품명:</b> {product_name}</p>
        <p><b>적용 전략:</b> {paper_strategy}</p>
        <p><b>원본링크:</b> <a href='{original_link}'>{original_link}</a></p>
        <hr>
        {st.session_state.plan_content.replace('\n', '<br>')}
        """
        payload = {"title": f"[트리거기획] {product_name}", "content": wp_body, "status": "draft"}
        res = requests.post(WP_URL, auth=auth, json=payload)
        if res.status_code == 201:
            st.balloons()
