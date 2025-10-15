import requests 
from bs4 import BeautifulSoup
import time
import json
import re

#  Hàm lấy dữ liệu 
def crawl_data(url):
    try:
        # Gửi yêu cầu GET đến trang web
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Phân tích HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup.prettify())  # In ra cấu trúc HTML để kiểm tra
        
        # Lấy tiêu đề bài viết - thử nhiều cách
        article_title = 'Không có tiêu đề'
        # Cách 1: Tìm trong span.title-cover (cho trang có cover image)
        title_cover = soup.find('span', class_='title-cover')
        if title_cover:
            article_title = title_cover.get_text(strip=True)
        else:
            # Cách 2: Tìm trong h1.title-detail (cho trang thông thường)
            title_detail = soup.find('h1', class_='title-detail')
            if title_detail:
                article_title = title_detail.get_text(strip=True)
            else:
                # Cách 3: Tìm h1 bất kỳ
                h1_tag = soup.find('h1')
                if h1_tag:
                    article_title = h1_tag.get_text(strip=True)
        # Lấy thêm location từ text-cover nếu có
        location = ''
        text_cover = soup.find('span', class_='text-cover')
        if text_cover:
            location_h1 = text_cover.find('h1')
            if location_h1:
                location = location_h1.get_text(strip=True)
                # Kết hợp tiêu đề và địa điểm
                if location and article_title != 'Không có tiêu đề':
                    article_title = f"{article_title} {location}"
                elif location:
                    article_title = location
        # print(f"Tiêu đề bài viết: {article_title}")
        
        ############################## Content Page ##############################
        # Lấy tất cả các section
        all_sections = soup.find_all('div', class_='section-inner')
        print(all_sections)
        data = {
            'url': url,
            'title': article_title,
            'content': []
        }
        print(f"\n{'='*80}")
        print(f"Đang crawl: {article_title}")
        print(f"URL: {url}")
        print(f"{'='*80}\n")
         # Biến để theo dõi và gộp text
        current_text_group = []
        processed_sections = set()
        
        for section in all_sections:
            # Tránh xử lý section trùng lặp
            section_id = id(section)
            if section_id in processed_sections:
                continue
            processed_sections.add(section_id)
            
            # CHỈ DỪNG NẾU section này CHỨA article-end VÀ KHÔNG CÓ NỘI DUNG GÌ KHÁC
            if section.find('span', {'id': 'article-end'}):
                # Kiểm tra xem section có text không (ngoài article-end)
                section_text = section.get_text(strip=True)
                # Nếu section chỉ có article-end thì dừng, còn không thì vẫn xử lý
                if len(section_text) < 50:  # Quá ngắn, chỉ là marker
                    print("[INFO] Đã đến article-end marker, dừng crawl")
                    break
            
            section_classes = section.get('class', [])
            
            # Kiểm tra xem section có chứa ảnh không
            images = section.find_all('img')
            
            if images:
                # Nếu đang có text group, lưu nó trước
                if current_text_group:
                    combined_text = '\n\n'.join(current_text_group)
                    data['content'].append({
                        'type': 'text',
                        'content': combined_text
                    })
                    # print(f"[TEXT GROUP] {len(current_text_group)} paragraphs combined")
                    current_text_group = []
                
                # Xử lý ảnh
                for img in images:
                    img_url = img.get('src')
                    if img_url:
                        alt_text = img.get('alt', '')
                        
                        # Lấy caption nếu có
                        caption = ''
                        figcaption = section.find('figcaption')
                        if figcaption:
                            caption = figcaption.get_text(strip=True)
                        
                        image_data = {
                            'type': 'image',
                            'url': img_url,
                            'alt': alt_text,
                            'caption': caption
                        }
                        data['content'].append(image_data)
                        
                        print(f"[IMAGE] {img_url[:80]}...")
                        if caption:
                            print(f"        Caption: {caption[:80]}...")
            
            # Kiểm tra nếu là section chứa text
            if 'inset-column' in section_classes:
                # Lấy text từ các thẻ - LẤY TẤT CẢ, KHÔNG GIỚI HẠN
                text_elements = section.find_all(['p', 'h2', 'h3'])
                
                for elem in text_elements:
                    # Bỏ qua nếu element chứa ảnh
                    if elem.find('img'):
                        continue
                    
                    text = elem.get_text(strip=True)
                    if not text:
                        continue
                    
                    # Kiểm tra class và style để bỏ qua timestamp
                    elem_class = ' '.join(elem.get('class', []))
                    elem_style = elem.get('style', '')
                    
                    # BỎ QUA timestamp (có class timestamp hoặc màu #757575)
                    if 'timestamp' in elem_class.lower():
                        print(f"[SKIP TIMESTAMP] {text[:50]}...")
                        continue
                    
                    if '#757575' in elem_style or 'color:#757575' in elem_style or 'color: #757575' in elem_style:
                        print(f"[SKIP TIMESTAMP] {text}...")
                        continue
                    
                    # BỎ QUA text-align:right (author)
                    if 'text-align:right' in elem_style or 'text-align: right' in elem_style:
                        print(f"[SKIP AUTHOR] {text[:50]}...")
                        continue
                    
                    # BỎ QUA pattern "Cập nhật DD/MM/YYYY, HH:MM"
                    if re.match(r'Cập nhật\s+\d{1,2}/\d{1,2}/\d{4}', text):
                        print(f"[SKIP DATE] {text}")
                        continue
                    
                    # Nếu là tiêu đề (h2, h3)
                    if elem.name in ['h2', 'h3']:
                        # Lưu text group trước đó (nếu có)
                        if current_text_group:
                            combined_text = '\n\n'.join(current_text_group)
                            data['content'].append({
                                'type': 'text',
                                'content': combined_text
                            })
                            print(f"[TEXT GROUP] {len(current_text_group)} paragraphs combined")
                            current_text_group = []
                        
                        # Thêm tiêu đề như một item riêng
                        data['content'].append({
                            'type': 'heading',
                            'content': text,
                            'level': elem.name
                        })
                        print(f"[HEADING {elem.name.upper()}] {text}")
                    else:
                        # Thêm vào text group
                        current_text_group.append(text)
                        print(f"[TEXT ADDED] {text[:80]}...")
        
        # Lưu text group cuối cùng (nếu có)
        if current_text_group:
            combined_text = '\n\n'.join(current_text_group)
            data['content'].append({
                'type': 'text',
                'content': combined_text
            })
            print(f"[TEXT GROUP FINAL] {len(current_text_group)} paragraphs combined")
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"Lỗi kết nối đến {url}: {e}")
        return None
    except Exception as e:
        print(f"Đã xảy ra lỗi khi crawl {url}: {e}")
        import traceback
        traceback.print_exc()
        return None
    
url = "https://vnexpress.net/cam-nang-du-lich-yen-bai-4701574.html"
crawl_data(url)
# if __name__ == "__main__":
#     input_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data_link.txt"
#     output_json = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data_image\data_crawled.json"
#     output_text = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data_image\data_image.txt"
#     for line in open(input_file, "r", encoding="utf-8"):
#         url = line.strip()
#         if url:
#             print(f"Crawling URL: {url}")
#             data = crawl_data(url)
