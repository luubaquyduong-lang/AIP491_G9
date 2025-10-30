
import os
import time
import random
import re
import json
import pickle
from tqdm import tqdm
# from openai import OpenAI
from sentence_transformers import InputExample

# # ==========================
# #  KHỞI TẠO OPENAI CLIENT
# ==========================
# api_gpt = "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"
#  # Điền API Key của bạn vào đây
# client = OpenAI(api_key=api_gpt)  # Khởi tạo client OpenAI

# ==========================
# 1. HÀM ĐỌC DỮ LIỆU JSONL
# ==========================
def load_passages_from_jsonl(file_path):
    passages = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                item = json.loads(line.strip())
                if "passage" in item and item["passage"].strip():
                    text = item["passage"].strip()
                    passages.append(text)
            except json.JSONDecodeError:
                continue
    print(f" Đã đọc {len(passages)} passages.")
    return passages


# ==========================
# 2. SINH QUERY BẰNG GPT
# ==========================
def create_query_gpt(text, retries=3):
    return text
#     """
#     Sinh 5 câu hỏi tự nhiên bằng GPT từ một passage du lịch.
#     Nếu API lỗi hoặc parse thất bại → dùng câu đầu tiên của passage (thêm '?').
#     """
#     # Cắt gọn passage dài
#     text = text[:1000]

#     # Prompt sinh 5 câu hỏi
#     prompt = f"""
# Bạn là trợ lý tạo câu hỏi cho chatbot du lịch Việt Nam.

# Hãy đọc đoạn nội dung (chunk) dưới đây và tạo ra đúng **5 câu hỏi** tự nhiên bằng tiếng Việt.
# Yêu cầu:
# - Câu hỏi chỉ dựa trên thông tin có trong đoạn.
# - Không thêm kiến thức ngoài.
# - Không trả lời, chỉ đặt câu hỏi.
# - Trả về đúng định dạng JSON list, ví dụ:
# [
#   "Câu hỏi 1",
#   "Câu hỏi 2",
#   "Câu hỏi 3",
#   "Câu hỏi 4",
#   "Câu hỏi 5"
# ]

# --- ĐOẠN NỘI DUNG ---
# {text}
# --- HẾT ---
# """.strip()
#     # Gọi GPT
#     for _ in range(retries):
#         try:
#             response = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.6,
#             )
#             content = response.choices[0].message.content.strip()

#             # Parse JSON nếu hợp lệ
#             try:
#                 import json
#                 questions = json.loads(content)
#                 if isinstance(questions, list) and len(questions) >= 1:
#                     # Làm sạch
#                     questions = [q.strip().strip("-• ") for q in questions if len(q.strip()) > 3]
#                     return questions[:5]
#             except json.JSONDecodeError:
#                 # Nếu không phải JSON → tách dòng
#                 questions = [q.strip("-• \n") for q in content.split("\n") if len(q.strip()) > 5]
#                 if questions:
#                     return questions[:5]

#         except Exception as e:
#             print("Lỗi API:", e)
#             time.sleep(5)

    # ====== Fallback khi thất bại ======
    # Lấy câu đầu tiên trong passage và thêm dấu hỏi
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    first_sentence = sentences[0].strip() if sentences else text[:60].strip()
    fallback = first_sentence.rstrip(".!?") + "?"
    return [fallback]


# ==========================
# 3. NEGATIVE SAMPLING (CITY-BASED)
# ==========================

# Danh sách 63 tỉnh/thành Việt Nam
VIETNAM_PROVINCES = [
    "An Giang", "Bà Rịa - Vũng Tàu", "Bắc Giang", "Bắc Kạn", "Bạc Liêu", "Bắc Ninh",
    "Bến Tre", "Bình Dương", "Bình Định", "Bình Phước", "Bình Thuận", "Cà Mau",
    "Cao Bằng", "Cần Thơ", "Đà Nẵng", "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai",
    "Đồng Tháp", "Gia Lai", "Hà Giang", "Hà Nam", "Hà Nội", "Hà Tĩnh", "Hải Dương",
    "Hải Phòng", "Hậu Giang", "Hòa Bình", "Hưng Yên", "Khánh Hòa", "Kiên Giang",
    "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Long An", "Nam Định",
    "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên", "Quảng Bình",
    "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sóc Trăng", "Sơn La",
    "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang",
    "thành phố Hồ Chí Minh", "Trà Vinh", "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái",
]

def extract_city_name(text):
    """
    Tìm tên tỉnh/thành Việt Nam có trong câu đầu tiên.
    """
    # Lấy câu đầu tiên (trước dấu . hoặc ? hoặc !)
    first_sentence = re.split(r'[\.!?]', text.strip())[0]
    first_sentence_lower = first_sentence.lower()

    for province in VIETNAM_PROVINCES:
        if province.lower() in first_sentence_lower:
            return province
    return None


def get_easy_negative(passages, positive_text, exclude_index):
    """
    Lấy easy negative: đoạn KHÔNG cùng tỉnh/thành với positive_text (chỉ so sánh ở câu đầu tiên).
    """
    city = extract_city_name(positive_text)
    candidates = []

    for i, p in enumerate(passages):
        if i == exclude_index:
            continue
        first_sentence = re.split(r'[.!?]', p.strip())[0]
        # chỉ lấy đoạn mà câu đầu KHÔNG chứa tên tỉnh
        if not city or city.lower() not in first_sentence.lower():
            candidates.append(p)

    # fallback nếu danh sách rỗng
    if not candidates:
        candidates = [p for i, p in enumerate(passages) if i != exclude_index]

    return random.choice(candidates)



def get_hard_negative(passages, positive_text, exclude_index):
    """
    Lấy hard negative: đoạn CÙNG tỉnh/thành với positive_text (so sánh ở câu đầu tiên).
    """
    city = extract_city_name(positive_text)
    if not city:
        return get_easy_negative(passages, positive_text, exclude_index)

    candidates = []
    for i, p in enumerate(passages):
        if i == exclude_index:
            continue
        first_sentence = re.split(r'[.!?]', p.strip())[0]
        if city.lower() in first_sentence.lower():
            candidates.append(p)

    if not candidates:
        return get_easy_negative(passages, positive_text, exclude_index)

    return random.choice(candidates)



# ==========================
# HÀM LẤY CÂU ĐẦU
# ==========================
def get_first_sentence(text):
    """
    Lấy câu đầu tiên từ passage, tính đến dấu . hoặc ? hoặc !
    """
    return re.split(r'[\.!?]', text.strip())[0].strip()


# ==========================
# 4. TẠO DỮ LIỆU TRAIN (NEGATIVE-ONLY)
# ==========================
def create_training_examples_with_api(file_path, output_pkl, limit=None, save_every=50):
    passages = load_passages_from_jsonl(file_path)
    if limit:
        passages = passages[:limit]
    print(f"📘 Tổng số passage đọc được: {len(passages)}")

    # Resume
    examples = []
    start_idx = 0
    if os.path.exists(output_pkl) and os.path.getsize(output_pkl) > 0:
        try:
            with open(output_pkl, "rb") as f:
                examples = pickle.load(f)
            start_idx = len(examples)
            print(f"🔁 Tiếp tục từ mẫu thứ {start_idx}")
        except Exception as e:
            print(f"⚠️ Không thể load pickle: {e}")

    # Loop
    for i in tqdm(range(start_idx, len(passages)), desc="🔹 Generating training examples"):
        pos = passages[i]
        first_sentence = get_first_sentence(pos)
        queries = create_query_gpt(str(i))

        for query in queries:
            # Hard negative
            hard_neg = get_hard_negative(passages, first_sentence, i)
            examples.append(InputExample(texts=[query, pos, hard_neg]))

            # Easy negative
            easy_neg = get_easy_negative(passages, first_sentence, i)
            examples.append(InputExample(texts=[query, pos, easy_neg]))

        # 💾 Lưu định kỳ mỗi 50 passage hoặc khi kết thúc
        if (i + 1) % save_every == 0 or i == len(passages) - 1:
            with open(output_pkl, "wb") as f:
                pickle.dump(examples, f)
            print(f"💾 Đã lưu {len(examples)} examples → {output_pkl}")

        time.sleep(0.1)  # giảm thời gian nghỉ nếu không dùng GPT

    print(f"✅ Hoàn tất! Tổng cộng {len(examples)} mẫu được lưu vào {output_pkl}")


# ==========================
# 5. MAIN
# ==========================
if __name__ == "__main__":
    input_file = r"D:\duongluuba\AIP491_G9\Data\\raw\\vnexpress\\vnexpress_corpus.jsonl"
    output_file = r"D:\duongluuba\AIP491_G9\Data\\embeddings\data_train_vnexpress_2.pkl"

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
        limit=None, 
        save_every=50,
                      # None = lấy hết
    )
