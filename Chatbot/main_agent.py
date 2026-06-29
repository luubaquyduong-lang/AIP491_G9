"""FastAPI backend that uses the tool-calling travel agent.

This is a copy of the original backend entrypoint, adapted to call
`run_travel_agent` so the Next.js frontend can keep using `/process`.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
from anyio import to_thread

from agent_with_tools import run_travel_agent


logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AIP491 Backend - Agent Mode")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    """Schema cho một tin nhắn trong cuộc hội thoại."""

    role: str
    content: str


class RequestData(BaseModel):
    """Schema cho request body từ frontend."""

    messages: List[Message]
    language: Optional[str] = "vi"


@app.get("/ping")
def ping():
    """Kiểm tra server có đang hoạt động không."""

    return {"ok": True}


@app.post("/process")
async def process_messages(request_data: RequestData):
    """Xử lý request chatbot từ frontend bằng tool-calling agent."""

    try:
        messages = [{"role": m.role, "content": m.content} for m in request_data.messages]
        language = request_data.language or "vi"

        logging.info("Received messages: %s", messages)

        user_query = ""
        for message in reversed(messages):
            if message["role"] == "user":
                user_query = message["content"]
                break

        if not user_query and messages:
            user_query = messages[-1]["content"]

        result = await to_thread.run_sync(run_travel_agent, user_query, language)

        if not isinstance(result, str):
            result = str(result)

        return {"answer": result}

    except Exception as e:
        logging.exception("Error inside /process")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main_agent:app", host="127.0.0.1", port=8000, reload=False)