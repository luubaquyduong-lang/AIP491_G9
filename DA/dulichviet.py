import requests
from bs4 import BeautifulSoup
import csv
import time

base_url = "https://www.ivivu.com/blog"
headers = {"User-Agent": "Mozilla/5.0"}
data = []

MAX_PAGE = 50  # Giới hạn trang tối đa
page = 1

while page <= MAX_PAGE:
    url = f"{base_url}/page/{page}" if page > 1 else base_url
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
    articles = soup.select("article.item-list")

    if not articles:
        print(f"🚫 Không còn bài viết ở trang {page}, dừng lại.")
        break

    print(f"🔍 Tìm thấy {len(articles)} bài viết ở trang {page}")

    for article in articles:
        link_tag = article.find("a")
        img_tag = article.find("img")

        if not link_tag:
            continue

        link = link_tag.get("href")
        if not link.startswith("http"):
            link = "https://www.ivivu.com" + link

        title = img_tag.get("alt") if img_tag and img_tag.get("alt") else link_tag.get_text(strip=True)
        image_url = img_tag.get("src") if img_tag else ""

        # 🟢 Crawl nội dung chi tiết
        try:
            post_resp = requests.get(link, headers=headers, timeout=10)
            post_soup = BeautifulSoup(post_resp.text, "html.parser")

            content_div = post_soup.find("div", class_="post-content")
            if content_div:
                content = "\n".join(p.get_text(strip=True) for p in content_div.find_all("p"))
            else:
                content = "Không tìm thấy nội dung"

        except Exception as e:
            content = f"Lỗi khi tải bài: {e}"

        data.append({
            "title": title,
            "link": link,
            "image_url": image_url,
            "content": content
        })

        print(f"📄 {title}")
        time.sleep(1)

    page += 1
    time.sleep(2)

csv_file = "ivivu_blog.csv"
with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "link", "image_url", "content"])
    writer.writeheader()
    writer.writerows(data)

print(f"\n🎉 Crawl hoàn tất! Tổng cộng {len(data)} bài viết.")
print(f"📁 Dữ liệu lưu tại: {csv_file}")

