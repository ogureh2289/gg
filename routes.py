from fastapi import APIRouter, HTTPException
import traceback
from pydantic import BaseModel
from typing import Optional
from .llm_service import AetherService, TOPICS
from .progress import load_progress, save_progress

router = APIRouter()
service = AetherService()


class LearnRequest(BaseModel):
    action: str
    topic_index: int = 0
    task_num: int = 1
    task: Optional[str] = None
    user_answer: Optional[str] = None
    question: Optional[str] = None

class ProgressData(BaseModel):
    topic_index: int
    task_num: int
    tasks_done: int


@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/progress")
async def get_progress():
    return load_progress()

@router.post("/progress")
async def set_progress(data: ProgressData):
    save_progress(data.dict())
    return {"status": "ok"}

@router.get("/topics")
async def get_topics():
    return {"topics": [{"title": t["title"], "tasks_count": t["tasks_count"]} for t in TOPICS]}

@router.post("/learn")
async def learn(req: LearnRequest):
    try:
        topic = TOPICS[req.topic_index] if req.topic_index < len(TOPICS) else TOPICS[-1]

        if req.action == "theory":
            text = service.get_theory(req.topic_index)
            return {"type": "theory", "topic": topic["title"], "text": text}

        elif req.action == "theory_detailed":
            text = service.get_theory_detailed(req.topic_index)
            return {"type": "theory_detailed", "topic": topic["title"], "text": text}

        elif req.action == "homework":
            task = service.get_homework(req.topic_index, req.task_num)
            return {"type": "homework", "topic": topic["title"], "task": task}

        elif req.action == "check":
            result = service.check_homework(topic["title"], req.task, req.user_answer)
            return {"type": "check", "topic": topic["title"], **result}

        elif req.action == "ask":
            answer = service.ask_question(topic["title"], req.question)
            return {"type": "ask", "topic": topic["title"], "answer": answer}

        else:
            raise HTTPException(status_code=400, detail="Неизвестный action")

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))