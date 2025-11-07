import os
import time
import random
import json
import pickle
from tqdm import tqdm
from openai import OpenAI
from rank_bm25 import BM25Okapi
from pyvi.ViTokenizer import tokenize
from sentence_transformers import InputExample

# ==========================
#  KHỞI TẠO OPENAI CLIENT
# ==========================
api_gpt = "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"
 # Điền API Key của bạn vào đây
client = OpenAI(api_key=api_gpt)  # Khởi tạo client OpenAI

# ==========================
# 1. HÀM ĐỌC DỮ LIỆU JSONL
# ==========================
def load_passages_from_jsonl(file_path):
    """
    Đọc passage từ JSONL, loại bỏ dòng 'Title: ...' và câu đầu dạng giới thiệu.
    Trả về list các string text thuần, chỉ giữ nội dung chính.
    """
    passages = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                item = json.loads(line.strip())
                if "passage" in item and item["passage"].strip():
                    text = item["passage"].strip()
                    lines = text.split("\n")
                    # Bỏ dòng title nếu có
                    if lines[0].lower().startswith("title:"):
                        lines = lines[1:]
                    clean_text = "\n".join(lines).strip()
                    
                    # Bỏ câu đầu nếu ngắn và có dấu hỏi
                    sentences = clean_text.split(". ")
                    if sentences and "?" in sentences[0]:
                        sentences = sentences[1:]  # loại bỏ câu đầu
                    final_text = ". ".join(sentences).strip()
                    
                    if final_text:
                        passages.append(final_text)
            except json.JSONDecodeError:
                continue
    return passages


# ==========================
# 2. SINH QUERY BẰNG GPT
# ==========================
def create_query_gpt(text, retries=3):
    """
    Tạo query tự nhiên bằng GPT từ một passage.
    Nếu API lỗi, thử lại `retries` lần.
    """
    text = text[:500]  # cắt passage quá dài
    prompt = f"""
Hãy tạo một câu hỏi ngắn gọn, tự nhiên, bằng tiếng Việt mà người dùng có thể hỏi
để nhận được nội dung sau:
---
{text}
---
Chỉ trả về câu hỏi, không giải thích thêm.
"""
    for _ in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini", # choice models 
                messages=[{"role": "user", "content": prompt}],
                temperature = 0.7, # Tham số điều chỉnh độ sáng tạo (0 = nghiêm ngặt, 1 = sáng tạo hơn)
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print("Lỗi API:", e)
            time.sleep(5)
    # fallback query nếu API không trả về kết quả
    return "Đoạn này nói về điều gì?"

# ==========================
# 3. NEGATIVE SAMPLING
# ==========================
def get_easy_negative(passages, positive_text, exclude_index):
    """
    Lấy easy negative: passage khác chủ đề hoàn toàn.
    Loại các passage có top 5 token giống passage positive.
    Nếu không có candidate nào, fallback random passage.
    """
    positive_tokens = set(tokenize(positive_text.lower()).split()[:5])
    candidates = [
        p for i, p in enumerate(passages)
        if i != exclude_index and len(set(tokenize(p.lower()).split()) & positive_tokens) == 0
    ]
    if not candidates:
        candidates = [p for i, p in enumerate(passages) if i != exclude_index]
    return random.choice(candidates)

def get_hard_negative(query, passages, bm25, positive_text, exclude_index):
    """
    Lấy hard negative: passage gần query nhưng khác nội dung positive.
    Sử dụng BM25 để xếp passage theo similarity với query,
    lọc các passage có nhiều token trùng với positive.
    Nếu không tìm được, fallback sang easy negative.
    """
    tokenized_query = tokenize(query.lower()).split()
    scores = bm25.get_scores(tokenized_query)
    sorted_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    
    positive_tokens = set(tokenize(positive_text.lower()).split()[:5])  # top 5 token quan trọng
    
    for idx in sorted_idx:
        if idx != exclude_index:
            hard_candidate = passages[idx]
            hard_tokens = set(tokenize(hard_candidate.lower()).split())
            if len(hard_tokens & positive_tokens) < 2:  # tránh overlap nhiều
                return hard_candidate
    # fallback nếu không có hard negative phù hợp
    return get_easy_negative(passages, positive_text, exclude_index)

# ==========================
# 4. TẠO DỮ LIỆU TRAIN (CÓ RESUME)
# ==========================
def create_training_examples_with_api(file_path, output_pkl, limit=None):
    passages = load_passages_from_jsonl(file_path)
    if limit:
        passages = passages[:limit]
    print(f" Tổng số passage đọc được: {len(passages)}")

    tokenized_passages = [tokenize(p.lower()).split() for p in passages]
    bm25 = BM25Okapi(tokenized_passages)

    # Resume: load file pickle nếu đã tồn tại và không rỗng
    examples = []
    start_idx = 0
    if os.path.exists(output_pkl) and os.path.getsize(output_pkl) > 0:
        try:
            with open(output_pkl, "rb") as f:
                examples = pickle.load(f)
            start_idx = len(examples)
            print(f" Tiếp tục từ mẫu thứ {start_idx} (đã có {len(examples)} mẫu)")
        except Exception as e:
            print(f" Không thể load file pickle: {e}. Bắt đầu từ đầu.")

    # Vòng lặp tạo training example
    for i in tqdm(range(start_idx, len(passages)), desc="🔹 Generating training examples"):
        print(f" Đang tạo query thứ {i+1}/{len(passages)}")
        pos = passages[i]
        query = create_query_gpt(pos)
        easy_neg = get_easy_negative(passages, pos, i)
        hard_neg = get_hard_negative(query, passages, bm25, pos, i)

        # Tạo InputExample
        example = InputExample(texts=[query, pos, hard_neg, easy_neg])
        examples.append(example)

        #  Lưu ngay mỗi lần tạo xong
        with open(output_pkl, "wb") as f:
            pickle.dump(examples, f)

        print(f"  Đã lưu mẫu thứ {len(examples)} vào {output_pkl}")

        time.sleep(1)  # tránh spam API

    print(f" Hoàn tất! Tổng cộng {len(examples)} mẫu được lưu vào {output_pkl}")
# ==========================
# 5. MAIN
# ==========================
if __name__ == "__main__":
    input_file = r"D:\duongluuba\AIP491_G9\Data\raw\vnexpress\vnexpress_data_v2.txt"
    output_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\embeddings\train_triplet.pkl"

    # ==========================
    # 1. Tạo thư mục nếu chưa tồn tại
    # ==========================
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📂 Đã tạo thư mục: {output_dir}")

    # ==========================
    # 2. Tạo file pickle rỗng nếu chưa có
    # ==========================
    if not os.path.exists(output_file):
        with open(output_file, "wb") as f:
            pickle.dump([], f)
        print(f" Đã tạo file pickle rỗng: {output_file}")

    # ==========================
    # 3. Chạy hàm tạo dữ liệu
    # ==========================
    create_training_examples_with_api(
        file_path=input_file,
        output_pkl=output_file,
        limit=None,        # None = lấy hết
    )
