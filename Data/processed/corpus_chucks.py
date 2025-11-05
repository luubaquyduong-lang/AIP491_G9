import json
import re

MAX_LEN = 150  # tối đa từ mỗi chunk
MIN_LEN = 50   # tối thiểu từ mỗi chunk (nếu < 50 thì sẽ mượn/gộp)

# --- Tách câu (có hỗ trợ …) ---
SENT_SPLIT_RE = re.compile(r'(?<=[\.\!\?…])\s+')

def count_words(s: str) -> int:
    return len(s.split())

def split_text_by_sentence_balanced(text: str, max_words: int, min_words: int) -> list[str]:
    """
    Chia văn bản thành các chunk theo CÂU, mỗi chunk <= max_words.
    Sau đó cân bằng để tránh chunk < min_words bằng cách mượn/gộp từ chunk trước.
    """
    text = text.strip()
    if not text:
        return []

    # 1) tách câu
    sentences = [s.strip() for s in SENT_SPLIT_RE.split(text) if s.strip()]

    # 2) gom câu thành chunk không vượt max_words
    chunks_sent = []              # danh sách chunk, mỗi chunk = list các câu
    cur_sent_list, cur_len = [], 0
    for s in sentences:
        sw = count_words(s)
        # nếu riêng một câu đã > max_words thì cho câu đó thành 1 chunk riêng (nhỡ câu quá dài)
        if sw > max_words:
            if cur_sent_list:
                chunks_sent.append(cur_sent_list)
                cur_sent_list, cur_len = [], 0
            chunks_sent.append([s])
            continue

        if cur_len + sw > max_words and cur_sent_list:
            chunks_sent.append(cur_sent_list)
            cur_sent_list, cur_len = [s], sw
        else:
            cur_sent_list.append(s)
            cur_len += sw

    if cur_sent_list:
        chunks_sent.append(cur_sent_list)

    # 3) cân bằng: nếu chunk i có tổng từ < min_words, mượn câu từ cuối chunk i-1
    def chunk_len(sent_list):  # số từ của 1 chunk (list câu)
        return sum(count_words(x) for x in sent_list)

    i = 1
    while i < len(chunks_sent):
        cur_len = chunk_len(chunks_sent[i])
        if cur_len >= min_words:
            i += 1
            continue

        # thử mượn câu từ cuối chunk trước
        prev = chunks_sent[i-1]
        cur  = chunks_sent[i]

        # mượn đến khi đủ min_words hoặc chunk trước còn tối thiểu min_words
        while chunk_len(cur) < min_words and len(prev) > 0:
            # nếu chuyển 1 câu sang mà chunk trước vẫn >= min_words hoặc trước đó có >1 câu
            last_sentence = prev[-1]
            if chunk_len(prev) - count_words(last_sentence) < min_words and len(prev) == 1:
                break  # không thể mượn thêm (tránh làm chunk trước quá nhỏ)
            cur.insert(0, prev.pop())  # chuyển câu cuối của prev sang đầu cur

        # nếu vẫn nhỏ hơn min_words thì gộp hẳn vào chunk trước
        if chunk_len(cur) < min_words:
            chunks_sent[i-1] = prev + cur
            del chunks_sent[i]
            # không tăng i để xét lại chunk mới gộp với chunk phía trước nó
        else:
            i += 1

    # 4) chuyển list câu -> string
    chunks = [" ".join(slist) for slist in chunks_sent if slist]
    return chunks


# ==========================
# MAIN
# ==========================
input_file  = r"D:\duongluuba\AIP491_G9\Data\processed\data_final.txt"
output_file = r"D:\duongluuba\AIP491_G9\Data\processed\data_final_sorted.jsonl"

output = []
line_id = 0

with open(input_file, 'r', encoding='utf-8') as f:
    for line_num, raw in enumerate(f, start=1):
        line = raw.strip()
        if not line:
            continue
        # Bỏ qua header nhóm kiểu "===== Huế ====="
        if line.startswith("=====") and line.endswith("====="):
            continue

        title = f"output_paragraph_{line_num}"
        chunks = split_text_by_sentence_balanced(line, MAX_LEN, MIN_LEN)

        for chunk in chunks:
            obj = {
                "title": title,
                "passage": chunk,
                "id": line_id,
                "len": len(chunk.split())
            }
            output.append(obj)
            line_id += 1

with open(output_file, 'w', encoding='utf-8') as f:
    for item in output:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"✅ Đã xử lý xong và xuất {len(output)} đoạn vào {output_file}")
