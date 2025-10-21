import requests
from bs4 import BeautifulSoup
import os
import re

def clean_text(text):
    """Chuẩn hóa text: bỏ ký tự đặc biệt, gộp khoảng trắng."""
    text = re.sub(r'[\xa0\n\r\t]+', ' ', text)  # bỏ ký tự ẩn
    text = re.sub(r'\s{2,}', ' ', text)         # gộp khoảng trắng kép
    return text.strip()

def crawl_data(url):
    """Crawl dữ liệu du lịch VnExpress: gộp <p>, nối <p> với <h3>/<b>/<strong>, giữ thứ tự, bỏ trống, không lặp."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.124 Safari/537.36'
        }

        print(f"🔄 Đang crawl: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # ===== Tiêu đề chính =====
        title_tag = soup.select_one("h1.title-detail, h1")
        title = clean_text(title_tag.get_text()) if title_tag else "Không có tiêu đề"
        print(f" Tiêu đề: {title}\n")

        # ===== Lấy nội dung =====
        content_divs = soup.find_all('div', class_='section-inner')
        collected_text = []
        stop_crawl = False

        current_h3 = None
        current_text_block = []
        paragraph_buffer = []
        last_tag = None

        for div in content_divs:
            if not any(cls in ['inset-column', 'outset-column'] for cls in div.get('class', [])):
                continue

            for el in div.find_all(['h3', 'b', 'strong', 'p'], recursive=True):
                if 'style' in el.attrs and 'text-align:right' in el['style'].replace(" ", ""):
                    stop_crawl = True
                    break

                text = clean_text(el.get_text(" ", strip=True))
                if not text:
                    continue

                # ===== Khi gặp h3 =====
                if el.name == 'h3':
                    if current_h3 and (paragraph_buffer or current_text_block):
                        if paragraph_buffer:
                            current_text_block.append(" ".join(paragraph_buffer).strip())
                            paragraph_buffer = []
                        collected_text.append("\n".join(current_text_block).strip())
                        current_text_block = []

                    current_h3 = text
                    paragraph_buffer = []
                    last_tag = 'h3'

                # ===== Khi gặp b hoặc strong =====
                elif el.name in ['b', 'strong']:
                    if paragraph_buffer:
                        current_text_block.append(" ".join(paragraph_buffer).strip())
                        paragraph_buffer = []

                    if current_h3:
                        current_text_block.append(f"{current_h3}: {text}")
                    else:
                        current_text_block.append(f"{text}")
                    last_tag = 'b'

                # ===== Khi gặp p =====
                elif el.name == 'p':
                    text = clean_text(text)
                    if not text:
                        continue

                    if last_tag == 'b':
                        current_text_block[-1] += " " + text
                    elif last_tag == 'p':
                        current_text_block[-1] += " " + text
                    elif last_tag == 'h3':
                        current_text_block.append(f"{current_h3}: {text}")
                    else:
                        current_text_block.append(text)
                    last_tag = 'p'

            if stop_crawl:
                break

        # ===== Lưu nhóm cuối =====
        if current_h3:
            if paragraph_buffer:
                current_text_block.append(" ".join(paragraph_buffer).strip())
            collected_text.append("\n".join(current_text_block).strip())

        # Xóa dòng trống, chuẩn hóa lại
        final_text = re.sub(r'\n{2,}', '\n', "\n".join(line.strip() for line in collected_text if line.strip()))

        return f"{title}\n\n{final_text}"

    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_to_file(text, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"💾 Đã lưu vào: {output_path}")


# --- Chạy thử ---
if __name__ == "__main__":
    url = "https://vnexpress.net/cam-nang-du-lich-binh-phuoc-4667906.html"
    output_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\vnexpress\data_text\binh_phuoc.txt"

    data = crawl_data(url)
    if data:
        save_to_file(data, output_file)
