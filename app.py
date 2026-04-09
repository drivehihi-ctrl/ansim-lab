import streamlit as st
import google.generativeai as genai
import requests
import re
import pandas as pd
from io import BytesIO
from PIL import Image

# 1. 화면 설정 및 스타일
st.set_page_config(page_title="안심이 비서 V2", page_icon="🕵️‍♂️", layout="wide")
st.title("🧪 안심이의 고도화 상품 연구소 V2")
st.subheader("이미지 분석 기능 탑재! 디테일까지 놓치지 않는 정밀 기획 👓✨")

# 2. 비밀 정보 설정 (Streamlit Secrets)
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    WP_URL = st.secrets["WP_URL"]
    WP_USER = st.secrets["WP_USER"]
    WP_APP_PW = st.secrets["WP_APP_PW"]
    
    genai.configure(api_key=GEMINI_API_KEY)
    # 이미지 분석을 위해 gemini-1.5-flash 모델 사용
    model = genai.GenerativeModel('gemini-1.5-flash')
except KeyError:
    st.error("Secrets 설정이 누락되었습니다. Streamlit Cloud 설정에서 API 키들을 확인해주세요.")

# 3. 세션 상태 초기화
if "plan_content" not in st.session_state:
    st.session_state.plan_content = ""

# 4. 입력부
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/dachshund.png")
    st.markdown("### 🐾 수석 연구원 안심이 V2")
    st.info("💡 링크가 읽지 못하는 '방울' 같은 디테일은 사진을 직접 올려주세요!")
    
    source_type = st.selectbox("📦 공급처 선택", ["도매매", "오너클랜"])
    original_link = st.text_input("🔗 원본 상품 링크", placeholder="https://...")
    
    # --- 추가된 이미지 업로드 기능 ---
    uploaded_file = st.file_uploader("📸 분석할 상세이미지 업로드 (방울 등 디테일 컷)", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="안심이가 이 사진을 분석합니다.", use_column_width=True)

product_name = st.text_input("📝 분석할 상품명", placeholder="예: [안심기획] 딸랑이 노즈워크 장난감")

col_a, col_b = st.columns(2)
with col_a:
    paper_strategy = st.text_area("🎯 적용할 논문 속 트리거/심리 전략", 
                                 placeholder="예: 이탈률을 줄이는 첫 3초 시각적 주목도 전략 등", height=150)
with col_b:
    product_spec = st.text_area("📏 상품 상세 스펙 (사이즈, 소재 등 필수)", 
                               placeholder="예: 가로 20cm / 주황색 플라스틱 방울 포함 / 청각 자극 요소", height=150)

# --- 기획 시작 버튼 ---
if st.button("🚀 안심이 정밀 분석 및 기획 시작!"):
    if not product_name:
        st.warning("상품명을 입력해주세요!")
    else:
        with st.spinner("수석 연구원 안심이가 이미지를 분석하고 기획서를 작성 중입니다..."):
            
            # 메시지 구성 (이미지 포함 여부에 따라 다름)
            content_list = []
            
            # 이미지 분석 가이드 포함
            prompt_main = f"""
            너는 Magentalab 연구소의 수석 연구원, 닥스훈트 '안심이'야.
            상품명 '{product_name}'을 분석해. 
            심리전략: '{paper_strategy}'
            상세스펙: '{product_spec}'

            [업로드된 이미지 분석 요청]
            만약 이미지가 제공되었다면, 이미지 속의 특이점(예: 방울, 특수 소재, 디자인 디테일)을 반드시 파악해서 기획에 반영해. 
            방울이 있다면 '청각적 자극'과 '호기심 유발'을 핵심 카피로 사용해.

            [절대 규칙]
            1. 모든 연출 이미지에는 안심이(브라운 닥스훈트, 가운, 뿔테안경)가 반드시 등장.
            2. 대표이미지(1000x1000): 상품 단독 프롬프트 (No Text).
            3. 사이즈 고정: {product_spec}을 참고해 왜곡 방지.
            4. 한글 카피 강제: 메인/서브카피 무조건 한글.
            5. 심리 트리거: 논문 전략({paper_strategy})을 이탈 방지용 카피로 승화.
            6. 8P 정보고시: 안심이 검수 이미지 + 표 포함.

            ---PLAN--- (8페이지 분량)
            ---TITLE_TOSS---
            ---TITLE_ALWAYZ---
            """
            
            content_list.append(prompt_main)
            
            # 파일이 업로드되었다면 이미지 객체를 리스트에 추가
            if uploaded_file:
                img = Image.open(uploaded_file)
                content_list.append(img)
            
            try:
                # 텍스트와 이미지를 동시에 모델에 전달 (멀티모달)
                response = model.generate_content(content_list)
                st.session_state.plan_content = response.text
                st.success("✨ 이미지를 포함한 정밀 기획이 완료되었습니다!")
            except Exception as e:
                st.error(f"분석 오류 발생: {e}")

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
        "공급처": [source_type],
        "원본링크": [original_link],
        "네이버_상품명": [toss_title],
        "토스_상품명": [toss_title],
        "올웨이즈_상품명": [alwayz_title],
        "판매가": [0],
        "대표이미지_경로": [f"d:/ansim_test/dome_product/product_main.jpg"],
        "상세이미지_폴더": [f"d:/ansim_test/dome_product/ansim_design/"],
        "정보고시": ["상세페이지 참조"]
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
            payload = {"title": f"[V2-정밀기획] {product_name}", "content": wp_body, "status": "draft"}
            res = requests.post(WP_URL, auth=auth, json=payload)
            if res.status_code == 201: st.balloons()

    with st.expander("🔍 안심이의 V2 기획 전문 보기", expanded=True):
        st.write(st.session_state.plan_content)
