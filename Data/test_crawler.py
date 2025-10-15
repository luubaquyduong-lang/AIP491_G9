import requests
from bs4 import BeautifulSoup, Tag
import time

def crawl_data(url, output_path):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Lấy tiêu đề bài viết
        title_tag = soup.select_one("h1.title-detail, h1")
        title = title_tag.get_text(strip=True) if title_tag else "Không rõ tiêu đề"
        print(f"📘 Tiêu đề: {title}")

        with open(output_path, 'a', encoding='utf-8') as file:
            file.write(f"\n# {title}\n\n")

            # Chọn các khối nội dung chính
            content_blocks = soup.select(
                ".section-inner.inset-column h2, "
                ".section-inner.inset-column h3, "
                ".section-inner.inset-column p, "
                ".section-inner.inset-column div[style*='text-align:left']"
            )

            current_header = None
            buffer = []

            def flush_buffer():
                nonlocal buffer
                if buffer:
                    file.write(" ".join(buffer).strip() + "\n\n")
                    buffer = []

            for block in content_blocks:
                if not isinstance(block, Tag):
                    continue
                text = block.get_text(strip=True)
                if not text:
                    continue

                # Nếu gặp tiêu đề phụ → ghi lại phần trước rồi xuống dòng
                if block.name in ["h2", "h3"]:
                    flush_buffer()
                    current_header = text
                    file.write(f"## {current_header}\n")
                else:
                    buffer.append(text)

            flush_buffer()

        print(f"✅ Đã lưu dữ liệu từ {url} vào {output_path}\n")

    except Exception as e:
        print(f"❌ Lỗi với {url}: {e}")


if __name__ == "__main__":
    input_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data_text\data_link.txt"
    output_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data_image\data_image.txt"

    with open(input_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        crawl_data(url, output_file)
        time.sleep(1)
