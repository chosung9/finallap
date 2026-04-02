import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="정시 입시컨설팅 상담 프로그램", layout="wide")

# 2. 가상 데이터 생성 (실제 엑셀 데이터를 이 형식으로 준비하시면 됩니다)
# 학생별 성적 데이터
student_data = {
    '홍길동': {'학교': '이우고등학교', '학년': '3', '성별': '남', '국어': 60, '수학': 3, '영어': 3, '탐구1': 18, '탐구2': 78},
    '김철수': {'학교': '체육고등학교', '학년': '3', '성별': '남', '국어': 80, '수학': 50, '영어': 2, '탐구1': 70, '탐구2': 65},
}

# 대학별 배치표 데이터
univ_data = [
    {'지역': '강원', '대학명': '강원대학교', '학과명': '스포츠과학과', '군': '가', '환산점수': 121.20, '실기종목': '800m, 싯업, 제멀'},
    {'지역': '서울', '대학명': '고려대학교', '학과명': '체육교육과', '군': '가', '환산점수': 321.54, '실기종목': '농구, 높이뛰기, 지그재그'},
    {'지역': '경기', '대학명': '경희대학교', '학과명': '체육학과', '군': '나', '환산점수': 675.00, '실기종목': '제멀, 사스, 좌전굴'},
]
df_univ = pd.DataFrame(univ_data)

# 3. 사이드바 - 이름 필터 (이 부분이 핵심입니다!)
st.sidebar.title("🔍 학생 선택")
selected_name = st.sidebar.selectbox("상담할 학생 이름을 선택하세요", list(student_data.keys()))

# 선택된 학생 정보 가져오기
s = student_data[selected_name]

# 4. 상단 헤더 및 학생 기본 정보
st.title("📋 정시 입시컨설팅 상담 프로그램")
col_info1, col_info2, col_info3, col_info4 = st.columns(4)
col_info1.write(f"**이름:** {selected_name}")
col_info2.write(f"**학교:** {s['학교']}")
col_info3.write(f"**학년:** {s['학년']}학년")
col_info4.write(f"**성별:** {s['성별']}")

st.markdown("---")

# 5. 성적표 뷰 (이미지의 상단 부분)
st.subheader("📝 성적표")
cols = st.columns(5)
cols[0].metric("국어(백분위)", s['국어'])
cols[1].metric("수학(백분위)", s['수학'])
cols[2].metric("영어(등급)", s['영어'])
cols[3].metric("탐구1(백분위)", s['탐구1'])
cols[4].metric("탐구2(백분위)", s['탐구2'])

st.markdown("---")

# 6. 대학 선정 뷰 (이미지의 하단 리스트 부분)
st.subheader("🏫 대학 선정 및 합격 예측")

# 군별 필터 (가/나/다)
gun_filter = st.multiselect("모집군 선택", ["가", "나", "다"], default=["가", "나", "다"])
filtered_univ = df_univ[df_univ['군'].isin(gun_filter)]

# 테이블 출력
st.dataframe(filtered_univ, use_container_width=True)

st.info("💡 학생 이름을 바꾸면 상단 성적과 하단 대학 리스트가 자동으로 업데이트됩니다.")