import json

MAX_LEN = 5000

def split_text_by_word_count(text, max_words):
    words = text.split()
    return [' '.join(words[i:i+max_words]) for i in range(0, len(words), max_words)]

output = []
line_id = 0  # tăng theo từng đoạn nhỏ

with open('D:\duongluuba\AIP491_G9\Data\\raw\\vnexpress\\vnexpress_data_v2.txt', 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f):
        line = line.strip()
        if not line:
            continue  # bỏ qua dòng trống

        title = f"output_paragraph_{line_num + 1}"
        chunks = split_text_by_word_count(line, MAX_LEN)

        for chunk in chunks:
            passage = f"{chunk}"
            obj = {
                "title": title,
                "passage": passage,
                "id": line_id,
                "len": len(chunk.split())
            }
            output.append(obj)
            line_id += 1

# Ghi ra file JSONL
with open('D:\duongluuba\AIP491_G9\Data\\raw\\vnexpress\\vnexpress_corpus_v2.jsonl', 'w', encoding='utf-8') as f:
    for item in output:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"✅ Đã xử lý xong và xuất {len(output)} đoạn vào vnexpress_corpus.jsonl")