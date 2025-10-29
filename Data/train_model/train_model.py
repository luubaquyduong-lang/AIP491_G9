# =============================
# FINE-TUNE MÔ HÌNH BI-ENCODER TIẾNG VIỆT
# =============================

from sentence_transformers import SentenceTransformer, losses, InputExample
from torch.utils.data import DataLoader
import pickle
import shutil
import os

# === ĐƯỜNG DẪN LƯU MODEL SAU KHI TRAIN ===
output_dir = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\Train_model\fine_tuned_biencoder"

# Xóa thư mục cũ nếu đã tồn tại để tránh lỗi "File exists"
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)


# === 1 LOAD DỮ LIỆU TRAIN (Triplet format) ===
# train_triplet.pkl chứa danh sách các InputExample, mỗi phần tử gồm:
# anchor (câu gốc), positive (câu liên quan), negative (câu không liên quan)
with open(r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\train_triplet.pkl", "rb") as f:
    train_examples = pickle.load(f)

print(f" Đã load {len(train_examples)} mẫu huấn luyện.")


# === 2 LOAD MÔ HÌNH GỐC ===
# Có thể thay đổi model gốc tùy nhu cầu:
#  - "bkai-foundation-models/vietnamese-bi-encoder" (cho tiếng Việt)
#  - "sentence-transformers/all-MiniLM-L6-v2" (cho tiếng Anh)
#  - Hoặc model fine-tuned trước đó của bạn
model = SentenceTransformer("bkai-foundation-models/vietnamese-bi-encoder")


# === 3 TẠO DATALOADER ===
# shuffle=True giúp trộn dữ liệu mỗi epoch để tránh overfitting
# batch_size càng lớn → học ổn định hơn nhưng tốn RAM GPU
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)


# === 4 CHỌN HÀM MẤT MÁT (LOSS FUNCTION) ===
# Một số lựa chọn phổ biến:
# - losses.MultipleNegativesRankingLoss: phù hợp cho contrastive learning (triplet-like)
# - losses.TripletLoss: dùng khi có cặp (anchor, positive, negative)
# - losses.CosineSimilarityLoss: dùng cho cặp (text1, text2)
train_loss = losses.MultipleNegativesRankingLoss(model)


# === 5 TIẾN HÀNH FINE-TUNE ===
# Đây là bước chính huấn luyện mô hình
# Các thông số có thể điều chỉnh gồm:
# - epochs: số vòng huấn luyện (thường 3–10 tùy dữ liệu)
# - warmup_steps: giai đoạn làm nóng learning rate (khoảng 10% tổng bước)
# - output_path: nơi lưu model sau khi train xong
# - optimizer_params={'lr': 2e-5}: điều chỉnh learning rate thủ công (nếu muốn)
# - show_progress_bar=True: hiển thị tiến độ huấn luyện
# - use_amp=True: bật mixed precision để tăng tốc (nếu có GPU hỗ trợ)
model.fit(
    train_objectives=[(train_dataloader, train_loss)],  # Bộ dữ liệu và hàm loss
    epochs=3,                                           #  có thể tăng lên 5–10 nếu dữ liệu nhiều
    warmup_steps=int(len(train_dataloader) * 0.1),      #  làm nóng learning rate trong 10% đầu
    output_path=output_dir,                             # Nơi lưu model đã fine-tune
    optimizer_params={'lr': 2e-5},
    show_progress_bar=True,                             # Hiển thị tiến trình
    use_amp=True                                        # Bật tăng tốc với GPU hỗ trợ FP16
)

print(f" Fine-tune hoàn tất! Mô hình được lưu tại: {output_dir}")
