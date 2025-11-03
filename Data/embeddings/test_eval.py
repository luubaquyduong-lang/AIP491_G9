"""
File: compare_bkai_models_jsonl.py

Mục đích
-------
1) Đọc corpus JSONL
2) Sinh 100 query tự nhiên từ 100 passage ngẫu nhiên (không cần API)
3) Lưu test_queries_100.jsonl
4) Đánh giá Recall@1, Recall@5 giữa:
   - Base: bkai-foundation-models/vietnamese-bi-encoder
   - Fine-tuned: model local của bạn
"""

import json, re, random, os
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------
# 0) Cấu hình đường dẫn
# ---------------------------
BASE_MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"
FT_MODEL_PATH   = r"D:\duongluuba\\model_bkai_v1\bkai_finetuned_vn_v1"
CORPUS_FILE     = r"D:\duongluuba\AIP491_G9\Data\\processed\\corpus_chunks_2.jsonl"
OUT_QUERIES     = r"D:\duongluuba\AIP491_G9\Data\\test_queries_100.jsonl"
NUM_QUERIES     = 100
RANDOM_SEED     = 42

random.seed(RANDOM_SEED)

# ---------------------------
# 1) Hàm tiện ích sinh query
# ---------------------------
TRAVEL_HINT_WORDS = [
    "lễ hội","đền","chùa","nhà thờ","bảo tàng","chợ","bãi biển","đảo","núi","thác",
    "vườn quốc gia","khu du lịch","khu sinh thái","ẩm thực","đặc sản","phố cổ",
    "cồn","động","hang","cánh đồng","ruộng bậc thang","đồi chè","làng nghề",
]

def first_sentence(text: str) -> str:
    s = re.split(r"(?<=[\.\?\!])\s+", text.strip())
    return s[0] if s else text.strip()

def extract_proper_phrases(text: str, k=3):
    # Lấy các cụm chữ cái đầu viết hoa (tạm coi là danh từ riêng / địa danh)
    tokens = re.findall(r"[A-ZÀ-Ỵ][\wÀ-Ỵà-ỹ\-]*(?:\s+[A-ZÀ-Ỵ][\wÀ-Ỵà-ỹ\-]*)*", text)
    # Lọc cụm quá ngắn/không hữu ích
    phrases = [t.strip() for t in tokens if len(t.split()) <= 5 and len(t) >= 2]
    # Giữ top k cụm dài nhất
    phrases = sorted(set(phrases), key=lambda x: -len(x))[:k]
    return phrases

def detect_hint(text: str):
    text_l = text.lower()
    for w in TRAVEL_HINT_WORDS:
        if w in text_l:
            return w
    return None

def generate_query_from_passage(passage: str) -> str:
    s1 = first_sentence(passage)
    proper = extract_proper_phrases(s1, k=2)
    hint = detect_hint(passage)

    # Một số mẫu câu tự nhiên
    if hint and proper:
        return f"{proper[0]} có gì đặc biệt liên quan đến {hint}?"
    if hint:
        return f"Đoạn này nhắc đến {hint} ở đâu và có gì thú vị?"
    if proper:
        # Nếu có địa danh/tên riêng
        templates = [
            f"{proper[0]} nổi tiếng vì điều gì?",
            f"Tôi nên tham quan gì khi đến {proper[0]}?",
            f"Có điểm nhấn nào đáng lưu ý tại {proper[0]}?",
        ]
        return random.choice(templates)
    # Fallback tự nhiên, ngắn gọn
    return "Những điểm nổi bật dành cho du khách trong đoạn này là gì?"

# ---------------------------
# 2) Đọc corpus
# ---------------------------
corpus = []
with open(CORPUS_FILE, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line.strip())
        corpus.append(obj["passage"])

print(f"📘 Tổng số passage trong corpus: {len(corpus)}")

# ---------------------------
# 3) Lấy ngẫu nhiên 100 passage và sinh query
# ---------------------------
n = min(NUM_QUERIES, len(corpus))
selected_idx = random.sample(range(len(corpus)), n)

queries = []
positive_idx = []
pairs = []  # để lưu ra file

for i in selected_idx:
    p = corpus[i]
    q = generate_query_from_passage(p)
    queries.append(q)
    positive_idx.append(i)
    pairs.append({"query": q, "positive": p, "positive_index": i})

# Lưu JSONL để dùng lại
Path(os.path.dirname(OUT_QUERIES)).mkdir(parents=True, exist_ok=True)
with open(OUT_QUERIES, "w", encoding="utf-8") as f:
    for item in pairs:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")
print(f"✅ Đã lưu {n} query tại: {OUT_QUERIES}")

# ---------------------------
# 4) Load models & encode
# ---------------------------
print("🔹 Load models...")
base_model = SentenceTransformer(BASE_MODEL_NAME)
ft_model   = SentenceTransformer(FT_MODEL_PATH)

print("🔹 Encode Base model...")
query_emb_base   = base_model.encode(queries, convert_to_numpy=True, normalize_embeddings=True)
passage_emb_base = base_model.encode(corpus,  convert_to_numpy=True, normalize_embeddings=True)

print("🔹 Encode Fine-tuned model...")
query_emb_ft   = ft_model.encode(queries, convert_to_numpy=True, normalize_embeddings=True)
passage_emb_ft = ft_model.encode(corpus,  convert_to_numpy=True, normalize_embeddings=True)

# ---------------------------
# 5) Tính Recall@K
# ---------------------------
def compute_recall(query_emb, passage_emb, pos_idx, K=(1,5)):
    recalls = {k:0 for k in K}
    for i, q_emb in enumerate(query_emb):
        scores = cosine_similarity([q_emb], passage_emb)[0]
        ranking = np.argsort(scores)[::-1]
        for k in K:
            if pos_idx[i] in ranking[:k]:
                recalls[k] += 1
    N = len(query_emb)
    return {k: recalls[k]/N for k in K}

recall_base = compute_recall(query_emb_base, passage_emb_base, positive_idx)
recall_ft   = compute_recall(query_emb_ft,   passage_emb_ft,   positive_idx)

delta_r1 = recall_ft[1] - recall_base[1]
delta_r5 = recall_ft[5] - recall_base[5]

# ---------------------------
# 6) In bảng so sánh
# ---------------------------
print("\n📊 So sánh Base model và Fine-tuned model (với 100 query tự sinh):")
print(f"{'Metric':<15}{'Base':<10}{'Fine-tune':<12}{'ΔImprovement'}")
print(f"{'Recall@1':<15}{recall_base[1]:<10.4f}{recall_ft[1]:<12.4f}{delta_r1:+.4f}")
print(f"{'Recall@5':<15}{recall_base[5]:<10.4f}{recall_ft[5]:<12.4f}{delta_r5:+.4f}")

# Xem thử 5 query đầu
print("\n🔎 Ví dụ 5 query đầu:")
for j in range(min(5, len(queries))):
    print(f"- Q{j+1}: {queries[j]}")
