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
def load_triplets(pkl_path, output_pkl):
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    triplets = []
    i = 0
    triplets_copy = []
    for ex in data:
        if isinstance(ex, InputExample) and len(ex.texts) >= 3:
            q = f"query {i}: {ex.texts[0].strip()}"
            p = f"passage: {ex.texts[1][:100]}"
            n = f"negative: {ex.texts[2][:100].strip()}"
            # q = f"{ex.texts[0].strip()}"
            # p = f"{ex.texts[1]}"
            # n = f"{ex.texts[2].strip()}"
            triplets.append(InputExample(texts=[q, p, n]))
            #  nếu i chia hết cho 2
            # if i % 2 == 1:
            #     triplets_copy.append(InputExample(texts=[q, p, n]))
            if i < 10:  
                print(f"{q}\n {p}\n {n}")
            i += 1
    print(f"✅ Tổng số mẫu hợp lệ: {len(triplets)}")
    # # Resume: load file pickle nếu đã tồn tại và không rỗng
    # try:
    #     with open(output_pkl, "wb") as f:
    #         pickle.dump(triplets_copy, f)
    #     print(f"💾 Đã lưu {len(triplets_copy)} mẫu vào {output_pkl} (triplets_copy)")
    # except Exception as e:
    #     print(f"⚠️ Lỗi khi lưu triplets_copy: {e}")

    # return triplets
    
# triplets = load_triplets(INPUT_FILE_PATH)

# # Chia train / val / test
# train_triplets, temp_triplets = train_test_split(triplets, test_size=0.2, random_state=42)
# val_triplets, test_triplets = train_test_split(temp_triplets, test_size=0.5, random_state=42)

# print(f"Train: {len(train_triplets)} | Val: {len(val_triplets)} | Test: {len(test_triplets)}")


if __name__ == "__main__":
    pkl_file = r"D:\duongluuba\AIP491_G9\Data\embeddings\data_train_vnexpress_copy.pkl"
    output_pkl=r"D:\duongluuba\AIP491_G9\Data\\embeddings\data_train_vnexpress_copy.pkl"
    load_triplets(pkl_file, output_pkl)
