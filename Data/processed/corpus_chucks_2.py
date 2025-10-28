import json
import re

MAX_LEN = 150  # giới hạn tối đa 150 từ mỗi chunk

def split_text_by_sentence(text, max_words):
    """
    Chia văn bản theo câu, đảm bảo mỗi chunk <= max_words và không bị cắt ngang câu.
    """
    # Tách câu theo dấu câu tiếng Việt
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        words = sentence.split()
        sentence_len = len(words)

        # Nếu thêm câu này mà vượt quá max_words → đóng chunk hiện tại lại
        if current_len + sentence_len > max_words:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            current_chunk = words
            current_len = sentence_len
        else:
            current_chunk.extend(words)
            current_len += sentence_len

    # Thêm chunk cuối cùng
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


output = []
line_id = 0  # tăng theo từng đoạn nhỏ

input_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data_final.txt"
output_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\corpus_chunks_2.jsonl"

with open(input_file, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f):
        line = line.strip()
        if not line:
            continue  # bỏ qua dòng trống

        title = f"output_paragraph_{line_num + 1}"
        chunks = split_text_by_sentence(line, MAX_LEN)

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
with open(output_file, 'w', encoding='utf-8') as f:
    for item in output:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"✅ Đã xử lý xong và xuất {len(output)} đoạn vào {output_file}")
