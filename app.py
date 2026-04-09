import streamlit as st
import google.generativeai as genai
import requests
import re

# 1. 화면 설정
st.set_page_config(page_title="안심이 통합 기획 비서", page_icon="🎯")
st.title("🧪 안심이의 고도화 상품 연구소")
st.subheader("심리 전략과 과학적 수치를 결합한 8P 기획서 👓✨")

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
    st.info("💡 상품 정보와 심리 전략, 그리고 논문 내용을 입력해주세요.")
    source_type = st.selectbox("공급처 선택", ["도매매", "오너클랜"])
    original_link = st.text_input("원본 상품 링크")

product_name = st.text_input("분석할 상품명")
paper_strategy = st.text_area("🎯 적용할 논문 속 트리거/심리 전략", placeholder="예: 시각적 주목도, 손실 회피 등 논문에서 읽은 전략을 적어주세요.", height=100)
product_spec = st.text_area("📏 상품 상세 스펙 (사이즈, 소재 등)", placeholder="예: 20cm x 15cm, 폴라폴리스 소재 등. 정확한 이미지 생성을 위해 꼭 필요해요!")

if st.button("🚀 안심이 통합 기획 시작!"):
    if not product_name:
        st.warning("상품명을 입력해주세요!")
    else:
        with st.spinner("수석 연구원 안심이가 정밀 기획서를 작성 중입니다..."):
            
            plan_prompt = f"""
            너는 Magentalab 연구소의 수석 연구원, 닥스훈트 '안심이'야.
            상품명 '{product_name}'에 전략 '{paper_strategy}'과 스펙 '{product_spec}'을 녹여낸 8P 기획서야.

            [절대 규칙 - 추가 사항 반영]
            1. **대표이미지 전용 프롬프트:** 기획서 맨 앞 혹은 별도 섹션에 1000x1000 픽셀 기준의 '상품 단독' 이미지 프롬프트를 작성해. 텍스트는 절대 포함하지 말고 상품 자체의 질감과 형태만 강조해.
            2. **상품정보 고시 표:** 마지막 8페이지는 반드시 '상품정보 고시'를 표(Table) 형태로 작성해. (제품유형, 용량, 제조국, 제조사, 수입자, 사이즈, 제조일/유통기한, 원재료, 영양성분, 상담번호 등 포함). 내용 확인이 안 되면 '상품 상단 표기'라고 적어.
            3. **사이즈 고정(Size Scaling):** 모든 이미지 프롬프트 작성 시, 상품 스펙({product_spec})을 반드시 참고해. 손바닥 만한 물건이 자동차만큼 커 보이는 등의 왜곡이 절대 없도록 배경 사물과 비교해 크기를 명시해.
            4. **한글 카피 강제:** 메인카피와 서브카피는 무조건 한글로만 작성해.
            5. **주인공 고정:** 모든 연출 이미지에는 안심이(브라운 닥스훈트, 가운, 뿔테안경)가 등장해야 해.
            6. **심리 트리거:** 논문 전략({paper_strategy})을 카피에 자연스럽게 녹여 이탈률을 방지해.

            [페이지 구성]
            - 대표이미지 프롬프트 (1000x1000, No Text)
            - 1P ~ 7P: 행동/배경/한글 메인/한글 서브/사이즈가 반영된 영문 프롬프트
            - 8P: 상품정보 고시 표

            결과 형식:
            ---PLAN---
            ---TITLE_TOSS---
            ---TITLE_ALWAYZ---
            """
            
            try:
                response = model.generate_content(plan_prompt)
                st.session_state.plan_content = response.text
                st.success("기획서 작성이 완료되었습니다!")
            except Exception as e:
                st.error(f"오류 발생: {e}")

# 5. 결과 확인 및 워드프레스 전송
if st.session_state.plan_content:
    st.markdown("### 🔍 안심이의 정밀 8P 기획서")
    st.text_area("기획 데이터", st.session_state.plan_content, height=400)

    if st.button("📦 워드프레스 작업대로 전송"):
        auth = (WP_USER, WP_APP_PW)
        wp_body = f"""
        <h2>🎯 정밀 전략 기획 보고서</h2>
        <p><b>공급처:</b> {source_type} | <b>링크:</b> <a href='{original_link}'>{original_link}</a></p>
        <p><b>입력된 스펙:</b> {product_spec}</p>
        <hr>
        {st.session_state.plan_content.replace('\n', '<br>')}
        """
        payload = {"title": f"[정밀기획] {product_name}", "content": wp_body, "status": "draft"}
        res = requests.post(WP_URL, auth=auth, json=payload)
        if res.status_code == 201:
            st.balloons()
            st.success("워드프레스로 전송 완료! 작업대에서 확인하세요.")
