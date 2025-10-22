# Danh sách các file cần gộp
input_files = [
    r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\vnexpress\vnexpress_data_v2.txt",
    r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\vietnamtourism\vietnamtourism_data.txt",
    r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\ivivu\ivivu_crawler_data.txt"
]

output_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data_final.txt"

with open(output_file, "w", encoding="utf-8") as outfile:
    for file_name in input_files:
        with open(file_name, "r", encoding="utf-8") as infile:
            content = infile.read().strip()
            outfile.write(content + "\n")  # thêm dòng trống giữa các file

print(f"✅ Đã gộp {len(input_files)} file vào '{output_file}' thành công!")

