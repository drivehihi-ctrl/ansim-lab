import streamlit as st
import google.generativeai as genai
import requests
import re
import pandas as pd
from io import BytesIO
from PIL import Image

# 1. 화면 설정
st.set_page_config(page_title="안심이 무인 기획 공장 V4.0", page_icon="🕵️‍♂️", layout="wide")
st.title("🧪 안심이의 2026 무인 기획 공장")
st.subheader("Gemini 2.5 Flash 기반 - 0P(대표) + 1~8P 완벽 구조 👓✨")

# 2. 비밀 정보 설정
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    WP_URL = st.secrets["WP_URL"]
    WP_USER = st.secrets["WP_USER"]
    WP_APP_PW = st.secrets["WP_APP_PW"]
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash') 
except KeyError:
    st.error("Secrets 설정 누락! Streamlit Secrets 메뉴를 확인해주세요.")

if "plan_content" not in st.session_state:
    st.session_state.plan_content = ""

# 4. 입력부
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/dachshund.png")
    st.markdown("### 🐾 수석 연구원 안심이 (2.5 Ver.)")
    source_type = st.selectbox("📦 공급처", ["도매매", "오너클랜"])
    original_link = st.text_input("🔗 원본 링크")
    uploaded_file = st.file_uploader("📸 이미지 분석 (방울 등 디테일 필수)", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="안심이가 이 요소를 분석하여 1-3P에 배치합니다.")

product_name = st.text_input("📝 분석할 상품명")
col_a, col_b = st.columns(2)
with col_a:
    paper_strategy = st.text_area("🎯 논문 심리 전략", placeholder="이탈률 방지 등 핵심 마케팅 전략", height=150)
with col_b:
    product_spec = st.text_area("📏 상품 상세 스펙", placeholder="사이즈, 소재 등 왜곡 방지용 정보", height=150)

# --- 기획 시작 ---
if st.button("🚀 Gemini 2.5 정밀 기획 시작! (양식 절대 엄수)"):
    if not product_name:
        st.warning("상품명을 입력해주세요!")
    else:
        with st.spinner("안심이 연구원이 0P부터 8P까지 완벽하게 기획 중입니다..."):
            content_parts = []
            
            # [대표님이 확정한 절대 규칙 및 구조]
            full_prompt = f"""
            너는 Magentalab 연구소의 수석 연구원, 닥스훈트 '안심이'야.
            상품명 '{product_name}'에 전략 '{paper_strategy}'과 스펙 '{product_spec}'을 녹여낸 9단위(대표+8P) 기획서야.

            [지상 과제]
            - 이미지나 스펙에서 발견된 상품의 핵심 장점(예: 딸랑딸랑 방울 소리)은 반드시 1P~3P 이내에 강력하게 배치해.
            - 업로드된 이미지가 있다면, 안심이가 그 이미지 속 디테일을 직접 확인하고 기획에 반영한 카피를 작성해.

            [절대 규칙 - 반드시 준수할 것]
            1. **이미지 주인공:** 모든 연출 이미지(1~8P)에는 안심이(브라운 닥스훈트, 가운, 뿔테안경)가 반드시 등장.
            2. **대표이미지 프롬프트 (0P):** 기획서 맨 앞에 1000x1000 픽셀 기준의 '상품 단독' 프롬프트를 작성해. 텍스트는 절대 금지(No Text). 이 페이지는 1~8P와 별개야.
            3. **사이즈 고정(Size Scaling):** 스펙({product_spec})을 엄격히 참고해 실제 크기가 왜곡되지 않게 주변 사물과 비교하는 묘사를 영문 프롬프트에 명시해.
            4. **한글 카피 강제:** 모든 메인카피와 서브카피는 '무조건 한글'로만 작성해.
            5. **심리 전략 적용:** 논문 전략({paper_strategy})을 마케팅 카피로 승화시키되 자연스럽게 녹여내.
            6. **정보고시 보증 (8P):** 마지막 8페이지는 안심이가 돋보기로 검수하는 이미지와 함께 '상품정보 고시' 표(Table)를 작성해.

            [페이지 구성 및 출력 양식]
            - **대표이미지 프롬프트 (별도):** (1000x1000, No Text 영문 프롬프트)
            - **1P ~ 7P:** - 안심이의 행동:
                - 배경:
                - 한글 메인카피:
                - 한글 서브카피:
                - 영문 프롬프트 (Flow용):
            - **8P (정보고시):** - 안심이의 검수 행동 및 한글 코멘트:
                - 영문 프롬프트:
                - 상품정보 고시 표:

            ---PLAN--- (위 구조대로 상세히 작성)
            ---TITLE_TOSS---
            ---TITLE_ALWAYZ---
            """
            
            content_parts.append(full_prompt)
            if uploaded_file:
                img = Image.open(uploaded_file)
                content_parts.append(img)
            
            try:
                response = model.generate_content(content_parts)
                st.session_state.plan_content = response.text
                st.success("✨ 완벽한 양식으로 기획이 완료되었습니다!")
            except Exception as e:
                st.error(f"오류: {e}")

# 5. 결과 확인 및 전송
if st.session_state.plan_content:
    st.divider()
    
    try:
        toss_title = st.session_state.plan_content.split("---TITLE_TOSS---")[1].split("---TITLE_ALWAYZ---")[0].strip()
        alwayz_title = st.session_state.plan_content.split("---TITLE_ALWAYZ---")[1].strip()
    except:
        toss_title = f"안심이 추천 {product_name}"
        alwayz_title = f"[특가] {product_name}"

    excel_data = {
        "공급처": [source_type], "원본링크": [original_link],
        "네이버_상품명": [toss_title], "토스_상품명": [toss_title], "올웨이즈_상품명": [alwayz_title],
        "판매가": [0], "대표이미지_경로": [f"d:/ansim_test/dome_product/product_main.jpg"],
        "상세이미지_폴더": [f"d:/ansim_test/dome_product/ansim_design/"], "정보고시": ["상세페이지 참조"]
    }
    df = pd.DataFrame(excel_data)
    csv_file = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(label="📊 마켓 데이터 CSV 다운로드", data=csv_file, file_name=f"market_data.csv", mime="text/csv")
    with col2:
        if st.button("📦 워드프레스 전송"):
            auth = (WP_USER, WP_APP_PW)
            wp_body = f"<h2>🎯 마켓 최적화 제목</h2><p>[네이버/토스]: {toss_title}</p><p>[올웨이즈]: {alwayz_title}</p><hr>{st.session_state.plan_content.replace('\n', '<br>')}"
            payload = {"title": f"[최종구조본] {product_name}", "content": wp_body, "status": "draft"}
            res = requests.post(WP_URL, auth=auth, json=payload)
            if res.status_code == 201: st.balloons()

    st.text_area("기획 전문 데이터", st.session_state.plan_content, height=500)
