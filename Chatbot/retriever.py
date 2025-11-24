from rank_bm25 import BM25Okapi
from pyvi.ViTokenizer import tokenize
from sentence_transformers import SentenceTransformer
import numpy as np
import string
import pickle

# Hàm tiền xử lý text: xóa dấu câu, chuyển về chữ thường và tách từ
def split_text(text):
    text = text.translate(str.maketrans('', '', string.punctuation))  # Xóa dấu câu
    words = text.lower().split()  # Chuyển về chữ thường và tách theo khoảng trắng
    return [word for word in words if len(word.strip()) > 0]  # Loại bỏ từ rỗng

class Retriever:
    def __init__(self, corpus, corpus_emb_path, model_name):
        # Khởi tạo bộ truy xuất với dữ liệu đầu vào
        self.corpus = corpus  # Tập văn bản (list các dict có key "passage")
        # Tiền xử lý toàn bộ corpus để phục vụ BM25
        self.tokenized_corpus = [split_text(doc["passage"]) for doc in corpus]
        # Khởi tạo mô hình BM25 trên tập tokenized corpus
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        # Nạp sẵn vector embedding của toàn bộ corpus để dùng cho truy vấn ngữ nghĩa
        with open(corpus_emb_path, 'rb') as f:
            self.corpus_embs = pickle.load(f)
        # Khởi tạo mô hình SentenceTransformer cho việc embedding câu truy vấn
        self.embedder = SentenceTransformer(model_name)

    def retrieve(self, question, topk=50):
        # Tách từ câu hỏi để tính điểm BM25
        tokenized_query = split_text(question)
        # Dùng PyVi để tách từ tiếng Việt cho embedding
        segmented_question = tokenize(question)
        # Mã hóa câu hỏi thành vector embedding
        question_emb = self.embedder.encode([segmented_question])
        # Chuẩn hóa vector embedding về độ dài 1
        question_emb /= np.linalg.norm(question_emb, axis=1)[:, np.newaxis]
        # Tính điểm BM25 cho từng tài liệu trong corpus
        bm25_scores = self.bm25.get_scores(tokenized_query)
        # Tính điểm tương đồng cosine giữa câu hỏi và các văn bản bằng embedding
        semantic_scores = question_emb @ self.corpus_embs.T
        semantic_scores = semantic_scores[0]
        # Chuẩn hóa điểm BM25 để đưa về cùng thang đo với điểm ngữ nghĩa
        max_bm25_score = max(bm25_scores)
        min_bm25_score = min(bm25_scores)
        normalize = lambda x: (x - min_bm25_score + 0.1) / (max_bm25_score - min_bm25_score + 0.1)
        # Kết hợp điểm BM25 và điểm ngữ nghĩa cho từng văn bản
        for i, doc in enumerate(self.corpus):
            doc["bm25_score"] = bm25_scores[i]
            doc["bm25_normed_score"] = normalize(bm25_scores[i])
            doc["semantic_score"] = semantic_scores[i]
            # Trọng số: 0.4 cho BM25 (từ khóa), 0.6 cho embedding (ngữ nghĩa)
            doc["combined_score"] = doc["bm25_normed_score"] * 0.4 + doc["semantic_score"] * 0.6
        # Trả về danh sách top-k văn bản có combined_score cao nhất
        return sorted(self.corpus, key=lambda x: x["combined_score"], reverse=True)[:topk]
