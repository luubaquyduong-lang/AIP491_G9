import pickle
import os

# def view_pkl_file(pkl_path):
#     """Đọc và hiển thị nội dung file .pkl"""
#     try:
#         with open(pkl_path, "rb") as f:
#             data = pickle.load(f)
        
#         print(f" File: {pkl_path}")
#         print(f" Số lượng mẫu: {len(data)}")
#         print("=" * 80)
        
#         for i, example in enumerate(data):
#             print(f"\nMẪU {i+1}:")
#             print(f"Query: {example.texts[0]}")
#             print(f"Positive: {example.texts[1][:100]}...")
#             print(f"Hard Negative: {example.texts[2][:100]}...")
#             print(f"Easy Negative: {example.texts[3][:100]}...")
#             print("-" * 60)
            
#             # Chỉ hiển thị 3 mẫu đầu để tránh spam
#             if i >= 5:
#                 print(f"\n... và {len(data) - 5} mẫu khác")
#                 break
                
#     except FileNotFoundError:
#         print(f" Không tìm thấy file: {pkl_path}")
#     except Exception as e:
#         print(f" Lỗi khi đọc file: {e}")

import os, pickle, random, torch
from pathlib import Path
# from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer, InputExample

# DATASET_NAME = "data-train"               # tên dataset trong /kaggle/input/
# PKL_FILE     = "data_train_vnexpress.pkl" # file dữ liệu .pkl

# INPUT_FILE_PATH = Path(f"/kaggle/input/{DATASET_NAME}/{PKL_FILE}")
# OUTPUT_DIR = Path("/kaggle/working/bkai_finetuned_vn")
# OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# print("✅ Input:", INPUT_FILE_PATH.exists(), "|", INPUT_FILE_PATH)

# Load triplets và thêm prefix chuẩn E5
def load_triplets(pkl_path):
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    triplets = []
    i = 0
    for ex in data:
        if isinstance(ex, InputExample) and len(ex.texts) >= 3:
            q = f"query {i}: {ex.texts[0].strip()}"
            p = f"passage: {ex.texts[1][:100]}"
            n = f"negative: {ex.texts[2][:100].strip()}"
            triplets.append(InputExample(texts=[q, p, n]))
            if i < 10:
                i += 1  
                print(f"❇️ Mẫu hợp lệ - Query: {q} \n Positive: {p} \n  Negative: {n}")
    print(f"✅ Tổng số mẫu hợp lệ: {len(triplets)}")
    return triplets

# triplets = load_triplets(INPUT_FILE_PATH)

# # Chia train / val / test
# train_triplets, temp_triplets = train_test_split(triplets, test_size=0.2, random_state=42)
# val_triplets, test_triplets = train_test_split(temp_triplets, test_size=0.5, random_state=42)

# print(f"Train: {len(train_triplets)} | Val: {len(val_triplets)} | Test: {len(test_triplets)}")


if __name__ == "__main__":
    pkl_file = r"D:\duongluuba\AIP491_G9\Data\\embeddings\data_train_vnexpress_3.pkl"
    load_triplets(pkl_file)
