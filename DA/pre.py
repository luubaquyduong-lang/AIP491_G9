# import pandas as pd
# import glob
# import os

# # 📂 Thư mục chứa dữ liệu
# folder_path = "preprocess/"

# # 🔍 Lấy tất cả file CSV trong thư mục đó
# all_files = glob.glob(os.path.join(folder_path, "*.csv"))

# dfs = []
# for file in all_files:
#     df = pd.read_csv(file)
#     df["source_file"] = os.path.basename(file)  # Thêm cột để biết file gốc
#     dfs.append(df)

# # 🧩 Gộp tất cả file thành một DataFrame
# merged_df = pd.concat(dfs, ignore_index=True)

# # 💾 Lưu thành 1 file duy nhất
# output_file = "merged_tourism_data.csv"
# merged_df.to_csv(output_file, index=False, encoding="utf-8-sig")

# print(f"✅ Đã gộp {len(all_files)} file lại thành: {output_file}")
# print(f"📄 Tổng số bài viết: {len(merged_df)}")

# ----------------------------------------
# import pandas as pd

# # 📂 Đọc file đã gộp
# df = pd.read_csv("merged_tourism_data.csv")

# print("📄 Số dòng ban đầu:", len(df))

# # 🧽 Loại bỏ các dòng có nội dung trống hoặc NaN
# df = df.dropna(subset=["content", "title"], how="any")

# # 🚫 Loại bỏ dòng trùng
# df = df.drop_duplicates(subset=["title", "content"], keep="first")

# # ✨ Làm sạch nội dung cơ bản
# def clean_text(text):
#     text = str(text)
#     text = text.replace("\n", " ").replace("\r", " ")
#     text = " ".join(text.split())  # loại bỏ khoảng trắng thừa
#     return text

# df["title"] = df["title"].apply(clean_text)
# df["content"] = df["content"].apply(clean_text)

# # 🧾 Giữ lại duy nhất 2 cột cần thiết
# df = df[["title", "content"]]

# # 💾 Lưu file kết quả
# output_file = "cleaned_tourism_data.csv"
# df.to_csv(output_file, index=False, encoding="utf-8-sig")

# print(f"✅ Đã làm sạch và chỉ giữ 2 cột (title, content).")
# print(f"📊 Còn lại: {len(df)} dòng sau khi làm sạch.")
# print(f"📁 File lưu tại: {output_file}")
# ----------------------------------------
# import pandas as pd

# # Đọc file đã làm sạch
# df = pd.read_csv("cleaned_tourism_data.csv")

# provinces = [
#     "An Giang", "Bà Rịa - Vũng Tàu", "Bắc Giang", "Bắc Kạn", "Bạc Liêu", "Bắc Ninh",
#     "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước", "Bình Thuận", "Cà Mau",
#     "Cần Thơ", "Cao Bằng", "Đà Nẵng", "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai",
#     "Đồng Tháp", "Gia Lai", "Hà Giang", "Hà Nam", "Hà Nội", "Hà Tĩnh", "Hải Dương",
#     "Hải Phòng", "Hậu Giang", "Hòa Bình", "Hưng Yên", "Khánh Hòa", "Kiên Giang",
#     "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Long An", "Nam Định",
#     "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên", "Quảng Bình",
#     "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sóc Trăng", "Sơn La",
#     "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế",
#     "Tiền Giang", "TP. Hồ Chí Minh", "Trà Vinh", "Tuyên Quang", "Vĩnh Long",
#     "Vĩnh Phúc", "Yên Bái"
# ]

# # Bản đồ địa danh về tỉnh
# location_to_provinces = {
#     "Hạ Long": "Quảng Ninh",
#     "Cô Tô": "Quảng Ninh",
#     "Móng Cái": "Quảng Ninh",
#     "Yên Tử": "Quảng Ninh",
#     "Phú Quốc": "Kiên Giang",
#     "Hà Tiên": "Kiên Giang",
#     "Rạch Giá": "Kiên Giang",
#     "Nha Trang": "Khánh Hòa",
#     "Cam Ranh": "Khánh Hòa",
#     "Đà Lạt": "Lâm Đồng",
#     "Bảo Lộc": "Lâm Đồng",
#     "Hội An": "Quảng Nam",
#     "Mỹ Sơn": "Quảng Nam",
#     "Huế": "Thừa Thiên Huế",
#     "Sa Pa": "Lào Cai",
#     "Fansipan": "Lào Cai",
#     "Phan Thiết": "Bình Thuận",
#     "Mũi Né": "Bình Thuận",
#     "Quy Nhơn": "Bình Định",
#     "Eo Gió": "Bình Định",
#     "Đà Nẵng": "Đà Nẵng",
#     "Bà Nà": "Đà Nẵng",
#     "Cần Thơ": "Cần Thơ",
#     "Vũng Tàu": "Bà Rịa - Vũng Tàu",
#     "Long Hải": "Bà Rịa - Vũng Tàu",
#     "Hồ Tràm": "Bà Rịa - Vũng Tàu",
#     "Hà Nội": "Hà Nội",
#     "Ba Vì": "Hà Nội",
#     "Hồ Tây": "Hà Nội",
#     "Tràng An": "Ninh Bình",
#     "Tam Cốc": "Ninh Bình",
#     "TPHCM": "TP. Hồ Chí Minh",
#     "Sài Gòn": "TP. Hồ Chí Minh",
#     "TP. HCM": "TP. Hồ Chí Minh",

#     # bạn có thể mở rộng thêm ở đây
# }

# # Hàm xác định tỉnh
# def detect_province(text):
#     text = str(text)
#     for loc, province in location_to_provinces.items():
#         if loc.lower() in text.lower():
#             return province
#     for province in provinces:
#         if province.lower() in text.lower():
#             return province
#     return "Không xác định"

# df["province"] = df["title"].apply(detect_province) + df["content"].apply(detect_province)

# # Loại bỏ trùng “Không xác địnhKhông xác định”
# df["province"] = df["province"].replace("Không xác địnhKhông xác định", "Không xác định")

# # Lưu file mới
# df.to_csv("tourism_with_province.csv", index=False, encoding="utf-8-sig")

# print("✅ Đã gắn nhãn tỉnh/thành cho từng bài viết.")

# ----------------------------------------
# 3️⃣ PHÂN LOẠI CHỦ ĐỀ
# ======================
# import pandas as pd

# # 🗂️ Đọc file gốc
# df = pd.read_csv("tourism_with_province.csv")

# # Xóa cột trùng nếu có
# df = df.loc[:, ~df.columns.duplicated()]

# # Danh sách tỉnh thành Việt Nam
# provinces = [
#     "An Giang", "Bà Rịa - Vũng Tàu", "Bạc Liêu", "Bắc Giang", "Bắc Kạn", "Bắc Ninh", "Bến Tre",
#     "Bình Dương", "Bình Định", "Bình Phước", "Bình Thuận", "Cà Mau", "Cần Thơ", "Cao Bằng",
#     "Đà Nẵng", "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Giang",
#     "Hà Nam", "Hà Nội", "Hà Tĩnh", "Hải Dương", "Hải Phòng", "Hậu Giang", "Hòa Bình", "Hưng Yên",
#     "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai",
#     "Long An", "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên",
#     "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sóc Trăng",
#     "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế",
#     "Tiền Giang", "TP. Hồ Chí Minh", "Trà Vinh", "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc",
#     "Yên Bái"
# ]

# # 🧹 Hàm làm sạch giá trị province
# def clean_province(value):
#     if not isinstance(value, str) or value.strip() == "":
#         return "Không xác định"
    
#     value = value.strip()

#     # Nếu có dạng "Thừa Thiên HuếThừa Thiên Huế" → chia đôi và so sánh
#     mid = len(value) // 2
#     if value[:mid] == value[mid:]:
#         return value[:mid]

#     # Nếu chứa 2 tỉnh liền nhau, chọn phần nào khớp danh sách
#     for p in provinces:
#         if p in value:
#             return p

#     return value

# # Áp dụng hàm
# df["province"] = df["province"].apply(clean_province)

# # Lưu lại
# df.to_csv("vietnam_tourism_with_province_fixed.csv", index=False, encoding="utf-8-sig")

# print("✅ Đã làm sạch cột 'province' thành công → vietnam_tourism_with_province_fixed.csv")

# # 3️⃣ PHÂN LOẠI CHỦ ĐỀ
# # ======================

# CATEGORY_KEYWORDS = {
#     "Ẩm thực": [
#         "ẩm thực", "ăn uống", "món ngon", "đặc sản", "nhà hàng", "quán ăn",
#         "food", "đồ ăn", "buffet", "hải sản", "ăn gì", "món ăn", "đi ăn"
#     ],
#     "Di chuyển": [
#         "di chuyển", "phương tiện", "đi lại", "xe khách", "máy bay", "tàu hỏa",
#         "xe bus", "đường đi", "phà", "đi xe", "vé máy bay"
#     ],
#     "Giới thiệu": [
#         "giới thiệu", "resort", "khách sạn", "villa", "homestay",
#         "lưu trú", "ở đâu", "review khách sạn", "nơi ở"
#     ],
#     "Mua sắm": [
#         "mua sắm", "mua gì", "quà", "quà lưu niệm", "đặc sản mang về", "shopping",
#         "chợ", "siêu thị", "món quà", "làm quà", "mua ở đâu"
#     ],
#     "Điểm đến": [
#         "đi đâu", "địa điểm", "check-in", "tham quan", "tour", "review", "đi chơi",
#         "khám phá", "khu du lịch", "điểm đến", "bãi biển", "núi", "hang động", "chùa",
#         "thắng cảnh", "trải nghiệm", "du lịch", "đi phượt"
#     ],
#     "Sự kiện - Văn hóa": [
#         "lễ hội", "văn hóa", "truyền thống", "festival", "nghệ thuật", "biểu diễn",
#         "tập tục", "phong tục", "sự kiện", "văn hóa dân gian", "ngày hội", "di sản"
#     ]
# }

# def detect_category(title, content):
#     text = (str(title) + " " + str(content)).lower()
#     for category, keywords in CATEGORY_KEYWORDS.items():
#         if any(kw in text for kw in keywords):
#             return category
#     return "Khác"

# df_all["category"] = df_all.apply(lambda x: detect_category(x["title"], x["content"]), axis=1)

# # ======================
# # 4️⃣ GOM NHÓM THEO TỈNH + CHỦ ĐỀ
# # ======================

# grouped = (
#     df_all.groupby(["province", "category"])["content"]
#     .apply(lambda x: "\n\n".join(x))
#     .reset_index()
# )

# # ======================
# # 5️⃣ LƯU FILE KẾT QUẢ
# # ======================
# output_file = "vietnam_tourism_cleaned.csv"
# grouped.to_csv(output_file, index=False, encoding="utf-8-sig")

# print("\n🎉 Đã xử lý xong dữ liệu du lịch Việt Nam!")
# print(f"📁 File kết quả: {output_file}")
# print(f"📊 Tổng số nhóm tỉnh + chủ đề: {len(grouped)}")
# -----------------------------------------
# import pandas as pd

# # 🗂️ Đọc file gốc
# df = pd.read_csv("tourism_with_province.csv")

# # Xóa cột trùng nếu có
# df = df.loc[:, ~df.columns.duplicated()]

# # Danh sách tỉnh thành Việt Nam
# provinces = [
#     "An Giang", "Bà Rịa - Vũng Tàu", "Bạc Liêu", "Bắc Giang", "Bắc Kạn", "Bắc Ninh", "Bến Tre",
#     "Bình Dương", "Bình Định", "Bình Phước", "Bình Thuận", "Cà Mau", "Cần Thơ", "Cao Bằng",
#     "Đà Nẵng", "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Giang",
#     "Hà Nam", "Hà Nội", "Hà Tĩnh", "Hải Dương", "Hải Phòng", "Hậu Giang", "Hòa Bình", "Hưng Yên",
#     "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai",
#     "Long An", "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên",
#     "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sóc Trăng",
#     "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế",
#     "Tiền Giang", "TP. Hồ Chí Minh", "Trà Vinh", "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc",
#     "Yên Bái"
# ]

# # 🧹 Hàm làm sạch giá trị province
# def clean_province(value):
#     if not isinstance(value, str) or value.strip() == "":
#         return "Không xác định"
    
#     value = value.strip()

#     # Nếu có dạng "Thừa Thiên HuếThừa Thiên Huế" → chia đôi và so sánh
#     mid = len(value) // 2
#     if value[:mid] == value[mid:]:
#         return value[:mid]

#     # Nếu chứa 2 tỉnh liền nhau, chọn phần nào khớp danh sách
#     for p in provinces:
#         if p in value:
#             return p

#     return value

# # Áp dụng hàm
# df["province"] = df["province"].apply(clean_province)

# # Lưu lại
# df.to_csv("vietnam_tourism_with_province_fixed.csv", index=False, encoding="utf-8-sig")

# print("✅ Đã làm sạch cột 'province' thành công → vietnam_tourism_with_province_fixed.csv")
# ------------------------------------------
# import pandas as pd

# # 🗂️ Đọc file sau khi đã fix province
# input_file = "vietnam_tourism_with_province_fixed.csv"
# output_file = "vietnam_tourism_with_province_filtered.csv"

# # Đọc dữ liệu
# df = pd.read_csv(input_file)

# # Kiểm tra trước khi lọc
# print(f"📊 Trước khi lọc: {len(df)} bài viết")

# # 🧹 Loại bỏ bài có province là "Không xác định" hoặc ô trống
# df = df[df["province"].notna()]                      # bỏ các ô NaN
# df = df[df["province"].str.strip() != "Không xác định"]  # bỏ giá trị không xác định
# df = df[df["province"].str.strip() != ""]            # bỏ rỗng

# # Lưu lại file mới
# df.to_csv(output_file, index=False, encoding="utf-8-sig")

# print(f"✅ Sau khi lọc: {len(df)} bài viết còn lại")
# print(f"📁 Dữ liệu đã lưu tại: {output_file}")
 # ------------------------------------------
# loại ivivu
# import pandas as pd
# import re

# # 🗂️ Đọc file đầu vào
# input_file = "vietnam_tourism_with_province_filtered.csv"
# output_file = "vietnam_tourism_cleaned.csv"

# # Đọc dữ liệu
# df = pd.read_csv(input_file)

# # 🧹 Hàm loại bỏ từ "ivivu" (bất kể viết hoa, thường, .com, v.v.)
# def remove_ivivu(text):
#     if pd.isna(text):
#         return text
#     # Xóa các cụm như ivivu, IVIVU.COM, www.ivivu.com
#     return re.sub(r"\bivivu(\.com)?\b", "", str(text), flags=re.IGNORECASE).strip()

# # Áp dụng cho tất cả các cột văn bản
# for col in df.columns:
#     if df[col].dtype == "object":
#         df[col] = df[col].apply(remove_ivivu)

# # 🧾 Xóa các khoảng trắng thừa do việc remove gây ra
# df = df.replace(r'\s+', ' ', regex=True)

# # 💾 Lưu lại file sạch
# df.to_csv(output_file, index=False, encoding="utf-8-sig")

# print(f"✅ Đã loại bỏ 'iVIVU' khỏi dữ liệu.")
# print(f"📁 File mới lưu tại: {output_file}")
# print(f"📊 Tổng số bài viết: {len(df)}")
# ------------------------------------------
# lọc tỉnh sai
# import pandas as pd
# import re

# # Danh sách 63 tỉnh/thành Việt Nam
# provinces = [
#     "An Giang", "Bà Rịa - Vũng Tàu", "Bắc Giang", "Bắc Kạn", "Bạc Liêu", "Bắc Ninh",
#     "Bến Tre", "Bình Dương", "Bình Định", "Bình Phước", "Bình Thuận", "Cà Mau",
#     "Cần Thơ", "Cao Bằng", "Đà Nẵng", "Đắk Lắk", "Đắk Nông", "Điện Biên",
#     "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Giang", "Hà Nam", "Hà Nội", "Hà Tĩnh",
#     "Hải Dương", "Hải Phòng", "Hậu Giang", "Hòa Bình", "Hưng Yên", "Khánh Hòa",
#     "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai",
#     "Long An", "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ",
#     "Phú Yên", "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị",
#     "Sóc Trăng", "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa",
#     "Thừa Thiên Huế", "Tiền Giang", "TP Hồ Chí Minh", "Trà Vinh", "Tuyên Quang",
#     "Vĩnh Long", "Vĩnh Phúc", "Yên Bái"
# ]

# # Đọc file CSV
# df = pd.read_csv("vietnam_tourism_cleaned.csv")

# def has_wrong_province(content, province):
#     if not isinstance(content, str):
#         return False
#     for prov in provinces:
#         if prov.lower() in content.lower() and prov.lower() != province.lower():
#             return True
#     return False

# # Lọc dữ liệu
# filtered_df = df[~df.apply(lambda row: has_wrong_province(row['content'], row['province']), axis=1)]

# # Lưu lại file mới
# filtered_df.to_csv("dulichviet_final.csv", index=False, encoding="utf-8-sig")

# print(f"✅ Đã lọc xong! Số bài còn lại: {len(filtered_df)} / {len(df)}")

# # ------------------------------------------
# import pandas as pd
# import os

# # INPUT / OUTPUT
# INPUT_CSV = "dulichviet_final.csv"
# OUTPUT_CSV = "dulichviet_filtered_final4.csv"
# OUTPUT_TXT = "dulichviet_filtered_by_province4.txt"

# # ---------------------
# # 1. Đọc dữ liệu
# # ---------------------
# df = pd.read_csv(INPUT_CSV)
# df = df[df["province"].notna()]
# df = df[df["province"].astype(str).str.strip().str.lower() != "không xác định"]

# df["title_lower"] = df["title"].astype(str).str.lower()
# df["content_lower"] = df["content"].astype(str).str.lower()

# # ---------------------
# # 2. Từ khóa chủ đề
# # ---------------------
# CATEGORY_KEYWORDS = {
#     "Ẩm thực": [
#         "ẩm thực", "ăn uống", "món ngon", "đặc sản", "nhà hàng", "quán ăn",
#         "food", "đồ ăn", "buffet", "hải sản", "ăn gì", "món ăn", "đi ăn",
#         "lẩu", "thưởng thức", "ăn", "ngon", "món", "bún"
    
#     ],
#     "Mua sắm": [
#         "mua gì", "mua sắm", "quà", "quà lưu niệm", "đặc sản mang về", "mua ở đâu", "làm quà"
#     ],
#     "Điểm đến": [
#         "đi đâu", "địa điểm", "check-in", "tham quan", "đi chơi", "khám phá",
#         "khu du lịch", "bãi biển", "hang động", "ghé thăm", "view",
#         "công trình", "chùa", "thắng cảnh", "trải nghiệm", "du lịch", "đi phượt", "chơi đâu"
#     ],
#     "Sự kiện - Văn hóa": [
#         "lễ hội", "văn hóa", "truyền thống", "festival", "nghệ thuật", "tập tục",
#         "phong tục", "sự kiện", "văn hóa dân gian", "ngày hội", "di sản"
#     ]
# }

# PLACE_KEYWORDS_IN_TITLE = [
#     "check-in", "khách sạn", "khu du lịch", "bãi biển",
#     "view", "công trình", "chùa", "thắng cảnh", "nghỉ dưỡng"
# ]

# # ---------------------
# # 3. Hàm phân loại
# # ---------------------
# def classify_row(title_lower: str, content_lower: str):
#     matched = []

#     # ✅ Ẩm thực (xét title + content)
#     text_for_food = title_lower + " " + content_lower
#     for kw in CATEGORY_KEYWORDS["Ẩm thực"]:
#         if kw in text_for_food:
#             matched.append("Ẩm thực")
#             break


#     # ✅ Các chủ đề khác (chỉ xét title như cũ)
#     for cat, kws in CATEGORY_KEYWORDS.items():
#         if cat in ["Ẩm thực", "Di chuyển"]:
#             continue
#         for kw in kws:
#             if kw in title_lower:
#                 matched.append(cat)
#                 break

#     # ✅ Nếu title chứa từ khóa địa điểm thì loại bỏ nhãn Ẩm thực
#     for place_kw in PLACE_KEYWORDS_IN_TITLE:
#         if place_kw in title_lower and "Ẩm thực" in matched:
#             matched = [c for c in matched if c != "Ẩm thực"]
#             break

#     return matched


# df["categories_list"] = df.apply(lambda r: classify_row(r["title_lower"], r["content_lower"]), axis=1)

# # ---------------------
# # 4. Loại bỏ bài không có chủ đề
# # ---------------------
# df = df[df["categories_list"].map(len) > 0].copy()

# # ---------------------
# # 5. Lọc lại riêng phần Ẩm thực
# # ---------------------
# FOOD_TITLE_KEYWORDS = CATEGORY_KEYWORDS["Ẩm thực"]

# def refine_food_category(row):
#     cats = row["categories_list"]
#     if "Ẩm thực" not in cats:
#         return cats
#     # Nếu không có bất kỳ từ khóa ẩm thực nào trong title thì xóa
#     if not any(kw in row["title_lower"] for kw in FOOD_TITLE_KEYWORDS):
#         cats = [c for c in cats if c != "Ẩm thực"]
#     return cats

# df["categories_list"] = df.apply(refine_food_category, axis=1)

# # Xóa bài không còn nhãn
# df = df[df["categories_list"].map(len) > 0].copy()

# df["categories"] = df["categories_list"].apply(lambda lst: "; ".join(lst))

# # ---------------------
# # 6. Xuất CSV
# # ---------------------
# out_cols = ["province", "title", "content", "categories"]
# df[out_cols].to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
# print(f"✅ Lưu CSV kết quả: {OUTPUT_CSV} (số bài giữ lại: {len(df)})")

# # ---------------------
# # 7. Xuất TXT nhóm theo tỉnh + chủ đề
# # ---------------------
# with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
#     for province, g in df.groupby("province"):
#         f.write(f"\n===== {province.upper()} =====\n")
#         for category in CATEGORY_KEYWORDS.keys():
#             subset = g[g["categories"].str.contains(category, na=False)]
#             if subset.empty:
#                 continue
#             f.write(f"\n## {category} ##\n")
#             for _, row in subset.iterrows():
#                 f.write(row["title"].strip() + "\n")
#                 f.write(row["content"].strip() + "\n\n")

# print(f"✅ Lưu TXT nhóm theo tỉnh: {OUTPUT_TXT}")

# # ---------------------
# # 8. Thống kê nhanh
# # ---------------------
# category_counts = {}
# for cat in CATEGORY_KEYWORDS.keys():
#     category_counts[cat] = df["categories"].str.contains(cat, na=False).sum()

# print("\n📊 Thống kê số bài cho mỗi chủ đề:")
# for cat, cnt in category_counts.items():
#     print(f" - {cat}: {cnt}")

# print("\n🎉 Hoàn tất. File CSV và TXT đã được tạo.")

import re
import pandas as pd

# Đọc file hiện có
df = pd.read_csv(r"C:\Users\admin\Documents\GitHub\AIP491_G9\DA\ivivu.txt", encoding="utf-8")


def remove_photo_credit(text):
    if isinstance(text, str):
        # Loại bỏ tất cả các cụm "Ảnh: ..." (có thể nhiều cụm trong 1 câu)
        text = re.sub(r'(Ảnh\s*:\s*[^.,\n]*[.,]?\s*)+', '', text)
        
        # Nếu còn cụm "Ảnh:" đứng lẻ thì xóa nốt
        text = re.sub(r'Ảnh\s*:\s*', '', text)

        # Loại bỏ khoảng trắng thừa
        text = re.sub(r'\s{2,}', ' ', text).strip()
    return text

# Áp dụng làm sạch
df['content'] = df['content'].apply(remove_photo_credit)

# Lưu lại file đã xử lý
df.to_csv("dulich_cleaned_final.csv", index=False, encoding="utf-8-sig")

print("✅ Đã loại bỏ các cụm 'Ảnh: ...' và lưu file thành dulich_cleaned_final.csv")

