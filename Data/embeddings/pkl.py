import os, pickle
from sentence_transformers import InputExample

# Đường dẫn file
file1 = r"D:\duongluuba\AIP491_G9\Data\embeddings\data_train_vnexpress.pkl"
file2 = r"D:\duongluuba\AIP491_G9\Data\embeddings\data_train_vnexpress_2.pkl"
file3 = r"D:\duongluuba\AIP491_G9\Data\embeddings\data_train_vnexpress_3.pkl"

# Đọc queries từ file 1
with open(file1, "rb") as f:
    data1 = pickle.load(f)
queries = []
for ex in data1:
    if isinstance(ex, InputExample) and len(ex.texts) >= 3:
        queries.append(ex.texts[0].strip())  # Lấy query gốc không có prefix

# Đọc examples từ file 2 và thay thế query
with open(file2, "rb") as f:
    data2 = pickle.load(f)

new_examples = []
for i, ex in enumerate(data2):
    if isinstance(ex, InputExample) and len(ex.texts) >= 3:
        # Lấy positive và negative texts từ example cũ
        _, pos_text, neg_text = ex.texts
        # Tạo example mới với query từ file 1
        if i < len(queries):
            new_example = InputExample(texts=[queries[i], pos_text, neg_text])
            new_examples.append(new_example)

# Ghi ra file mới
with open(file3, "wb") as f:
    pickle.dump(new_examples, f)

print(f'✅ Đã tạo file mới với {len(new_examples)} examples')
print(f'   - Số queries từ file 1: {len(queries)}')
print(f'   - Số examples từ file 2: {len(data2)}')
print(f'   - Số examples mới đã tạo: {len(new_examples)}')