import streamlit as st

st.set_page_config(page_title="재고 시스템")

try:
    user_agent = st.context.headers.get("User-Agent", "")
except:
    user_agent = ""

is_mobile = any(k in user_agent for k in ["Mobile", "Android", "iPhone"])

mode = st.sidebar.selectbox("모드 선택", ["자동", "웹", "모바일"])

st.title("📦 재고 시스템")

if mode == "자동":
    st.write("자동 모드:", "📱 모바일" if is_mobile else "💻 웹")
    
    if st.button("페이지 이동"):
        if is_mobile:
            st.switch_page("pages/mobile.py")
        else:
            st.switch_page("pages/web.py")

elif mode == "웹":
    st.switch_page("pages/web.py")

elif mode == "모바일":
    st.switch_page("pages/mobile.py")
