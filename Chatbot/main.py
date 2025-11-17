# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
from anyio import to_thread

from chat import chatbot

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
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


# # main.py
# from typing import List, Optional, Literal
# import asyncio, os, traceback
# from fastapi import FastAPI, HTTPException, Request
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from anyio import to_thread
# from chat import chatbot  # <- giữ nguyên

# app = FastAPI(title="AIP491 Backend", version="1.0")

# # ===== CORS =====
# ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ===== Schemas =====
# class Message(BaseModel):
#     role: Literal["user", "assistant", "system"] = Field(..., description="message role")
#     content: str

# class RequestData(BaseModel):
#     messages: List[Message]
#     language: Optional[str] = "vi"

# class ChatResponse(BaseModel):
#     answer: str

# # ===== Simple logging =====
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     try:
#         response = await call_next(request)
#         return response
#     finally:
#         # đơn giản: method + path + status
#         # có thể thêm thời gian xử lý nếu muốn
#         try:
#             print(f"{request.method} {request.url.path} -> {getattr(response,'status_code', 'NA')}")
#         except Exception:
#             pass

# # ===== Health =====
# @app.get("/ping")
# def ping():
#     return {"ok": True, "service": "AIP491 backend"}

# @app.get("/")
# def root():
#     return {"ok": True, "service": "AIP491 backend", "endpoints": ["/ping", "/process"]}

# # ===== Main endpoint =====
# CHATBOT_TIMEOUT_S = int(os.getenv("CHATBOT_TIMEOUT_S", "120"))  # 120s mặc định

# @app.post("/process", response_model=ChatResponse)
# async def process_messages(request_data: RequestData):
#     messages = [{"role": m.role, "content": m.content} for m in request_data.messages]
#     language = (request_data.language or "vi").strip() or "vi"

#     if not messages:
#         raise HTTPException(status_code=400, detail="messages must be a non-empty array")

#     try:
#         # Nếu chatbot là sync: chạy trong thread + timeout
#         result = await asyncio.wait_for(
#             to_thread.run_sync(chatbot, messages, language),
#             timeout=CHATBOT_TIMEOUT_S,
#         )
#         # Nếu chatbot của bạn là async: dùng thẳng
#         # result = await asyncio.wait_for(chatbot(messages, language), timeout=CHATBOT_TIMEOUT_S)

#     except asyncio.TimeoutError:
#         raise HTTPException(status_code=504, detail=f"chatbot timeout after {CHATBOT_TIMEOUT_S}s")
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"chatbot error: {e}")

#     if not isinstance(result, str):
#         result = str(result)

#     return ChatResponse(answer=result)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
