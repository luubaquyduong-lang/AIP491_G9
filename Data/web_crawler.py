import requests
from bs4 import BeautifulSoup, Tag
import time 

def crawl_data(url, output_path):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Lấy tiêu đề chính
        title_tag = soup.select_one("h1.title-detail, h1")
        title = title_tag.get_text(strip=True) if title_tag else "Không rõ tiêu đề"
        print(f"Tiêu đề: {title}")

        with open(output_path, 'a', encoding='utf-8') as file:
            file.write(f"\nGiới thiệu về {title}. ")
            # Lấy nội dung gồm cả tiêu đề phụ và đoạn văn theo thứ tự
            content_blocks = soup.select(
                ".section-inner.inset-column h2, "
                ".section-inner.inset-column h3, "
                ".section-inner.inset-column p, "
                ".section-inner.inset-column div[style*='text-align:left']"
            )

            current_subheader = None
            buffer_text = []  # chứa các đoạn văn để gộp

            def flush_buffer():
                """Ghi các đoạn văn đã gom"""
                nonlocal buffer_text
                if buffer_text:
                    file.write(" ".join(buffer_text))
                    buffer_text = []

            for block in content_blocks:
                if not isinstance(block, Tag):
                    continue
                text = block.get_text(strip=True)
                if not text:
                    continue

                if block.name in ["h2", "h3"]:   # Nếu gặp tiêu đề phụ mới
                    flush_buffer()               # ghi đoạn cũ ra file
                    current_subheader = text
                    file.write(f"\n{current_subheader}. ")
                else:
                    buffer_text.append(text)     # gom các đoạn văn

            flush_buffer()  # ghi phần còn lại cuối cùng

        print(f"✅ Đã lưu dữ liệu từ {url} vào {output_path}")

    except Exception as e:
        print(f"❌ Lỗi với {url}: {e}")



if __name__ == "__main__":
    input_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data_link.txt"
    output_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data.txt"

    # Đọc danh sách link từ file
    with open(input_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]  # bỏ dòng trống

    # Vòng lặp crawl từng link
    for url in urls:
        crawl_data(url, output_file)
