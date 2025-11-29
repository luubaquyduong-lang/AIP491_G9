import json
import re

# ================== CẤU HÌNH CHUNKING ==================
MAX_LEN   = 300  # tối đa số từ mỗi chunk
MIN_LEN   = 50   # tối thiểu số từ mỗi chunk (nếu < MIN_LEN thì bỏ)
OVERLAP   = 80  # số từ overlap giữa 2 chunk liên tiếp
STRIDE    = MAX_LEN - OVERLAP  # số từ "bước trượt" thực tế

# --- Tách câu (có hỗ trợ …) ---
SENT_SPLIT_RE = re.compile(r'(?<=[\.\!\?…])\s+')

def count_words(s: str) -> int:
    return len(s.strip().split())

def split_text_by_sentence_with_overlap(text: str,
                                        max_words: int,
                                        min_words: int,
                                        overlap_words: int) -> list[str]:
    """
    Chia văn bản thành các chunk theo CÂU.

    - Mỗi chunk chứa các câu liên tiếp, tổng số từ <= max_words.
    - Các chunk được trượt bằng bước (max_words - overlap_words),
      nên giữa 2 chunk liên tiếp sẽ có khoảng overlap_words từ
      được lặp lại (overlap theo vị trí từ, nhưng vẫn căn chỉnh theo câu).
    - Các chunk có ít hơn min_words sẽ bị bỏ qua.
    """
    text = text.strip()
    if not text:
        return []

    # 1) Tách câu
    sentences = [s.strip() for s in SENT_SPLIT_RE.split(text) if s.strip()]
    if not sentences:
        return []

    # 2) Đếm từ từng câu + prefix sum để tính nhanh số từ trong đoạn [i, j]
    word_counts = [count_words(s) for s in sentences]
    prefix = [0]
    for wc in word_counts:
        prefix.append(prefix[-1] + wc)

    total_words = prefix[-1]
    chunks = []

    start_idx = 0  # câu bắt đầu của window

    while start_idx < len(sentences):
        start_word_pos = prefix[start_idx]

        # Nếu số từ còn lại < min_words thì dừng luôn
        if total_words - start_word_pos < min_words:
            break

        # 3) Tìm end_idx sao cho số từ trong [start_idx, end_idx] <= max_words
        end_idx = start_idx
        while end_idx < len(sentences):
            words_in_span = prefix[end_idx + 1] - prefix[start_idx]
            if words_in_span > max_words:
                break
            end_idx += 1

        # lùi lại 1 câu vì end_idx đang +1
        end_idx -= 1

        if end_idx < start_idx:
            # Phòng trường hợp 1 câu quá dài > max_words:
            # cho câu đó thành 1 chunk riêng nếu >= min_words, rồi nhảy sang câu kế tiếp
            if word_counts[start_idx] >= min_words:
                chunks.append(sentences[start_idx])
            start_idx += 1
            continue

        # 4) Ghép chunk
        chunk_sentences = sentences[start_idx:end_idx + 1]
        chunk_text = " ".join(chunk_sentences).strip()
        n_words = count_words(chunk_text)

        if n_words >= min_words:
            chunks.append(chunk_text)

        # 5) Tính vị trí bắt đầu mới theo STRIDE (có overlap)
        target_next_start = start_word_pos + STRIDE
        new_start = start_idx

        # tìm câu đầu tiên sao cho prefix[new_start] >= target_next_start
        while new_start < len(sentences) and prefix[new_start] < target_next_start:
            new_start += 1

        # tránh đứng yên gây vòng lặp vô hạn
        if new_start <= start_idx:
            new_start = start_idx + 1

        start_idx = new_start

    return chunks


# ==========================
# MAIN
# ==========================
input_file  = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\data_final_train_v2\data_final_sort_v2_output.txt"
output_file = r"D:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\AIP491_G9\Data\\processed\data_final_sort_v2.jsonl"

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
        chunks = split_text_by_sentence_with_overlap(
            line,
            max_words=MAX_LEN,
            min_words=MIN_LEN,
            overlap_words=OVERLAP
        )

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
