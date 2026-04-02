import streamlit as st
import pandas as pd

# 1. 구글 시트 CSV 링크
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQKELDL8KGooVOUxgK2TEqkHebD74Sh3HrTMOajWRkQX0rBsPyQIk-obyh7n_FhGKkHl3YIDLnJGGoK/pub?output=csv"

@st.cache_data(ttl=60)
def load_data(url):
    return pd.read_csv(url, on_bad_lines='skip')

try:
    df = load_data(sheet_url)
    st.sidebar.title("🔍 학생 성적 조회")
    selected_name = st.sidebar.selectbox("이름을 선택하세요", df['이름'].unique())
    s = df[df['이름'] == selected_name].iloc[0]

    # 헤더 섹션
    st.title(f"📊 {selected_name} 학생 성적 리포트")
    st.markdown(f"**캠퍼스:** {s['캠퍼스']} | **학교:** {s['학교']} ({s['학년']}학년)")
    
    st.divider()

    # --- 📊 1. 막대 그래프 섹션 ---
    st.subheader("📈 과목별 백분위 분석")
    chart_data = pd.DataFrame({
        "과목": ["국어", "수학", "탐구1", "탐구2"],
        "백분위": [pd.to_numeric(s['국어_백'], errors='coerce'), 
                   pd.to_numeric(s['수학_백'], errors='coerce'), 
                   pd.to_numeric(s['탐구1_백'], errors='coerce'), 
                   pd.to_numeric(s['탐구2_백'], errors='coerce')]
    })
    st.bar_chart(data=chart_data, x="과목", y="백분위", color="#0072B2")

    st.divider()

    # --- 📋 2. 표 형태의 성적표 섹션 (이미지 스타일) ---
    st.subheader("📋 상세 성적표")
    
    # HTML과 CSS를 사용하여 표 디자인
    st.markdown(f"""
    <style>
        .report-table {{
            width: 100%;
            border-collapse: collapse;
            text-align: center;
            font-family: sans-serif;
        }}
        .report-table th {{
            background-color: #f0f2f6;
            padding: 10px;
            border: 1px solid #ddd;
            font-weight: bold;
        }}
        .report-table td {{
            padding: 10px;
            border: 1px solid #ddd;
        }}
        .row-title {{
            background-color: #f8f9fb;
            font-weight: bold;
            width: 15%;
        }}
        .highlight-red {{ color: #d32f2f; font-weight: bold; }}
        .highlight-green {{ color: #2e7d32; font-weight: bold; }}
    </style>
    
    <table class="report-table">
        <tr>
            <th>구분</th>
            <th>국어</th>
            <th>수학</th>
            <th>영어</th>
            <th>탐구1</th>
            <th>탐구2</th>
            <th>한국사</th>
        </tr>
        <tr>
            <td class="row-title">과목</td>
            <td>{s['국어_과목']}</td>
            <td>{s['수학_과목']}</td>
            <td>-</td>
            <td>{s['탐구1_과목']}</td>
            <td>{s['탐구2_과목']}</td>
            <td>-</td>
        </tr>
        <tr>
            <td class="row-title">원점수</td>
            <td>{s['국어_원']}</td>
            <td>{s['수학_원']}</td>
            <td>{s['영어_원']}</td>
            <td>{s['탐구1_원']}</td>
            <td>{s['탐구2_원']}</td>
            <td>{s['한국사_원']}</td>
        </tr>
        <tr>
            <td class="row-title">표준점수</td>
            <td>{s['국어_표']}</td>
            <td>{s['수학_표']}</td>
            <td>-</td>
            <td>{s['탐구1_표']}</td>
            <td>{s['탐구2_표']}</td>
            <td>-</td>
        </tr>
        <tr>
            <td class="row-title">백분위</td>
            <td class="highlight-green">{s['국어_백']}</td>
            <td class="highlight-green">{s['수학_백']}</td>
            <td>-</td>
            <td class="highlight-green">{s['탐구1_백']}</td>
            <td class="highlight-green">{s['탐구2_백']}</td>
            <td>-</td>
        </tr>
        <tr>
            <td class="row-title">등급</td>
            <td class="highlight-red">{s['국어_등']}</td>
            <td class="highlight-red">{s['수학_등']}</td>
            <td class="highlight-red">{s['영어_등']}</td>
            <td class="highlight-red">{s['탐구1_등']}</td>
            <td class="highlight-red">{s['탐구2_등']}</td>
            <td class="highlight-red">{s['한국사_등']}</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"⚠️ 데이터 로드 오류: {e}")