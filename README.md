# 🌏 Smart Tourism Chatbot for Vietnam using RAG and LLM

> **AIP491 - Final Project**: Building an intelligent chatbot for Vietnam tourism using Retrieval-Augmented Generation (RAG) and Large Language Models

## 📋 Mục lục
- [Giới thiệu](#-giới-thiệu)
- [Tính năng chính](#-tính-năng-chính)
- [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
- [Công nghệ sử dụng](#️-công-nghệ-sử-dụng)
- [Cài đặt và Cấu hình](#-cài-đặt-và-cấu-hình)
- [Hướng dẫn chạy dự án](#-hướng-dẫn-chạy-dự-án)
- [Cấu trúc thư mục](#-cấu-trúc-thư-mục)
- [API Documentation](#-api-documentation)
- [Demo và Screenshots](#-demo-và-screenshots)

---

## 🎯 Giới thiệu

Dự án xây dựng một chatbot thông minh chuyên tư vấn về du lịch Việt Nam, sử dụng công nghệ RAG (Retrieval-Augmented Generation) kết hợp với Large Language Models (LLM). Hệ thống có khả năng:

- Trả lời các câu hỏi về địa điểm du lịch, ẩm thực, văn hóa Việt Nam
- Hiểu ngữ cảnh hội thoại và duy trì lịch sử trò chuyện
- Tự động viết lại câu hỏi (Query Rewriting) để hiểu ý người dùng tốt hơn
- Truy xuất thông tin chính xác từ cơ sở dữ liệu vector (ChromaDB)
- Hỗ trợ đa ngôn ngữ (Tiếng Việt, Tiếng Anh)

---

## ✨ Tính năng chính

### 🤖 Backend (Python + FastAPI)
- **RAG Pipeline**: Kết hợp retrieval và generation để tạo câu trả lời chính xác
- **Query Rewriting**: Tự động viết lại câu hỏi dựa trên context hội thoại
- **Small Talk Detection**: Phân biệt câu hỏi chính thức và small talk
- **Context Smoothing**: Tối ưu hóa ngữ cảnh được truy xuất
- **Vector Database**: Sử dụng ChromaDB để lưu trữ và tìm kiếm embeddings
- **Fine-tuned Embedding Model**: Model embedding được fine-tune trên dữ liệu du lịch Việt Nam

### 🖥️ Frontend (Next.js + TypeScript)
- Giao diện chat hiện đại và thân thiện
- Real-time messaging
- Responsive design
- Hỗ trợ đa ngôn ngữ
- Authentication với Clerk

### 📊 Data Processing
- Thu thập dữ liệu từ nhiều nguồn: dulichviet, ivivu, vietnamtourism, vnexpress
- Xử lý và làm sạch dữ liệu
- Tạo training dataset cho fine-tuning
- Đánh giá và tối ưu hóa model

---

## 🏗️ Kiến trúc hệ thống

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │────────▶│   Backend    │────────▶│   OpenAI    │
│  (Next.js)  │  HTTP   │  (FastAPI)   │   API   │  GPT-4o-mini│
└─────────────┘         └──────────────┘         └─────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  ChromaDB    │
                        │ (Vector DB)  │
                        └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │ Fine-tuned   │
                        │ Embedding    │
                        │ Model (BKAI) │
                        └──────────────┘
```

### RAG Pipeline Flow:

1. **User Input** → Query từ người dùng
2. **Small Talk Detection** → Kiểm tra xem có phải small talk không
3. **Query Rewriting** → Viết lại câu hỏi dựa trên context
4. **Embedding** → Chuyển query thành vector
5. **Retrieval** → Tìm kiếm top-k documents liên quan từ ChromaDB
6. **Context Smoothing** → Tối ưu hóa các contexts đã retrieve
7. **Prompt Generation** → Tạo prompt cho LLM
8. **LLM Generation** → GPT-4o-mini tạo câu trả lời
9. **Response** → Trả về câu trả lời cho người dùng

---

## 🛠️ Công nghệ sử dụng

### Backend
- **Framework**: FastAPI
- **Language Model**: OpenAI GPT-4o-mini
- **Embedding Model**: Fine-tuned BKAI Foundation Model
  - Base: `bkai-foundation-models`
  - Fine-tuned version: `duongluuba/AIP491_G9_Vietnam_tourism_data_bkai-foundation-fine-tuned-v1`
- **Vector Database**: ChromaDB (Persistent)
- **Libraries**:
  - `sentence-transformers`: Tạo embeddings
  - `openai`: API client cho OpenAI
  - `chromadb`: Vector database
  - `datasets`: Load và xử lý data
  - `python-dotenv`: Quản lý environment variables
  - `uvicorn`: ASGI server

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **UI Components**: Radix UI, Tailwind CSS
- **Authentication**: Clerk
- **Database**: Prisma + MongoDB
- **State Management**: React Hooks
- **HTTP Client**: Fetch API

### Data Processing & Training
- **Data Collection**: Custom web scrapers
- **Data Processing**: Pandas, Datasets
- **Model Training**: Sentence-Transformers
- **Evaluation**: Custom metrics (Cosine Similarity, BGE Rerank)
- **Notebook Environment**: Jupyter Notebooks

---

## 📦 Cài đặt và Cấu hình

### Yêu cầu hệ thống
- Python 3.8+
- Node.js 18+
- Git
- 8GB RAM (khuyến nghị)
- GPU (tùy chọn, cho training model)

### 1. Clone repository

```bash
git clone <repository-url>
cd AIP491_FINAL/Code
```

### 2. Backend Setup

#### 2.1. Tạo môi trường ảo Python

```bash
cd Chatbot
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 2.2. Cài đặt dependencies

**Cách 1: Cài từng package**
```bash
pip install fastapi uvicorn
pip install openai chromadb sentence-transformers
pip install python-dotenv datasets
pip install anyio pydantic
```

**Cách 2: Tạo và dùng requirements.txt** (Khuyến nghị)

Tạo file `requirements.txt` trong thư mục `Chatbot/`:
```txt
fastapi==0.104.1
uvicorn==0.24.0
openai==1.3.0
chromadb==0.4.18
sentence-transformers==2.2.2
python-dotenv==1.0.0
datasets==2.14.6
anyio==4.0.0
pydantic==2.5.0
```

Sau đó cài đặt:
```bash
pip install -r requirements.txt
```

**Cách 3: Cài tất cả cùng lúc**
```bash
pip install fastapi uvicorn openai chromadb sentence-transformers python-dotenv datasets anyio pydantic
```

#### 2.3. Cấu hình Environment Variables

Tạo file `.env` trong thư mục `Chatbot/`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

#### 2.4. Chuẩn bị dữ liệu

Đảm bảo các file sau tồn tại:
- `Data/processed/data_final_train_v1/data_final_sort_v1_fisrt_se.jsonl` - Corpus data
- `Data/data_store/` - ChromaDB database

Nếu chưa có database, cần chạy script để tạo:

```bash
cd ../data_store
python chroma_db_v1.py
```

### 3. Frontend Setup

#### 3.1. Cài đặt dependencies

```bash
cd Frontend
npm install
```

#### 3.2. Cấu hình Environment Variables

Tạo file `.env.local` trong thư mục `Frontend/`:

```env
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key

# Database
DATABASE_URL=your_mongodb_connection_string

# API URLs
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

#### 3.3. Setup Database

```bash
npx prisma generate
npx prisma db push
```

---

## 🚀 Hướng dẫn chạy dự án

### Chạy Backend

Backend có **3 cách chạy** khác nhau:

#### **Cách 1: Chạy trực tiếp với Python** (Khuyến nghị cho development)

```bash
cd Chatbot
python main.py
```

#### **Cách 2: Chạy với Uvicorn CLI** (Linh hoạt hơn)

```bash
cd Chatbot
uvicorn main:app --host 127.0.0.1 --port 8000
```

Với auto-reload (tự động restart khi code thay đổi):
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Với custom host/port:
```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

#### **Cách 3: Chạy trong background (Production)**

**Windows (PowerShell):**
```powershell
Start-Process python -ArgumentList "main.py" -WindowStyle Hidden
```

**Windows (CMD):**
```cmd
start /B python main.py
```

**Linux/Mac:**
```bash
nohup python main.py > backend.log 2>&1 &
```

Hoặc với Uvicorn:
```bash
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
```

---

Backend sẽ chạy tại: `http://127.0.0.1:8000`

**Test API:**
```bash
# Windows (PowerShell)
Invoke-WebRequest http://127.0.0.1:8000/ping

# Linux/Mac/Git Bash
curl http://127.0.0.1:8000/ping

# Hoặc mở trình duyệt
# http://127.0.0.1:8000/ping
```

### Chạy Frontend

Mở terminal mới:

```bash
cd Frontend
npm run dev
```

Frontend sẽ chạy tại: `http://localhost:3000`

### Chạy toàn bộ hệ thống

**Terminal 1** (Backend):
```bash
cd Code/Chatbot
python main.py
# Hoặc: uvicorn main:app --reload
```

**Terminal 2** (Frontend):
```bash
cd Code/Frontend
npm run dev
```

Truy cập `http://localhost:3000` để sử dụng chatbot.

---

### Chạy với Script (Tiện lợi)

Bạn có thể tạo script để chạy nhanh:

**`start_backend.bat` (Windows):**
```batch
@echo off
cd /d "%~dp0\Chatbot"
echo Starting Backend Server...
python main.py
pause
```

**`start_backend.sh` (Linux/Mac):**
```bash
#!/bin/bash
cd "$(dirname "$0")/Chatbot"
echo "Starting Backend Server..."
python main.py
```

Sau đó chạy:
```bash
# Windows
start_backend.bat

# Linux/Mac
chmod +x start_backend.sh
./start_backend.sh
```

---

## 📁 Cấu trúc thư mục

```
Code/
├── Chatbot/                          # Backend API
│   ├── main.py                       # FastAPI application
│   ├── chat.py                       # RAG pipeline logic
│   ├── data_loader.py                # Load corpus data
│   ├── smoonth_context.py            # Context optimization
│   └── test.py                       # Testing scripts
│
├── Data/                             # Data storage
│   ├── data_store/                   # ChromaDB vector database
│   │   ├── chroma.sqlite3
│   │   └── 44cae0a4.../              # Vector collections
│   │
│   ├── data_train/                   # Training datasets
│   │   ├── data_final_train_v1/
│   │   └── data_final_train_v2/
│   │
│   ├── embeddings/                   # Embedding models
│   │   ├── eval_model/               # Model evaluation
│   │   ├── model_base/               # Base models
│   │   └── model_fine_tuning/        # Fine-tuned models
│   │
│   ├── processed/                    # Processed datasets
│   │   └── data_final_train_v*/
│   │
│   └── raw/                          # Raw crawled data
│       ├── dulichviet/
│       ├── ivivu/
│       ├── vietnamtourism/
│       └── vnexpress/
│
├── Fine_tuning_model/                # Model training
│   ├── train_model_v1/
│   │   └── fine_tuning_models_v1.ipynb
│   └── train_model_v2/
│       ├── fine_tuning_models_v2_bkai.ipynb
│       └── fine_tuning_models_v2_e5.ipynb
│
├── Frontend/                         # Next.js application
│   ├── src/
│   │   ├── app/                      # App router pages
│   │   ├── components/               # Reusable components
│   │   ├── features/                 # Feature modules
│   │   └── lib/                      # Utilities
│   ├── prisma/                       # Database schema
│   └── package.json
│
├── data_store/                       # ChromaDB scripts
│   ├── chroma_db_v1.py
│   └── chroma_db.py
│
├── model_train/                      # Trained models
│   └── bkai_foundation_models_fine_tuning/
│
└── README.md                         # Documentation (file này)
```

---

## 📡 API Documentation

### Base URL
```
http://127.0.0.1:8000
```

### Endpoints

#### 1. Health Check
```http
GET /ping
```

**Response:**
```json
{
  "ok": true
}
```

#### 2. Process Chat Message
```http
POST /process
```

**Request Body:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hà Nội có món ăn gì ngon?"
    }
  ],
  "language": "vi"
}
```

**Response:**
```json
{
  "answer": "Hà Nội nổi tiếng với nhiều món ăn đặc sản như phở, bún chả, chả cá Lã Vọng, bánh cuốn..."
}
```

**Parameters:**
- `messages` (array, required): Danh sách tin nhắn trong hội thoại
  - `role` (string): "user" hoặc "assistant"
  - `content` (string): Nội dung tin nhắn
- `language` (string, optional): Ngôn ngữ trả lời ("vi" hoặc "en"), mặc định "vi"

---

## 🎨 Demo và Screenshots

### Chat Interface
- Giao diện chat hiện đại với theme sáng/tối
- Real-time streaming responses
- Lịch sử hội thoại được lưu trữ

### Sample Conversations

**Example 1: Địa điểm du lịch**
```
User: Vịnh Hạ Long ở đâu?
Bot: Vịnh Hạ Long nằm ở tỉnh Quảng Ninh, cách Hà Nội khoảng 170km về phía đông bắc...

User: Vé vào cửa bao nhiêu?
Bot: Giá vé tham quan Vịnh Hạ Long hiện tại là...
```

**Example 2: Ẩm thực**
```
User: Sài Gòn có món gì ngon?
Bot: Sài Gòn nổi tiếng với nhiều món ăn đặc sản như bánh mì, phở, hủ tiếu, cơm tấm...

User: Quán nào nổi tiếng?
Bot: Một số quán ăn nổi tiếng ở Sài Gòn bao gồm...
```

---

## 🧪 Testing

### Test Backend API

```bash
cd Chatbot
python test.py
```

### Test Frontend

```bash
cd Frontend
npm run test
```

---

## 📊 Model Information

### Embedding Model
- **Base Model**: BKAI Foundation Model
- **Fine-tuned on**: Vietnam tourism dataset (~25,000 samples)
- **Training Method**: Sentence-Transformers
- **Performance**: 
  - Cosine Similarity improvement: +15%
  - BGE Rerank score: 0.87

### LLM
- **Model**: GPT-4o-mini
- **Temperature**: 0.3 (for focused responses)
- **Max Tokens**: Context-dependent

---

## 🔧 Troubleshooting

### Lỗi thường gặp

**1. ModuleNotFoundError: No module named 'xxx'**
```bash
pip install xxx
```

**2. ChromaDB connection error**
- Kiểm tra đường dẫn DB_PATH trong `chat.py`
- Đảm bảo thư mục `Data/data_store/` tồn tại

**3. OpenAI API Error**
- Kiểm tra OPENAI_API_KEY trong file `.env`
- Đảm bảo có đủ credits trong tài khoản OpenAI

**4. CORS Error**
- Kiểm tra CORS middleware trong `main.py`
- Đảm bảo frontend URL được thêm vào `allow_origins`

**5. Model loading error**
- Model sẽ tự động download khi chạy lần đầu
- Cần kết nối internet ổn định

---

## 📝 Notes

- Dự án được phát triển cho mục đích học tập (AIP491)
- Model embedding đã được fine-tune trên dữ liệu du lịch Việt Nam
- Dữ liệu được thu thập từ các nguồn công khai
- Sử dụng OpenAI API (cần API key)

---

## 👥 Contributors

- **Team**: AIP491_G9
- **Model**: Fine-tuned by duongluuba

---

## 📄 License

This project is for educational purposes.

---

## 🔮 Future Improvements

- [ ] Thêm hỗ trợ cho nhiều ngôn ngữ hơn
- [ ] Tích hợp voice chat
- [ ] Thêm khả năng đề xuất lịch trình du lịch
- [ ] Cải thiện context smoothing algorithm
- [ ] Deploy lên production
- [ ] Thêm analytics và monitoring

---

**Happy Coding! 🚀**
