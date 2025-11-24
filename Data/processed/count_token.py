from transformers import AutoTokenizer
import pandas as pd

# ==========================
# 1. Cấu hình
# ==========================
MODEL_NAME = "hiieu/halong_embedding"  # hoặc "bkai-foundation-models/vietnamese-bi-encoder"
FILE_PATH = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\data_final_sort_v2_output.txt"
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

print(f"\n📘 Tổng số dòng đọc được: {len(lines)}\n")

for i, line in enumerate(lines):
    words = line.split()           # tách thành danh sách từ
    text = " ".join(words)   # ghép lại 500 từ đầu
    # text = PREFIX + line
    n_tokens = len(tokenizer(text, add_special_tokens=True)["input_ids"])
    n_count = len(text.split())
    records.append({"index": i + 1, "text": text, "tokens": n_tokens, 'count': n_count})

    # In nếu vượt quá 512 tokens
    if n_tokens > MAX_TOKENS:
        # print(f"⚠️  Dòng thứ {i+1} có {n_tokens} tokens (vượt {MAX_TOKENS}) co {len(line.split())}")
        too_long.append({"index": i + 1, "tokens": n_tokens, "text": line})

# ==========================
# 4. Xuất thống kê
# ==========================
df = pd.DataFrame(records)
print(f"\n📊 Tổng số dòng: {len(df)}")
print(f"🔸 Trung bình tokens: {df['tokens'].mean():.1f} ")
print(f"🔸 Trung bình counts: {df['count'].mean():.1f} ")
print(f"🔸 Max count: {df['count'].max()}")
print(f"🔸 Min count: {df['count'].min()}")
print(f"🔸 Max tokens: {df['tokens'].max()}")
print(f"🔸 Min tokens: {df['tokens'].min()}")
print(f"🔸 Số dòng > {MAX_TOKENS} tokens: {len(too_long)}")
# 🔹 Đếm số dòng có count < 100
num_under_100 = (df["count"] < 300).sum()
print(f"🔹 Số dòng có count < 100: {num_under_100}")


# # # ==========================
# # # 5. Lưu kết quả (tuỳ chọn)
# # # ==========================
# # df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
# # if too_long:
# #     long_df = pd.DataFrame(too_long)
# #     out_long = OUTPUT_CSV.replace(".csv", "_too_long.csv")
# #     long_df.to_csv(out_long, index=False, encoding="utf-8-sig")
# #     print(f"\n⚠️  Đã lưu {len(long_df)} dòng vượt {MAX_TOKENS} tokens vào: {out_long}")

# # print(f"\n✅ Đã lưu thống kê tổng vào: {OUTPUT_CSV}")


# import os, time, re
# from pathlib import Path
# from typing import List
# from openai import OpenAI
# from transformers import AutoTokenizer

# # ==========================
# # 1) Cấu hình
# # ==========================
# MODEL_NAME     = "intfloat/multilingual-e5-base"  # hoặc "bkai-foundation-models/vietnamese-bi-encoder"
# FILE_PATH      = r"D:\duongluuba\AIP491_G9\Data\raw\vnexpress\vnexpress_data_v2.txt"
# DATA_FINAL_TXT = r"D:\duongluuba\AIP491_G9\Data\raw\vnexpress\vnexpress_data_final_512.txt"
# PREFIX         = "passage: "   # E5 cần prefix, BKAI có thể bỏ
# MAX_TOKENS     = 512           # mục tiêu mỗi dòng output
# RETRIES        = 3

# # ==========================
# # 2) KHỞI TẠO OPENAI CLIENT (theo cách bạn yêu cầu)
# # ==========================
# api_gpt = "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"
# client = OpenAI(api_key=api_gpt)  # Khởi tạo client OpenAI

# # ==========================
# # 3) Tokenizer
# # ==========================
# tok = AutoTokenizer.from_pretrained(MODEL_NAME)

# def token_len_with_prefix(text: str) -> int:
#     s = PREFIX + text
#     return len(tok(s, add_special_tokens=True)["input_ids"])

# # ==========================
# # 4) Prompts
# # ==========================
# SYSTEM_PROMPT = """
# Bạn là trợ lý xử lý dữ liệu tiếng Việt để chuẩn bị cho huấn luyện mô hình embedding du lịch.

# Nhiệm vụ:
# - Chia đoạn văn (passage) tiếng Việt thành nhiều đoạn nhỏ (chunk) sao cho:
#   • Mỗi chunk ≤ 512 tokens (không được vượt quá).
#   • Nghĩa của mỗi chunk phải trọn vẹn, không bị cắt ngang ý.
#   • Nếu passage ngắn thì chỉ tạo 1 chunk duy nhất.
# - Mỗi chunk PHẢI bắt đầu bằng tiêu đề gốc, ví dụ:
#   "Chơi đâu ở Bà Rịa - Vũng Tàu:" hoặc "Tham quan ở Bình Thuận:".
# - Không được thêm bất kỳ chú thích, đánh số, tiêu đề phụ hoặc ký hiệu nào khác.
# - Không dùng markdown, không JSON, không thêm giải thích.

# Định dạng đầu ra:
# - Chỉ trả về nội dung các chunk, mỗi chunk nằm trên một dòng riêng.
# - Không để dòng trống giữa các chunk.
# """


# USER_PROMPT_TEMPLATE = """Chia đoạn sau thành các dòng (mỗi dòng là một chunk) theo yêu cầu ở trên.

# --- PASSAGE ---
# {passage}
# --- HẾT ---
# """

# # ==========================
# # 5) Gọi API theo mẫu của bạn (có retry)
# # ==========================
# def llm_split_to_lines(passage: str, retries: int = RETRIES, sleep: float = 2.0) -> List[str]:
#     prompt = USER_PROMPT_TEMPLATE.format(passage=passage.strip())
#     last_err = None
#     for _ in range(retries):
#         try:
#             response = client.chat.completions.create(
#                 model="gpt-4o-mini",  # choice models
#                 messages=[
#                     {"role": "system", "content": SYSTEM_PROMPT},
#                     {"role": "user", "content": prompt},
#                 ],
#                 temperature=0,  # ổn định để chia đều tay
#             )
#             content = response.choices[0].message.content.strip()
#             lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
#             if lines:
#                 return lines
#             else:
#                 raise ValueError("LLM trả về rỗng.")
#         except Exception as e:
#             last_err = e
#             print("Lỗi API:", e)
#             time.sleep(sleep)
#     # fallback nếu API không trả về kết quả
#     # -> trả về đúng 1 dòng gốc (để không mất dữ liệu)
#     print("⚠️ Fallback: trả về dòng gốc vì LLM lỗi sau nhiều lần thử.")
#     return [passage]

# # ==========================
# # 6) Fallback cắt theo câu nếu vẫn quá dài
# # ==========================
# SENT_SPLIT_RE = re.compile(r'(?<=[\.\?\!…])\s+')

# def split_by_sentence_token_guard(text: str, max_tokens: int) -> List[str]:
#     sents = [s.strip() for s in SENT_SPLIT_RE.split(text) if s.strip()]
#     chunks, cur, cur_tokens = [], [], 0
#     for s in sents:
#         nt = token_len_with_prefix(s)
#         if nt > max_tokens:
#             # câu đơn lẻ quá dài -> cắt đôi
#             mid = len(s)//2
#             s1, s2 = s[:mid].rstrip(), s[mid:].lstrip()
#             for piece in (s1, s2):
#                 if token_len_with_prefix(piece) <= max_tokens:
#                     if cur and cur_tokens + token_len_with_prefix(piece) > max_tokens:
#                         chunks.append(" ".join(cur))
#                         cur, cur_tokens = [piece], token_len_with_prefix(piece)
#                     else:
#                         cur.append(piece)
#                         cur_tokens += token_len_with_prefix(piece)
#             continue
#         if cur_tokens + nt > max_tokens and cur:
#             chunks.append(" ".join(cur))
#             cur, cur_tokens = [s], nt
#         else:
#             cur.append(s)
#             cur_tokens += nt
#     if cur:
#         chunks.append(" ".join(cur))
#     return chunks

# # ==========================
# # 7) Xử lý một dòng
# # ==========================
# def process_one_line(line: str) -> List[str]:
#     # Nếu ngắn, giữ nguyên
#     if token_len_with_prefix(line) <= MAX_TOKENS:
#         return [line]

#     # Dài -> gọi LLM chia
#     lines = llm_split_to_lines(line)

#     # Bảo đảm từng dòng ≤ MAX_TOKENS; nếu chưa, cắt tiếp theo câu
#     final_lines = []
#     for ln in lines:
#         if token_len_with_prefix(ln) <= MAX_TOKENS:
#             final_lines.append(ln)
#         else:
#             final_lines.extend(split_by_sentence_token_guard(ln, MAX_TOKENS))

#     # Nếu vì lý do nào đó vẫn rỗng, đảm bảo không mất dữ liệu
#     return final_lines or [line]

# # ==========================
# # 8) MAIN
# # ==========================
# if __name__ == "__main__":
#     Path(DATA_FINAL_TXT).parent.mkdir(parents=True, exist_ok=True)

#     total_src, total_out, long_count = 0, 0, 0

#     with open(FILE_PATH, "r", encoding="utf-8") as fin, open(DATA_FINAL_TXT, "w", encoding="utf-8") as fout:
#         for raw in fin:
#             line = raw.strip()
#             if not line:
#                 continue
#             total_src += 1
#             try:
#                 out_lines = process_one_line(line)
#                 if len(out_lines) > 1:
#                     long_count += 1
#                 for ln in out_lines:
#                     fout.write(ln + "\n")
#                     total_out += 1
#             except Exception as e:
#                 print(f"⚠️  Lỗi dòng {total_src}: {e} -> ghi nguyên dòng.")
#                 fout.write(line + "\n")
#                 total_out += 1

#     print("========== DONE ==========")
#     print(f"📘 Số dòng input: {total_src}")
#     print(f"🧩 Dòng phải chia (> {MAX_TOKENS} tokens): {long_count}")
#     print(f"✅ Tổng dòng đã ghi: {total_out}")
#     print(f"📄 Output: {DATA_FINAL_TXT}")
#     print(f"ℹ️ Tokenizer: {MODEL_NAME} | PREFIX: '{PREFIX}' | MAX_TOKENS: {MAX_TOKENS}")
