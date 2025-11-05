
import os, pickle, random, torch
from pathlib import Path
from sentence_transformers import SentenceTransformer, InputExample
import pickle

def load_triplets(pkl_path, output_pkl=None, show_samples=20):
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
        if len(texts) == 3:
            q = f"query {i}: {texts[0].strip()}"
            p = f"positive: {texts[1][:150].strip()}"
            n = f"negative: {texts[2][:150].strip()}"
            triplets.append(InputExample(texts=[texts[0], texts[1], texts[2]]))
        elif len(texts) == 2:
            q = f"query {i}: {texts[0].strip()}"
            p = f"positive: {texts[1].strip()}"
            n = "(no negative)"
            triplets.append(InputExample(texts=[texts[0], texts[1]]))
        else:
            continue

        # Hiển thị vài mẫu đầu
        if i < show_samples:
            print(f"\n🔹 Mẫu {i+1}:")
            print(f"  {q}\n  {p}\n  {n}")

        i += 1

    print(f"\n✅ Tổng số mẫu hợp lệ: {len(triplets)}")

    # Ghi ra file mới (tuỳ chọn)
    if output_pkl:
        try:
            with open(output_pkl, "wb") as f:
                pickle.dump(triplets, f)
            print(f"💾 Đã lưu {len(triplets)} mẫu vào {output_pkl}")
        except Exception as e:
            print(f"⚠️ Lỗi khi lưu file pickle: {e}")

    return triplets


# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    pkl_file = r"D:\duongluuba\AIP491_G9\Data\embeddings\data_train_singlequery.pkl"
    output_pkl = r"D:\duongluuba\AIP491_G9\Data\embeddings\data_train_viewed.pkl"
    load_triplets(pkl_file, output_pkl)
