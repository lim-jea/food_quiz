import streamlit as st
import json


st.title("음식 퀴즈")
st.write("학번: 2022204048  이름: 임재영")


def load_user_data():
    with open("data/user_data.json", "r", encoding="utf-8") as user_file:
        return json.load(user_file)


def save_user_data(user_data):
    with open("data/user_data.json", "w", encoding="utf-8") as user_file:
        json.dump(user_data, user_file, ensure_ascii=False, indent=4)


if "user" not in st.session_state:
    st.session_state.user = None
if "password" not in st.session_state:
    st.session_state.password = None

login_tab, quiz_tab, result_tab = st.tabs(["로그인", "퀴즈", "결과"])

with login_tab:
    st.subheader("로그인")

    if st.session_state.user is not None:
        st.success(f"이미 로그인된 사용자: {st.session_state.user}")

    username = st.text_input("아이디를 입력하세요", key="login_id")
    password = st.text_input("비밀번호를 입력하세요", type="password", key="login_pw")

    if st.button("로그인", key="login_btn"):
        user_data = load_user_data()
        user = None
        for item in user_data:
            if item["user_id"] == username and item["password"] == password:
                user = item
                break

        if user is not None:
            st.success("로그인 성공!")
            st.session_state.user = username
            st.session_state.password = password
        else:
            st.error("아이디 또는 비밀번호가 잘못되었습니다.")


with quiz_tab:
    st.subheader("음식 퀴즈")

    st.write(f"환영합니다! 퀴즈를 시작하세요.")
    st.markdown("## 음식 잡상식 퀴즈")

with result_tab:
    st.subheader("퀴즈 결과")
