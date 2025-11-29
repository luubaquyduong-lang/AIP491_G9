import json
import re

MAX_LEN = 150  # tối đa từ mỗi chunk
MIN_LEN = 50   # tối thiểu từ mỗi chunk (nếu < 50 thì sẽ mượn/gộp)

# --- Tách câu (có hỗ trợ …) ---
SENT_SPLIT_RE = re.compile(r'(?<=[\.\!\?…])\s+')

def count_words(s: str) -> int:
    return len(s.split())

def first_sentence(text: str) -> str:
    """Lấy câu đầu tiên của đoạn gốc."""
    text = text.strip()
    if not text:
        return ""
    parts = SENT_SPLIT_RE.split(text)
    return parts[0].strip() if parts else text

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
    chunks_sent = []
    cur_sent_list, cur_len = [], 0
    for s in sentences:
        sw = count_words(s)

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

    # 3) cân bằng chunk < min_words
    def chunk_len(sent_list):
        return sum(count_words(x) for x in sent_list)

    i = 1
    while i < len(chunks_sent):
        cur_len = chunk_len(chunks_sent[i])
        if cur_len >= min_words:
            i += 1
            continue

        prev = chunks_sent[i-1]
        cur = chunks_sent[i]

        while chunk_len(cur) < min_words and len(prev) > 0:
            last_sentence = prev[-1]
            if chunk_len(prev) - count_words(last_sentence) < min_words and len(prev) == 1:
                break
            cur.insert(0, prev.pop())

        if chunk_len(cur) < min_words:
            chunks_sent[i-1] = prev + cur
            del chunks_sent[i]
        else:
            i += 1

    chunks = [" ".join(slist) for slist in chunks_sent if slist]
    return chunks


# ==========================
# MAIN
# ==========================
input_file  = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\data_final_train_v2\data_final_sort_v2_output.txt"
output_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\data_final_train_v1\data_final_sort_v1_fisrt_se.jsonl"

output = []
line_id = 0

with open(input_file, 'r', encoding='utf-8') as f:
    for line_num, raw in enumerate(f, start=1):
        line = raw.strip()
        if not line:
            continue

        # bỏ header kiểu "===== Huế ====="
        if line.startswith("=====") and line.endswith("====="):
            continue

        title = f"output_paragraph_{line_num}"

        # 🔥 LẤY CÂU ĐẦU TIÊN CỦA DÒNG GỐC (bạn yêu cầu)
        first_sent = first_sentence(line)

        chunks = split_text_by_sentence_balanced(line, MAX_LEN, MIN_LEN)

        for chunk in chunks:
            obj = {
                "title": title,
                "line_first_sentence": first_sent, # dòng đầu 
                "passage": chunk,
                "id": line_id,
                "len": len(chunk.split()),
            }
            output.append(obj)
            line_id += 1

with open(output_file, 'w', encoding='utf-8') as f:
    for item in output:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"✅ Đã xử lý xong và xuất {len(output)} đoạn vào {output_file}")

