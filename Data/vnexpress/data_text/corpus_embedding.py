import json
import pickle
from sentence_transformers import SentenceTransformer

# Load mô hình Bi-Encoder dùng trong dự án
model = SentenceTransformer("bkai-foundation-models/vietnamese-bi-encoder")

# Đọc từng passage từ file output.jsonl
passages = []
with open('D:\ARTIFICIAL_INTELLIGENCE\KY_8\DSP391m\Project_DSP391m_Group_6\Project_DSP391m\Data\corpus_chunks.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        passages.append(obj['passage'])

# Tạo embedding (batch encode)
embeddings = model.encode(passages, show_progress_bar=True)

# Lưu vào file .pkl
with open('D:\ARTIFICIAL_INTELLIGENCE\KY_8\DSP391m\Project_DSP391m_Group_6\Project_DSP391m\Data\corpus_embedding_w150.pkl', 'wb') as f:
    pickle.dump(embeddings, f)

# import numpy as np
# import pickle

# with open(r"D:\ARTIFICIAL_INTELLIGENCE\KY_8\DSP391m\Project_DSP391m_Group_6\Project_DSP391m\Data\corpus_embedding.pkl", 'rb') as f:
#     embeddings = pickle.load(f)

# print(type(embeddings))  # Có thể là list, np.ndarray hoặc dict
# print(len(embeddings))   # Số lượng embedding
# print(embeddings[0])     # In vector đầu tiên
