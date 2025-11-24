
import os, pickle, random, torch
from pathlib import Path
from sentence_transformers import SentenceTransformer, InputExample
import pickle

def load_triplets(pkl_path, output_pkl=None, show_samples = 3):
    """
    Đọc file .pkl chứa InputExample và hiển thị nội dung các mẫu.
    Nếu có negative -> in ra 3 trường, nếu không -> in ra query và positive.
    """
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    triplets = []
    i = 0
    for ex in data:
        if not isinstance(ex, InputExample):
            continue
        texts = ex.texts
        if len(texts) == 2:
            q = f"{texts[0].strip()}"
            p = f"{texts[1].strip()}"
            # n = "(no negative)"
            triplets.append(InputExample(texts=[texts[0], texts[1]]))
        else:
            continue
        # Hiển thị vài mẫu đầu 
        if 290 < i < 300:
            print(f"\n🔹 Mẫu {i+1}:")
            print(f"  {q}\n  {p}")
        i += 1
    print(f"\n✅ Tổng số mẫu hợp lệ: {len(triplets)}")
if __name__ == "__main__":
    pkl_file = r"C:\Users\Acer\Downloads\data_train_v2_part_151.pkl"
    output_pkl = r"D:\duongluuba\AIP491_G9\Data\\embeddings\data_train_viewed.pkl"
    load_triplets(pkl_file, output_pkl)



# import os, re, pickle
# from sentence_transformers import InputExample

# # --- 1) Chuẩn hoá prefix: gộp "passage: passage: ..." -> "passage: "
# #     và "query: query: ..." -> "query: "
# PREFIX_RE = re.compile(r'^(?P<prefix>(?:passage|query)):\s*', flags=re.I)
# DUP_PREFIX_RE = re.compile(r'^(?:\s*(?:passage|query):\s*)+', flags=re.I)

# def normalize_prefix(text: str) -> tuple[str, str]:
#     """
#     Trả về (prefix_norm, content) với prefix_norm ∈ {"passage: ", "query: ", ""}.
#     Gộp nhiều prefix liên tiếp về 1 cái duy nhất (nếu có).
#     """
#     t = text.strip()
#     if DUP_PREFIX_RE.match(t):
#         # rút gọn nhiều prefix liên tiếp về 1
#         # lấy prefix đầu tiên
#         m = PREFIX_RE.match(t)
#         pf = m.group('prefix').lower() + ': '
#         # bỏ toàn bộ prefix lặp
#         content = DUP_PREFIX_RE.sub('', t, count=1)    # bỏ 1 cụm lặp lớn ở đầu
#         content = PREFIX_RE.sub('', content)           # phòng khi còn sót
#         return pf, content.lstrip()
#     m = PREFIX_RE.match(t)
#     if m:
#         pf = m.group('prefix').lower() + ': '
#         return pf, t[m.end():].lstrip()
#     return '', t

# def readd_prefix(prefix: str, content: str) -> str:
#     """Gắn lại prefix nếu có."""
#     return (prefix + content.strip()) if prefix else content.strip()


# # --- 2) Cắt header nếu cần ---
# def remove_header_if_needed(content: str, headers: list[str]) -> str:
#     """
#     Chỉ cắt phần trước dấu '.' đầu tiên nếu content BẮT ĐẦU bằng 1 cụm header trong danh sách.
#     So khớp không phân biệt hoa/thường, cho phép sai khác khoảng trắng nhẹ.
#     """
#     head = content[:80].lower()  # chỉ xét phần đầu để nhanh
#     for h in headers:
#         h_norm = h.lower().strip()
#         if not h_norm:
#             continue
#         # khớp nếu header nằm sát đầu (<=80 ký tự đầu)
#         if head.startswith(h_norm):
#             parts = content.split('.', 1)
#             if len(parts) == 2:
#                 return parts[1].strip()
#             return content.strip()
#     return content.strip()


# # --- 3) Pipeline xử lý pkl ---
# def process_triplets(input_pkl, headers_txt, output_pkl, show_samples=10):
#     # load headers
#     with open(headers_txt, 'r', encoding='utf-8') as f:
#         headers = [line.strip() for line in f if line.strip()]
#     print(f"📄 Headers loaded: {len(headers)}")

#     with open(input_pkl, 'rb') as f:
#         data = pickle.load(f)

#     new_items = []
#     shown = 0

#     for ex in data:
#         if not isinstance(ex, InputExample) or len(ex.texts) < 2:
#             continue

#         # --- query ---
#         q_prefix, q_content = normalize_prefix(ex.texts[0])

#         # --- positive ---
#         p_prefix, p_content = normalize_prefix(ex.texts[1])
#         # chỉ cắt header nếu p_content bắt đầu bằng 1 trong headers
#         p_new_content = remove_header_if_needed(p_content, headers)
#         p_new = readd_prefix(p_prefix, p_new_content)

#         if len(ex.texts) == 3:
#             # --- negative (nếu có) cũng chuẩn hóa prefix (không bắt buộc) ---
#             n_prefix, n_content = normalize_prefix(ex.texts[2])
#             n_new = readd_prefix(n_prefix, n_content)
#             new_items.append(InputExample(texts=[readd_prefix(q_prefix, q_content),
#                                                  p_new,
#                                                  n_new]))
#         else:
#             new_items.append(InputExample(texts=[readd_prefix(q_prefix, q_content), p_new]))

#         if shown < show_samples:
#             shown += 1
#             print(f"\n🔹 Mẫu {shown}:")
#             print("  query", readd_prefix(q_prefix, q_content)[:140])
#             print("  positive", ex.texts[1][:140])
#             print("  positive new", p_new[:140])
#             if len(ex.texts) == 3:
#                 print("  negative", new_items[-1].texts[2][:140])

#     print(f"\n✅ Tổng số mẫu xử lý: {len(new_items)}")
#     with open(output_pkl, 'wb') as f:
#         pickle.dump(new_items, f)
#     print(f"💾 Saved to: {output_pkl}")


# # ---- MAIN (đổi path theo của bạn) ----
# if __name__ == "__main__":
#     input_pkl  = r"D:\duongluuba\AIP491_G9\Data\embeddings\data_train_singlequery.pkl"
#     headers_txt = r"D:\duongluuba\AIP491_G9\Data\processed\headers_list.txt"
#     output_pkl = r"D:\duongluuba\AIP491_G9\Data\embeddings\data_train_singlequery_copy.pkl"
#     process_triplets(input_pkl, headers_txt, output_pkl)
