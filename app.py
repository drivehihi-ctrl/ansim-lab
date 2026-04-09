import streamlit as st
import google.generativeai as genai
import requests
import re

# 1. 화면 설정
st.set_page_config(page_title="안심이 상세기획 비서", page_icon="🐶")
st.title("🧪 안심이의 상품 연구소")
st.subheader("도매매/오너클랜 상품을 1등 상세페이지로 기획합니다 👓✨")

# 2. 비밀 정보 설정 (Streamlit Secrets 기준)
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
WP_URL = st.secrets["WP_URL"]
WP_USER = st.secrets["WP_USER"]
WP_APP_PW = st.secrets["WP_APP_PW"]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

# 3. 데이터 보관함
if "plan_content" not in st.session_state:
    st.session_state.plan_content = ""

# 4. 입력부 확장 (도매매/오너클랜 정보 입력)
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/dachshund.png")
    st.info("💡 도매처에서 긁어온 원본 정보를 입력해주세요.")
    source_type = st.selectbox("공급처 선택", ["도매매", "오너클랜"])
    original_link = st.text_input("원본 상품 링크", placeholder="https://...")

product_name = st.text_input("분석할 상품명", placeholder="예: [PETLEAD 제외] 강아지 당근밭 노즈워크")
extracted_info = st.text_area("이미지 텍스트 추출 내용 (선택)", placeholder="이미지에서 읽어온 핵심 특징들을 적어주면 더 정확해져요!", height=150)

if st.button("🚀 안심 연구원에게 기획 요청!"):
    if not product_name:
        st.warning("상품명을 입력해주세요!")
    else:
        with st.spinner("수석 연구원 안심이가 상품을 정밀 분석하여 10P 기획서를 작성 중입니다..."):
            
            plan_prompt = f"""
            너는 Magentalab 반려동물 연구소의 수석 연구원, 닥스훈트 '안심이'야.
            이번 연구 과제는 상품명 '{product_name}'의 상세페이지 기획이야.
            참고 정보: {extracted_info}

            [절대 규칙]
            1. 모든 이미지는 실사(Hyper-realistic)여야 하며, 주인공은 '안심이(브라운 닥스훈트 연구원)'야.
            2. 안심이는 뿔테 안경과 흰 가운을 입고 있어야 함.
            3. 기획서는 [1페이지]부터 [10페이지]까지 순서대로 작성해.
            4. 각 페이지는 반드시 아래 형식을 포함해:
               - 안심이의 행동: (구체적인 실사 동작)
               - 배경: (연구소, 거실 등 사실적 배경)
               - 메인카피: (한글로 강렬하게)
               - 서브카피: (한글로 설득력 있게)
               - 영문 프롬프트: (이미지 생성 AI용 영문 묘사. Fujifilm style, 8k 등 포함)
            
            [추가 과업]
            - 토스용 상품명과 올웨이즈용 상품명을 각각 제안해줘.

            결과 형식:
            ---PLAN---
            (여기에 1~10페이지 기획 내용 작성)
            ---TITLE_TOSS---
            토스 상품명
            ---TITLE_ALWAYZ---
            올웨이즈 상품명
            """
            
            try:
                response = model.generate_content(plan_prompt)
                st.session_state.plan_content = response.text
                st.success("기획서 작성이 완료되었습니다!")
            except Exception as e:
                st.error(f"오류가 발생했어요: {e}")

# 5. 결과물 확인 및 워드프레스 전송
if st.session_state.plan_content:
    st.markdown("### 🔍 안심이의 10P 기획서 미리보기")
    st.text_area("기획 데이터", st.session_state.plan_content, height=400)

    if st.button("📦 이 기획서를 워드프레스 작업대로 전송"):
        auth = (WP_USER, WP_APP_PW)
        
        # 데이터 분리
        content = st.session_state.plan_content
        post_title = f"[안심이 기획서] {product_name}"
        
        # 워드프레스 본문 구성 (HTML)
        wp_body = f"""
        <h2>🔗 원본 상품 정보</h2>
        <p><b>공급처:</b> {source_type}</p>
        <p><b>원본링크:</b> <a href='{original_link}'>{original_link}</a></p>
        <hr>
        {content.replace('\n', '<br>')}
        """
        
        payload = {
            "title": post_title,
            "content": wp_body,
            "status": "draft" # 임시글로 전송
        }
        
        res = requests.post(WP_URL, auth=auth, json=payload)
        
        if res.status_code == 201:
            st.balloons()
            st.success("워드프레스에 성공적으로 담았습니다! 이제 블로그에서 보면서 작업하세요!")
