import json
import pickle
from sentence_transformers import SentenceTransformer

# Dùng mô hình đã fine-tune để mã hóa toàn bộ corpus thành embeddings và lưu ra .pkl phục vụ RAG/tìm kiếm.
# === 1. Load model đã fine-tune ===
model = SentenceTransformer(r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\Train_model\fine_tuned_biencoder")

# === 2. Đọc corpus gốc ===
passages = []
with open(r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\corpus_chunks.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        passages.append(obj["passage"])

# === 3. Encode toàn bộ corpus ===
embeddings = model.encode(passages, show_progress_bar=True)

# === 4. Lưu ra file để dùng trong RAG ===
with open(r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\Train_model\corpus_embedding_ft.pkl", "wb") as f:
    pickle.dump(embeddings, f)
