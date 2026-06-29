# ===== FASTAPI BACKEND SERVER =====
# File: main.py
# Mô tả: API server chính xử lý request từ frontend Next.js và trả về response từ chatbot RAG (Retrieval-Augmented Generation)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
from anyio import to_thread

from chat import chatbot

# ===== CẤU HÌNH LOGGING =====
logging.basicConfig(level=logging.INFO)

# ===== KHỞI TẠO FASTAPI APP =====
app = FastAPI(title="AIP491 Backend")

# ===== CẤU HÌNH CORS (Cross-Origin Resource Sharing) =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",  # Frontend phát triển local
        "http://localhost:3000",   
    ],
    allow_credentials=True,  
    allow_methods=["*"],     
    allow_headers=["*"],     
)

# class Message:
#     def __init__(self, role, content):
#         self.role = role
#         self.content = content

# # Sử dụng:
# msg = Message(role="user", content="xin chào")

# ===== ĐỊNH NGHĨA DATA SCHEMAS (Pydantic Models) =====
class Message(BaseModel):
    """Schema cho một tin nhắn trong cuộc hội thoại"""
    role: str      # "user" (người dùng) hoặc "assistant" (trợ lý)
    content: str   

class RequestData(BaseModel):
    """Schema cho request body từ frontend"""
    messages: List[Message]           
    language: Optional[str] = "vi"    

# ===== HEALTH CHECK ENDPOINT =====
@app.get("/ping")
def ping():
    """Kiểm tra server có đang hoạt động không"""
    return {"ok": True}

# ===== MAIN CHATBOT ENDPOINT =====
@app.post("/process")
async def process_messages(request_data: RequestData):
    """
    Endpoint chính xử lý request chatbot từ frontend.
    
    Quy trình xử lý:
    1. Nhận toàn bộ lịch sử hội thoại từ frontend
    2. Chuyển đổi sang định dạng phù hợp với module chatbot
    3. Gọi hàm chatbot() để xử lý (RAG pipeline)
    4. Trả về câu trả lời cho frontend
    
    Tham số:
        request_data (RequestData): Đối tượng chứa messages và language
        
    Trả về:
        dict: {"answer": str} - Câu trả lời từ chatbot
        
    Ngoại lệ:
        HTTPException: 500 nếu có lỗi trong quá trình xử lý
    """
    try:
        # Chuyển đổi Pydantic models thành list of dicts
        messages = [{"role": m.role, "content": m.content} for m in request_data.messages]
        language = request_data.language or "vi"

        logging.info(f"Received messages: {messages}")

        # Chạy chatbot trong thread riêng (convert sync function -> async)
        # Lý do: chatbot() là hàm sync nhưng FastAPI endpoint là async
        # to_thread.run_sync giúp chạy sync code mà không block event loop
        result = await to_thread.run_sync(chatbot, messages, language)

        # Đảm bảo result là string (phòng trường hợp chatbot trả về kiểu khác)
        if not isinstance(result, str):
            result = str(result)

        # Trả về JSON response cho frontend
        return {"answer": result}

    except Exception as e:
        # Log đầy đủ stack trace để debug
        logging.exception("Error inside /process")
        # Trả về HTTP 500 với thông báo lỗi
        raise HTTPException(status_code=500, detail=str(e))

# ===== KHỞI CHẠY SERVER =====
if __name__ == "__main__":
    import uvicorn
    # Chạy server tại localhost:8000
    # reload=False: không tự động reload khi code thay đổi (dùng cho production)
    # Đổi reload=True nếu muốn auto-reload khi dev
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)




