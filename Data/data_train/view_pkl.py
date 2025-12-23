
import os, pickle, random, torch, json
from pathlib import Path
from sentence_transformers import SentenceTransformer, InputExample
import pickle

def load_triplets(pkl_path, output_pkl=None, show_samples = 20):
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

    return triplets

def write_queries_to_jsonl(pkl_path, output_jsonl, num_samples=100):
    """
    Đọc file .pkl và ghi ra file JSONL với số lượng cặp query-positive được chỉ định.
    
    Args:
        pkl_path: Đường dẫn file .pkl chứa InputExample
        output_jsonl: Đường dẫn file JSONL output
        num_samples: Số lượng cặp query cần ghi (mặc định 100)
    """
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)

    query_pairs = []
    
    for ex in data:
        if not isinstance(ex, InputExample):
            continue

        texts = ex.texts
        if len(texts) == 2:
            query = texts[0].strip()
            positive = texts[1].strip()
            query_pairs.append({
                "query": query,
                "positive": positive
            })
        
        # Dừng khi đủ số lượng mẫu
        if len(query_pairs) >= num_samples:
            break
    
    # Ghi ra file JSONL
    with open(output_jsonl, "w", encoding="utf-8") as f:
        for pair in query_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    
    print(f"\n✅ Đã ghi {len(query_pairs)} cặp query vào file: {output_jsonl}")
    return query_pairs


# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    pkl_file = r"Code/Data/data_train/data_final_train_v1/data_filtered_v1.pkl"
    output_jsonl = r"query_pairs_100.jsonl"
    
    # Ghi 100 cặp query ra file JSONL
    write_queries_to_jsonl(pkl_file, output_jsonl, num_samples=100)

