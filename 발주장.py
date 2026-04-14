import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# python -m streamlit run app.py


st.title("📊 발주장 대시보드 (Drive API)")

# 🔐 서비스 계정 파일
SERVICE_ACCOUNT_FILE = "azyapp-5eb899c87965.json"

# 📁 구글 드라이브 폴더 ID
FOLDER_ID = "1WDZZ8kL1YbU5u4OjN1ePFtd0mJCYvyFI"

# 1️⃣ 인증
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/drive.readonly"],
)

service = build("drive", "v3", credentials=credentials)

# 2️⃣ 파일 목록 가져오기
results = service.files().list(
    q=f"'{FOLDER_ID}' in parents",
    fields="files(id, name, mimeType)",
    supportsAllDrives=True,
    includeItemsFromAllDrives=True
).execute()

files = results.get("files", [])

if not files:
    st.error("❌ 파일 없음 (공유 권한 확인)")
    st.stop()

# 🔥 3️⃣ 주차 목록 생성
week_options = list(set([
    f["name"].replace(".xlsx", "")
    for f in files
]))

selected_week = st.selectbox("📅 주차 선택", week_options)

# 🔍 4️⃣ 해당 주차 파일 필터
filtered_files = [
    f for f in files if selected_week in f["name"]
]

if not filtered_files:
    st.error("❌ 해당 주차 파일 없음")
    st.stop()
    

# 👉 파일이 하나면 자동 선택
selected_file = filtered_files[0]["name"]

# 📌 file_id 찾기
file_id = next(
    f["id"] for f in filtered_files
    if f["name"] == selected_file
)

# 5️⃣ 파일 다운로드
request = service.files().export_media(
    fileId=file_id,
    mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

file_bytes = io.BytesIO()
downloader = MediaIoBaseDownload(file_bytes, request)

done = False
while not done:
    status, done = downloader.next_chunk()

file_bytes.seek(0)

# 6️⃣ 시트 목록
xls = pd.ExcelFile(file_bytes)
sheet_names = xls.sheet_names

selected_sheet = st.selectbox("👥 팀 선택", sheet_names)

# 7️⃣ 데이터 읽기
df = pd.read_excel(file_bytes, sheet_name=selected_sheet)

# 🔥 데이터 검증
if df.shape[0] < 3:
    st.error("❌ 데이터 구조 이상")
    st.stop()

# 🔥 전처리
# df = df.iloc[2:].reset_index(drop=True)

if selected_sheet == "발주장취합" and "순서" in df.columns:
    df = df.drop(columns=["순서"])
elif selected_sheet == "매입" and "날짜" in df.columns:
    df = df.drop(columns=["날짜"])
else:
    df.columns = df.iloc[1]
    df = df.iloc[2:]
    df = df.drop(columns=["순서"])

if "거래처" in df.columns:
    # 거래처 리스트 (전체 포함)
    company_list = ["전체"] + sorted(df["거래처"].dropna().unique())

    # 선택박스
    selected_company = st.selectbox("🏢 거래처 선택", company_list)

    # 필터링
    if selected_company != "전체":
        df = df[df["거래처"] == selected_company]
if "구역" in df.columns:
    # 구역 리스트 (전체 포함)
    company_list = ["전체"] + sorted(df["구역"].dropna().unique())

    # 선택박스
    selected_company = st.selectbox("🏢 구역 선택", company_list)

    # 필터링
    if selected_company != "전체":
        df = df[df["구역"] == selected_company]
elif "매입처" in df.columns:
    # 매입처 리스트 (전체 포함)
    company_list = ["전체"] + sorted(df["매입처"].dropna().unique())

    # 선택박스
    selected_company = st.selectbox("🏢 매입처 선택", company_list)

    # 필터링
    if selected_company != "전체":
        df = df[df["매입처"] == selected_company]





st.dataframe(df)

# new_columns = df.iloc[0].fillna("")
# df.columns = [
#     f"col_{i}" if str(col).strip() == "" else str(col)
#     for i, col in enumerate(new_columns)
# ]

# df = df.drop(index=0).reset_index(drop=True)
# df = df.iloc[:, 3:]

# df = df[
#     df.iloc[:, 0].notna() &
#     (df.iloc[:, 0].astype(str).str.strip() != "")
# ]

# df = df.loc[:, ~df.columns.duplicated()]

# # 8️⃣ 출력
# st.dataframe(df)

# # 🔥 추가 기능 (필터)
# st.subheader("📌 필터")

# if len(df.columns) > 0:
#     company_list = df.iloc[:, 0].unique()
#     selected_company = st.selectbox("거래처 선택", company_list)

#     df_filtered = df[df.iloc[:, 0] == selected_company]

#     st.dataframe(df_filtered)

#     # 그래프
#     if df_filtered.shape[1] > 1:
#         try:
#             st.bar_chart(df_filtered.iloc[:, 1])
#         except:
#             pass
