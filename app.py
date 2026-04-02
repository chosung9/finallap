import streamlit as st
import pandas as pd

# 구글 시트 CSV 링크 (선생님의 링크를 넣어주세요)
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQKELDL8KGooVOUxgK2TEqkHebD74Sh3HrTMOajWRkQX0rBsPyQIk-obyh7n_FhGKkHl3YIDLnJGGoK/pubhtml"

@st.cache_data(ttl=60)
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(sheet_url)

    # 사이드바 학생 선택
    st.sidebar.title("🔍 학생 성적 조회")
    selected_name = st.sidebar.selectbox("이름을 선택하세요", df['이름'].unique())
    s = df[df['이름'] == selected_name].iloc[0]

    # 메인 타이틀 및 기본 정보 (캠퍼스 추가)
    st.title(f"🏆 {selected_name} 학생 성적 리포트")
    st.info(f"**캠퍼스:** {s['캠퍼스']} | **소속:** {s['학교']} ({s['학년']}학년) | **성별:** {s['성별']}")

    # --- 국어 & 수학 (원점수 포함) ---
    col_k, col_m = st.columns(2)
    with col_k:
        st.markdown(f"#### 📘 국어 <small>({s['국어_과목']})</small>", unsafe_allow_html=True)
        st.write(f"원점수: **{s['국어_원']}** / 표준: **{s['국어_표']}** / 백분위: **{s['국어_백']}** / **{s['국어_등']}등급**")
    with col_m:
        st.markdown(f"#### 📕 수학 <small>({s['수학_과목']})</small>", unsafe_allow_html=True)
        st.write(f"원점수: **{s['수학_원']}** / 표준: **{s['수학_표']}** / 백분위: **{s['수학_백']}** / **{s['수학_등']}등급**")

    st.divider()

    # --- 탐구 1 & 탐구 2 (원점수 포함) ---
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown(f"#### 📙 탐구1 <small>({s['탐구1_과목']})</small>", unsafe_allow_html=True)
        st.write(f"원점수: **{s['탐구1_원']}** / 표준: **{s['탐구1_표']}** / 백분위: **{s['탐구1_백']}** / **{s['탐구1_등']}등급**")
    with col_t2:
        st.markdown(f"#### 📒 탐구2 <small>({s['탐구2_과목']})</small>", unsafe_allow_html=True)
        st.write(f"원점수: **{s['탐구2_원']}** / 표준: **{s['탐구2_표']}** / 백분위: **{s['탐구2_백']}** / **{s['탐구2_등']}등급**")

    st.divider()

    # --- 영어 & 한국사 ---
    st.subheader("📝 기타 과목 (절대평가)")
    c_eng, c_kor = st.columns(2)
    with c_eng:
        st.metric("📗 영어", f"{s['영어_등']} 등급", f"원점수 {s['영어_원']}")
    with c_kor:
        st.metric("🏮 한국사", f"{s['한국사_등']} 등급", f"원점수 {s['한국사_원']}")

except Exception as e:
    st.error(f"⚠️ 데이터 로드 오류! 시트 제목을 다시 확인해주세요. 에러내용: {e}")