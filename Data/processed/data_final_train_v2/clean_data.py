import re

def clean_passage(text: str) -> str:
    if not text:
        return ""

    t = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = t.split("\n")

    cleaned_lines = []
    for line in lines:
        s = line.strip()
        if not s:
            continue

        lower = s.lower()

        if lower.startswith("ảnh:") or lower.startswith("ảnh:") or lower.startswith("ảnh :"):
            continue
        if lower.startswith("ảnh minh họa") or lower.startswith("ảnh minh hoạ"):
            continue

        if lower.startswith("xem thêm:") or lower.startswith("xem thêm"):
            continue

        if lower.startswith("nguồn:") or lower.startswith("nguồn:") or lower.startswith("nguon:"):
            continue

        if set(s) <= {">"}:
            continue
        if s.startswith(">>") or s.startswith("> >"):
            continue

        cleaned_lines.append(s)

    cleaned = "\n".join(cleaned_lines).strip()

    cleaned = re.sub(r"\(?Ảnh: [^)]+?\)?", "", cleaned)
    cleaned = re.sub(r"Xem thêm:[^\n]+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"Nguồn:[^\n]+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r">+", "", cleaned)

    return cleaned.strip()


# ===============================
#  LOAD FILE VÀ CLEAN TỪNG DÒNG
# ===============================

input_path  = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\data_final_train_v2\data_final_sort_v2.txt"
output_path = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\data_final_train_v2\data_final_sort_v2_output.txt"

cleaned_lines = []

with open(input_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        clean = clean_passage(line)
        cleaned_lines.append(clean)

        if i % 500 == 0:
            print(f"Đã xử lý {i} dòng...")

# ===============================
#   GHI RA FILE MỚI
# ===============================

with open(output_path, "w", encoding="utf-8") as f:
    for cl in cleaned_lines:
        f.write(cl + "\n")

print("🎉 DONE! Đã lưu dữ liệu sạch vào:")
print(output_path)


