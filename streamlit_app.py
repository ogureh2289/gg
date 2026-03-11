import streamlit as st
import requests


API = "http://localhost:8000/api/v1"

TOPICS = [
    {"title": "Переменные и типы данных",  "tasks_count": 4},
    {"title": "Строки",                    "tasks_count": 5},
    {"title": "Списки",                    "tasks_count": 5},
    {"title": "Условия if/elif/else",      "tasks_count": 4},
    {"title": "Циклы for и while",         "tasks_count": 5},
    {"title": "Функции",                   "tasks_count": 6},
    {"title": "Словари и множества",       "tasks_count": 5},
    {"title": "Файлы и модули",            "tasks_count": 5},
    {"title": "Исключения и отладка",      "tasks_count": 4},
    {"title": "Классы и ООП",              "tasks_count": 6},
]

if "loaded" not in st.session_state:
    try:
        r = requests.get(f"{API}/progress", timeout=5)
        if r.status_code == 200:
            data = r.json()
            st.session_state.topic_index = data["topic_index"]
            st.session_state.task_num    = data["task_num"]
            st.session_state.tasks_done  = data["tasks_done"]
            if data["topic_index"] > 0 or data["tasks_done"] > 0:
                st.session_state.stage = "continue"
            else:
                st.session_state.stage = "theory"
        else:
            st.session_state.stage = "theory"
    except:
        st.session_state.topic_index = 0
        st.session_state.task_num    = 1
        st.session_state.tasks_done  = 0
        st.session_state.stage       = "theory"
    st.session_state.loaded = True

for key, val in {
    "topic_index":  0,
    "stage":        "theory",
    "messages":     [],
    "current_task": "",
    "task_num":     1,
    "tasks_done":   0,
    "ask_messages": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


def save_progress():
    try:
        requests.post(f"{API}/progress", json={
            "topic_index": st.session_state.topic_index,
            "task_num":    st.session_state.task_num,
            "tasks_done":  st.session_state.tasks_done
        }, timeout=5)
    except:
        pass


def api_post(action, **kwargs):
    try:
        r = requests.post(f"{API}/learn", json={
            "action":      action,
            "topic_index": st.session_state.topic_index,
            "task_num":    st.session_state.task_num,
            **kwargs
        }, timeout=90)
        return r.json() if r.status_code == 200 else None
    except:
        return None


def add_msg(role, text):
    st.session_state.messages.append({"role": role, "text": text})


with st.sidebar:
    idx = st.session_state.topic_index
    topic = TOPICS[idx]
    tasks_count = topic["tasks_count"]
    done = st.session_state.tasks_done

    st.markdown(f"**Тема {idx+1}/{len(TOPICS)}:** {topic['title']}")
    st.progress(idx / len(TOPICS))
    st.caption(f"Заданий выполнено: {done}/{tasks_count}")
    st.progress(done / tasks_count)
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

    st.divider()
    if st.button("Начать заново", use_container_width=True):
        for key, val in {
            "topic_index": 0, "stage": "theory", "messages": [],
            "current_task": "", "task_num": 1, "tasks_done": 0, "ask_messages": []
        }.items():
            st.session_state[key] = val
        save_progress()
        st.rerun()


col_learn, col_ask = st.columns([2, 1])

with col_learn:
    st.title(f"Тема {idx+1}: {topic['title']}")
    if st.session_state.stage == "repeat":
        st.info(f"Повторение темы **{topic['title']}**")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Читать теорию снова", use_container_width=True):
                with st.spinner("Загружаю теорию..."):
                    data = api_post("theory")
                if data:
                    add_msg("bot", data["text"])
                    st.session_state.stage = "wait_homework"
                st.rerun()
        with c2:
            if st.button("✏️ Сразу к заданиям", use_container_width=True):
                st.session_state.stage = "wait_homework"
                st.rerun()
        if st.button("Вернуться к текущей теме", use_container_width=True):
            saved = requests.get(f"{API}/progress").json()
            st.session_state.topic_index = saved["topic_index"]
            st.session_state.task_num = saved["task_num"]
            st.session_state.tasks_done = saved["tasks_done"]
            st.session_state.stage = "continue"
            st.session_state.messages = []
            st.rerun()
    if st.session_state.stage == "continue":
        st.info(f"Добро пожаловать! Вы продолжаете тему **{topic['title']}**\n\nВыполнено заданий: **{done}/{tasks_count}**")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Продолжить", use_container_width=True):
                st.session_state.stage = "wait_homework"
                st.rerun()
        with c2:
            if st.button("Начать тему заново", use_container_width=True):
                st.session_state.messages     = []
                st.session_state.current_task = ""
                st.session_state.task_num     = 1
                st.session_state.tasks_done   = 0
                st.session_state.stage        = "theory"
                save_progress()
                st.rerun()

    if st.session_state.stage == "theory" and not st.session_state.messages:
        if st.button("Начать изучение", use_container_width=True):
            with st.spinner("Загружаю теорию..."):
                data = api_post("theory")
            if data:
                add_msg("bot", data["text"])
                st.session_state.stage = "wait_homework"
            else:
                st.error("Сервер недоступен")
            st.rerun()

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**Вы:** {msg['text']}")
        else:
            st.markdown(msg["text"])
        st.divider()

    if st.session_state.stage == "wait_homework":
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✏Получить задание", use_container_width=True):
                with st.spinner("Генерирую задание..."):
                    data = api_post("homework")
                if data:
                    st.session_state.current_task = data["task"]
                    add_msg("bot", f"**Задание {st.session_state.task_num}/{tasks_count}:**\n\n{data['task']}")
                    st.session_state.stage = "homework"
                st.rerun()
        with c2:
            if st.button(" Объясни подробнее", use_container_width=True):
                with st.spinner("Объясняю подробнее..."):
                    data = api_post("theory_detailed")
                if data:
                    add_msg("bot", f"**Подробное объяснение:**\n\n{data['text']}")
                st.rerun()

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
                        if st.session_state.tasks_done >= tasks_count:
                            st.session_state.stage = "passed"
                        else:
                            st.session_state.task_num += 1
                            st.session_state.stage = "next_task"
                        save_progress()
                st.rerun()
            else:
                st.warning("Напишите ответ!")

    if st.session_state.stage == "next_task":
        st.success(f"Задание {st.session_state.task_num - 1} выполнено! Осталось: {tasks_count - st.session_state.tasks_done}")
        if st.button(" Следующее задание", use_container_width=True):
            with st.spinner("Генерирую задание..."):
                data = api_post("homework")
            if data:
                st.session_state.current_task = data["task"]
                add_msg("bot", f"**Задание {st.session_state.task_num}/{tasks_count}:**\n\n{data['task']}")
                st.session_state.stage = "homework"
            st.rerun()

    if st.session_state.stage == "passed":
        if st.session_state.topic_index + 1 < len(TOPICS):
            st.success(f"Все {tasks_count} заданий выполнены! Тема пройдена!")
            if st.button(" Следующая тема", use_container_width=True):
                st.session_state.topic_index += 1
                st.session_state.stage        = "theory"
                st.session_state.messages     = []
                st.session_state.current_task = ""
                st.session_state.task_num     = 1
                st.session_state.tasks_done   = 0
                save_progress()
                st.rerun()
        else:
            st.balloons()
            st.success("Поздравляем! Вы прошли весь курс Python!")

with col_ask:
    st.markdown("Задать вопрос")
    st.caption("Не понимаешь что-то? Спроси здесь")

    for msg in st.session_state.ask_messages:
        if msg["role"] == "user":
            st.markdown(f"**Вы:** {msg['text']}")
        else:
            st.markdown(msg["text"])
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
        else:
            st.warning("Введите вопрос!")

    if st.session_state.ask_messages:
        if st.button("Очистить", use_container_width=True):
            st.session_state.ask_messages = []
            st.rerun()