
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
        if len(texts) == 2:
            q = f"{texts[0].strip()}"
            p = f"{texts[1].strip()}"
            # n = "(no negative)"
            triplets.append(InputExample(texts=[texts[0], texts[1]]))
        else:
            continue

        # Hiển thị vài mẫu đầu
        if i < show_samples:
            print(f"\n🔹 Mẫu {i+1}:")
            print(f"  {q}\n  {p}")

        i += 1

    print(f"\n✅ Tổng số mẫu hợp lệ: {len(triplets)}")

    # # Ghi ra file mới (tuỳ chọn)
    # if output_pkl:
    #     try:
    #         with open(output_pkl, "wb") as f:
    #             pickle.dump(triplets, f)
    #         print(f"💾 Đã lưu {len(triplets)} mẫu vào {output_pkl}")
    #     except Exception as e:
    #         print(f"⚠️ Lỗi khi lưu file pickle: {e}")

    # return triplets


# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    pkl_file = r"Code/Data/data_train/data_final_train_v1/data_filtered_v1.pkl"
    load_triplets(pkl_file, "output_pkl")

