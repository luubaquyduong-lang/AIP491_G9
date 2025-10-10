import requests
from bs4 import BeautifulSoup, Tag

def crawl_data(url, output_path):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Lấy tiêu đề chính
        title_tag = soup.select_one("h1.title-detail, h1")
        title = title_tag.get_text(strip=True) if title_tag else "Không rõ tiêu đề"
        print(f"Tiêu đề: {title}")

        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(f"# {title}\n\n")

            # ✅ Lấy tất cả khối nội dung chính (bao gồm cả hình ảnh, tiêu đề, đoạn văn)
            content_blocks = soup.select(
                "div.section-inner h2, "
                "div.section-inner h3, "
                "div.section-inner p, "
                "div.section-inner div[style*='text-align'], "
                "div.medium-insert-images-large figure"
            )

            buffer_text = []

            def flush_buffer():
                """Ghi các đoạn văn đã gom thành 1 đoạn"""
                nonlocal buffer_text
                if buffer_text:
                    file.write(" ".join(buffer_text) + "\n\n")
                    buffer_text = []

            for block in content_blocks:
                if not isinstance(block, Tag):
                    continue

                # Nếu là tiêu đề phụ
                if block.name in ["h2", "h3"]:
                    flush_buffer()
                    subheader = block.get_text(strip=True)
                    file.write(f"## {subheader}\n")

                # Nếu là đoạn văn
                elif block.name in ["p", "div"]:
                    text = block.get_text(strip=True)
                    if text:
                        buffer_text.append(text)

                # Nếu là ảnh
                elif block.name == "figure":
                    flush_buffer()
                    img = block.find("img")
                    caption = block.find("figcaption")

                    if img:
                        src = (
                            img.get("data-src")
                            or img.get("data-original")
                            or img.get("srcset")
                            or img.get("src")
                        )
                        if src:
                            # Nếu srcset có nhiều link → lấy link đầu tiên
                            if " " in src:
                                src = src.split()[0]
                            caption_text = caption.get_text(strip=True) if caption else ""
                            file.write(f"![{caption_text}]({src})\n\n")

            flush_buffer()  # Ghi nốt phần còn lại

        print(f"✅ Đã lưu dữ liệu từ {url} vào {output_path}")

    except Exception as e:
        print(f"❌ Lỗi với {url}: {e}")


if __name__ == "__main__":
    url = "https://vnexpress.net/cam-nang-du-lich-phu-yen-4465949.html"
    output_path = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\nhatrang.txt"
    crawl_data(url, output_path)
