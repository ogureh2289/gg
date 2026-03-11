import os
from typing import Dict, List
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

TOPICS = [
    {
        "title": "Переменные и типы данных",
        "subtopics": ["int, float, str, bool", "Операции с числами", "Преобразование типов", "Константы"],
        "tasks_count": 4
    },
    {
        "title": "Строки",
        "subtopics": ["Методы строк", "Срезы", "Форматирование f-строки", "Поиск в строке", "Разбивка и объединение"],
        "tasks_count": 5
    },
    {
        "title": "Списки",
        "subtopics": ["Создание и индексы", "Методы списков", "Срезы", "Вложенные списки", "List comprehension"],
        "tasks_count": 5
    },
    {
        "title": "Условия if/elif/else",
        "subtopics": ["Операторы сравнения", "Логические операторы", "Вложенные условия", "Тернарный оператор"],
        "tasks_count": 4
    },
    {
        "title": "Циклы for и while",
        "subtopics": ["Цикл for + range", "Цикл while", "break и continue", "Вложенные циклы", "Перебор списков"],
        "tasks_count": 5
    },
    {
        "title": "Функции",
        "subtopics": ["def и return", "Аргументы и параметры", "Значения по умолчанию", "args и kwargs", "Рекурсия", "Lambda"],
        "tasks_count": 6
    },
    {
        "title": "Словари и множества",
        "subtopics": ["Создание словаря", "Методы словаря", "Перебор словаря", "Множества set", "Dict comprehension"],
        "tasks_count": 5
    },
    {
        "title": "Файлы и модули",
        "subtopics": ["Чтение файлов", "Запись в файлы", "Модуль os", "Модуль json", "import и создание модуля"],
        "tasks_count": 5
    },
    {
        "title": "Исключения и отладка",
        "subtopics": ["try/except", "Несколько исключений", "finally", "Свои исключения raise", "Логирование"],
        "tasks_count": 4
    },
    {
        "title": "Классы и ООП",
        "subtopics": ["Класс и объект", "__init__", "Методы", "Наследование", "Инкапсуляция", "Полиморфизм"],
        "tasks_count": 6
    },
]


class AetherService:
    def __init__(self):
        api_key = os.environ.get("GIGACHAT_API_KEY")
        if not api_key:
            raise ValueError("Не найден GIGACHAT_API_KEY!")
        self.api_key = api_key
        print("GigaChat готов к работе!")

    def _chat(self, messages):
        with GigaChat(credentials=self.api_key, verify_ssl_certs=False) as giga:
            response = giga.chat(Chat(messages=messages, temperature=0.7, max_tokens=2048))
        return response.choices[0].message.content

    def get_theory(self, topic_index: int) -> str:
        topic = TOPICS[topic_index]
        subtopics = ", ".join(topic["subtopics"])
        messages = [
            Messages(role=MessagesRole.SYSTEM, content="Ты — преподаватель Python для новичков. Объясняй подробно, с примерами кода."),
            Messages(role=MessagesRole.USER, content=(
                f"Объясни тему '{topic['title']}' для новичка.\n"
                f"Обязательно покрой эти подтемы: {subtopics}\n"
                f"Для каждой подтемы дай объяснение и пример кода в блоке ```python.\n"
                f"В конце напиши: 'Готов к заданиям? Нажми кнопку ниже!'"
            ))
        ]
        return self._chat(messages)

    def get_theory_detailed(self, topic_index: int) -> str:
        topic = TOPICS[topic_index]
        messages = [
            Messages(role=MessagesRole.SYSTEM, content="Ты — преподаватель Python. Объясняй очень подробно с аналогиями."),
            Messages(role=MessagesRole.USER, content=(
                f"Объясни тему '{topic['title']}' ещё раз но намного подробнее.\n"
                f"Используй простые аналогии из жизни.\n"
                f"Добавь больше примеров кода.\n"
                f"Объясни типичные ошибки новичков по этой теме."
            ))
        ]
        return self._chat(messages)

    def get_homework(self, topic_index: int, task_num: int) -> str:
        topic = TOPICS[topic_index]
        subtopics = topic["subtopics"]
        subtopic = subtopics[(task_num - 1) % len(subtopics)]
        messages = [
            Messages(role=MessagesRole.SYSTEM, content="Ты — преподаватель Python. Давай практические задания."),
            Messages(role=MessagesRole.USER, content=(
                f"Тема: '{topic['title']}'\n"
                f"Подтема: '{subtopic}'\n"
                f"Это задание №{task_num}. Придумай уникальное задание именно по подтеме '{subtopic}'.\n"
                f"ВАЖНО: используй ТОЛЬКО то что есть в этой подтеме. Не используй if/else, циклы, функции или другие темы которые ещё не изучались.\n"
                f"Сложность: {'лёгкая' if task_num <= 2 else 'средняя' if task_num <= 4 else 'высокая'}.\n"
                f"Только формулировка задания — без решения."
            ))
        ]
        return self._chat(messages)

    def check_homework(self, topic: str, task: str, user_answer: str) -> Dict:
        messages = [
            Messages(role=MessagesRole.SYSTEM, content="Ты — преподаватель Python. Проверяй задания доброжелательно."),
            Messages(role=MessagesRole.USER, content=(
                f"Тема: {topic}\n"
                f"Задание: {task}\n"
                f"Ответ ученика: {user_answer}\n\n"
                f"Проверь ответ. Если правильно или близко к правильному — похвали и напиши ЗАЧЕТ.\n"
                f"Если неправильно — объясни ошибку, дай подсказку, попроси попробовать ещё раз.\n"
                f"Не давай готовый ответ."
            ))
        ]
        result = self._chat(messages)
        passed = "ЗАЧЕТ" in result.upper() or "ЗАЧЁТ" in result.upper()
        return {"feedback": result, "passed": passed}

    def ask_question(self, topic: str, question: str) -> str:
        messages = [
            Messages(role=MessagesRole.SYSTEM, content=(
                f"Ты — преподаватель Python. Ученик изучает тему '{topic}'. "
                f"Отвечай понятно, с примерами кода."
            )),
            Messages(role=MessagesRole.USER, content=question)
        ]
        return self._chat(messages)

    def generate_answer(self, question: str) -> Dict:
        return {"answer": question, "sources": [], "related_topics": [], "recommended_resources": []}


TinyLlamaService = AetherService