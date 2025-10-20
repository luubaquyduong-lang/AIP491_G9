import requests
from bs4 import BeautifulSoup, Tag
import time
from itertools import islice

def make_subtitle(text, location):
    """Thêm chữ 'đến' hoặc 'ở' tùy theo tiêu đề phụ"""
    text_lower = text.lower()
    if any(k in text_lower for k in ["di chuyển", "đi lại"]):
        return f"{text} đến {location}"
    elif any(k in text_lower for k in ["ăn", "uống", "lưu trú", "khách sạn", "homestay"]):
        return f"{text} ở {location}"
    elif any(k in text_lower for k in ["chơi", "giải trí", "tham quan", "mua sắm"]):
        return f"{text} ở {location}"
    else:
        return text if location.lower() in text_lower else f"{text} {location}"


def crawl_sections(url, output_file):
    """Crawl nội dung từ 1 URL, lưu trực tiếp vào file TXT"""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 🔹 Lấy tiêu đề chính
        title_tag = soup.select_one("h1.title-detail, h1")
        title = title_tag.get_text(strip=True) if title_tag else "Không rõ tiêu đề"

        # Chuẩn hóa địa danh (bỏ chữ “Du lịch”, “Cẩm nang”)
        for prefix in ["Du lịch", "Cẩm nang", "Khám phá", "Kinh nghiệm"]:
            title = title.replace(prefix, "").strip()

        # 🔹 Lấy phần nội dung chính (thử nhiều layout khác nhau)
        content = (
            soup.select_one(".section-inner.inset-column") or
            soup.select_one(".article-body") or
            soup.select_one(".main-content") or
            soup.select_one(".fck_detail") or
            soup
        )

        sections = []
        current_subtitle = "Giới thiệu về " + title
        current_text = []

        # Duyệt toàn bộ các thẻ h2, h3, p
        for el in content.find_all(["h2", "h3", "p"], recursive=True):
            if not isinstance(el, Tag):
                continue

            text = el.get_text(" ", strip=True)
            if not text:
                continue

            if el.name in ["h2", "h3"]:
                # Nếu có phần cũ → lưu lại
                if current_text:
                    sections.append({
                        "tieu_de_phu": current_subtitle,
                        "noi_dung": " ".join(current_text).strip()
                    })
                    current_text = []

                current_subtitle = make_subtitle(text, title)

            elif el.name == "p":
                current_text.append(text)

        # Lưu phần cuối cùng
        if current_text:
            sections.append({
                "tieu_de_phu": current_subtitle,
                "noi_dung": " ".join(current_text).strip()
            })

        # 🔹 Ghi ra file TXT
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"\n# {title}\n\n")
            if sections:
                for sec in sections:
                    f.write(f"{sec['tieu_de_phu']}\n{sec['noi_dung']}\n\n")
            else:
                f.write("(Không có nội dung chính)\n\n")

        print(f"📘 {title}: {len(sections)} mục đã thu thập.")
        return len(sections)

    except Exception as e:
        print(f"❌ Lỗi khi crawl {url}: {e}")
        return 0


if __name__ == "__main__":
    input_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\vnexpress\data_text\vnexpress_link.txt"
    output_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\vnexpress\data_text\test.txt"

    # ✅ Lấy 10 link đầu
    with open(input_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in islice(f, 10) if line.strip()]

    print(f"🔗 Đang crawl {len(urls)} link đầu tiên...\n")

    for url in urls:
        crawl_sections(url, output_file)
        time.sleep(1)

    print(f"\n✅ Đã lưu toàn bộ kết quả vào: {output_file}")
