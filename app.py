import streamlit as st
import google.generativeai as genai
import requests
import re
import pandas as pd
from io import BytesIO

# 1. 화면 설정 및 스타일
st.set_page_config(page_title="안심이 통합 기획 비서", page_icon="🎯", layout="wide")
st.title("🧪 안심이의 고도화 상품 연구소")
st.subheader("심리 전략과 데이터가 결합된 1등 상세페이지 제작소 👓✨")

# 2. 비밀 정보 설정 (Streamlit Secrets)
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    WP_URL = st.secrets["WP_URL"]
    WP_USER = st.secrets["WP_USER"]
    WP_APP_PW = st.secrets["WP_APP_PW"]
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')
except KeyError:
    st.error("Secrets 설정이 누락되었습니다. Streamlit Cloud 설정에서 API 키들을 확인해주세요.")

# 3. 세션 상태 초기화
if "plan_content" not in st.session_state:
    st.session_state.plan_content = ""

# 4. 입력부 (사이드바 및 메인)
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/dachshund.png")
    st.markdown("### 🐾 수석 연구원 안심이")
    st.info("💡 상품 정보와 심리 전략을 입력하면 안심이가 기획을 시작합니다.")
    
    source_type = st.selectbox("📦 공급처 선택", ["도매매", "오너클랜"])
    original_link = st.text_input("🔗 원본 상품 링크", placeholder="https://...")
    
product_name = st.text_input("📝 분석할 상품명", placeholder="예: [PETLEAD 제외] 강아지 당근밭 노즈워크")

col_a, col_b = st.columns(2)
with col_a:
    paper_strategy = st.text_area("🎯 적용할 논문 속 트리거/심리 전략", 
                                 placeholder="예: 이탈률을 줄이는 첫 3초 시각적 주목도 전략 등", height=150)
with col_b:
    product_spec = st.text_area("📏 상품 상세 스펙 (사이즈, 소재 등 필수)", 
                               placeholder="예: 가로 20cm, 세로 15cm / 폴라폴리스 소재 / 손바닥 만한 크기", height=150)

# --- 기획 시작 버튼 ---
if st.button("🚀 안심이 통합 기획 및 데이터 생성 시작!"):
    if not product_name:
        st.warning("상품명을 입력해주세요!")
    else:
        with st.spinner("수석 연구원 안심이가 고객의 마음을 훔칠 8P 기획서를 작성 중입니다..."):
            
            # 안심이의 페르소나와 절대 규칙이 담긴 프롬프트
            plan_prompt = f"""
            너는 Magentalab 연구소의 수석 연구원, 닥스훈트 '안심이'야.
            상품명 '{product_name}'에 전략 '{paper_strategy}'과 스펙 '{product_spec}'을 녹여낸 8P 상세페이지 기획서를 작성해.

            [절대 규칙]
            1. **이미지 주인공:** 모든 연출 이미지에는 안심이(브라운 닥스훈트, 가운, 뿔테안경)가 반드시 등장해야 함.
            2. **대표이미지 (썸네일):** 기획서 최상단에 1000x1000 픽셀 기준의 '상품 단독' 프롬프트를 작성해. 텍스트는 절대 넣지 마.
            3. **사이즈 고정:** 상품 스펙({product_spec})을 엄격히 준수해. 실제 크기가 왜곡되지 않도록 주변 사물과 비교하는 묘사를 영문 프롬프트에 넣어.
            4. **한글 카피 강제:** 모든 메인카피와 서브카피는 '무조건 한글'로만 작성해.
            5. **심리 트리거:** 논문 전략({paper_strategy})을 직접적으로 언급하지 말고(예: '논문에 따르면' 금지), 자연스러운 카피와 구성으로 고객의 구매를 유도해.
            6. **정보고시:** 8페이지는 반드시 안심이가 돋보기로 검수하는 이미지와 함께 '상품정보 고시' 표(Table)를 포함해. (확인 안되는 항목은 '상품 상단 표기'로 기재)

            [페이지 구성]
            - 대표이미지 전용 프롬프트 (No Text)
            - 1P ~ 7P: 안심이의 행동 / 배경 / 한글 메인카피 / 한글 서브카피 / 영문 프롬프트(Flow용)
            - 8P: 안심이의 검수 코멘트 / 영문 프롬프트 / 상품정보 고시 표

            결과 형식 (구분자를 반드시 지킬 것):
            ---PLAN---
            (1~8페이지 내용)
            ---TITLE_TOSS---
            토스용 상품명
            ---TITLE_ALWAYZ---
            올웨이즈용 상품명
            """
            
            try:
                response = model.generate_content(plan_prompt)
                st.session_state.plan_content = response.text
                st.success("✨ 안심이의 정밀 기획이 완료되었습니다!")
            except Exception as e:
                st.error(f"안심이가 연구 중에 오류를 발견했어요: {e}")

# 5. 결과 표시 및 데이터 추출 (엑셀 & 워드프레스)
if st.session_state.plan_content:
    st.divider()
    
    # 데이터 추출 (Regex 사용)
    try:
        toss_title = st.session_state.plan_content.split("---TITLE_TOSS---")[1].split("---TITLE_ALWAYZ---")[0].strip()
        alwayz_title = st.session_state.plan_content.split("---TITLE_ALWAYZ---")[1].strip()
    except:
        toss_title = f"안심이 추천 {product_name}"
        alwayz_title = f"[연구소특가] {product_name}"

    st.markdown("### 💾 마켓 등록용 데이터 및 전송")
    
    # 엑셀 데이터 구성
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
        st.download_button(
            label="📊 네이버/토스 등록용 CSV 다운로드",
            data=csv_file,
            file_name=f"market_upload_{product_name}.csv",
            mime="text/csv",
            help="이 파일을 다운로드하여 로봇이 읽을 수 있는 폴더에 넣어주세요."
        )

    with btn_col2:
        if st.button("📦 워드프레스 작업대로 전송"):
            auth = (WP_USER, WP_APP_PW)
            wp_body = f"""
            <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px;">
                <h2>🎯 마켓별 최적화 제목</h2>
                <p><b>[네이버/토스]:</b> {toss_title}</p>
                <p><b>[올웨이즈]:</b> {alwayz_title}</p>
            </div>
            <hr>
            <h2>🔗 원본 상품 정보</h2>
            <p><b>공급처:</b> {source_type} | <b>링크:</b> <a href='{original_link}'>{original_link}</a></p>
            <hr>
            {st.session_state.plan_content.replace('\n', '<br>')}
            """
            
            payload = {
                "title": f"[정밀기획] {product_name}",
                "content": wp_body,
                "status": "draft"
            }
            
            res = requests.post(WP_URL, auth=auth, json=payload)
            if res.status_code == 201:
                st.balloons()
                st.success("워드프레스에 작업 지시서가 무사히 도착했습니다!")
            else:
                st.error("워드프레스 전송에 실패했습니다. 설정을 확인해주세요.")

    # 기획서 전문 보기
    with st.expander("🔍 안심이의 8P 기획 전문 보기", expanded=True):
        st.write(st.session_state.plan_content)
