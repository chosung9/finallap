import streamlit as st
import os

st.set_page_config(
    page_title="정시 입시 계산기 — 수지 2026",
    page_icon="🎯",
    layout="wide",
)

# HTML 파일 읽기
html_path = os.path.join(os.path.dirname(__file__), "index.html")
with open(html_path, encoding="utf-8") as f:
    html_content = f.read()

# 전체 화면으로 HTML 임베드
st.components.v1.html(html_content, height=900, scrolling=True)
