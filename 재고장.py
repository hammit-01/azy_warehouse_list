import streamlit as st
import pandas as pd

# =========================
# 기본 설정
# =========================
st.set_page_config(layout="wide")

# 제목
st.markdown(
    "<h1 style='font-size:3rem; padding-top: 3rem; padding-bottom: 1rem;'>📊 재고장 대시보드 mobile</h1>",
    unsafe_allow_html=True
)

# =========================
# CSS (필터 UI)
# =========================
st.markdown("""
<style>

/* 필터 영역 */
div[data-testid="stHorizontalBlock"] {
    background-color: #f5f5f5;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 10px;
}

/* selectbox 내부 */
div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] > div {
    background-color: white;
    font-size: 1rem;
}

/* 라벨 */
label[data-testid="stWidgetLabel"] {
    font-size: 1rem !important;
    font-weight: 700;
}

/* 전체 컨텐츠 영역 */
.block-container {
    max-width: auto;   /* 가로 길이 제한 */
    margin: 0 auto;      /* 가운데 정렬 */
    padding-top: 1rem;
}

</style>
""", unsafe_allow_html=True)

# =========================
# 데이터 로드
# =========================
df = pd.read_excel("data/jns.xlsx")

# =========================
# 날짜 기준
# =========================
today = pd.Timestamp.today().normalize()
limit = today + pd.Timedelta(days=30)

# =========================
# 데이터 전처리
# =========================

# 숫자 처리
df["중량"] = df["중량"].astype(str).str.replace(",", "").astype(float)
df["재고수량"] = pd.to_numeric(df["재고수량"], errors="coerce").astype("Int64")

# 이력번호 (핵심 처리)
df["이력번호"] = (
    pd.to_numeric(df["이력번호"], errors="coerce")
    .astype("Int64")
    .astype("string")
)

# 날짜 처리
df["소비기한"] = pd.to_datetime(df["소비기한"], errors="coerce")

# 컬럼 정리
cols = [
    "수탁품", "브랜드", "등급", "ESTNO", "BL번호", "이력번호",
    "재고수량", "중량", "평균중량",
    "소비기한", "창고"
]
df = df[cols]

# =========================
# 필터 UI
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    brand = st.selectbox(
        "브랜드",
        ["전체"] + sorted(df["브랜드"].dropna().unique())
    )

with col2:
    bl = st.selectbox(
        "BL번호",
        ["전체"] + sorted(df["BL번호"].dropna().unique())
    )

with col3:
    warehouse = st.selectbox(
        "창고",
        ["전체"] + sorted(df["창고"].dropna().unique())
    )

# =========================
# 필터 적용
# =========================
filtered_df = df.copy()

if brand != "전체":
    filtered_df = filtered_df[filtered_df["브랜드"] == brand]

if bl != "전체":
    filtered_df = filtered_df[filtered_df["BL번호"] == bl]

if warehouse != "전체":
    filtered_df = filtered_df[filtered_df["창고"] == warehouse]

# =========================
# 내림차 오름차
# =========================
col_sort, col_order = st.columns(2)

with col_sort:
    sort_col = st.selectbox("정렬 컬럼", filtered_df.columns)

with col_order:
    sort_order = st.selectbox("정렬 방식", ["오름차순", "내림차순"])

ascending = True if sort_order == "오름차순" else False

filtered_df = filtered_df.sort_values(by=sort_col, ascending=ascending)





# =========================
# KPI
# =========================
colA, colB, colC = st.columns(3)

colA.metric("총 재고수량", int(filtered_df["재고수량"].sum()))
colB.metric("총 중량", round(filtered_df["중량"].sum(), 2))
colC.metric("업데이트 일자", today.strftime("%Y-%m-%d"))

colA, colB, colC = st.columns([1,2,1])

# =========================
# 유통기한 강조 함수
# =========================
def highlight_expiry(val):
    if pd.isna(val):
        return ""
    if today <= pd.Timestamp(val) <= limit:
        return "color: red; font-weight: bold; font-size: 1.2rem;"
    return ""

# =========================
# 스타일 적용
# =========================
styled_df = (
    filtered_df.style
    .map(highlight_expiry, subset=["소비기한"])
    .format({
        "중량": "{:.2f}",
        "평균중량": "{:.2f}",
        "소비기한": lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else ""
    })
    .set_properties(subset=["수탁품"], **{"font-size": "1.5rem; font-weight: bold;"})
    .set_properties(subset=["브랜드"], **{"font-size": "1.3rem; font-weight: bold;"})
    .set_properties(subset=["중량"], **{"font-size": "1.4rem; font-weight: bold;"})
    .hide(axis="index")
)

# =========================
# 출력
# =========================
st.markdown(
    f"""
    <div style="display:flex; justify-content:center;">
        <div style="width:100%;">
            {styled_df.to_html()}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

