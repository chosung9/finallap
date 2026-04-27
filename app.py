import streamlit as st
import json
import math
import re
import httpx
import asyncio
from typing import Optional

# ── 페이지 설정 ──
st.set_page_config(
    page_title="정시 입시 계산기 — 수지 2026",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──
st.markdown("""
<style>
.pass-badge  { background:#dcfce7; color:#15803d; padding:3px 10px; border-radius:5px; font-weight:700; font-size:12px; }
.near-badge  { background:#fef3c7; color:#92400e; padding:3px 10px; border-radius:5px; font-weight:700; font-size:12px; }
.fail-badge  { background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:5px; font-weight:700; font-size:12px; }
.unk-badge   { background:#f1f5f9; color:#64748b; padding:3px 10px; border-radius:5px; font-weight:700; font-size:12px; }
.metric-box  { background:#f8f9fc; border:1px solid #e2e8f0; border-radius:8px; padding:12px 16px; text-align:center; }
.metric-val  { font-size:28px; font-weight:800; color:#1a2140; }
.metric-lbl  { font-size:11px; color:#9aa3bc; margin-top:2px; }
div[data-testid="stMetric"] { background:#f8f9fc; border:1px solid #e2e8f0; border-radius:8px; padding:10px; }
</style>
""", unsafe_allow_html=True)

# ── 상수 ──
SHEET_ID = "13oCsMNYUsj1R1Pftg3PmgL7V63pr-oJGgoe4NM4GZZ8"
API_KEY  = "AIzaSyDfmvDwAXcu6_Xu-h5iEaYr2jtQ0uGX-Fg"

SUBJECTS_KOR = ["화법과작문", "언어와매체"]
SUBJECTS_MAT = ["확률과통계", "미적분", "기하"]
SUBJECTS_EXP = [
    "생활과윤리","윤리와사상","한국지리","세계지리",
    "동아시아사","세계사","경제","정치와법","사회문화",
    "물리1","화학1","생명과학1","지구과학1"
]

# ── 데이터 로드 ──
@st.cache_data
def load_unis():
    with open("data/universities.json", encoding="utf-8") as f:
        return json.load(f)

UNIS = load_unis()
REGIONS = ["전체"] + sorted({u.get("region","") for u in UNIS if u.get("region")})

# ── 구글 시트 로드 ──
@st.cache_data(ttl=300)
def load_google_sheet(sheet_name: str):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{sheet_name}?key={API_KEY}"
    try:
        r = httpx.get(url, timeout=10)
        r.raise_for_status()
        return r.json().get("values", [])
    except Exception as e:
        return []

def parse_students(rows):
    if not rows:
        return []
    start = 1 if rows and any(v.strip() in ("이름","캠퍼스","학교") for v in rows[0]) else 0
    students = []
    for row in rows[start:]:
        def g(i, d=""): return row[i].strip() if i < len(row) and row[i] else d
        def n(i):
            try: return float(g(i)) if g(i) else None
            except: return None
        def ni(i):
            try: return int(float(g(i))) if g(i) else None
            except: return None
        name = g(1)
        if not name: continue
        students.append({
            "name": name, "gender": g(2,"남"), "school": g(3), "grade": ni(4) or 3,
            "korean_subject": g(5,"화법과작문"), "korean_std": n(7), "korean_pct": n(8),
            "math_subject": g(10,"확률과통계"), "math_std": n(12), "math_pct": n(13),
            "english_grade": ni(16) or 3,
            "explore1_subject": g(17,"생활과윤리"), "explore1_std": n(19), "explore1_pct": n(20),
            "explore2_subject": g(22,"사회문화"), "explore2_std": n(24), "explore2_pct": n(25),
            "hs_grade": ni(28) or 6,
        })
    return students

# ── 수식 엔진 ──
def sorted_desc(args):
    return sorted([v for v in args if v is not None and not math.isnan(v)], reverse=True)

def nth(n, *args):
    s = sorted_desc(args)
    return s[n-1] if len(s) >= n else 0.0

def top_sum(n, *args):
    return sum(sorted_desc(args)[:n])

def top_avg(n, *args):
    vals = sorted_desc(args)[:n]
    return sum(vals)/len(vals) if vals else 0.0

def eval_formula(formula, scores, eng_score, hs_score):
    ex1s = scores.get("explore1_std") or 0
    ex1p = scores.get("explore1_pct") or 0
    ex2s = scores.get("explore2_std") or 0
    ex2p = scores.get("explore2_pct") or 0
    vars_map = {
        "국표": scores.get("korean_std") or 0,
        "국백": scores.get("korean_pct") or 0,
        "수표": scores.get("math_std") or 0,
        "수백": scores.get("math_pct") or 0,
        "영어": eng_score, "영등": eng_score,
        "탐1표": ex1s, "탐1백": ex1p,
        "탐2표": ex2s, "탐2백": ex2p,
        "탐평표": (ex1s+ex2s)/2, "탐평백": (ex1p+ex2p)/2,
        "한국사": hs_score, "한점": hs_score,
    }
    expr = formula.replace("×","*").replace("÷","/")
    # topW 전개
    def expand_topw(m):
        parts = m.group(1).split(",")
        return "("+"+".join(
            f"{p.split(':')[0].strip()}*{p.split(':')[1].strip()}" if ":" in p else p.strip()
            for p in parts
        )+")"
    expr = re.sub(r"topW\s*\(([^)]+)\)", expand_topw, expr)
    for i in range(1,5):
        expr = re.sub(rf"nth{i}\s*\(", f"__nth{i}(", expr)
    expr = re.sub(r"top1\s*\(", "__nth1(", expr)
    expr = re.sub(r"top2\s*\(", "__top2(", expr)
    expr = re.sub(r"top3\s*\(", "__top3(", expr)
    expr = re.sub(r"avg2\s*\(", "__avg2(", expr)
    expr = re.sub(r"avg3\s*\(", "__avg3(", expr)
    expr = re.sub(r"\(([^)]+)\)\s+or\s+\(([^)]+)\)", r"max(\1,\2)", expr)
    for name in sorted(vars_map.keys(), key=len, reverse=True):
        expr = expr.replace(name, str(vars_map[name]))
    safe_env = {
        "__builtins__": {}, "max": max, "min": min, "abs": abs,
        "__nth1": lambda *a: nth(1,*a), "__nth2": lambda *a: nth(2,*a),
        "__nth3": lambda *a: nth(3,*a), "__nth4": lambda *a: nth(4,*a),
        "__top2": lambda *a: top_sum(2,*a), "__top3": lambda *a: top_sum(3,*a),
        "__avg2": lambda *a: top_avg(2,*a), "__avg3": lambda *a: top_avg(3,*a),
    }
    try:
        return round(float(eval(expr, safe_env)), 2)  # noqa: S307
    except:
        return 0.0

def build_default_formula(u):
    ind = (u.get("indicator") or "").lower()
    suf = "백" if "백" in ind else "표"
    ts  = float(u.get("total_score") or 1000)
    kr  = float(u.get("korean_ratio") or 0)
    ma  = float(u.get("math_ratio") or 0)
    exr = float(u.get("explore_ratio") or 0)
    parts = []
    if kr  > 0: parts.append(f"국{suf}*{kr}*{ts}/100")
    if ma  > 0: parts.append(f"수{suf}*{ma}*{ts}/100")
    if exr > 0: parts.append(f"탐평{suf}*{exr}*{ts}/100")
    if any(v is not None for v in (u.get("eng_scores") or [])): parts.append("영어")
    if any(v is not None for v in (u.get("hs_scores")  or [])): parts.append("한국사")
    return " + ".join(parts) if parts else "0"

def calc_score(u, scores, calc_overrides):
    key = f"{u['university']}||{u['department']}"
    ovr = calc_overrides.get(key, {})
    formula = ovr.get("formula") or build_default_formula(u)
    eng_g = scores.get("english_grade") or 3
    hs_g  = scores.get("hs_grade") or 6
    eng_scores = ovr.get("eng_scores") or u.get("eng_scores") or []
    hs_scores  = u.get("hs_scores") or []
    def get_gs(arr, g): return float(arr[g-1]) if arr and len(arr) >= g and arr[g-1] is not None else 0.0
    eng_val = get_gs(eng_scores, eng_g)
    hs_val  = get_gs(hs_scores, hs_g)
    cut = ovr.get("cutline")
    cut = float(cut) if cut not in (None,"") else u.get("cutline_suneung")
    my  = eval_formula(formula, scores, eng_val, hs_val)
    diff = round(my - cut, 2) if cut is not None else None
    if cut is None: status = "unknown"
    elif my >= cut: status = "pass"
    elif my >= cut - cut*0.05: status = "near"
    else: status = "fail"
    return {"my": my, "cut": cut, "diff": diff, "status": status, "formula": formula}

# ── 세션 상태 초기화 ──
if "calc_overrides" not in st.session_state: st.session_state.calc_overrides = {}
if "students_google" not in st.session_state: st.session_state.students_google = []
if "synced" not in st.session_state: st.session_state.synced = False

# ══════════════════════════════════════
# 사이드바
# ══════════════════════════════════════
with st.sidebar:
    st.title("🎯 정시 입시 계산기")
    st.caption("수지캠퍼스 2026학년도")

    # ── 구글 시트 동기화 ──
    st.divider()
    st.subheader("📊 구글 시트 연동")
    if st.button("🔄 학생 데이터 새로고침", use_container_width=True):
        load_google_sheet.clear()
        rows = load_google_sheet("시트1")
        st.session_state.students_google = parse_students(rows)
        st.session_state.synced = True
        st.success(f"✅ {len(st.session_state.students_google)}명 로드 완료!")

    if not st.session_state.synced:
        rows = load_google_sheet("시트1")
        st.session_state.students_google = parse_students(rows)
        st.session_state.synced = True

    # ── 학생 선택 ──
    st.divider()
    st.subheader("👤 학생 선택")
    all_students = st.session_state.students_google
    schools = ["전체"] + sorted({s["school"] for s in all_students if s.get("school")})
    sel_school = st.selectbox("학교", schools)
    filtered_s = all_students if sel_school == "전체" else [s for s in all_students if s.get("school") == sel_school]
    names = ["직접 입력"] + [f"{s['name']} ({s.get('school','')})" for s in filtered_s]
    sel_name = st.selectbox("학생", names)

    # ── 성적 입력 ──
    st.divider()
    st.subheader("📝 수능 성적 입력")

    # 학생 선택 시 자동 입력
    sel_student = None
    if sel_name != "직접 입력":
        idx = names.index(sel_name) - 1
        sel_student = filtered_s[idx]

    def sv(key, default):
        if sel_student and key in sel_student and sel_student[key] is not None:
            return sel_student[key]
        return default

    with st.expander("국어", expanded=True):
        kor_subj = st.selectbox("선택과목", SUBJECTS_KOR, index=SUBJECTS_KOR.index(sv("korean_subject","화법과작문")))
        kor_std  = st.number_input("표준점수", 0, 200, int(sv("korean_std",0) or 0), key="kor_std")
        kor_pct  = st.number_input("백분위",   0.0, 100.0, float(sv("korean_pct",0.0) or 0.0), 0.1, key="kor_pct")

    with st.expander("수학", expanded=True):
        mat_subj = st.selectbox("선택과목", SUBJECTS_MAT, index=SUBJECTS_MAT.index(sv("math_subject","확률과통계")))
        mat_std  = st.number_input("표준점수", 0, 200, int(sv("math_std",0) or 0), key="mat_std")
        mat_pct  = st.number_input("백분위",   0.0, 100.0, float(sv("math_pct",0.0) or 0.0), 0.1, key="mat_pct")

    with st.expander("영어 / 한국사", expanded=True):
        eng_grade = st.selectbox("영어 등급", list(range(1,10)), index=int(sv("english_grade",3))-1)
        hs_grade  = st.selectbox("한국사 등급", list(range(1,10)), index=int(sv("hs_grade",6))-1)

    with st.expander("탐구", expanded=True):
        e1_subj = st.selectbox("탐구1 과목", SUBJECTS_EXP, index=SUBJECTS_EXP.index(sv("explore1_subject","생활과윤리")) if sv("explore1_subject","생활과윤리") in SUBJECTS_EXP else 0)
        e1_std  = st.number_input("탐구1 표준점수", 0, 100, int(sv("explore1_std",0) or 0), key="e1_std")
        e1_pct  = st.number_input("탐구1 백분위",   0.0, 100.0, float(sv("explore1_pct",0.0) or 0.0), 0.1, key="e1_pct")
        e2_subj = st.selectbox("탐구2 과목", SUBJECTS_EXP, index=SUBJECTS_EXP.index(sv("explore2_subject","사회문화")) if sv("explore2_subject","사회문화") in SUBJECTS_EXP else 0)
        e2_std  = st.number_input("탐구2 표준점수", 0, 100, int(sv("explore2_std",0) or 0), key="e2_std")
        e2_pct  = st.number_input("탐구2 백분위",   0.0, 100.0, float(sv("explore2_pct",0.0) or 0.0), 0.1, key="e2_pct")

    # ── 필터 ──
    st.divider()
    st.subheader("🔍 필터")
    sel_gun    = st.multiselect("군", ["가","나","다"], default=["가","나","다"])
    sel_region = st.selectbox("지역", REGIONS)
    sel_type   = st.selectbox("형태", ["전체","국립","사립"])
    gyojik     = st.toggle("교직 가능 대학만")
    pass_filter = st.radio("합격 가능성", ["전체","✅ 합격권","⚠️ 근접","❌ 미달","— 미공개"], horizontal=False)

# ── 현재 성적 정리 ──
scores = {
    "korean_std": kor_std, "korean_pct": kor_pct,
    "math_std": mat_std,   "math_pct": mat_pct,
    "english_grade": eng_grade,
    "explore1_std": e1_std, "explore1_pct": e1_pct,
    "explore2_std": e2_std, "explore2_pct": e2_pct,
    "hs_grade": hs_grade,
}
has_score = any([kor_std, mat_std, e1_std, e2_std])

# ══════════════════════════════════════
# 메인 화면
# ══════════════════════════════════════
st.title("🎯 정시 입시 계산기")

if sel_student:
    st.info(f"**{sel_student['name']}** ({sel_student.get('school','')} / {sel_student.get('gender','')}) 성적 불러옴")

if not has_score:
    st.warning("👈 왼쪽에서 학생을 선택하거나 성적을 입력하세요")
    st.stop()

# ── 대학 필터링 ──
unis = UNIS
if sel_gun:    unis = [u for u in unis if u.get("gun") in sel_gun]
if sel_region != "전체": unis = [u for u in unis if u.get("region") == sel_region]
if sel_type   != "전체": unis = [u for u in unis if u.get("type") == sel_type]
if gyojik:     unis = [u for u in unis if u.get("has_gyojik") == "O"]

# ── 환산점수 계산 ──
results = []
for u in unis:
    r = calc_score(u, scores, st.session_state.calc_overrides)
    results.append({**u, **r})

# pass 필터
pmap = {"✅ 합격권":"pass","⚠️ 근접":"near","❌ 미달":"fail","— 미공개":"unknown"}
if pass_filter != "전체":
    results = [r for r in results if r["status"] == pmap[pass_filter]]

# 정렬
results.sort(key=lambda r: (r["diff"] is None, -(r["diff"] or 0)))

# ── 통계 ──
all_r = [r for r in results]
cnts = {"pass":0,"near":0,"fail":0,"unknown":0}
for r in results: cnts[r["status"]] += 1

c1,c2,c3,c4 = st.columns(4)
c1.metric("✅ 합격권", cnts["pass"])
c2.metric("⚠️ 근접",   cnts["near"])
c3.metric("❌ 미달",   cnts["fail"])
c4.metric("— 미공개", cnts["unknown"])

st.caption(f"총 **{len(results)}개** 대학 표시")
st.divider()

# ── 결과 테이블 ──
STATUS_LABEL = {"pass":"✅ 합격권","near":"⚠️ 근접","fail":"❌ 미달","unknown":"— 미공개"}
STATUS_COLOR = {"pass":"🟢","near":"🟡","fail":"🔴","unknown":"⚪"}

for r in results:
    status_icon = STATUS_COLOR[r["status"]]
    diff_str = (f"+{r['diff']:.1f}" if r["diff"] >= 0 else f"{r['diff']:.1f}") if r["diff"] is not None else "—"
    cut_str  = f"{r['cut']:.1f}" if r["cut"] is not None else "미공개"
    gun_color = {"가":"🔵","나":"🟢","다":"🟠"}.get(r.get("gun",""),"⚪")

    with st.expander(
        f"{status_icon} {r['university']} {r['department']}  |  "
        f"{gun_color}{r.get('gun','')}군  |  "
        f"내 점수: **{r['my']:.1f}**  |  커트: {cut_str}  |  차이: **{diff_str}**"
    ):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**기본 정보**")
            st.write(f"📍 지역: {r.get('region','—')}")
            st.write(f"🏛 형태: {r.get('type','—')}")
            st.write(f"👥 정원: {r.get('capacity','—')}명")
            st.write(f"📚 교직: {r.get('has_gyojik','—')}")

        with col2:
            st.markdown("**전형 비율**")
            sr = r.get("suneung_ratio")
            gr = r.get("silgi_ratio")
            kr2 = r.get("korean_ratio")
            ma2 = r.get("math_ratio")
            ex2 = r.get("explore_ratio")
            st.write(f"수능: {f'{sr*100:.0f}%' if sr else '—'}")
            st.write(f"실기: {f'{gr*100:.0f}%' if gr else '—'}")
            st.write(f"국어: {f'{kr2*100:.0f}%' if kr2 else '—'} | 수학: {f'{ma2*100:.0f}%' if ma2 else '—'} | 탐구: {f'{ex2*100:.0f}%' if ex2 else '—'}")
            st.write(f"활용지표: {r.get('indicator','—')}")

        with col3:
            st.markdown("**실기 종목**")
            silgi = [r.get(f"silgi{i}") for i in range(1,7) if r.get(f"silgi{i}")]
            if silgi:
                for s in silgi: st.write(f"🏃 {s}")
            else:
                st.write("—")

        # 커트라인 히스토리
        h25 = r.get("history_2025")
        h24 = r.get("history_2024")
        if h25 or h24:
            st.markdown("**📊 입결 히스토리**")
            hcol1, hcol2 = st.columns(2)
            with hcol1:
                if h25:
                    st.write("**2025년**")
                    st.write(f"평균: {h25.get('avg','—')} | 최저: {h25.get('low','—')} | 예비: {h25.get('yebee','—')}")
            with hcol2:
                if h24:
                    st.write("**2024년**")
                    st.write(f"평균: {h24.get('avg','—')} | 최저: {h24.get('low','—')} | 예비: {h24.get('yebee','—')}")

        # 계산식
        st.markdown("**⚙️ 계산식**")
        key = f"{r['university']}||{r['department']}"
        ovr = st.session_state.calc_overrides.get(key, {})
        current_formula = ovr.get("formula") or build_default_formula(r)
        new_formula = st.text_input(
            "수식 수정 (국표, 수표, 영어, 탐평표, 한국사 등)",
            value=current_formula,
            key=f"formula_{key}"
        )
        new_cut = st.number_input(
            "수능 커트라인 수정",
            value=float(ovr.get("cutline") or r.get("cutline_suneung") or 0),
            step=0.1,
            key=f"cut_{key}"
        )
        if st.button("💾 저장", key=f"save_{key}"):
            st.session_state.calc_overrides[key] = {
                "formula": new_formula,
                "cutline": new_cut,
            }
            st.success("저장됨! 새로고침하면 반영됩니다.")
            st.rerun()