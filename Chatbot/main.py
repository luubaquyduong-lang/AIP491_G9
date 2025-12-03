# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
from anyio import to_thread

from chat_new import chatbot

# ===== Logging =====
logging.basicConfig(level=logging.INFO)

# ===== FastAPI app =====
app = FastAPI(title="AIP491 Backend")

# ===== CORS =====
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

# ===== Data schemas =====
class Message(BaseModel):
    role: str
    content: str

class RequestData(BaseModel):
    messages: List[Message]
    language: Optional[str] = "vi"

@app.get("/ping")
def ping():
    return {"ok": True}

# ===== MAIN CHATBOT ENDPOINT =====
@app.post("/process")
async def process_messages(request_data: RequestData):
    try:
        messages = [{"role": m.role, "content": m.content} for m in request_data.messages]
        language = request_data.language or "vi"

        logging.info(f"Received messages: {messages}")

        # Chạy chatbot trong thread (sync -> async)
        result = await to_thread.run_sync(chatbot, messages, language)

        if not isinstance(result, str):
            result = str(result)

        return {"answer": result}

    except Exception as e:
        logging.exception("Error inside /process")
        raise HTTPException(status_code=500, detail=str(e))

# ===== RUN SERVER =====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)




