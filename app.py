import streamlit as st
import google.generativeai as genai
import requests
import re
import pandas as pd
from io import BytesIO
from PIL import Image

# 1. 화면 설정
st.set_page_config(page_title="안심이 통합 기획 V2.2", page_icon="🕵️‍♂️", layout="wide")
st.title("🧪 안심이의 정밀 전략 연구소 V2.2")
st.subheader("모든 절대 규칙이 복구된 멀티모달 정밀 기획 시스템 👓✨")

# 2. 비밀 정보 설정
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    WP_URL = st.secrets["WP_URL"]
    WP_USER = st.secrets["WP_USER"]
    WP_APP_PW = st.secrets["WP_APP_PW"]
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except KeyError:
    st.error("Secrets 설정 누락! Streamlit Cloud의 Secrets를 확인해주세요.")

if "plan_content" not in st.session_state:
    st.session_state.plan_content = ""

# 4. 입력부
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/dachshund.png")
    st.markdown("### 🐾 수석 연구원 안심이")
    source_type = st.selectbox("📦 공급처", ["도매매", "오너클랜"])
    original_link = st.text_input("🔗 원본 링크")
    uploaded_file = st.file_uploader("📸 이미지 분석 (방울 등 디테일 컷)", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="안심이가 이 요소를 분석합니다.")

product_name = st.text_input("📝 상품명")
col_a, col_b = st.columns(2)
with col_a:
    paper_strategy = st.text_area("🎯 논문 심리 전략", placeholder="이탈 방지, 트리거 전략 등", height=150)
with col_b:
    product_spec = st.text_area("📏 상품 스펙 (사이즈 필무)", placeholder="정확한 이미지 생성을 위한 실제 사이즈 정보", height=150)

# --- 기획 시작 ---
if st.button("🚀 정밀 기획 및 데이터 생성!"):
    if not product_name:
        st.warning("상품명을 입력해주세요!")
    else:
        with st.spinner("안심이 연구원이 모든 규칙을 준수하여 기획 중입니다..."):
            content_list = []
            
            # 대표님의 '절대 규칙'을 하나하나 다시 다 박아넣었습니다.
            full_prompt = f"""
            너는 Magentalab 연구소의 수석 연구원, 닥스훈트 '안심이'야.
            상품명 '{product_name}'에 전략 '{paper_strategy}'과 스펙 '{product_spec}'을 녹여낸 8P 기획서야.

            [절대 규칙 - 반드시 준수할 것]
            1. **이미지 주인공:** 모든 연출 이미지(1~8P)에는 안심이(브라운 닥스훈트, 가운, 뿔테안경)가 반드시 등장.
            2. **대표이미지 프롬프트:** 기획서 맨 앞에 1000x1000 픽셀 기준의 '상품 단독' 프롬프트를 작성해. 텍스트는 절대 금지(No Text).
            3. **핵심 트리거 전면 배치:** 이미지나 스펙에서 발견된 상품의 최대 장점(예: 방울 소리)은 반드시 1P~3P 이내에 강력하게 배치하여 고객 이탈을 막아.
            4. **사이즈 고정(Size Scaling):** 스펙({product_spec})을 엄격히 참고해. 손바닥 만한 물건이 자동차보다 커 보이는 등 왜곡이 없도록 주변 사물과 비교하는 묘사를 영문 프롬프트에 명시해.
            5. **한글 카피 강제:** 모든 메인카피와 서브카피는 '무조건 한글'로만 작성해. 영어가 섞이지 않게 해.
            6. **심리 전략 적용:** 논문 전략({paper_strategy})을 마케팅 카피로 승화시키되, "논문에 따르면" 같은 딱딱한 표현은 절대 쓰지 마.
            7. **정보고시 보증:** 마지막 8페이지는 안심이가 돋보기로 검수하는 이미지와 함께 '상품정보 고시' 표(Table)를 작성해. 
               (제품유형, 용량, 제조국, 제조사, 수입자, 사이즈, 제조일, 원재료, 영양성분, 상담번호 포함. 모르면 '상품 상단 표기' 기재)

            [페이지 구성]
            - 대표이미지 전용 프롬프트 (No Text)
            - 1P ~ 7P: 안심이의 행동 / 배경 / 한글 메인카피 / 한글 서브카피 / 사이즈 반영된 영문 프롬프트
            - 8P: 안심이의 검수 행동 및 한글 코멘트 / 영문 프롬프트 / 상품정보 고시 표

            결과 형식:
            ---PLAN---
            ---TITLE_TOSS---
            ---TITLE_ALWAYZ---
            """
            
            content_list.append(full_prompt)
            if uploaded_file:
                img = Image.open(uploaded_file)
                content_list.append(img)
            
            try:
                response = model.generate_content(content_list)
                st.session_state.plan_content = response.text
                st.success("✨ 모든 규칙이 반영된 정밀 기획이 완료되었습니다!")
            except Exception as e:
                st.error(f"오류: {e}")

# 5. 결과 및 엑셀/워드프레스 전송 (동일)
if st.session_state.plan_content:
    st.divider()
    
    try:
        toss_title = st.session_state.plan_content.split("---TITLE_TOSS---")[1].split("---TITLE_ALWAYZ---")[0].strip()
        alwayz_title = st.session_state.plan_content.split("---TITLE_ALWAYZ---")[1].strip()
    except:
        toss_title = f"안심이 추천 {product_name}"
        alwayz_title = f"[특가] {product_name}"

    # 엑셀 데이터 생성
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
        st.download_button(label="📊 등록용 CSV 다운로드", data=csv_file, file_name=f"market_data.csv", mime="text/csv")
    with col2:
        if st.button("📦 워드프레스 전송"):
            auth = (WP_USER, WP_APP_PW)
            wp_body = f"<h2>🎯 마켓 최적화 제목</h2><p>[네이버/토스]: {toss_title}</p><p>[올웨이즈]: {alwayz_title}</p><hr>{st.session_state.plan_content.replace('\n', '<br>')}"
            payload = {"title": f"[통합기획] {product_name}", "content": wp_body, "status": "draft"}
            res = requests.post(WP_URL, auth=auth, json=payload)
            if res.status_code == 201: st.balloons()

    st.text_area("기획 전문", st.session_state.plan_content, height=400)
