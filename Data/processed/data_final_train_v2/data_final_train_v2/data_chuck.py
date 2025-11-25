import os

# ===== CẤU HÌNH =====
input_path  = "D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\data_final_train\data_final_sort_v2.jsonl"  # đường dẫn file gốc
output_dir  = "D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\data_final_train"                                     # thư mục lưu các file con
lines_per_file = 100
max_files = 151   # tách thành 150 file

os.makedirs(output_dir, exist_ok=True)

file_idx = 1
line_in_current = 0
out_f = None

with open(input_path, "r", encoding="utf-8") as f:
    for line in f:
        # mở file đầu tiên
        if out_f is None:
            out_name = os.path.join(
                output_dir,
                f"data_final_sort_v2_part_{file_idx:02d}.jsonl"
            )
            out_f = open(out_name, "w", encoding="utf-8")
            print(f"🔹 Đang ghi vào {out_name}")

        out_f.write(line)
        line_in_current += 1

        # nếu đủ 1000 dòng và chưa tới file thứ 15 thì chuyển sang file mới
        if line_in_current >= lines_per_file and file_idx < max_files:
            out_f.close()
            file_idx += 1
            line_in_current = 0
            out_f = None

# đóng file cuối
if out_f is not None:
    out_f.close()

print("✅ Hoàn tất tách file!")
