import streamlit as st
import pandas as pd

# 1. 구글 시트 CSV 링크 (선생님의 링크를 따옴표 안에 넣어주세요)
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQKELDL8KGooVOUxgK2TEqkHebD74Sh3HrTMOajWRkQX0rBsPyQIk-obyh7n_FhGKkHl3YIDLnJGGoK/pub?output=csv"

@st.cache_data(ttl=60)
def load_data(url):
    # 데이터 읽기 시 에러 줄은 건너뛰도록 설정
    return pd.read_csv(url, on_bad_lines='skip')

try:
    df = load_data(sheet_url)

    # 사이드바: 학생 선택
    st.sidebar.title("🔍 학생 성적 조회")
    selected_name = st.sidebar.selectbox("이름을 선택하세요", df['이름'].unique())
    
    # 선택된 학생의 전체 데이터 추출
    s = df[df['이름'] == selected_name].iloc[0]

    # 메인 타이틀
    st.title(f"🏆 {selected_name} 학생 성적 리포트")
    st.info(f"**캠퍼스:** {s['캠퍼스']} | **학교:** {s['학교']} ({s['학년']}학년) | **성별:** {s['성별']}")

    st.divider()

    # --- 📊 2. 백분위 막대그래프 섹션 ---
    st.subheader("📊 과목별 백분위 분석")
    
    # 그래프용 데이터 정리
    chart_data = pd.DataFrame({
        "과목": ["국어", "수학", "탐구1", "탐구2"],
        "백분위": [
            pd.to_numeric(s['국어_백'], errors='coerce'), 
            pd.to_numeric(s['수학_백'], errors='coerce'), 
            pd.to_numeric(s['탐구1_백'], errors='coerce'), 
            pd.to_numeric(s['탐구2_백'], errors='coerce')
        ]
    })
    
    # 막대 그래프 출력 (가로축: 과목, 세로축: 백분위)
    st.bar_chart(data=chart_data, x="과목", y="백분위", color="#0072B2")
    st.caption("※ 백분위는 100에 가까울수록 성적이 우수함을 의미합니다.")

    st.divider()

    # --- 📝 3. 상세 성적 지표 섹션 ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### 📘 국어 <small>({s['국어_과목']})</small>", unsafe_allow_html=True)
        st.write(f"원점수: **{s['국어_원']}** / 표준: **{s['국어_표']}** / 백분위: **{s['국어_백']}** / **{s['국어_등']}등급**")
        
        st.markdown(f"#### 📙 탐구1 <small>({s['탐구1_과목']})</small>", unsafe_allow_html=True)
        st.write(f"원점수: **{s['탐구1_원']}** / 표준: **{s['탐구1_표']}** / 백분위: **{s['탐구1_백']}** / **{s['탐구1_등']}등급**")

    with col2:
        st.markdown(f"#### 📕 수학 <small>({s['수학_과목']})</small>", unsafe_allow_html=True)
        st.write(f"원점수: **{s['수학_원']}** / 표준: **{s['수학_표']}** / 백분위: **{s['수학_백']}** / **{s['수학_등']}등급**")
        
        st.markdown(f"#### 📒 탐구2 <small>({s['탐구2_과목']})</small>", unsafe_allow_html=True)
        st.write(f"원점수: **{s['탐구2_원']}** / 표준: **{s['탐구2_표']}** / 백분위: **