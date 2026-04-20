import streamlit as st


st.title("음식 퀴즈")
st.write("학번: 2022204048  이름: 임재영")


user_data = [
    {"user_id": "admin", "password": "1234"},
    {"user_id": "user1", "password": "pass1"},
]


login_tab, quiz_tab, result_tab = st.tabs(["로그인", "퀴즈", "결과"])

with login_tab:
    st.subheader("로그인")

    username = st.text_input("아이디를 입력하세요", key="login_id")
    password = st.text_input("비밀번호를 입력하세요", type="password", key="login_pw")

    if st.button("로그인", key="login_btn"):
        
        user = None
        for item in user_data:
            if item["user_id"] == username and item["password"] == password:
                user = item
                break

        if user is not None:
            st.success("로그인 성공!")
        else:
            st.error("아이디 또는 비밀번호가 잘못되었습니다.")

with quiz_tab:
    st.subheader("음식 퀴즈")

    st.write(f"환영합니다! 퀴즈를 시작하세요.")
    st.markdown("## 음식 잡상식 퀴즈")

with result_tab:
    st.subheader("퀴즈 결과")
