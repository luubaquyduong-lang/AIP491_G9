import requests
from bs4 import BeautifulSoup
import csv
import time
import os

base_url = "https://www.ivivu.com/blog/category/an-choi/an-choi-am-thuc/"
headers = {"User-Agent": "Mozilla/5.0"}
data = []

START_PAGE = 1   # 👈 Bắt đầu từ trang 21
MAX_PAGE = 999         # 👈 Crawl đến trang 999
csv_file = "ivivu_amthuc.csv"

# 🟢 Kiểm tra xem file đã tồn tại chưa
file_exists = os.path.exists(csv_file)

for page in range(START_PAGE, MAX_PAGE + 1):
    url = f"{base_url}/page/{page}/"
    print(f"\n🕸️ Đang crawl: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"⚠️ Lỗi {response.status_code} khi tải trang {url}")
            break
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi kết nối ở trang {page}: {e}")
        break

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article", class_="post")

    if not articles:
        print(f"🚫 Không còn bài viết ở trang {page}, dừng lại.")
        break

    print(f"🔍 Tìm thấy {len(articles)} bài viết ở trang {page}")

    for article in articles:
        link_tag = article.find("a", href=True)
        img_tag = article.find("img")
        title_tag = article.find("h2")
        date_tag = article.find("span", class_="date")
        views_tag = article.find("span", class_="views")
        excerpt_tag = article.find("div", class_="entry-excerpt")

        link = link_tag["href"] if link_tag else ""
        title = title_tag.get_text(strip=True) if title_tag else ""
        image_url = img_tag["src"] if img_tag else ""
        date = date_tag.get_text(strip=True) if date_tag else ""
        views = views_tag.get_text(strip=True).replace("/", "").strip() if views_tag else ""
        excerpt = excerpt_tag.get_text(strip=True) if excerpt_tag else ""

        # Crawl nội dung chi tiết
        try:
            post_resp = requests.get(link, headers=headers, timeout=10)
            post_soup = BeautifulSoup(post_resp.text, "html.parser")

            content_div = post_soup.find("div", class_="entry-content")
            if content_div:
                content = " ".join(p.get_text(strip=True) for p in content_div.find_all("p"))
            else:
                content = "Không tìm thấy nội dung"
        except Exception as e:
            content = f"Lỗi khi tải bài: {e}"

        data.append({
            "title": title,
            "link": link,
            "image_url": image_url,
            "date": date,
            "views": views,
            "excerpt": excerpt,
            "content": content
        })

        print(f"📄 {title}")
        time.sleep(1)

    time.sleep(2)

# ✍️ Ghi dữ liệu vào file CSV — append thay vì ghi đè
with open(csv_file, "a", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "link", "image_url", "date", "views", "excerpt", "content"])

    # chỉ ghi header nếu file chưa có
    if not file_exists:
        writer.writeheader()

    writer.writerows(data)

print(f"\n🎉 Đã thêm {len(data)} bài mới (từ trang {START_PAGE} → {MAX_PAGE}) vào file {csv_file}")
