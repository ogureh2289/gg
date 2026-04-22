import streamlit as st
import requests
from db import init_db, register_user, verify_user

init_db()
API = "http://localhost:8000/api/v1"

TOPICS = [
    {"title": "Переменные и типы данных", "tasks_count": 4},
    {"title": "Строки", "tasks_count": 5},
    {"title": "Списки", "tasks_count": 5},
    {"title": "Условия if/elif/else", "tasks_count": 4},
    {"title": "Циклы for и while", "tasks_count": 5},
    {"title": "Функции", "tasks_count": 6},
    {"title": "Словари и множества", "tasks_count": 5},
    {"title": "Файлы и модули", "tasks_count": 5},
    {"title": "Исключения и отладка", "tasks_count": 4},
    {"title": "Классы и ООП", "tasks_count": 6},
]

for key, val in {
    "username": None, "authenticated": False,
    "topic_index": 0, "stage": "theory", "messages": [],
    "current_task": "", "task_num": 1, "tasks_done": 0, "ask_messages": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


def api_post(action, **kwargs):
    try:
        r = requests.post(f"{API}/learn", json={
            "username": st.session_state.username,
            "action": action,
            "topic_index": st.session_state.topic_index,
            "task_num": st.session_state.task_num,
            **kwargs
        }, timeout=90)
        return r.json() if r.status_code == 200 else None
    except:
        return None


def api_get_progress():
    try:
        r = requests.get(f"{API}/progress", params={"username": st.session_state.username}, timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None


def add_msg(role, text):
    st.session_state.messages.append({"role": role, "text": text})



if not st.session_state.authenticated:
    st.title("Python Учитель")
    tab1, tab2 = st.tabs(["🔑 Вход", "📝 Регистрация"])

    with tab1:
        u = st.text_input("Логин")
        p = st.text_input("Пароль", type="password")
        if st.button("Войти", use_container_width=True):
            if verify_user(u, p):
                st.session_state.username = u
                st.session_state.authenticated = True
                prog = api_get_progress()
                if prog:
                    st.session_state.topic_index = prog["topic_index"]
                    st.session_state.task_num = prog["task_num"]
                    st.session_state.tasks_done = prog["tasks_done"]
                    st.session_state.stage = "continue" if prog["tasks_done"] > 0 else "theory"
                st.rerun()
            else:
                st.error("Неверный логин или пароль")

    with tab2:
        u = st.text_input("Придумайте логин")
        n = st.text_input("Ваше имя")
        p = st.text_input("Придумайте пароль", type="password")
        if st.button("Зарегистрироваться", use_container_width=True):
            if not u or not n or not p:
                st.warning("Заполните все поля")
            else:
                if register_user(u, n, p):
                    st.success("Регистрация успешна! Войдите в систему.")
                else:
                    st.error("Этот логин уже занят")
    st.stop()


idx = st.session_state.topic_index
topic = TOPICS[idx]
tasks_count = topic["tasks_count"]
done = st.session_state.tasks_done

with st.sidebar:
    st.markdown(f"**👤 {st.session_state.username}**")
    st.markdown(f"**Тема {idx + 1}/{len(TOPICS)}:** {topic['title']}")
    st.progress(idx / len(TOPICS))
    st.caption(f"Заданий выполнено: {done}/{tasks_count}")
    st.progress(done / tasks_count)
    st.divider()
    if st.button("Выйти", use_container_width=True):
        for key in ["username", "authenticated", "topic_index", "stage", "messages", "current_task", "task_num",
                    "tasks_done", "ask_messages"]:
            st.session_state.pop(key, None)
        st.rerun()

    st.divider()
    st.markdown("**Все темы:**")
    for i, t in enumerate(TOPICS):
        if i < idx:
            if st.button(f"{i + 1}. {t['title']}", key=f"topic_{i}", use_container_width=True):
                st.session_state.topic_index = i
                st.session_state.stage = "repeat"
                st.session_state.messages = []
                st.session_state.current_task = ""
                st.session_state.task_num = 1
                st.session_state.tasks_done = 0
                st.rerun()
        elif i == idx:
            st.markdown(f"📖 **{i + 1}. {t['title']}**")
        else:
            st.markdown(f"🔒 {i + 1}. {t['title']}")

col_learn, col_ask = st.columns([2, 1])

with col_learn:
    st.title(f"Тема {idx + 1}: {topic['title']}")

    if st.session_state.stage == "repeat":
        st.info(f"Повторение темы **{topic['title']}**")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Читать теорию снова", use_container_width=True):
                with st.spinner("Загружаю теорию..."):
                    data = api_post("theory")
                    if data: add_msg("bot", data["text"]); st.session_state.stage = "wait_homework"; st.rerun()
        with c2:
            if st.button("️ Сразу к заданиям", use_container_width=True):
                st.session_state.stage = "wait_homework";
                st.rerun()

    if st.session_state.stage == "continue":
        st.info(
            f"Добро пожаловать! Вы продолжаете тему **{topic['title']}**\n\nВыполнено заданий: **{done}/{tasks_count}**")
        if st.button("Продолжить", use_container_width=True):
            st.session_state.stage = "wait_homework";
            st.rerun()

    if st.session_state.stage == "theory" and not st.session_state.messages:
        if st.button("Начать изучение", use_container_width=True):
            with st.spinner("Загружаю теорию..."):
                data = api_post("theory")
                if data:
                    add_msg("bot", data["text"]); st.session_state.stage = "wait_homework"
                else:
                    st.error("Сервер недоступен")
            st.rerun()

    for msg in st.session_state.messages:
        st.markdown(f"**{'Вы' if msg['role'] == 'user' else '🤖 Бот'}:** {msg['text']}")
        st.divider()

    if st.session_state.stage == "wait_homework":
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✏️ Получить задание", use_container_width=True):
                with st.spinner("Генерирую задание..."):
                    data = api_post("homework")
                    if data:
                        st.session_state.current_task = data["task"]
                        add_msg("bot", f"**Задание {st.session_state.task_num}/{tasks_count}:**\n\n{data['task']}")
                        st.session_state.stage = "homework";
                        st.rerun()
        with c2:
            if st.button(" Объясни подробнее", use_container_width=True):
                with st.spinner("Объясняю подробнее..."):
                    data = api_post("theory_detailed")
                    if data: add_msg("bot", f"**Подробное объяснение:**\n\n{data['text']}"); st.rerun()

    if st.session_state.stage == "homework":
        answer = st.text_area("Ваш код:", height=150, placeholder="# Напишите код здесь...")
        if st.button("Проверить", use_container_width=True):
            if answer.strip():
                add_msg("user", answer)
                with st.spinner("Проверяю..."):
                    data = api_post("check", task=st.session_state.current_task, user_answer=answer)
                    if data:
                        add_msg("bot", data["feedback"])
                        if data["passed"]:
                            st.session_state.tasks_done += 1
                            st.session_state.stage = "next_task" if st.session_state.tasks_done < tasks_count else "passed"
                        st.rerun()
                    else:
                        st.error("Ошибка проверки")
            else:
                st.warning("Напишите ответ!")

    if st.session_state.stage == "next_task":
        st.success(f" Задание выполнено! Осталось: {tasks_count - st.session_state.tasks_done}")
        if st.button("Следующее задание", use_container_width=True):
            with st.spinner("Генерирую задание..."):
                data = api_post("homework")
                if data:
                    st.session_state.current_task = data["task"]
                    st.session_state.task_num += 1
                    add_msg("bot", f"**Задание {st.session_state.task_num}/{tasks_count}:**\n\n{data['task']}")
                    st.session_state.stage = "homework";
                    st.rerun()

    if st.session_state.stage == "passed":
        st.balloons()
        st.success(f" Все {tasks_count} заданий выполнены!")
        if idx + 1 < len(TOPICS):
            if st.button("Следующая тема", use_container_width=True):
                st.session_state.topic_index += 1;
                st.session_state.stage = "theory"
                st.session_state.messages = [];
                st.session_state.current_task = ""
                st.session_state.task_num = 1;
                st.session_state.tasks_done = 0
                st.rerun()

with col_ask:
    st.markdown("Задать вопрос")
    for msg in st.session_state.ask_messages:
        st.markdown(f"**{'Вы' if msg['role'] == 'user' else '🤖 Бот'}:** {msg['text']}")
        st.divider()
    question = st.text_input("Ваш вопрос:", placeholder="Что непонятно?")
    if st.button("Спросить", use_container_width=True):
        if question.strip():
            st.session_state.ask_messages.append({"role": "user", "text": question})
            with st.spinner("Отвечаю..."):
                data = api_post("ask", question=question)
                if data:
                    st.session_state.ask_messages.append({"role": "bot", "text": data["answer"]})
                else:
                    st.session_state.ask_messages.append({"role": "bot", "text": "Сервер недоступен"})
            st.rerun()
    if st.session_state.ask_messages:
        if st.button(" Очистить", use_container_width=True):
            st.session_state.ask_messages = [];
            st.rerun()

