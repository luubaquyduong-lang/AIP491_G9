import pandas as pd

# Đọc file CSV bạn gửi
df = pd.read_csv("ivivu_sapa.csv")

# Kiểm tra cột nào có title và content (giả sử tên là 'title' và 'content')
print(df.columns)

# Nếu khác thì sửa tên cột tương ứng
title_col = "title"
content_col = "content"

# Các nhóm từ khóa để phân loại
tour_keywords = ["tour", "nhà nghỉ", "khách sạn", "resort", "hotel"]
food_keywords = ["ăn", "món ăn", "đặc sản", "quán", "nhà hàng"]
culture_keywords = ["festival", "lễ hội"]

# Kết quả đầu ra
results = []
results.append("Tỉnh: Lào Cai\n")

for _, row in df.iterrows():
    title = str(row[title_col]).strip()
    content = str(row[content_col]).strip()

    title_lower = title.lower()

    if any(k in title_lower for k in tour_keywords):
        section = "Các tour hay ở đâu Lào Cai"
    elif any(k in title_lower for k in food_keywords):
        section = "Ẩm thực ở Lào Cai"
    elif any(k in title_lower for k in culture_keywords):
        section = "Sự kiện - Văn hóa ở Lào Cai"
    else:
        section = "Điểm đến ở Lào Cai"

    results.append(f"{section}:\n- {title}\n{content}\n")

# Ghi ra file .txt
with open("laocai_filtered.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))

print("✅ Lọc và ghi dữ liệu hoàn tất! File lưu tại: laocai_filtered.txt")
