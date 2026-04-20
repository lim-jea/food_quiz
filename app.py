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
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

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

    if st.button("회원가입 창 열기", key="open_signup"):
        st.session_state.show_signup = True

    if st.session_state.show_signup:
        st.markdown("---")
        st.subheader("회원가입")

        new_username = st.text_input("새 아이디를 입력하세요", key="signup_id")
        new_password = st.text_input("새 비밀번호를 입력하세요", type="password", key="signup_pw")
        confirm_password = st.text_input("비밀번호를 다시 입력하세요", type="password", key="signup_pw_check")

        if st.button("회원가입 완료", key="signup_done"):
            user_data = load_user_data()
            duplicated = any(user["user_id"] == new_username for user in user_data)

            if new_username == "":
                st.error("아이디를 입력해주세요.")
            elif new_password == "":
                st.error("비밀번호를 입력해주세요.")
            elif new_password != confirm_password:
                st.error("비밀번호가 일치하지 않습니다.")
            elif duplicated:
                st.error("이미 존재하는 아이디입니다.")
            else:
                user_data.append(
                    {
                        "user_id": new_username,
                        "password": new_password
                    }
                )
                save_user_data(user_data)
                st.success("회원가입이 완료되었습니다!")
                st.session_state.user = new_username
                st.session_state.password = new_password
                st.session_state.show_signup = False
                
                user_data = load_user_data()
                updated = False

                for user in user_data:
                    if user["user_id"] != username:
                        continue
                    break

                if updated:
                    save_user_data(user_data)

        if st.button("회원가입 창 닫기", key="close_signup"):
            st.session_state.show_signup = False

with quiz_tab:
    st.subheader("음식 퀴즈")

    st.write(f"환영합니다! 퀴즈를 시작하세요.")
    st.markdown("## 음식 잡상식 퀴즈")

with result_tab:
    st.subheader("퀴즈 결과")
