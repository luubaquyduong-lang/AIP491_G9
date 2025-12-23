import requests
from bs4 import BeautifulSoup
import os
import re
import traceback


# ==========================
# HÀM CHUẨN HÓA TEXT
# ==========================
def clean_text(text):
    """
    Chuẩn hóa chuỗi văn bản:
    - Xóa ký tự thừa (\xa0, xuống dòng, tab)
    - Gộp khoảng trắng
    - Loại bỏ trường hợp tiêu đề lặp lại hai lần (VD: 'Giới thiệu Hà Giang: Giới thiệu Hà Giang')
    """
    text = re.sub(r'[\xa0\n\r\t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()
    text = re.sub(r'^([A-ZĐÂÊÔƠƯ][^:]{1,25}:\s*)\1', r'\1', text)
    return text


def merge_spans(el):
    """
    Hợp nhất các <span> con trong thẻ p/b/strong để tránh lỗi văn bản bị chia nhỏ.
    Trả về phần tử đã được gộp text.
    """
    for span_group in el.find_all('span'):
        if span_group.string:
            span_group.replace_with(span_group.get_text(" ", strip=True))
    return el


# ========================================================
# HÀM CRAWL + LƯU TRỰC TIẾP
# ========================================================
def crawl_and_save(url, output_path):
    """Crawl dữ liệu bài viết du lịch VnExpress và ghi vào file đầu ra."""
    try:
        # ---- Gửi request tới trang ----
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91 Safari/537.36'}
        print(f"🔄 Đang crawl: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # ---- 1. Lấy tiêu đề bài viết ----
        selectors = [
            "h1.title-detail",
            "h1.title-page",
            "span.text-cover > h1",
            "section.page-detail h1"
        ]
        title_tag = None
        for selector in selectors:
            title_tag = soup.select_one(selector)
            if title_tag:
                break
        
        # Nếu không có, fallback lấy h1 đầu tiên
        if not title_tag:
            title_tag = soup.select_one("h1")

        # Làm sạch tiêu đề
        title = clean_text(title_tag.get_text()) if title_tag else None

        # ---- 2. Nếu không có tiêu đề, sinh ra từ URL ----
        if not title:
            print("⚠️ Không tìm thấy H1, tự tạo tiêu đề từ URL...")
            try:
                path_part = url.split('/')[-1]
                slug = path_part.split('.')[0]
                slug_no_id = re.sub(r'-\d+$', '', slug)

                parts = slug_no_id.split('-')
                start_index = 0
                if all(x in parts for x in ["cam", "nang", "du", "lich"]):
                    start_index = 4  # sau "cam-nang-du-lich-"
                
                name_parts = parts[start_index:]
                if name_parts:
                    location_name = ' '.join(word.capitalize() for word in name_parts)
                    title = f"Giới thiệu {location_name}"
                else:
                    title = "Giới thiệu chung"
            except Exception as e:
                print(f" Lỗi khi parse URL: {e}")
                title = "Giới thiệu chung"

        print(f" Tiêu đề: {title}\n")

        # ---- 3. Lấy nội dung bài viết ----
        content_divs = soup.find_all('div', class_='section-inner')
        collected_text = []

        current_h3 = None
        current_block = []
        last_tag = None

        for div in content_divs:
            # Chỉ xử lý phần chứa nội dung chính
            div_classes = div.get('class', [])
            if not div_classes or not any(cls in ['inset-column', 'outset-column'] for cls in div_classes):
                continue

            # Duyệt các thẻ h3, p, b, strong trong mỗi khối
            for el in div.find_all(['h3', 'p', 'b', 'strong'], recursive=False):
                # Bỏ phần căn phải (thường là chữ ký, nguồn)
                if 'style' in el.attrs and 'text-align:right' in el['style'].replace(" ", ""):
                    continue

                el = merge_spans(el)

                # ===== Xử lý các thẻ H3 (tiêu đề phụ) =====
                if el.name == 'h3':
                    if current_block:
                        collected_text.append("\n".join(current_block).strip())
                    current_block = []
                    current_h3 = clean_text(el.get_text())
                    last_tag = 'h3'

                # ===== Xử lý các thẻ B hoặc STRONG (đề mục con) =====
                elif el.name in ['b', 'strong']:
                    text = clean_text(el.get_text())
                    if not text:
                        continue
                    if current_h3:
                        current_block.append(f"{current_h3}: {text}")
                    else:
                        current_block.append(text)
                    last_tag = 'b'

                # ===== Xử lý đoạn văn <p> =====
                elif el.name == 'p':
                    current_sub_heading = ""
                    current_sub_text = []
                    is_first_segment = True

                    # Duyệt nội dung bên trong thẻ p
                    for node in el.contents:
                        if isinstance(node, str):
                            cleaned_node_text = clean_text(node)
                            if cleaned_node_text:
                                current_sub_text.append(cleaned_node_text)
                        elif node.name in ['b', 'strong']:
                            # Gặp tiêu đề nhỏ trong đoạn p
                            if current_sub_heading or current_sub_text:
                                full_segment = " ".join([current_sub_heading] + current_sub_text).strip()

                                # Nếu nối tiếp đoạn trước thì nối vào cuối
                                if is_first_segment and last_tag == 'b' and current_block:
                                    current_block[-1] += ". " + full_segment
                                else:
                                    # Nếu có h3 thì prefix thêm "ở ..."
                                    if current_h3 and not full_segment.startswith(current_h3):
                                        current_block.append(f"{current_h3}: {full_segment}")
                                    else:
                                        current_block.append(full_segment)
                                is_first_segment = False

                            current_sub_heading = clean_text(node.get_text())
                            current_sub_text = []

                    # Sau khi duyệt hết p, lưu lại đoạn cuối cùng
                    if current_sub_heading or current_sub_text:
                        full_segment = " ".join([current_sub_heading] + current_sub_text).strip()
                        is_wrapper_p = (not current_sub_text and is_first_segment)

                        if is_wrapper_p:
                            # Dạng p chứa trực tiếp nội dung
                            if current_h3:
                                current_block.append(f"{current_h3} ở {title}: {full_segment}")
                            else:
                                current_block.append(full_segment)
                            last_tag = 'b'

                        elif is_first_segment and last_tag == 'b' and current_block:
                            current_block[-1] += ". " + full_segment
                            last_tag = 'p'
                        elif is_first_segment and last_tag == 'p' and current_block:
                            current_block[-1] += " " + full_segment
                            last_tag = 'p'
                        elif is_first_segment and last_tag == 'h3' and current_block:
                            current_block.append(f"{current_h3} ở {title}: {full_segment}")
                            last_tag = 'p'
                        else:
                            if current_h3 and not full_segment.startswith(current_h3):
                                current_block.append(f"{current_h3} ở {title}: {full_segment}")
                            else:
                                current_block.append(full_segment)
                            last_tag = 'p'
                    elif not current_block:
                        last_tag = 'p_empty'

        # Kết thúc một khối cuối cùng
        if current_block:
            collected_text.append("\n".join(current_block).strip())

        # Loại bỏ trùng lặp và dòng rỗng
        final_text = "\n".join(dict.fromkeys(line.strip() for line in collected_text if line.strip()))
        final_text = re.sub(r'\n{2,}', '\n', final_text)

        # Kiểm tra nếu không có nội dung
        if not final_text.strip():
            print(f"⚠️ Không thu thập được nội dung từ URL: {url}")
            return False

        # ---- 4. Tạo output cuối ----
        output_text = f"Giới thiệu {title}. {final_text}"

        # ---- 5. Lưu vào file ----
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(output_text + "\n")

        print(f"✅ Đã lưu vào: {output_path}")
        print(f"📝 Số ký tự: {len(output_text)}\n")
        return True

    except requests.RequestException as e:
        print(f"❌ Lỗi kết nối khi crawl {url}: {e}")
        return False
    except Exception as e:
        print(f"❌ Lỗi khi crawl {url}: {e}")
        traceback.print_exc()
        return False


# ==========================
# CHƯƠNG TRÌNH CHÍNH
# ==========================
# if __name__ == "__main__":
#     input_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\raw\vnexpress\vnexpress_link.txt"
#     output_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\raw\vnexpress\test.txt"

#     # Xóa file cũ nếu có
#     if os.path.exists(output_file):
#         os.remove(output_file)
#         print(f" Đã xóa file cũ: {output_file}")

#     try:
#         # Đọc danh sách link
#         with open(input_file, "r", encoding="utf-8") as f:
#             urls = [line.strip() for line in f if line.strip() and line.startswith('http')]

#         if not urls:
#             print(f" Không tìm thấy link nào trong file: {input_file}")

#         # Chạy crawl từng link
#         for i, url in enumerate(urls, start=1):
#             print(f"\n▶ [{i}/{len(urls)}] Crawl: {url}")
#             crawl_and_save(url, output_file)

#         print("\n Hoàn thành tất cả!")

#     except FileNotFoundError:
#         print(f" Lỗi: Không tìm thấy file input: {input_file}")
#     except Exception as e:
#         print(f" Lỗi không xác định: {e}")
url = 'https://vnexpress.net/cam-nang-du-lich-binh-thuan-4749039.html'
output_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\raw\vnexpress\test.txt"
crawl_and_save(url, output_file)