from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
import time

options = Options()
options.add_argument("--headless")  # chạy ẩn
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

all_data = []

for page in range(1, 6):
    url = f"https://vietnamtourism.gov.vn/cat/80/page/{page}"
    print(f"🕸️ Đang tải danh mục: {url}")
    driver.get(url)
    time.sleep(3)  # chờ JS load bài viết

    soup = BeautifulSoup(driver.page_source, "html.parser")
    containers = soup.select("div.section-default-list-news-post-info-container")

    if not containers:
        print(f"❌ Không tìm thấy bài viết ở trang {page}")
        continue

    for c in containers:
        a_tag = c.select_one("a.section-default-list-news-post-info-title-link")
        if not a_tag:
            continue

        title = a_tag.get("title", "").strip()
        link = a_tag.get("href", "").strip()
        date_tag = c.select_one("span.post-publish-date")
        date = date_tag.get_text(strip=True) if date_tag else ""

        all_data.append([title, link, date])

    time.sleep(1)

driver.quit()

print(f"🎉 Crawl hoàn tất! Tổng cộng {len(all_data)} bài viết")

with open("vietnamtourism.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["title", "link", "date"])
    writer.writerows(all_data)

print("📁 Dữ liệu lưu tại: vietnamtourism.csv")
