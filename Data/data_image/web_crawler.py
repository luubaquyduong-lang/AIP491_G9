import requests
from bs4 import BeautifulSoup
import time
import json
import re

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
        
        # Tìm điểm kết thúc bài viết
        article_end = soup.find('span', {'id': 'article-end'})
        
        # Lấy tất cả các section
        all_sections = soup.find_all('div', class_='section-inner')
        
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
        processed_images = set()  # Tránh lấy ảnh trùng
        
        for section in all_sections:
            # Tránh xử lý section trùng lặp
            section_id = id(section)
            if section_id in processed_sections:
                continue
            processed_sections.add(section_id)
            
            # CHỈ DỪNG NẾU section này CHỨA article-end VÀ KHÔNG CÓ NỘI DUNG GÌ KHÁC
            if section.find('span', {'id': 'article-end'}):
                section_text = section.get_text(strip=True)
                if len(section_text) < 50:
                    print("[INFO] Đã đến article-end marker, dừng crawl")
                    break
            
            section_classes = section.get('class', [])
            
            # CÁCH 1: Tìm ảnh trực tiếp trong section
            images = section.find_all('img')
            
            # CÁCH 2: Tìm trong div.medium-insert-images (nested deeper)
            if not images:
                image_containers = section.find_all('div', class_=re.compile(r'medium-insert-images'))
                for container in image_containers:
                    images.extend(container.find_all('img'))
            
            # CÁCH 3: Tìm trong figure tag
            if not images:
                figures = section.find_all('figure')
                for figure in figures:
                    images.extend(figure.find_all('img'))
            
            if images:
                # Nếu đang có text group, lưu nó trước
                if current_text_group:
                    combined_text = '\n\n'.join(current_text_group)
                    data['content'].append({
                        'type': 'text',
                        'content': combined_text
                    })
                    print(f"[TEXT GROUP] {len(current_text_group)} paragraphs combined")
                    current_text_group = []
                
                # Xử lý ảnh
                for img in images:
                    img_url = img.get('src') or img.get('data-src')  # Thêm data-src cho lazy load
                    if img_url and img_url not in processed_images:
                        processed_images.add(img_url)
                        
                        alt_text = img.get('alt', '')
                        
                        # Lấy caption - thử nhiều cách
                        caption = ''
                        
                        # Cách 1: Tìm figcaption trong cùng section
                        figcaption = section.find('figcaption')
                        if figcaption:
                            caption = figcaption.get_text(strip=True)
                        else:
                            # Cách 2: Tìm figcaption trong parent figure của img
                            parent_figure = img.find_parent('figure')
                            if parent_figure:
                                figcaption = parent_figure.find('figcaption')
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
                # Lấy text từ các thẻ - LẤY TẤT CẢ
                text_elements = section.find_all(['p', 'h2', 'h3', 'h4', 'strong'])
                
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
                    
                    # BỎ QUA timestamp
                    if 'timestamp' in elem_class.lower():
                        print(f"[SKIP TIMESTAMP] {text[:50]}...")
                        continue
                    
                    if '#757575' in elem_style or 'color:#757575' in elem_style or 'color: #757575' in elem_style:
                        print(f"[SKIP TIMESTAMP] {text[:50]}...")
                        continue
                    
                    # BỎ QUA text-align:right (author)
                    if 'text-align:right' in elem_style or 'text-align: right' in elem_style:
                        print(f"[SKIP AUTHOR] {text[:50]}...")
                        continue
                    
                    # BỎ QUA text-align:left (có thể là metadata)
                    if 'text-align:left' in elem_style and elem.name == 'p' and elem.get('style'):
                        # Nếu có style text-align:left explicit, có thể là metadata
                        if len(text) < 100:  # Và text ngắn
                            print(f"[SKIP METADATA] {text[:50]}...")
                            continue
                    
                    # BỎ QUA pattern "Cập nhật DD/MM/YYYY, HH:MM"
                    if re.match(r'Cập nhật\s+\d{1,2}/\d{1,2}/\d{4}', text):
                        print(f"[SKIP DATE] {text}")
                        continue
                    
                    # Nếu là tiêu đề (h2, h3, h4)
                    if elem.name in ['h2', 'h3', 'h4']:
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

def save_to_json(all_data, output_file):
    """Lưu dữ liệu dưới dạng JSON"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Đã lưu dữ liệu vào {output_file}")
    except Exception as e:
        print(f"Lỗi khi lưu file: {e}")

def save_to_text(all_data, output_file):
    """Lưu dữ liệu dưới dạng text với format đẹp hơn"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for article in all_data:
                if article:
                    f.write(f"TIÊU ĐỀ: {article['title']}\n\n")
                    for item in article['content']:
                        if item['type'] == 'heading':
                            # Tiêu đề phụ
                            f.write(f"\n{'★ ' + item['content'].upper() + ' ★'}\n\n")
                        elif item['type'] == 'text':
                            # Đoạn văn (đã được gộp)
                            f.write(f"{item['content']}\n\n")
                        elif item['type'] == 'image':
                            # Ảnh
                            f.write(f"\n[ẢNH]\n")
                            f.write(f"URL: {item['url']}\n")
                            if item['caption']:
                                f.write(f"Chú thích: {item['caption']}\n")
                            f.write("\n")
                    
                    f.write("\n")
        print(f"✓ Đã lưu dữ liệu text vào {output_file}")
    except Exception as e:
        print(f"Lỗi khi lưu file text: {e}")
        
        
if __name__ == "__main__":
    url = "https://vnexpress.net/cam-nang-du-lich-yen-bai-4701574.html"
    output_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data_image\test.txt"
    
    data = crawl_data(url)
    all_data = []
    successful = 0
    failed = 0
    
    if data:
        all_data.append(data)
        successful += 1
        
        # Thống kê
        text_count = len([item for item in data['content'] if item['type'] == 'text'])
        image_count = len([item for item in data['content'] if item['type'] == 'image'])
        heading_count = len([item for item in data['content'] if item['type'] == 'heading'])
        print(f"\n✓ Thành công: {text_count} text groups, {heading_count} headings, {image_count} images")
        
        save_to_text(all_data, output_file)
    else:
        failed += 1
        print(f"✗ Thất bại")