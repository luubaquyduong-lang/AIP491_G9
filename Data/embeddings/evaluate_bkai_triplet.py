"""
File: evaluate_bkai_triplet.py

Mục đích:
----------
1. Fine-tune mô hình Bi-Encoder BKAI trên dataset train_triplet.pkl.
2. Đánh giá hiệu suất trước và sau fine-tune dựa trên metric Recall@1, Recall@5.
3. Xuất bảng so sánh cải thiện hiệu suất của mô hình sau fine-tune.
4. Hỗ trợ việc lựa chọn và cải thiện mô hình embedding cho RAG/Information Retrieval.

Pipeline tổng quan:
------------------
1. Load mô hình Bi-Encoder gốc (BKAI).
2. Load dữ liệu train_triplet và chia validation set.
3. Tính Recall@1, Recall@5 trên validation trước fine-tune (baseline).
4. Fine-tune mô hình trên train_triplet với MultipleNegativesRankingLoss.
5. Encode validation set sau fine-tune, tính Recall@1, Recall@5.
6. So sánh và in ra bảng cải thiện hiệu suất.
"""

import pickle
import numpy as np
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

# ==========================
# 1. Cấu hình mô hình và thiết bị
# ==========================
model_name = "bkai-foundation-models/vietnamese-bi-encoder"
device = "cuda" if __import__('torch').cuda.is_available() else "cpu"
print(f" Sử dụng thiết bị: {device}")

# Load mô hình Bi-Encoder base (chưa fine-tune)
base_model = SentenceTransformer(model_name, device=device)

# ==========================
# 2. Load dữ liệu train_triplet
# ==========================
with open("train_triplet.pkl", "rb") as f:
    train_examples = pickle.load(f)

# Chia validation set (10% dataset tạm thời)
split_idx = int(len(train_examples) * 0.9)
train_data = train_examples[:split_idx]
val_data = train_examples[split_idx:]

# Chuẩn bị danh sách query và positive passage
val_queries = [ex.texts[0] for ex in val_data]
val_positives = [ex.texts[1] for ex in val_data]

# Tạo mapping passage -> index để dễ tính Recall
all_passages = list(set(val_positives + [ex.texts[2] for ex in val_data] + [ex.texts[3] for ex in val_data]))
passage2idx = {p:i for i,p in enumerate(all_passages)}
positive_idx = [passage2idx[p] for p in val_positives]

# ==========================
# 3. Encode validation set với mô hình base (baseline)
# ==========================
print(" Encode validation với base model...")
query_emb_base = base_model.encode(val_queries, convert_to_numpy=True, normalize_embeddings=True)
passage_emb_base = base_model.encode(all_passages, convert_to_numpy=True, normalize_embeddings=True)

# ==========================
# 4. Hàm tính Recall@K
# ==========================
def compute_recall(query_emb, passage_emb, positive_idx, K=(1,5)):
    """
    Tính Recall@K cho tập query và passage.
    Parameters:
    - query_emb: embedding của query
    - passage_emb: embedding của tất cả passage
    - positive_idx: index của passage đúng cho mỗi query
    - K: tuple các giá trị K muốn tính Recall
    Returns:
    - dictionary Recall@K
    """
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

# Tính Recall baseline trước fine-tune
recall_base = compute_recall(query_emb_base, passage_emb_base, positive_idx)
print(f"[BASELINE] Recall@1: {recall_base[1]:.4f}, Recall@5: {recall_base[5]:.4f}")

# ==========================
# 5. Fine-tune mô hình trên train_triplet
# ==========================
print(" Fine-tune model...")
train_dataloader = DataLoader(train_data, shuffle=True, batch_size=16)
train_loss = losses.MultipleNegativesRankingLoss(base_model)

base_model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=5,               # số epoch fine-tune
    warmup_steps=100,       # warmup để ổn định gradient
    output_path="bkai_finetuned_triplet"  # lưu mô hình fine-tune
)

# ==========================
# 6. Encode validation set sau fine-tune
# ==========================
print("🔹 Encode validation sau fine-tune...")
query_emb_ft = base_model.encode(val_queries, convert_to_numpy=True, normalize_embeddings=True)
passage_emb_ft = base_model.encode(all_passages, convert_to_numpy=True, normalize_embeddings=True)

recall_ft = compute_recall(query_emb_ft, passage_emb_ft, positive_idx)
print(f"[FINETUNE] Recall@1: {recall_ft[1]:.4f}, Recall@5: {recall_ft[5]:.4f}")

# ==========================
# 7. So sánh cải thiện hiệu suất
# ==========================
delta_r1 = recall_ft[1] - recall_base[1]
delta_r5 = recall_ft[5] - recall_base[5]

print("\n📊 So sánh hiệu suất trước và sau fine-tune:")
print(f"{'Metric':<15}{'Baseline':<10}{'Fine-tune':<12}{'ΔImprovement'}")
print(f"{'Recall@1':<15}{recall_base[1]:<10.4f}{recall_ft[1]:<12.4f}{delta_r1:.4f}")
print(f"{'Recall@5':<15}{recall_base[5]:<10.4f}{recall_ft[5]:<12.4f}{delta_r5:.4f}")
