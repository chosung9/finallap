import streamlit as st
import pandas as pd

# 1. 구글 시트 CSV 링크 (본인의 링크를 꼭 넣어주세요)
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQKELDL8KGooVOUxgK2TEqkHebD74Sh3HrTMOajWRkQX0rBsPyQIk-obyh7n_FhGKkHl3YIDLnJGGoK/pub?output=csv"

@st.cache_data(ttl=60)
def load_data(url):
    return pd.read_csv(url, on_bad_lines='skip')

try:
    df = load_data(sheet_url)

    # 사이드바 설정
    st.sidebar.title("🔍 학생 성적 조회")
    selected_name = st.sidebar.selectbox("이름을 선택하세요", df['이름'].unique())
    s = df[df['이름'] == selected_name].iloc[0]

    # 상단 정보 표시
    st.title(f"🏆 {selected_name} 학생 성적 리포트")
    st.info(f"**캠퍼스:** {s['캠퍼스']} | **학교:** {s['학교']} ({s['학년']}학년)")

    st.divider()

    # --- 📊 백분위 막대그래프 섹션 ---
    st.subheader("📊 과목별 백분위 분석")
    chart_data = pd.DataFrame({
        "과목": ["국어", "수학", "탐구1", "탐구2"],
        "백분위": [
            pd.to_numeric(s['국어_백'], errors='coerce'), 
            pd.to_numeric(s['수학_백'], errors='coerce'), 
            pd.to_numeric(s['탐구1_백'], errors='coerce'), 
            pd.to_numeric(s['탐구2_백'], errors='coerce')
        ]
    })
    st.bar_chart(data=chart_data, x="과목", y="백분위", color="#0072B2")

    st.divider()

    # --- 📝 상세 성적 섹션 (들여쓰기 정밀 교정) ---
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
        st.write(f"원점수: **{s['탐구2_원']}** / 표준: **{s['탐구2_표']}** / 백분위: **{s['탐구2_백']}** / **{s['탐구2_등']}등급**")

    st.divider()
    
    # 영어 및 한국사 섹션
    c_eng, c_kor = st.columns(2)
    with c_eng:
        st.metric("📗 영어 등급", f"{s['영어_등']} 등급", f"원점수 {s['영어_원']}")
    with c_kor:
        st.metric("🏮 한국사 등급", f"{s['한국사_등']} 등급", f"원점수 {s['한국사_원']}")

except Exception as e:
    st.error(f"⚠️ 에러 발생: {e}")