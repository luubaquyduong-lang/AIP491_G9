import requests
from bs4 import BeautifulSoup
import os

def crawl_data(url):
    """Crawl dữ liệu du lịch VnExpress: gộp <p>, nối <p> với <h3> hoặc <b>/<strong>, giữ đúng thứ tự, không lặp lại h3 riêng."""
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
        title = title_tag.get_text(strip=True) if title_tag else "Không có tiêu đề"
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
            # chỉ lấy section hợp lệ
            if not any(cls in ['inset-column', 'outset-column'] for cls in div.get('class', [])):
                continue

            for el in div.find_all(['h3', 'b', 'strong', 'p'], recursive=True):
                # Dừng nếu gặp phần cuối bài (căn phải)
                if 'style' in el.attrs and 'text-align:right' in el['style'].replace(" ", ""):
                    stop_crawl = True
                    break

                text = el.get_text(" ", strip=True)
                if not text:
                    continue

                # ===== Khi gặp h3 =====
                if el.name == 'h3':
                    # Lưu nhóm trước
                    if current_h3 and (paragraph_buffer or current_text_block):
                        if paragraph_buffer:
                            joined_p = " ".join(paragraph_buffer).strip()
                            current_text_block.append(joined_p)
                            paragraph_buffer = []
                        # ⚠️ KHÔNG thêm dòng h3 riêng nữa
                        collected_text.append("\n".join(current_text_block).strip())
                        current_text_block = []

                    current_h3 = text
                    paragraph_buffer = []
                    last_tag = 'h3'

                # ===== Khi gặp b hoặc strong =====
                elif el.name in ['b', 'strong']:
                    if paragraph_buffer:
                        # gộp p trước b (thuộc h3)
                        current_text_block.append(" ".join(paragraph_buffer).strip())
                        paragraph_buffer = []

                    # Thêm b/strong (kèm h3 nếu có)
                    if current_h3:
                        current_text_block.append(f"{current_h3}: {text}")
                    else:
                        current_text_block.append(f"{text}")
                    last_tag = 'b'

                # ===== Khi gặp p =====
                elif el.name == 'p':
                    text = el.get_text(" ", strip=True)
                    if not text:
                        continue

                    if last_tag == 'b':
                        # p ngay sau b/strong → nối liền dòng b
                        current_text_block[-1] += " " + text
                    elif last_tag == 'p':
                        # p liên tiếp → nối liền không xuống dòng
                        current_text_block[-1] += " " + text
                    elif last_tag == 'h3':
                        # p đầu tiên sau h3 → nối với h3
                        current_text_block.append(f"{current_h3}: {text}")
                    else:
                        # p đầu tiên trong nhóm → thêm mới
                        current_text_block.append(text)
                    last_tag = 'p'

            if stop_crawl:
                break

        # ===== Lưu nhóm cuối =====
        if current_h3:
            if paragraph_buffer:
                current_text_block.append(" ".join(paragraph_buffer).strip())
            collected_text.append("\n".join(current_text_block).strip())

        # Xóa dòng trống thừa
        final_text = "\n".join(
            line.strip() for line in ("\n".join(collected_text)).splitlines() if line.strip()
        )

        return f"{title}{final_text}"

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


# --- Chạy toàn bộ ---
if __name__ == "__main__":
    # input_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\vnexpress\data_text\vnexpress_link.txt"
    # output_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\vnexpress\data_text\test.txt"

    # with open(input_file, "r", encoding="utf-8") as f:
    #     urls = [line.strip() for line in f if line.strip()]

    # for i, url in enumerate(urls, start=1):
    #     print(f"▶️ [{i}/{len(urls)}] Đang crawl: {url}")
    #     data = crawl_data(url)
    #     save_to_file(data, output_file)
    url = r'https://vnexpress.net/cam-nang-du-lich-binh-phuoc-4667906.html'
    output_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\vnexpress\data_text\yen_bai.txt"
    data = crawl_data(url) 
    save_to_file(data, output_file)