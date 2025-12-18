from transformers import AutoTokenizer
import pandas as pd

# ==========================
# 1. Cấu hình
# ==========================
MODEL_NAME = "intfloat/multilingual-e5-base"  # hoặc "bkai-foundation-models/vietnamese-bi-encoder"
FILE_PATH = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\data_final_train_v2\data_final_sort_v2.txt"
OUTPUT_CSV = r"D:\duongluuba\AIP491_G9\Data\raw\vnexpress\token_count_vnexpress.csv"
# PREFIX = "passage: "  # E5 cần prefix, BKAI thì có thể bỏ
MAX_TOKENS = 512

# ==========================
# 2. Tải tokenizer
# ==========================
print(f"🔹 Đang tải tokenizer từ {MODEL_NAME} ...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# ==========================
# 3. Đọc file & tính token
# ==========================
records = []
too_long = []  # lưu các dòng vượt 512 tokens

with open(FILE_PATH, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

print(f"\n Tổng số dòng đọc được: {len(lines)}\n")

for i, line in enumerate(lines):
    words = line.split()           # tách thành danh sách từ
    text = " ".join(words[:150])   # ghép lại 500 từ đầu
    # text = PREFIX + line
    n_tokens = len(tokenizer(text, add_special_tokens=True)["input_ids"])
    n_count = len(text.split())
    records.append({"index": i + 1, "text": text, "tokens": n_tokens, 'count': n_count})

    # In nếu vượt quá 512 tokens
    if n_tokens > MAX_TOKENS:
        # print(f"  Dòng thứ {i+1} có {n_tokens} tokens (vượt {MAX_TOKENS}) co {len(line.split())}")
        too_long.append({"index": i + 1, "tokens": n_tokens, "text": line})

# ==========================
# 4. Xuất thống kê
# ==========================
df = pd.DataFrame(records)
print(f"\n Tổng số dòng: {len(df)}")
print(f" Trung bình tokens: {df['tokens'].mean():.1f} ")
print(f" Trung bình counts: {df['count'].mean():.1f} ")
print(f" Max count: {df['count'].max()}")
print(f" Min count: {df['count'].min()}")
print(f" Max tokens: {df['tokens'].max()}")
print(f" Min tokens: {df['tokens'].min()}")
print(f" Số dòng > {MAX_TOKENS} tokens: {len(too_long)}")
# Đếm số dòng có count < 100
num_under_100 = (df["count"] < 50).sum()
print(f" Số dòng có count < 100: {num_under_100}")

