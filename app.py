import streamlit as st
import json
import matplotlib.pyplot as plt
from pathlib import Path
import random



st.title("음식 퀴즈")
st.write("학번: 2022204048  이름: 임재영")


@st.cache_data
def load_quiz_data():
    with open("data/quiz_data.json", "r", encoding="utf-8") as quiz_file:
        return json.load(quiz_file)


@st.cache_resource
def build_image_cache():
    cache = {}
    for question in QUIZ_QUESTIONS:
        image_path = get_local_image_path(question)
        if image_path is not None and image_path.exists():
            cache[question["id"]] = image_path.read_bytes()
    return cache


def load_user_data():
    with open("data/user_data.json", "r", encoding="utf-8") as user_file:
        return json.load(user_file)


def save_user_data(user_data):
    with open("data/user_data.json", "w", encoding="utf-8") as user_file:
        json.dump(user_data, user_file, ensure_ascii=False, indent=4)


QUIZ_QUESTIONS = load_quiz_data()
IMAGE_DIR = Path("data/images")


if "user" not in st.session_state:
    st.session_state.user = None
if "password" not in st.session_state:
    st.session_state.password = None
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {
        question["id"]: {"selected": None, "is_correct": None}
        for question in QUIZ_QUESTIONS
    }
if "quiz_options_order" not in st.session_state:
    st.session_state.quiz_options_order = {}

for question in QUIZ_QUESTIONS:
    if question["id"] not in st.session_state.quiz_options_order:
        shuffled_options = question["options"][:]
        random.shuffle(shuffled_options)
        st.session_state.quiz_options_order[question["id"]] = shuffled_options


def reset_quiz(clear_saved_result=False):
    st.session_state.current_question_index = 0
    st.session_state.quiz_completed = False
    st.session_state.quiz_answers = {
        question["id"]: {"selected": None, "is_correct": None}
        for question in QUIZ_QUESTIONS
    }
    st.session_state.quiz_options_order = {}
    for question in QUIZ_QUESTIONS:
        shuffled_options = question["options"][:]
        random.shuffle(shuffled_options)
        st.session_state.quiz_options_order[question["id"]] = shuffled_options

    if clear_saved_result and st.session_state.user is not None:
        user_data = load_user_data()
        for user in user_data:
            if user["user_id"] == st.session_state.user:
                user["quiz_result"] = {
                    question["id"]: None for question in QUIZ_QUESTIONS
                }
                user["score"] = 0
                break
        save_user_data(user_data)
        
def save_result():
    if st.session_state.user is None:
        return

    quiz_result = {
        question["id"]: st.session_state.quiz_answers[question["id"]]["is_correct"]
        for question in QUIZ_QUESTIONS
    }
    score = sum(1 for result in quiz_result.values() if result is True)

    user_data = load_user_data()
    for user in user_data:
        if user["user_id"] == st.session_state.user:
            user["quiz_result"] = quiz_result
            user["score"] = score
            break
    save_user_data(user_data)


def get_local_image_path(question):
    image_value = question["image"]
    image_path = Path(image_value)
    if image_path.exists():
        return image_path

    for local_path in IMAGE_DIR.glob(f"{question['id']}.*"):
        if local_path.exists():
            return local_path

    return None


def get_cached_image(question_id):
    return build_image_cache().get(question_id)



def render_result_chart(correct_count, wrong_count):
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["Correct", "Wrong"]
    values = [correct_count, wrong_count]
    colors = ["#2E8B57", "#D9534F"]

    bars = ax.bar(labels, values, color=colors)
    ax.set_title("Quiz Result")
    ax.set_ylabel("Question Count")
    ax.set_ylim(0, len(QUIZ_QUESTIONS))

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.1,
            str(value),
            ha="center",
            va="bottom",
        )

    st.pyplot(fig)
    plt.close(fig)


def render_question_accuracy_chart(user_data):
    question_labels = [f"Q{index}" for index, _ in enumerate(QUIZ_QUESTIONS, start=1)]
    correct_rates = []
    wrong_rates = []

    for question in QUIZ_QUESTIONS:
        results = [
            user.get("quiz_result", {}).get(question["id"])
            for user in user_data
            if user.get("quiz_result", {}).get(question["id"]) is not None
        ]

        if results:
            total = len(results)
            correct_count = sum(1 for result in results if result is True)
            wrong_count = sum(1 for result in results if result is False)
            correct_rates.append(correct_count / total * 100)
            wrong_rates.append(wrong_count / total * 100)
        else:
            correct_rates.append(0)
            wrong_rates.append(0)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(question_labels, correct_rates, color="#2E8B57", label="Correct %")
    ax.bar(
        question_labels,
        wrong_rates,
        bottom=correct_rates,
        color="#D9534F",
        label="Wrong %",
    )
    ax.set_title("Per-Question Accuracy")
    ax.set_ylabel("Percentage")
    ax.set_ylim(0, 100)
    ax.legend()

    st.pyplot(fig)
    plt.close(fig)


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

    if st.session_state.user is None:
        st.warning("로그인이 필요합니다. 로그인 탭에서 로그인해주세요.")
    else:
        answered_count = sum(
            1 for answer in st.session_state.quiz_answers.values()
            if answer["selected"] is not None
        )
        correct_count = sum(
            1 for answer in st.session_state.quiz_answers.values()
            if answer["is_correct"] is True
        )
        total_questions = len(QUIZ_QUESTIONS)
        progress_ratio = answered_count / total_questions if total_questions else 0

        st.write(f"환영합니다, {st.session_state.user}님! 퀴즈를 시작하세요.")
        st.markdown("## 음식 잡상식 퀴즈")
        st.write(f"현재 진행도: **{answered_count} / {total_questions}**")
        st.write(f"현재 정답 수: **{correct_count} / {total_questions}**")
        st.progress(progress_ratio)

        if st.session_state.quiz_completed:
            st.success("모든 문제를 완료했습니다. 결과 탭에서 확인해주세요.")
            if st.button("다시 풀기", key="restart_quiz_in_quiz_tab"):
                reset_quiz(clear_saved_result=True)
                st.rerun()
        else:
            current_index = st.session_state.current_question_index
            if current_index >= total_questions:
                current_index = total_questions - 1
                st.session_state.current_question_index = current_index
            question = QUIZ_QUESTIONS[current_index]

            st.write(f"현재 문제: **{current_index + 1} / {total_questions}**")

            with st.expander(question["title"], expanded=True):
                cached_image = get_cached_image(question["id"])
                if cached_image is not None:
                    st.image(cached_image, width=400)
                else:
                    st.warning("이미지 캐시 파일이 없습니다.")
                st.caption(question["caption"])
                st.markdown(f"### {question['question']}")

                selected_option = st.radio(
                    "정답을 선택하세요:",
                    st.session_state.quiz_options_order[question["id"]],
                    key=f"quiz_answer_{question['id']}",
                )

                if st.button("다음 문제로", key=f"submit_{question['id']}"):
                    is_correct = selected_option == question["answer"]
                    st.session_state.quiz_answers[question["id"]] = {
                        "selected": selected_option,
                        "is_correct": is_correct,
                    }

                    if current_index + 1 < total_questions:
                        st.session_state.current_question_index += 1
                    else:
                        st.session_state.quiz_completed = True
                        save_result()

                    st.rerun()
with result_tab:
    st.subheader("퀴즈 결과")

    if st.session_state.user is None:
        st.warning("로그인이 필요합니다. 로그인 탭에서 로그인해주세요.")
    else:
        answered_count = sum(
            1 for answer in st.session_state.quiz_answers.values()
            if answer["is_correct"] is not None
        )
        if answered_count == 0:
            st.warning("퀴즈를 풀거나 저장된 결과가 있으면 여기에 표시됩니다.")
            st.stop()

        total_questions = len(QUIZ_QUESTIONS)
        correct_count = sum(
            1 for answer in st.session_state.quiz_answers.values()
            if answer["is_correct"] is True
        )
        wrong_count = answered_count - correct_count

        if st.session_state.quiz_completed:
            st.write(f"최종 점수: **{correct_count} / {total_questions}**")
        else:
            st.info("저장된 진행 결과를 보여주는 중입니다.")
            st.write(f"현재 결과: **{correct_count} / {answered_count}**")

        render_result_chart(correct_count, wrong_count)
        st.markdown("### Question Accuracy")
        render_question_accuracy_chart(load_user_data())

        if st.session_state.quiz_completed and correct_count >= 9:
            st.write("당신은 음식 문화 탐험가입니다!")
        elif st.session_state.quiz_completed and correct_count >= 6:
            st.write("음식 상식이 꽤 풍부하네요!")
        elif st.session_state.quiz_completed:
            st.write("다음에는 더 높은 점수에 도전해보세요!")

        st.markdown("### 문제별 결과")
        for index, question in enumerate(QUIZ_QUESTIONS, start=1):
            user_answer = st.session_state.quiz_answers[question["id"]]
            if user_answer["is_correct"] is None:
                continue
            status = "정답" if user_answer["is_correct"] else "오답"
            st.write(
                f"{index}. {question['question']}  \n"
                f"- 선택한 답: {user_answer['selected']}  \n"
                f"- 정답: {question['answer']}  \n"
                f"- 결과: {status}"
            )

        if st.button("다시 풀기", key="restart_quiz_in_result_tab"):
            reset_quiz(clear_saved_result=True)
            st.rerun()
