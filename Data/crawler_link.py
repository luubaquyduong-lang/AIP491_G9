from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re

# Cấu hình Chrome headless()
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Chạy Chrome ở chế độ headless
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# Khởi tạo trình duyệt
driver = webdriver.Chrome(service = Service(), options = chrome_options)

# Truy cập trang 
url = "https://vnexpress.net/du-lich/cam-nang"
driver.get(url)
time.sleep(3)  # đợi trang load JS

# Cuộn qua các phần swiper nếu cần 

# lấy HTML sau khi render JS
html = driver.page_source
driver.quit()

# Parse bằng BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Rengex để lấy link đúng định dạng bài viết cam-nang-du-lich
pattern = re.compile(r'^https://vnexpress\.net/cam-nang-du-lich-[a-z0-9\-]+-\d+\.html$')

# Tìm tất cả các thẻ <a> chứa hrel phù hợp 
links = soup.find_all('a', href=True)
valid_links = {a['href'] for a in links if pattern.match(a['href'])} # lưu vào set để loại bỏ trùng lặp

# In ra các link hợp lệ
for link in valid_links:
    print(link)
    
# Lưu vào file text
with open('D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data_link.txt', 'w', encoding='utf-8') as f:
    for link in valid_links:
        f.write(link + '\n')