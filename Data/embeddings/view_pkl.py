import pickle
import os

def view_pkl_file(pkl_path):
    """Đọc và hiển thị nội dung file .pkl"""
    try:
        with open(pkl_path, "rb") as f:
            data = pickle.load(f)
        
        print(f" File: {pkl_path}")
        print(f" Số lượng mẫu: {len(data)}")
        print("=" * 80)
        
        for i, example in enumerate(data):
            print(f"\nMẪU {i+1}:")
            print(f"Query: {example.texts[0]}")
            print(f"Positive: {example.texts[1][:100]}...")
            print(f"Hard Negative: {example.texts[2][:100]}...")
            print(f"Easy Negative: {example.texts[3][:100]}...")
            print("-" * 60)
            
            # Chỉ hiển thị 3 mẫu đầu để tránh spam
            if i >= 5:
                print(f"\n... và {len(data) - 5} mẫu khác")
                break
                
    except FileNotFoundError:
        print(f" Không tìm thấy file: {pkl_path}")
    except Exception as e:
        print(f" Lỗi khi đọc file: {e}")

if __name__ == "__main__":
    pkl_file = r"D:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\AIP491_G9\Data\\embeddings\\train_triplet.pkl"
    view_pkl_file(pkl_file)
