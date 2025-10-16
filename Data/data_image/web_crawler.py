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
        
        # Biến để theo dõi
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
            
            # XỬ LÝ THEO THỨ TỰ XUẤT HIỆN TRONG HTML
            # Tìm tất cả các element có thể chứa nội dung
            all_content_elements = []
            
            # Lấy tất cả elements trong section theo thứ tự xuất hiện
            # Bao gồm cả các div chứa ảnh trong gallery structure
            section_elements = section.find_all(['figure', 'img', 'p', 'h2', 'h3', 'h4', 'strong', 'div'])
            
            # Thêm index để xác định thứ tự
            for index, elem in enumerate(section_elements):
                elem_tag = elem.name
                
                # Xử lý figure (cho tất cả sections)
                if elem_tag == 'figure':
                    # Tìm tất cả ảnh trong figure (bao gồm cả gallery structure)
                    images_in_figure = elem.find_all('img')
                    
                    for img in images_in_figure:
                        # Ưu tiên data-desktop-src, sau đó data-src, cuối cùng là src
                        img_url = (img.get('data-desktop-src') or 
                                  img.get('data-src') or 
                                  img.get('src'))
                        
                        if img_url and img_url not in processed_images:
                            processed_images.add(img_url)
                            
                            alt_text = img.get('alt', '')
                            
                            # Tìm caption từ nhiều nguồn khác nhau
                            caption = ''
                            
                            # Cách 1: Tìm figcaption truyền thống
                            figcaption = elem.find('figcaption')
                            if figcaption:
                                caption = figcaption.get_text(strip=True)
                            
                            # Cách 2: Tìm div.desc_cation hoặc div.desc_caption (cho gallery structure)
                            if not caption:
                                desc_cation = elem.find('div', class_='desc_cation')
                                if not desc_cation:
                                    desc_cation = elem.find('div', class_='desc_caption')
                                if desc_cation:
                                    caption = desc_cation.get_text(strip=True)
                            
                            # Cách 3: Tìm caption trong div.item_gallery gần nhất
                            if not caption:
                                item_gallery = img.find_parent('div', class_='item_gallery')
                                if item_gallery:
                                    gallery_caption = item_gallery.find('div', class_='desc_cation')
                                    if not gallery_caption:
                                        gallery_caption = item_gallery.find('div', class_='desc_caption')
                                    if gallery_caption:
                                        caption = gallery_caption.get_text(strip=True)
                            
                            # Cách 4: Tìm trong các div có class chứa 'desc' hoặc 'caption'
                            if not caption:
                                all_desc_divs = elem.find_all('div', class_=lambda x: x and ('desc' in x.lower() or 'caption' in x.lower()))
                                for desc_div in all_desc_divs:
                                    text = desc_div.get_text(strip=True)
                                    if text and len(text) > 5:  # Caption thường có độ dài > 5 ký tự
                                        caption = text
                                        break
                            
                            # Cách 5: Tìm title attribute của ảnh
                            if not caption:
                                title = img.get('title', '')
                                if title:
                                    caption = title
                            
                            # Thêm figure vào danh sách
                            all_content_elements.append({
                                'element': elem,
                                'type': 'figure',
                                'img_url': img_url,
                                'alt': alt_text,
                                'caption': caption,
                                'position': index
                            })
                
                # Xử lý ảnh không nằm trong figure (cho tất cả sections)
                elif elem_tag == 'img':
                    # Kiểm tra xem ảnh này đã được xử lý trong figure chưa
                    already_processed = False
                    for existing in all_content_elements:
                        if existing['type'] == 'figure' and elem in existing['element'].descendants:
                            already_processed = True
                            break
                    
                    if not already_processed:
                        # Ưu tiên data-desktop-src, sau đó data-src, cuối cùng là src
                        img_url = (elem.get('data-desktop-src') or 
                                  elem.get('data-src') or 
                                  elem.get('src'))
                        
                        if img_url and img_url not in processed_images:
                            processed_images.add(img_url)
                            
                            alt_text = elem.get('alt', '')
                            
                            # Tìm caption gần nhất với img này
                            caption = ''
                            
                            # Tìm trong parent figure trước
                            parent_figure = elem.find_parent('figure')
                            if parent_figure:
                                # Cách 1: figcaption truyền thống
                                figcaption = parent_figure.find('figcaption')
                                if figcaption:
                                    caption = figcaption.get_text(strip=True)
                                
                                # Cách 2: div.desc_cation hoặc div.desc_caption
                                if not caption:
                                    desc_cation = parent_figure.find('div', class_='desc_cation')
                                    if not desc_cation:
                                        desc_cation = parent_figure.find('div', class_='desc_caption')
                                    if desc_cation:
                                        caption = desc_cation.get_text(strip=True)
                                
                                # Cách 3: Tìm trong các div có class chứa 'desc' hoặc 'caption'
                                if not caption:
                                    all_desc_divs = parent_figure.find_all('div', class_=lambda x: x and ('desc' in x.lower() or 'caption' in x.lower()))
                                    for desc_div in all_desc_divs:
                                        text = desc_div.get_text(strip=True)
                                        if text and len(text) > 5:
                                            caption = text
                                            break
                            else:
                                # Nếu không có figure parent, tìm trong section
                                figcaption = section.find('figcaption')
                                if figcaption:
                                    caption = figcaption.get_text(strip=True)
                                
                                # Tìm div.desc_cation hoặc div.desc_caption trong section
                                if not caption:
                                    desc_cation = section.find('div', class_='desc_cation')
                                    if not desc_cation:
                                        desc_cation = section.find('div', class_='desc_caption')
                                    if desc_cation:
                                        caption = desc_cation.get_text(strip=True)
                                
                                # Tìm trong các div có class chứa 'desc' hoặc 'caption'
                                if not caption:
                                    all_desc_divs = section.find_all('div', class_=lambda x: x and ('desc' in x.lower() or 'caption' in x.lower()))
                                    for desc_div in all_desc_divs:
                                        text = desc_div.get_text(strip=True)
                                        if text and len(text) > 5:
                                            caption = text
                                            break
                            
                            # Cách cuối: Tìm title attribute của ảnh
                            if not caption:
                                title = elem.get('title', '')
                                if title:
                                    caption = title
                            
                            # Thêm ảnh vào danh sách
                            all_content_elements.append({
                                'element': elem,
                                'type': 'image',
                                'img_url': img_url,
                                'alt': alt_text,
                                'caption': caption,
                                'position': index
                            })
                
                # Xử lý div có thể chứa ảnh (gallery structure)
                elif elem_tag == 'div':
                    # Chỉ xử lý các div có class liên quan đến ảnh
                    div_classes = elem.get('class', [])
                    is_image_div = any(cls in ['item_gallery', 'medium-insert-images', 'gallery_block'] 
                                     for cls in div_classes)
                    
                    if is_image_div:
                        # Tìm ảnh trong div này
                        div_images = elem.find_all('img')
                        for img in div_images:
                            # Kiểm tra xem ảnh này đã được xử lý chưa
                            already_processed = False
                            for existing in all_content_elements:
                                if existing['type'] in ['figure', 'image'] and img in existing['element'].descendants:
                                    already_processed = True
                                    break
                            
                            if not already_processed:
                                # Ưu tiên data-desktop-src, sau đó data-src, cuối cùng là src
                                img_url = (img.get('data-desktop-src') or 
                                          img.get('data-src') or 
                                          img.get('src'))
                                
                                if img_url and img_url not in processed_images:
                                    processed_images.add(img_url)
                                    
                                    alt_text = img.get('alt', '')
                                    
                                    # Tìm caption
                                    caption = ''
                                    
                                    # Tìm div.desc_cation hoặc div.desc_caption trong div hiện tại
                                    desc_cation = elem.find('div', class_='desc_cation')
                                    if not desc_cation:
                                        desc_cation = elem.find('div', class_='desc_caption')
                                    if desc_cation:
                                        caption = desc_cation.get_text(strip=True)
                                    
                                    # Tìm trong các div có class chứa 'desc' hoặc 'caption'
                                    if not caption:
                                        all_desc_divs = elem.find_all('div', class_=lambda x: x and ('desc' in x.lower() or 'caption' in x.lower()))
                                        for desc_div in all_desc_divs:
                                            text = desc_div.get_text(strip=True)
                                            if text and len(text) > 5:
                                                caption = text
                                                break
                                    
                                    # Tìm trong parent figure nếu có
                                    if not caption:
                                        parent_figure = elem.find_parent('figure')
                                        if parent_figure:
                                            desc_cation = parent_figure.find('div', class_='desc_cation')
                                            if not desc_cation:
                                                desc_cation = parent_figure.find('div', class_='desc_caption')
                                            if desc_cation:
                                                caption = desc_cation.get_text(strip=True)
                                    
                                    # Cách cuối: Tìm title attribute của ảnh
                                    if not caption:
                                        title = img.get('title', '')
                                        if title:
                                            caption = title
                                    
                                    # Thêm ảnh vào danh sách
                                    all_content_elements.append({
                                        'element': elem,
                                        'type': 'image',
                                        'img_url': img_url,
                                        'alt': alt_text,
                                        'caption': caption,
                                        'position': index
                                    })
                
                # Xử lý text elements (chỉ trong inset-column)
                elif elem_tag in ['p', 'h2', 'h3', 'h4', 'strong'] and 'inset-column' in section_classes:
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
                    if 'text-align:left' in elem_style and elem_tag == 'p' and elem.get('style'):
                        # Nếu có style text-align:left explicit, có thể là metadata
                        if len(text) < 100:  # Và text ngắn
                            print(f"[SKIP METADATA] {text[:50]}...")
                            continue
                    
                    # BỎ QUA pattern "Cập nhật DD/MM/YYYY, HH:MM"
                    if re.match(r'Cập nhật\s+\d{1,2}/\d{1,2}/\d{4}', text):
                        print(f"[SKIP DATE] {text}")
                        continue
                    
                    # Thêm text element vào danh sách
                    all_content_elements.append({
                        'element': elem,
                        'type': 'text',
                        'text': text,
                        'tag': elem_tag,
                        'position': index
                    })
            
            # SẮP XẾP THEO THỨ TỰ XUẤT HIỆN (position)
            all_content_elements.sort(key=lambda x: x['position'])
            
            # XỬ LÝ THEO THỨ TỰ ĐÃ SẮP XẾP
            current_text_group = []
            
            for item in all_content_elements:
                if item['type'] == 'figure' or item['type'] == 'image':
                    # Nếu đang có text group, lưu nó trước
                    if current_text_group:
                        combined_text = '\n\n'.join(current_text_group)
                        data['content'].append({
                            'type': 'text',
                            'content': combined_text
                        })
                        print(f"[TEXT GROUP] {len(current_text_group)} paragraphs combined")
                        current_text_group = []
                    
                    # Thêm ảnh
                    image_data = {
                        'type': 'image',
                        'url': item['img_url'],
                        'alt': item['alt'],
                        'caption': item['caption']
                    }
                    data['content'].append(image_data)
                    
                    print(f"[IMAGE] {item['img_url'][:80]}...")
                    if item['caption']:
                        print(f"        Caption: {item['caption'][:80]}...")
                
                elif item['type'] == 'text':
                    # Nếu là tiêu đề (h2, h3, h4)
                    if item['tag'] in ['h2', 'h3', 'h4']:
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
                            'content': item['text'],
                            'level': item['tag']
                        })
                        print(f"[HEADING {item['tag'].upper()}] {item['text']}")
                    else:
                        # Thêm vào text group
                        current_text_group.append(item['text'])
                        print(f"[TEXT ADDED] {item['text'][:80]}...")
            
            # Lưu text group cuối cùng của section này (nếu có)
            if current_text_group:
                combined_text = '\n\n'.join(current_text_group)
                data['content'].append({
                    'type': 'text',
                    'content': combined_text
                })
                print(f"[TEXT GROUP SECTION END] {len(current_text_group)} paragraphs combined")
        
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
    url = "https://vnexpress.net/cam-nang-du-lich-binh-thuan-4749039.html"
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