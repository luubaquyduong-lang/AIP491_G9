import os
import time
import json
import re
import pickle
from tqdm import tqdm
from sentence_transformers import InputExample
from openai import OpenAI

# ==========================
# 1️⃣ KHỞI TẠO OPENAI CLIENT
# ==========================
api_gpt = "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"
client = OpenAI(api_key=api_gpt)

# ==========================
# 2️⃣ ĐỌC FILE JSONL
# ==========================
def load_passages_from_jsonl(file_path):
    passages = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line.strip())
                if "passage" in obj and obj["passage"].strip():
                    passages.append(obj["passage"].strip())
            except json.JSONDecodeError:
                continue
    print(f"📘 Đã đọc {len(passages)} passages từ {file_path}")
    return passages

# ==========================
# 3️⃣ GỌI GPT SINH 1 CÂU HỎI
# ==========================
def create_query_gpt(text, retries=3):
    prompt = f"""
Bạn là trợ lý tạo câu hỏi cho chatbot du lịch Việt Nam.

Hãy đọc đoạn nội dung dưới đây và tạo ra **một câu hỏi duy nhất** bằng tiếng Việt,
dựa hoàn toàn trên thông tin trong đoạn. 
Câu hỏi phải tự nhiên, dễ hiểu, không thêm kiến thức ngoài, không trả lời.

--- ĐOẠN NỘI DUNG ---
{text}
--- HẾT ---
""".strip()

    for _ in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            content = response.choices[0].message.content.strip()
            question = re.split(r'[\n\r]+', content)[0].strip("-• ")

            if len(question) > 5 and question.endswith("?"):
                return [question]
            elif len(question) > 5:
                return [question.rstrip(".") + "?"]

        except Exception as e:
            print("⚠️ Lỗi API:", e)
            time.sleep(0.3)

    # fallback
    sentences = re.split(r'(?<=[.!?])\s+', text)
    first_sentence = sentences[0].strip() if sentences else text[:60].strip()
    fallback = first_sentence.rstrip(".!?") + "?"
    return [fallback]

# ==========================
# 4️⃣ SINH DỮ LIỆU TRAIN (QUERY, POS)
# ==========================
def create_training_examples_with_api(file_path, output_pkl, limit=None, prefix_style="e5"):
    passages = load_passages_from_jsonl(file_path)
    if limit:
        passages = passages[:limit]
    print(f"📗 Tổng số passage cần xử lý: {len(passages)}")

    # Nếu file pickle có sẵn, đọc để resume
    examples = []
    processed_passages = set()  # lưu nội dung các passage đã xử lý (tránh trùng)
    if os.path.exists(output_pkl) and os.path.getsize(output_pkl) > 0:
        try:
            with open(output_pkl, "rb") as f:
                examples = pickle.load(f)
            processed_passages = {ex.texts[1] for ex in examples if len(ex.texts) >= 2}
            print(f"🔁 Resume: đã có {len(examples)} mẫu → bỏ qua {len(processed_passages)} passage đầu")
        except Exception as e:
            print(f"⚠️ Không thể load pickle cũ: {e}")

    # Lặp qua passage
    for i, passage in enumerate(tqdm(passages, desc="🔹 Generating training examples")):
        if passage in processed_passages:
            continue  # skip passage đã xử lý

        queries = create_query_gpt(passage)
        for q in queries:
            if prefix_style == "e5":
                q_text = f"query: {q}"
                p_text = f"passage: {passage}"
            else:
                q_text, p_text = q, passage

            examples.append(InputExample(texts=[q_text, p_text]))

        # Lưu định kỳ (mỗi 20 mẫu)
        if (i + 1) % 20 == 0 or i == len(passages) - 1:
            with open(output_pkl, "wb") as f:
                pickle.dump(examples, f)
            print(f"💾 Đã lưu {len(examples)} mẫu (tới passage {i+1}/{len(passages)}) → {output_pkl}")

        time.sleep(0.05)

    print(f"\n✅ Hoàn tất! Tổng cộng {len(examples)} mẫu được lưu vào {output_pkl}")
    return examples

# ==========================
# 5️⃣ MAIN
# ==========================
if __name__ == "__main__":
    input_file = r"D:\duongluuba\AIP491_G9\Data\processed\data_final_sorted_4347.jsonl"
    output_file = r"D:\duongluuba\AIP491_G9\Data\embeddings\data_train_singlequery.pkl"

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    if not os.path.exists(output_file):
        with open(output_file, "wb") as f:
            pickle.dump([], f)
        print(f"📂 Đã tạo file pickle rỗng: {output_file}")

    create_training_examples_with_api(
        file_path=input_file,
        output_pkl=output_file,
        limit=None,         # có thể đặt 1000 để test trước
        prefix_style="e5",  # "bkai" nếu dùng BKAI Bi-Encoder
    )
