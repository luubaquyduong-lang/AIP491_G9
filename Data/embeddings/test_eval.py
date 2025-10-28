"""
File: compare_bkai_models_jsonl.py

Mục đích:
----------
So sánh hiệu suất của mô hình Bi-Encoder BKAI cơ bản và mô hình fine-tuned trên corpus thực tế.
Tính metric: Recall@1, Recall@5.
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================
# 1. Load models
# ==========================
print("🔹 Load models...")
base_model = SentenceTransformer("bkai-foundation-models/vietnamese-bi-encoder")
ft_model = SentenceTransformer(r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\train_model_v2\fine_tuned_biencoder")

# ==========================
# 2. Load corpus JSONL
# ==========================
corpus_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\corpus_chunks_2.jsonl"
corpus = []
with open(corpus_file, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line.strip())
        corpus.append(obj["passage"])

print(f"📘 Tổng số passage trong corpus: {len(corpus)}")

# ==========================
# 3. Tạo queries test (ví dụ: 10 queries đầu, hoặc bạn có file query riêng)
# ==========================
# Ở đây tạm thời dùng chính passage làm "query" test cho demo
queries = corpus[:10]          # 10 query đầu
positive_passages = corpus[:10] # Giả sử mỗi query match passage cùng index

# ==========================
# 4. Encode queries và passage
# ==========================
print("🔹 Encode Base model...")
query_emb_base = base_model.encode(queries, convert_to_numpy=True, normalize_embeddings=True)
passage_emb_base = base_model.encode(corpus, convert_to_numpy=True, normalize_embeddings=True)

print("🔹 Encode Fine-tuned model...")
query_emb_ft = ft_model.encode(queries, convert_to_numpy=True, normalize_embeddings=True)
passage_emb_ft = ft_model.encode(corpus, convert_to_numpy=True, normalize_embeddings=True)

# ==========================
# 5. Hàm tính Recall@K
# ==========================
def compute_recall(query_emb, passage_emb, positive_idx, K=(1,5)):
    recalls = {k:0 for k in K}
    for i, q_emb in enumerate(query_emb):
        scores = cosine_similarity([q_emb], passage_emb)[0]
        ranking = np.argsort(scores)[::-1]
        for k in K:
            if positive_idx[i] in ranking[:k]:
                recalls[k] += 1
    N = len(query_emb)
    for k in K:
        recalls[k] /= N
    return recalls

positive_idx = list(range(len(queries)))  # query i match passage i
recall_base = compute_recall(query_emb_base, passage_emb_base, positive_idx)
recall_ft = compute_recall(query_emb_ft, passage_emb_ft, positive_idx)

delta_r1 = recall_ft[1] - recall_base[1]
delta_r5 = recall_ft[5] - recall_base[5]

# ==========================
# 6. In bảng so sánh
# ==========================
print("\n📊 So sánh Base model và Fine-tuned model:")
print(f"{'Metric':<15}{'Base':<10}{'Fine-tune':<12}{'ΔImprovement'}")
print(f"{'Recall@1':<15}{recall_base[1]:<10.4f}{recall_ft[1]:<12.4f}{delta_r1:.4f}")
print(f"{'Recall@5':<15}{recall_base[5]:<10.4f}{recall_ft[5]:<12.4f}{delta_r5:.4f}")
