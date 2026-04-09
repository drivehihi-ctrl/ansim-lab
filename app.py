import streamlit as st
import google.generativeai as genai
import requests
import re
import pandas as pd
from io import BytesIO
from PIL import Image

# 1. 화면 설정
st.set_page_config(page_title="안심이 무인 기획 공장 V4.3", page_icon="🕵️‍♂️", layout="wide")
st.title("🧪 안심이의 2026 무인 기획 공장 V4.3")
st.subheader("모든 절대 규칙 100% 복원 및 로봇 데이터 구조 통합판 👓✨")

# 2. 비밀 정보 설정 (Streamlit Secrets)
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    WP_URL = st.secrets["WP_URL"]
    WP_USER = st.secrets["WP_USER"]
    WP_APP_PW = st.secrets["WP_APP_PW"]
    genai.configure(api_key=GEMINI_API_KEY)
    # 대표님 대시보드의 최신 엔진 호출
    model = genai.GenerativeModel('gemini-2.5-flash') 
except KeyError:
    st.error("Secrets 설정 누락! Streamlit Cloud의 Secrets 메뉴를 확인해주세요.")

if "plan_content" not in st.session_state:
    st.session_state.plan_content = ""

# 4. 입력부 (사이드바 - 로봇 데이터 입력칸 추가)
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/dachshund.png")
    st.markdown("### 🐾 로봇 입력용 데이터 세팅")
    
    source_type = st.selectbox("📦 공급처", ["도매매", "오너클랜"])
    original_link = st.text_input("🔗 원본 링크")
    
    # 💡 로봇이 네이버/토스에 입력할 필수 데이터
    category_id = st.text_input("📁 카테고리 (로봇 입력용)", "반려동물 용품")
    final_price = st.number_input("💰 판매가 (로봇 입력용)", value=15000, step=100)
    
    uploaded_file = st.file_uploader("📸 이미지 분석 (디테일 컷)", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="안심이가 이 요소를 1-3P에 배치합니다.")

product_name = st.text_input("📝 분석할 상품명")
col_a, col_b = st.columns(2)
with col_a:
    paper_strategy = st.text_area("🎯 논문 심리 전략", placeholder="이탈률 방지 등 핵심 전략", height=150)
with col_b:
    product_spec = st.text_area("📏 상품 상세 스펙", placeholder="사이즈, 소재 등 왜곡 방지용 정보", height=150)

# --- 기획 시작 ---
if st.button("🚀 Gemini 2.5 정밀 기획 시작! (양식 절대 엄수)"):
    if not product_name:
        st.warning("상품명을 입력해주세요!")
    else:
        with st.spinner("안심이 연구원이 0P부터 8P까지 완벽하게 기획 중입니다..."):
            content_parts = []
            
            # [대표님 지식란 원본 규칙 100% 복사]
            full_prompt = f"""
            너는 Magentalab 연구소의 수석 연구원, 닥스훈트 '안심이'야.
            상품명 '{product_name}'에 전략 '{paper_strategy}'과 스펙 '{product_spec}'을 녹여낸 9단위(대표+8P) 기획서야.

            [지상 과제]
            - 이미지나 스펙에서 발견된 상품의 핵심 장점(예: 딸랑딸랑 방울 소리)은 반드시 1P~3P 이내에 강력하게 배치해.
            - 업로드된 이미지가 있다면, 안심이가 그 이미지 속 디테일을 직접 확인하고 기획에 반영한 카피를 작성해.

            [절대 규칙 - 반드시 준수할 것]
            1. **이미지 주인공:** 모든 연출 이미지(1~8P)에는 안심이(브라운 닥스훈트, 가운, 뿔테안경)가 반드시 등장.
            2. **대표이미지 프롬프트 (0P):** 기획서 맨 앞에 1000x1000 픽셀 기준의 '상품 단독' 프롬프트를 작성해. 텍스트는 절대 금지(No Text). 이 페이지는 1~8P와 별개야.
            3. **핵심 트리거 전면 배치:** 이미지나 스펙에서 발견된 상품의 최대 장점(예: 방울 소리)은 반드시 1P~3P 이내에 강력하게 배치하여 고객 이탈을 막아.
            4. **사이즈 고정(Size Scaling):** 스펙({product_spec})을 엄격히 참고해. 손바닥 만한 물건이 자동차보다 커 보이는 등 왜곡이 없도록 주변 사물과 비교하는 묘사를 영문 프롬프트에 명시해.
            5. **한글 카피 강제:** 모든 메인카피와 서브카피는 '무조건 한글'로만 작성해. 영어가 섞이지 않게 해.
            6. **심리 전략 적용:** 논문 전략({paper_strategy})을 마케팅 카피로 승화시키되, "논문에 따르면" 같은 딱딱한 표현은 절대 쓰지 마.
            7. **정보고시 보증:** 마지막 8페이지는 안심이가 돋보기로 검수하는 이미지와 함께 '상품정보 고시' 표(Table)를 작성해. 
               (제품유형, 용량, 제조국, 제조사, 수입자, 사이즈, 제조일, 원재료, 영양성분, 상담번호 포함. 모르면 '상품 상단 표기' 기재)

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

            ---PLAN---
            ---TITLE_TOSS---
            (네이버/토스용 한 줄 제목)
            ---TITLE_ALWAYZ---
            (올웨이즈용 한 줄 제목)
            """
            
            content_parts.append(full_prompt)
            if uploaded_file:
                img = Image.open(uploaded_file)
                content_parts.append(img)
            
            try:
                response = model.generate_content(content_parts)
                st.session_state.plan_content = response.text
                st.success("✨ 기획 완료! 데이터가 생성되었습니다.")
            except Exception as e:
                st.error(f"오류: {e}")

# 5. 결과 확인 및 [로봇 데이터 추출]
if st.session_state.plan_content:
    st.divider()
    
    # 💡 엑셀 데이터 정제를 위한 정밀 추출
    toss_match = re.search(r"---TITLE_TOSS---(.*?)---TITLE_ALWAYZ---", st.session_state.plan_content, re.DOTALL)
    alwayz_match = re.search(r"---TITLE_ALWAYZ---(.*)", st.session_state.plan_content, re.DOTALL)
    
    clean_toss_title = toss_match.group(1).strip() if toss_match else f"안심이 추천 {product_name}"
    clean_alwayz_title = alwayz_match.group(1).strip() if alwayz_match else f"[특가] {product_name}"

    # 💡 [로봇이 읽을 데이터 구조] - 대표님 지식란 사양 100% 적용
    excel_data = {
        "카테고리": [category_id],
        "네이버_상품명": [clean_toss_title],
        "토스_상품명": [clean_toss_title],
        "올웨이즈_상품명": [clean_alwayz_title],
        "판매가": [final_price],
        "공급처": [source_type],
        "원본링크": [original_link],
        "대표이미지_경로": [f"d:/ansim_test/dome_product/product_main.jpg"],
        "상세이미지_폴더": [f"d:/ansim_test/dome_product/ansim_design/"],
        "정보고시": ["상세페이지 참조"]
    }
    
    df = pd.DataFrame(excel_data)
    csv_file = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(label="📊 로봇 업로드용 CSV 다운로드", data=csv_file, file_name=f"market_data.csv", mime="text/csv")
    with col2:
        if st.button("📦 워드프레스 전송"):
            auth = (WP_USER, WP_APP_PW)
            wp_body = f"<h2>🎯 마켓 제목</h2><p>[네이버/토스]: {clean_toss_title}</p><p>[올웨이즈]: {clean_alwayz_title}</p><hr>{st.session_state.plan_content.replace('\n', '<br>')}"
            payload = {"title": f"[최종본] {product_name}", "content": wp_body, "status": "draft"}
            res = requests.post(WP_URL, auth=auth, json=payload)
            if res.status_code == 201: st.balloons()

    st.text_area("기획 전문 데이터", st.session_state.plan_content, height=500)
