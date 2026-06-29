import requests
from bs4 import BeautifulSoup
import re
import time

# --- Hàm làm sạch text ---
def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)  # bỏ khoảng trắng thừa
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)  # bỏ cách trước dấu câu
    text = re.sub(r'https?://\S+', '', text)  # bỏ link
    return text.strip()

# --- Hàm crawl 1 link ---
def crawl_data(url, output_file, error_file):
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            # --- Gửi request ---
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # --- Lấy phần tiêu đề & địa chỉ ---
            info_div = soup.select_one('div.col-md-12.h-100.cslt-detail')
            h4 = diachi = province = None

            if info_div:
                h4_tag = info_div.select_one('h4')
                h4 = h4_tag.get_text(strip=True) if h4_tag else None

                span_tag = info_div.select_one('span.d-block')
                if span_tag:
                    diachi_text = span_tag.get_text(separator=' ', strip=True)
                    diachi = diachi_text.replace("Địa chỉ:", "").strip()
                    if ',' in diachi:
                        province = diachi.split(',')[-1].strip()

            # --- Lấy phần nội dung chi tiết ---
            content_divs = soup.select('div.col-12.py-2.content-detail')
            full_text = ""

            for div in content_divs:
                p_tags = div.select('p')
                if p_tags:
                    paragraph_text = ' '.join(p.get_text(separator=' ', strip=True) for p in p_tags)
                else:
                    paragraph_text = div.get_text(separator=' ', strip=True)
                full_text += paragraph_text + " "

            # --- Làm sạch nội dung ---
            full_text = clean_text(full_text)
            dac_diem = full_text.split("Đặc điểm:")[-1].strip() if "Đặc điểm:" in full_text else full_text
            dac_diem = clean_text(dac_diem)

            # --- Ghi dữ liệu ---
            with open(output_file, 'a', encoding='utf-8') as file:
                if province:
                    file.write(f"Chơi ở đâu {province}? ")
                if h4:
                    file.write(f"Địa điểm: {h4}. ")
                if diachi:
                    file.write(f"Địa chỉ: {diachi}. ")
                if dac_diem:
                    file.write(f"Đặc điểm: {dac_diem}.")
                file.write("\n")

            print(f" [{attempt}] Đã lưu: {h4 or 'Không tiêu đề'} ({province or 'Không rõ tỉnh'})\n")
            time.sleep(1)  # Nghỉ nhẹ giữa các link
            break  # Dừng retry nếu thành công

        except Exception as e:
            print(f" Lần {attempt} lỗi với {url}: {e}")
            if attempt < max_retries:
                wait_time = 5 * attempt
                print(f" Đợi {wait_time}s rồi thử lại...")
                time.sleep(wait_time)
            else:
                print(f" Bỏ qua link sau {max_retries} lần lỗi: {url}\n")
                with open(error_file, "a", encoding="utf-8") as log:
                    log.write(f"{url}\t{e}\n")

# ---  ---
if __name__ == "__main__":
    input_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\raw\vietnamtourism\vietnamtourism_link.txt"
    output_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\raw\vietnamtourism\vietnamtourism_data.txt"
    error_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\raw\vietnamtourism\error_links.txt"

    with open(input_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f" Tổng số link cần crawl: {len(urls)}")
    for i, url in enumerate(urls, start=1):
        print(f"▶ [{i}/{len(urls)}] Đang crawl: {url}")
        crawl_data(url, output_file, error_file)

