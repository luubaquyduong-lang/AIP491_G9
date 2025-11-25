


import json
import re

# ⚠️ 1) ĐƯỜNG DẪN INPUT / OUTPUT
INPUT_PATH  = "D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\data_final_train_v1\corpus_chunks_4347.jsonl"
OUTPUT_PATH = "D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\data_final_train_v1\corpus_chunks_4347_with_titles.jsonl"

def extract_section_title(text: str) -> str:
    """
    Lấy câu đầu tiên làm title thật.
    Cắt đến dấu . ? ! hoặc : đầu tiên.
    """
    text = text.strip()
    # ví dụ: "Giới thiệu An Giang. An Giang là tỉnh..."
    parts = re.split(r'(?<=[\.\?\!:])\s+', text, maxsplit=1)
    return parts[0].strip()

# ========= B1: Đọc & group theo title cũ (output_paragraph_x) =========
groups: dict[str, list[dict]] = {}

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        key = row["title"]              # ví dụ: "output_paragraph_15"
        groups.setdefault(key, []).append(row)

print(f"Đã đọc xong: {sum(len(v) for v in groups.values())} dòng,"
      f" có {len(groups)} đoạn gốc (output_paragraph_x).")

# ========= B2: Ghi file mới với section_title + chunk_id =========
with open(OUTPUT_PATH, "w", encoding="utf-8") as f_out:
    count = 0
    for para_key, rows in groups.items():
        # tiêu đề thật = câu đầu tiên của passage chunk đầu
        section_title = extract_section_title(rows[0]["passage"])

        for idx, row in enumerate(rows):
            # ID unique cho từng chunk
            row["chunk_id"] = f"{para_key}_chunk_{idx}"
            # tiêu đề thật để hiển thị / filter
            row["section_title"] = section_title
            # giữ lại title cũ như paragraph_id nếu muốn debug
            row["paragraph_id"] = row["title"]

            json.dump(row, f_out, ensure_ascii=False)
            f_out.write("\n")
            count += 1

print(f"✅ DONE. Đã ghi {count} dòng vào: {OUTPUT_PATH}")
