import json
import pickle
from sentence_transformers import SentenceTransformer

# Load mô hình Bi-Encoder dùng trong dự án
model = SentenceTransformer("bkai-foundation-models/vietnamese-bi-encoder") #intfloat/multilingual-e5-base

passages = []
with open(r"D:\duongluuba\AIP491_G9\Data\processed\data_final_sorted.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        try:
            obj = json.loads(line)
            passages.append(obj["passage"])
        except json.JSONDecodeError:
            print("⚠️ Lỗi JSON ở dòng:", len(passages))
            continue

print("✅ Đọc được:", len(passages))


# Tạo embedding (batch encode)
embeddings = model.encode(passages, show_progress_bar=True)

# Lưu vào file .pkl
with open('D:\duongluuba\AIP491_G9\Data\embeddings\model_base\corpus_embedding_bkai_foundation_models.pkl', 'wb') as f:
    pickle.dump(embeddings, f)

# import numpy as np
# import pickle

# with open(r"D:\ARTIFICIAL_INTELLIGENCE\KY_8\DSP391m\Project_DSP391m_Group_6\Project_DSP391m\Data\corpus_embedding.pkl", 'rb') as f:
#     embeddings = pickle.load(f)

# print(type(embeddings))  # Có thể là list, np.ndarray hoặc dict
# print(len(embeddings))   # Số lượng embedding
# print(embeddings[0])     # In vector đầu tiên
