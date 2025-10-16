# import requests
# from bs4 import BeautifulSoup

# def crawl_data(url):
#     try:
#         # Gửi yêu cầu GET đến trang web
#         response = requests.get(url)
#         response.raise_for_status()  # Kiểm tra xem yêu cầu có thành công không

#         # Phân tích HTML
#         soup = BeautifulSoup(response.text, 'html.parser')

#         # Tìm tất cả các thẻ <p> trong class "section-inner inset-column"
#         paragraphs = soup.select('.section-inner.inset-column p')

#         # Mở file để ghi dữ liệu
#         with open(r'D:\ARTIFICIAL_INTELLIGENCE\KY_8\DSP391m\Project_DSP391m_Group_6\Project_DSP391m\Data\preprocessing_data\output.txt', 'a', encoding='utf-8') as file:
#             for paragraph in paragraphs:
#                 file.write(paragraph.get_text() + '\n') 
#         print("Dữ liệu đã được lưu vào file output.txt.")
    
#     except Exception as e:
#         print(f"Đã xảy ra lỗi: {e}")

# # Ví dụ sử dụng
# url = 'https://vnexpress.net/cam-nang-du-lich-an-giang-4445399.html' 
# crawl_data(url)


import requests
from bs4 import BeautifulSoup
import time

def crawl_data(url, output_file):
    try:
        print(f"Đang crawl: {url}")
        
        # Gửi yêu cầu GET đến trang web
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Phân tích HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Tìm tất cả các thẻ <p> trong class "section-inner inset-column"
        paragraphs = soup.select('.section-inner.inset-column p')

        # Mở file để ghi dữ liệu
        with open(output_file, 'a', encoding='utf-8') as file:
            # Ghi URL nguồn
            file.write(f"\n{'='*80}\n")
            file.write(f"URL: {url}\n")
            file.write(f"{'='*80}\n")
            
            for paragraph in paragraphs:
                file.write(paragraph.get_text() + '\n')
        
        print(f"✓ Thành công: {url}")
        return True
    
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        return False

# Đọc file chứa danh sách URLs
input_file = r'D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data_link.txt'
output_file = r'D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data_text\text.txt'

# Xóa nội dung file output cũ
open(output_file, 'w', encoding='utf-8').close()

# Đọc danh sách URLs
with open(input_file, 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip()]

print(f"Tìm thấy {len(urls)} URLs\n")

# Crawl từng URL
success = 0
fail = 0

for i, url in enumerate(urls, 1):
    print(f"[{i}/{len(urls)}] ", end="")
    
    if crawl_data(url, output_file):
        success += 1
    else:
        fail += 1
    
    # Nghỉ giữa các request
    if i < len(urls):
        time.sleep(1.5)

# Thống kê
print(f"\n{'='*80}")
print(f"Hoàn thành! Thành công: {success}/{len(urls)} | Thất bại: {fail}/{len(urls)}")
print(f"Dữ liệu đã được lưu vào: {output_file}")
print(f"{'='*80}")