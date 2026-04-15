import streamlit as st

st.set_page_config(page_title="재고 시스템")

# User-Agent 감지
try:
    user_agent = st.context.headers.get("User-Agent", "")
except:
    user_agent = ""

is_mobile = any(k in user_agent for k in ["Mobile", "Android", "iPhone"])

# 모드 선택 (기본값 자동)
mode = st.sidebar.selectbox("모드 선택", ["자동", "웹", "모바일"])

# 분기 처리
if mode == "자동":
    if is_mobile:
        st.switch_page("pages/mobile.py")
    else:
        st.switch_page("pages/web.py")

elif mode == "웹":
    st.switch_page("pages/web.py")

elif mode == "모바일":
    st.switch_page("pages/mobile.py")
