import streamlit as st
import pandas as pd

# =========================
# CSS
# =========================
st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important;
}

div[data-testid="stHorizontalBlock"] > div {
    flex: 1 !important;
}
div[data-baseweb="select"] {
    width: 300px !important;
}
</style>
""", unsafe_allow_html=True)



# =========================
# 기본 설정
# =========================
today = pd.Timestamp.today().strftime("%Y-%m-%d")

col_title, col_update = st.columns([4,1])

with col_title:
    st.markdown(
        "<h1 style='margin:0; padding:12px;'>📊 모바일 재고\n대시보드</h1>",
        unsafe_allow_html=True
    )

with col_update:
    st.markdown(
        f"""
        <div style="
            background-color:#f0f2f6;
            padding:10px;
            border-radius:10px;
            text-align:center;
            font-weight:600;
        ">
        📅 {today}
        </div>
        """,
        unsafe_allow_html=True
    )
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
df["중량"] = df["중량"].astype(str).str.replace(",", "").astype(float)
df["재고수량"] = pd.to_numeric(df["재고수량"], errors="coerce").astype("Int64")

df["이력번호"] = (
    pd.to_numeric(df["이력번호"], errors="coerce")
    .astype("Int64")
    .astype("string")
)

df["소비기한"] = pd.to_datetime(df["소비기한"], errors="coerce")

cols = [
    "수탁품", "브랜드", "등급", "ESTNO", "BL번호", "이력번호",
    "재고수량", "중량", "평균중량",
    "소비기한", "창고"
]
df = df[cols]

# =========================
# 필터 UI
# =========================
# 1줄
col1, col2 = st.columns([1, 1], gap="small")

with col1:
    brand = st.selectbox("브랜드", ["전체"] + sorted(df["브랜드"].dropna().unique()))

with col2:
    bl = st.selectbox("BL번호", ["전체"] + sorted(df["BL번호"].dropna().unique()))

# 2줄
col3, col4 = st.columns([1, 1], gap="small")

with col3:
    warehouse = st.selectbox("창고", ["전체"] + sorted(df["창고"].dropna().unique()))

with col4:
    name = st.selectbox("품목", ["전체"] + sorted(df["수탁품"].dropna().unique()))


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

if name != "전체":
    filtered_df = filtered_df[filtered_df["수탁품"] == name]
# =========================
# 정렬
# =========================
col_sort, col_order = st.columns([1,1])

with col_sort:
    sort_col = st.selectbox("정렬 컬럼", filtered_df.columns)

with col_order:
    sort_order = st.selectbox("정렬 방식", ["오름차순", "내림차순"])

ascending = True if sort_order == "오름차순" else False
filtered_df = filtered_df.sort_values(by=sort_col, ascending=ascending)

# =========================
# KPI
# =========================
col1, col2 = st.columns(2)

total_qty = int(filtered_df["재고수량"].sum())
total_weight = round(filtered_df["중량"].sum(), 2)

with col1:
    st.markdown(
        f"""
        <div style="
            background-color:#e3f2fd;
            margin: 10px;
            padding:20px;
            border-radius:15px;
            text-align:center;
        ">
            <div style="font-size:1.2rem;">총 재고수량</div>
            <div style="font-size:2rem; font-weight:bold;">{total_qty}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style="
            background-color:#e8f5e9;
            margin: 10px;
            padding:20px;
            border-radius:15px;
            text-align:center;
        ">
            <div style="font-size:1.2rem;">총 중량</div>
            <div style="font-size:2rem; font-weight:bold;">{total_weight}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# 유통기한 강조 컬럼 생성
# =========================
def mark_expiry(row):
    if pd.isna(row["소비기한"]):
        return ""
    if today <= row["소비기한"] <= limit:
        return "⚠️ 임박"
    return ""

filtered_df["유통상태"] = filtered_df.apply(mark_expiry, axis=1)

# =========================
# 자동 컬럼 사이즈 설정
# =========================
def auto_column_config(df):
    config = {}

    for col in df.columns:
        max_len = df[col].astype(str).str.len().max()

        if max_len < 8:
            size = "small"
        elif max_len < 20:
            size = "medium"
        else:
            size = "large"

        config[col] = st.column_config.TextColumn(width=size)

    # 숫자 컬럼은 작게
    config["재고수량"] = st.column_config.NumberColumn(width="small")
    config["중량"] = st.column_config.NumberColumn(width="small")
    config["평균중량"] = st.column_config.NumberColumn(width="small")

    return config

# =========================
# 출력
# =========================
st.dataframe(
    filtered_df,
    column_config=auto_column_config(filtered_df),
    use_container_width=True,
    hide_index=True
)
