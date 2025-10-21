import requests
from bs4 import BeautifulSoup
import csv
import time

# URL chuyên mục Du lịch
BASE_URL = "https://vnexpress.net/du-lich-p{}"

# File CSV lưu dữ liệu
OUTPUT_FILE = "vnexpress_du_lich.csv"

def crawl_page(page_num):
    """Crawl 1 trang danh sách bài viết"""
    url = BASE_URL.format(page_num)
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")

    # Tìm link bài viết
    articles = []
    for a in soup.select("h3.title-news a"):
        link = a.get("href")
        if link and link.startswith("https://vnexpress.net"):
            articles.append(link)
    return list(set(articles))  # loại bỏ trùng lặp


def crawl_article(url):
    """Crawl nội dung 1 bài viết"""
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")

    title = soup.select_one("h1.title-detail")
    if title:
        title = title.get_text(strip=True)

    content = soup.select("p.Normal")
    content = " ".join([p.get_text(strip=True) for p in content])

    return {
        "url": url,
        "title": title,
        "content": content
    }


def main():
    # Mở file CSV để lưu
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "title", "content"])
        writer.writeheader()

        # Crawl 5 trang đầu (bạn có thể tăng lên)
        for page in range(1, 6):
            print(f"🔎 Đang crawl trang {page}...")
            article_links = crawl_page(page)
            for link in article_links:
                try:
                    data = crawl_article(link)
                    writer.writerow(data)
                    print("✅ Lưu:", data["title"])
                    time.sleep(1)  # nghỉ 1s để tránh bị chặn
                except Exception as e:
                    print("❌ Lỗi với link:", link, e)


if __name__ == "__main__":
    main()
