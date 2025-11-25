# ########################################### Danh sách các file cần gộp ############################################## 
# input_files = [
#     r"D:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\AIP491_G9\Data\\raw\vnexpress\\vnexpress_data_v2.txt",
#     r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\raw\vietnamtourism\vietnamtourism_data.txt",
#     r"D:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\AIP491_G9\Data\\raw\\ivivu\\ivivu_crawler_data.txt",
#     # r"D:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\AIP491_G9\Data\\raw\\dulichviet\dulichviet_crawler_data.txt"
# ]

# output_file = r"D:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\AIP491_G9\Data\\processed\data_final_v2.txt"

# with open(output_file, "w", encoding="utf-8") as outfile:
#     for file_name in input_files:
#         with open(file_name, "r", encoding="utf-8") as infile:
#             content = infile.read().strip()
#             outfile.write(content + "\n")  # thêm dòng trống giữa các file

# print(f"✅ Đã gộp {len(input_files)} file vào '{output_file}' thành công!")



# ########################################### sắp xếp dữ liệu theo danh sách địa danh chuẩn ##############################################

# import re
# from collections import defaultdict

# INPUT_FILE  = r"D:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\AIP491_G9\Data\\processed\data_final_v2.txt"
# OUTPUT_FILE = r"D:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\AIP491_G9\Data\\processed\data_final_sort_v2.txt"

# CANONICAL = [
#     "An Giang", "Bà Rịa - Vũng Tàu", "Bạc Liêu", "Bắc Giang", "Bắc Kạn", "Bắc Ninh",
#     "Bến Tre", "Bình Dương", "Bình Định", "Bình Phước", "Bình Thuận", "Cà Mau",
#     "Cao Bằng", "Cần Thơ", "Đà Nẵng", "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai", "Đồng Tháp",
#     "Gia Lai", "Hà Giang", "Hà Nam", "Hà Nội", "Hà Tĩnh", "Hải Dương", "Hải Phòng",
#     "Hậu Giang", "Hòa Bình", "Hưng Yên", "Khánh Hòa", "Kiên Giang", "Kon Tum",
#     "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Long An", "Nam Định", "Nghệ An",
#     "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên", "Quảng Bình", "Quảng Nam",
#     "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sóc Trăng", "Sơn La", "Tây Ninh",
#     "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang",
#     "Trà Vinh", "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái",
#     "TP HCM",  # Thành phố Hồ Chí Minh
#     "Cần Thơ", # Thành phố trực thuộc TW
#     "Đà Nẵng", # Thành phố trực thuộc TW
#     "Hải Phòng", # Thành phố trực thuộc TW
#     "Hà Nội"   # Thủ đô
# ]
# print(len(
# CANONICAL))
# ALIASES = {
#     r"TP\.?\s*HCM": "TP HCM",
#     r"TPHCM": "TP HCM",
#     r"Tp\.?\s*Hồ\s*Chí\s*Minh": "TP HCM",
#     r"Thành\s+phố\s+Hồ\s+Chí\s+Minh": "TP HCM",
#     r"Hoà\s*Bình": "Hòa Bình",
#     r"Đăk\s*Nông": "Đắk Nông",
#     r"Lý\s*Sơn": "Lý Sơn",
#     r"VQG\s*Cát\s*Tiên": "Vườn quốc gia Cát Tiên",
# }

# def normalize_text(s: str) -> str:
#     s = re.sub(r"\s+", " ", s.strip())
#     for pat, rep in ALIASES.items():
#         s = re.sub(pat, rep, s, flags=re.IGNORECASE)
#     s = re.sub(r"\s*-\s*", " - ", s)
#     return s

# def make_name_pattern(names):
#     def to_piece(name: str) -> str:
#         piece = re.escape(name)
#         piece = piece.replace(r"\ -\ ", r"\s*-\s*").replace(r"\ ", r"\s+")
#         return piece
#     names = sorted(names, key=len, reverse=True)
#     pattern = r"(?<!\w)(" + "|".join(to_piece(n) for n in names) + r")(?!\w)"
#     return re.compile(pattern, flags=re.IGNORECASE)

# NAME_RE = make_name_pattern(CANONICAL)

# # mapping tên "đã chuẩn hoá khoảng trắng" -> tên chuẩn
# def squash(x: str) -> str:
#     return re.sub(r"\s+", " ", x.strip()).lower()

# CANON_MAP = {squash(c): c for c in CANONICAL}

# # ---- đọc & group
# with open(INPUT_FILE, "r", encoding="utf-8") as f:
#     raw_lines = [ln.strip() for ln in f if ln.strip()]

# groups = defaultdict(list)
# others = []

# for ln in raw_lines:
#     text = normalize_text(ln)
#     m = NAME_RE.search(text)
#     if m:
#         matched = normalize_text(m.group(1))
#         canon = CANON_MAP.get(squash(matched), matched)  # ánh xạ về tên chuẩn
#         groups[canon].append(ln)
#     else:
#         others.append(ln)

# # ---- ghi kết quả
# with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#     for name in CANONICAL:
#         if groups.get(name):
#             # f.write(f"\n===== {name} =====\n")
#             for line in groups[name]:
#                 f.write(line + "\n")
#     if others:
#         f.write("\n===== KHÁC =====\n")
#         for line in others:
#             f.write(line + "\n")

# print(f"✅ Đã sắp xếp và lưu vào: {OUTPUT_FILE}")

from transformers import AutoTokenizer


