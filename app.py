import streamlit as st
import google.generativeai as genai
import requests
import re
import pandas as pd
from io import BytesIO
from PIL import Image

# 1. 화면 설정 및 스타일
st.set_page_config(page_title="안심이 비서 V2.1", page_icon="🎯", layout="wide")
st.title("🧪 안심이의 고도화 상품 연구소 V2.1")
st.subheader("핵심 트리거(방울 등) 전면 배치! 이탈 방지형 정밀 기획 👓✨")

# 2. 비밀 정보 설정 (Streamlit Secrets)
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    WP_URL = st.secrets["WP_URL"]
    WP_USER = st.secrets["WP_USER"]
    WP_APP_PW = st.secrets["WP_APP_PW"]
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except KeyError:
    st.error("Secrets 설정이 누락되었습니다. Streamlit Cloud 설정에서 API 키들을 확인해주세요.")

# 3. 세션 상태 초기화
if "plan_content" not in st.session_state:
    st.session_state.plan_content = ""

# 4. 입력부
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/dachshund.png")
    st.markdown("### 🐾 수석 연구원 안심이 V2.1")
    st.info("💡 이미지 속 '방울' 같은 핵심 장점은 기획서 앞부분에 배치됩니다!")
    
    source_type = st.selectbox("📦 공급처 선택", ["도매매", "오너클랜"])
    original_link = st.text_input("🔗 원본 상품 링크", placeholder="https://...")
    
    uploaded_file = st.file_uploader("📸 디테일 컷 업로드 (방울 소리 등 핵심 강조용)", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="안심이가 이 요소를 초반에 배치합니다.", use_column_width=True)

product_name = st.text_input("📝 분석할 상품명", placeholder="예: [안심기획] 딸랑이 노즈워크")

col_a, col_b = st.columns(2)
with col_a:
    paper_strategy = st.text_area("🎯 적용할 논문 속 트리거/심리 전략", 
                                 placeholder="예: 첫 3초 시각적 주목도, 손실 회피 등", height=150)
with col_b:
    product_spec = st.text_area("📏 상품 상세 스펙 (사이즈, 소재 등)", 
                               placeholder="예: 가로 20cm / 주황색 방울 포함 / 소리 나는 장난감", height=150)

# --- 기획 시작 버튼 ---
if st.button("🚀 안심이 정밀 전략 기획 시작!"):
    if not product_name:
        st.warning("상품명을 입력해주세요!")
    else:
        with st.spinner("수석 연구원 안심이가 핵심 소구점을 전면에 배치한 기획서를 작성 중입니다..."):
            
            content_list = []
            
            # 전략적 프롬프트 수정
            prompt_main = f"""
            너는 Magentalab 연구소의 수석 연구원, 닥스훈트 '안심이'야.
            상품명 '{product_name}'을 분석하여 8P 기획서를 작성해.

            [핵심 기획 전략]
            1. **트리거 전면 배치:** 이미지나 스펙에서 발견된 핵심 장점(예: 딸랑딸랑 소리 나는 방울)은 반드시 1P~3P 이내에 강력하게 노출해. 고객의 이탈을 막기 위해 초반에 시청각적 자극을 극대화할 것.
            2. **심리 전략 적용:** 논문 전략({paper_strategy})을 활용해 첫 페이지부터 구매 욕구를 자극해.
            3. **사이즈 현실감:** 스펙({product_spec})을 반영해 실제 크기가 체감되도록 배경을 설정해.

            [절대 규칙]
            - 모든 이미지에는 안심이(닥스훈트 연구원) 등장.
            - 메인/서브카피는 '무조건 한글'.
            - 대표이미지(1000x1000): 상품 단독, No Text.
            - 8P: 상품정보 고시 표와 안심이의 검수 코멘트.

            ---PLAN--- (1~8페이지 순서대로)
            ---TITLE_TOSS---
            ---TITLE_ALWAYZ---
            """
            
            content_list.append(prompt_main)
            if uploaded_file:
                img = Image.open(uploaded_file)
                content_list.append(img)
            
            try:
                response = model.generate_content(content_list)
                st.session_state.plan_content = response.text
                st.success("✨ 핵심 소구점이 반영된 기획이 완료되었습니다!")
            except Exception as e:
                st.error(f"분석 오류: {e}")

# 5. 결과 표시 및 데이터 추출 (동일)
if st.session_state.plan_content:
    st.divider()
    
    try:
        toss_title = st.session_state.plan_content.split("---TITLE_TOSS---")[1].split("---TITLE_ALWAYZ---")[0].strip()
        alwayz_title = st.session_state.plan_content.split("---TITLE_ALWAYZ---")[1].strip()
    except:
        toss_title = f"안심이 추천 {product_name}"
        alwayz_title = f"[연구소특가] {product_name}"

    st.markdown("### 💾 마켓 등록용 데이터 및 전송")
    
    excel_data = {
        "공급처": [source_type], "원본링크": [original_link],
        "네이버_상품명": [toss_title], "토스_상품명": [toss_title], "올웨이즈_상품명": [alwayz_title],
        "판매가": [0], "대표이미지_경로": [f"d:/ansim_test/dome_product/product_main.jpg"],
        "상세이미지_폴더": [f"d:/ansim_test/dome_product/ansim_design/"], "정보고시": ["상세페이지 참조"]
    }
    
    df = pd.DataFrame(excel_data)
    csv_file = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.download_button(label="📊 등록용 CSV 다운로드", data=csv_file, file_name=f"market_upload.csv", mime="text/csv")

    with btn_col2:
        if st.button("📦 워드프레스 작업대로 전송"):
            auth = (WP_USER, WP_APP_PW)
            wp_body = f"<h2>🎯 마켓 최적화 제목</h2><p>[네이버/토스]: {toss_title}</p><p>[올웨이즈]: {alwayz_title}</p><hr>{st.session_state.plan_content.replace('\n', '<br>')}"
            payload = {"title": f"[V2.1-전략기획] {product_name}", "content": wp_body, "status": "draft"}
            res = requests.post(WP_URL, auth=auth, json=payload)
            if res.status_code == 201: st.balloons()

    with st.expander("🔍 안심이의 전략 기획 전문 보기", expanded=True):
        st.write(st.session_state.plan_content)
