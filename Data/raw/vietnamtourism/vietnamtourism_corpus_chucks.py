# import json
# from itertools import islice

# MAX_LEN = 150  # tùy chỉnh nếu cần chia nhỏ theo số từ

# def split_text_by_word_count(text, max_words):
#     """Chia văn bản thành các đoạn nhỏ theo số lượng từ."""
#     words = text.split()
#     return [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

# output = []
# line_id = 0

# #  File input và output
# input_path = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\vietnamtourism\vietnamtourism_data.txt"
# output_path = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\vietnamtourism\vietnamtourism_corpus_chunks.jsonl"

# #  Đọc 10 dòng đầu tiên
# with open(input_path, 'r', encoding='utf-8') as f:
#     lines = list(islice(f, 10))

# #  Xử lý từng dòng
# for line_num, line in enumerate(lines):
#     line = line.strip()
#     if not line:
#         continue

#     title = f"output_paragraph_{line_num + 1}"
#     chunks = [line]  # giữ nguyên dòng (hoặc thay bằng split_text_by_word_count nếu muốn chia nhỏ)

#     for chunk in chunks:
#         passage = f"Title: {title}\n\n{chunk}"
#         obj = {
#             "title": title,
#             "passage": passage,
#             "id": line_id,
#             "len": len(chunk.split())
#         }
#         output.append(obj)
#         line_id += 1

# #  Ghi ra file JSONL (mỗi đối tượng trên 1 dòng)
# with open(output_path, 'w', encoding='utf-8') as f:
#     for item in output:
#         f.write(json.dumps(item, ensure_ascii=False) + '\n')

# print(f" Đã xử lý và ghi {len(output)} đoạn vào file JSONL:")
# print(output_path)

import json

MAX_LEN = 150

def split_text_by_word_count(text, max_words):
    words = text.split()
    return [' '.join(words[i:i+max_words]) for i in range(0, len(words), max_words)]

output = []
line_id = 0  # tăng theo từng đoạn nhỏ

with open('D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data/vietnamtourism/vietnamtourism_data.txt', 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f):
        line = line.strip()
        if not line:
            continue  # bỏ qua dòng trống

        title = f"output_paragraph_{line_num + 1}"
        chunks = split_text_by_word_count(line, MAX_LEN)

        for chunk in chunks:
            passage = f"Title: {title}\n\n{chunk}"
            obj = {
                "title": title,
                "passage": passage,
                "id": line_id,
                "len": len(chunk.split())
            }
            output.append(obj)
            line_id += 1

# Ghi ra file JSONL
with open('D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data/vietnamtourism/vietnamtourism_corpus_chunks.jsonl', 'w', encoding='utf-8') as f:
    for item in output:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f" Đã xử lý xong và xuất {len(output)} đoạn vào output.jsonl")
