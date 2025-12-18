import requests
from bs4 import BeautifulSoup
import time
import re
import os

# --- CẤU HÌNH ---

# URL trang chủ để tìm danh sách các tỉnh/thành
HOME_PAGE_URL = "https://dulichvietnam.com.vn/"
# Tên file output chung cho tất cả các tỉnh
OUTPUT_FILE = "bai_viet_all_provinces.txt" 
SLEEP_TIME = 2  # Thời gian chờ giữa các request (giúp tránh bị chặn)

# Các từ khóa để phân loại là "Ẩm Thực"
AM_THUC_KEYWORDS = [
    "đặc sản", "món ngon", "ẩm thực", "ăn gì", "hải sản", "quán ăn"
]

# --- CẤU HÌNH SELECTOR CSS ---
SELECTORS = {
    # Trang danh sách (listing page): Selector cho thẻ <a> chứa link bài viết
    "article_links": "div.i-title h3 a", 

    # Trang chi tiết (detail page): Selector cho Tiêu đề
    "title": "div.the-title h1", 

    # Trang chi tiết: Selector cho Nội dung chính (phần text)
    "content": "div.the-content div.desc", 

    # Trang chi tiết: Selector cho khối Tags 
    "tags_list": "div.box-tags a"
}

# --- HÀM HỖ TRỢ CHUNG ---

def get_html(url):
    """Lấy nội dung HTML từ URL."""
    # Dùng header giả lập trình duyệt để giảm khả năng bị chặn
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15) # Tăng timeout
        if response.status_code == 200:
            response.encoding = 'utf-8' 
            return response.text
        elif response.status_code == 404: 
            return None
        else:
            print(f"[LỖI] Không thể truy cập {url}. Mã trạng thái: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[LỖI KẾT NỐI] Không thể kết nối tới {url}: {e}")
        return None

def get_article_links(page_url):
    """Lấy danh sách link bài viết từ một trang danh sách."""
    html_content = get_html(page_url)
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    links = []
    article_elements = soup.select(SELECTORS['article_links'])

    for element in article_elements:
        href = element.get('href')
        # Xử lý URL tương đối
        if href and href.endswith('.html') and not href.startswith('#'):
            if 'http' not in href:
                # Xử lý link tương đối (vd: /son-la.html)
                full_url = "https://dulichvietnam.com.vn" + href
            else:
                # Xử lý link tuyệt đối (nếu có)
                full_url = href
                
            links.append(full_url)

    return list(set(links)) 

# --- HÀM MỚI ĐỂ LẤY LINK TỈNH/THÀNH (CẬP NHẬT) ---

def get_province_links():
    """Lấy danh sách link và tên tỉnh từ trang chủ."""
    print(f"Đang lấy danh sách các tỉnh/thành từ {HOME_PAGE_URL}...")
    html_content = get_html(HOME_PAGE_URL)
    
    if not html_content:
        print("[LỖI KẾT NỐI CHỦ] Không truy cập được trang chủ.")
        return []
    
    # Định nghĩa domain cơ sở
    BASE_DOMAIN = "https://dulichvietnam.com.vn"
    
    soup = BeautifulSoup(html_content, 'html.parser')
    province_links = []
    
    # 1. CẬP NHẬT: Dùng selector tổng quát để lấy tất cả link tỉnh từ các khối menu có thể có.
    # Lấy link từ cả div.vhsubmns và div.mnconts
    province_elements = soup.select('div.vhsubmns ul a[href], div.mnconts ul a[href]')
    
    if not province_elements:
        print("[LỖI PHÂN TÍCH] Không tìm thấy link tỉnh nào trong các container menu (vhsubmns, mnconts).")
        # Dùng danh sách tỉnh cứng làm dự phòng để đảm bảo chương trình chạy
        print("[SỬ DỤNG DỰ PHÒNG] Tạm thời dùng danh sách tĩnh.")
        return [
            ("Quảng Ninh", f"{BASE_DOMAIN}/du-lich-quang-ninh.html"),
            ("Hà Giang", f"{BASE_DOMAIN}/ha-giang.html"),
            ("Đà Nẵng", f"{BASE_DOMAIN}/da-nang.html"),
            ("Hà Nội", f"{BASE_DOMAIN}/ha-noi.html"),
            ("Lâm Đồng", f"{BASE_DOMAIN}/lam-dong.html")
        ]
        
    for element in province_elements:
        href = element.get('href')
        name = element.get_text(strip=True)
        
        # Chỉ lấy các link dẫn đến trang tỉnh/thành (link .html)
        if href and href.endswith('.html') and not href.startswith('#'):
            
            # Xử lý link tương đối (vd: /son-la.html)
            if 'http' not in href and href.startswith('/'):
                # Sử dụng BASE_DOMAIN để tạo URL tuyệt đối
                full_url = BASE_DOMAIN + href
            else:
                full_url = href # Giữ nguyên nếu đã là link tuyệt đối
            
            # Loại bỏ các link không phải tỉnh (ví dụ: link "/" của "Việt Nam")
            if name and name.lower() not in ["việt nam", "trong nước"] and full_url != HOME_PAGE_URL:
                province_links.append((name, full_url))
        
        # Xử lý link "Việt Nam" nếu nó có href rỗng (trường hợp này bỏ qua)
        if name == "Việt Nam" and href == "":
             continue

    # Loại bỏ các URL trùng lặp 
    unique_links = {url: name for name, url in province_links}
    
    if not unique_links:
        print("[LỖI PHÂN TÍCH] Không tìm thấy link tỉnh nào hợp lệ. Có thể do lỗi phân tích hoặc trang web đã thay đổi cấu trúc.")
        return []
        
    return [(name, url) for url, name in unique_links.items()]

# --- HÀM CRAWL CHI TIẾT VÀ PHÂN LOẠI (HỮU CƠ HÓA) ---

def crawl_article_detail(article_url, province_name):
    """Crawl tiêu đề, nội dung, tags và phân loại bài viết."""
    html_content = get_html(article_url)
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. Lấy Tiêu đề
    title_element = soup.select_one(SELECTORS['title'])
    title = title_element.get_text(strip=True) if title_element else "Không tìm thấy Tiêu đề"

    # 2. Lấy Tags và Phân loại
    category = "Điểm Đến"
    
    tags_texts = []
    tags_elements = soup.select(SELECTORS['tags_list'])
    
    # Tạo chuỗi kiểm tra bao gồm Tiêu đề và nội dung tag (để phát hiện ẩm thực tốt hơn)
    check_string = title.lower() 

    if tags_elements:
        for tag_a in tags_elements:
            tag_text = tag_a.get_text(strip=True).lower()
            tags_texts.append(tag_text)
            check_string += " " + tag_text

    # Kiểm tra từ khóa Ẩm Thực trong Tiêu đề và Tags
    is_am_thuc = False
    for keyword in AM_THUC_KEYWORDS:
        if keyword in check_string: 
            is_am_thuc = True
            break
        
    if is_am_thuc:
        category = "Ẩm Thực"


    # 3. Lấy Nội dung
    content = ""
    content_element = soup.select_one(SELECTORS['content'])
    if content_element:
        # Lấy nội dung, dùng ' ' làm separator để giữ khoảng cách giữa các thẻ
        content_raw = content_element.get_text(separator=' ', strip=True)
        
        # Loại bỏ các đoạn văn bản dư thừa không mong muốn:
        content_raw = re.sub(r'Mục lục bài viết\s*.*?1\. ', '1. ', content_raw, flags=re.DOTALL | re.IGNORECASE)
        content_raw = re.sub(r'(?:Xem thêm|>>Xem thêm):.*', '', content_raw).strip()
        
        # Làm sạch khoảng trắng và ký tự non-breaking space
        content = re.sub(r'\s+', ' ', content_raw).replace('\xa0', ' ').strip()
        
        # Loại bỏ các chuỗi tên tác giả cuối bài
        content = re.sub(r'\s+[A-Za-z]+\s+[A-Za-z]+$', '', content).strip()
    
    # Thêm cơ chế fallback nội dung nếu nội dung quá ngắn hoặc không tìm thấy
    if len(content) < 50 and soup.select_one("div.the-content"):
        content_fallback = soup.select_one("div.the-content").get_text(separator=' ', strip=True)
        content_fallback = re.sub(r'\s+', ' ', content_fallback).strip()
        if len(content_fallback) > len(content) and len(content_fallback) > 50:
            content = content_fallback 
    
    if len(content) < 50:
        content = "Nội dung bài viết quá ngắn hoặc không tìm thấy nội dung."

    # 4. CẬP NHẬT: Định dạng và trả về theo yêu cầu mới
    cleaned_title = title.replace('\n', ' ').strip()
    cleaned_content = content.replace('\n', ' ').strip()
    
    # Tạo prefix mới dựa trên category
    if category == "Ẩm Thực":
        prefix = f"Ăn gì ở {province_name}"
    elif category == "Điểm Đến":
        prefix = f"Chơi ở đâu {province_name}"
    else:
        # Giữ định dạng cũ nếu có category mới phát sinh
        prefix = f"[{province_name}] - [{category}]"
        
    # Định dạng mới: [Prefix] + [Tiêu đề] + [Nội dung]
    formatted_data = f"{prefix} {cleaned_title} {cleaned_content}"
    
    return formatted_data, category

# --- HÀM CRAWL THEO TỈNH ---

def crawl_province(province_name, province_url, f):
    """Crawl tất cả bài viết của một tỉnh, lưu vào file f theo thứ tự Ẩm Thực -> Điểm Đến."""
    # base_url_province là link gốc của tỉnh (ví dụ: https://dulichvietnam.com.vn/du-lich-quang-ninh.html)
    
    print(f"\n=============================================")
    print(f"BẮT ĐẦU CRAWL TỈNH: {province_name}")
    print(f"Link gốc: {province_url}")
    print(f"=============================================")
    
    page_num = 1
    crawled_links = set()
    province_am_thuc = []
    province_diem_den = []
    
    while True:
        # Xây dựng URL trang danh sách (vd: .../du-lich-quang-ninh.html/?p=1)
        # province_url đã là URL đầy đủ, chỉ cần thêm '?p=page_num'
        current_page_url = f"{province_url}/?p={page_num}"
        print(f"  [{time.strftime('%H:%M:%S')}] Đang crawl trang {page_num}...")
        
        article_links = get_article_links(current_page_url)

        if not article_links:
            if page_num > 1:
                print(f"  [THÔNG BÁO] Hết bài viết trên trang {page_num} của {province_name}. Dừng crawl tỉnh này.")
            else:
                # Thay đổi thông báo để phản ánh URL đang được sử dụng (URL tuyệt đối)
                print(f"  [LƯU Ý] Trang đầu tiên ({province_url}) không tìm thấy bài viết nào.")
            break

        links_to_crawl = [link for link in article_links if link not in crawled_links]

        if not links_to_crawl:
            print(f"  [KẾT THÚC] Không tìm thấy link mới trên trang {page_num}. Dừng crawl tỉnh này.")
            break
            
        print(f"  Tìm thấy {len(links_to_crawl)} bài viết mới. Bắt đầu crawl chi tiết...")
        
        for link in links_to_crawl:
            result = crawl_article_detail(link, province_name)
            
            if result:
                formatted_data, category = result
                
                # Lưu vào danh sách tương ứng để sắp xếp sau
                if category == "Ẩm Thực":
                    province_am_thuc.append(formatted_data)
                else:
                    province_diem_den.append(formatted_data)
                    
                crawled_links.add(link)
            
            time.sleep(SLEEP_TIME / 2)

        page_num += 1
        time.sleep(SLEEP_TIME)

    # SAU KHI CRAWL HẾT TẤT CẢ CÁC TRANG CỦA TỈNH:
    total_province_articles = len(province_am_thuc) + len(province_diem_den)
    print(f"\n[KẾT THÚC TỈNH {province_name}] Tổng số bài viết: {total_province_articles} (Ẩm Thực: {len(province_am_thuc)}, Điểm Đến: {len(province_diem_den)})")
    
    # Ghi dữ liệu vào file theo thứ tự: Ẩm Thực -> Điểm Đến, mỗi bài viết là một dòng mới
    
    # 1. Ghi bài Ẩm Thực
    for article in province_am_thuc:
        f.write(article + '\n') 
    
    # 2. Ghi bài Điểm Đến
    for article in province_diem_den:
        f.write(article + '\n')
    
    if total_province_articles > 0:
        print(f"[ĐÃ LƯU] Đã ghi {total_province_articles} bài viết của {province_name} vào file.")
    else:
        print(f"[LƯU Ý] Tỉnh {province_name} không có bài viết nào được crawl thành công.")

    return total_province_articles
    
# --- CHƯƠNG TRÌNH CHÍNH ---

def main():
    print(f"--- BẮT ĐẦU CRAWL TẤT CẢ CÁC TỈNH ---")
    
    # Dùng hàm mới để lấy link tỉnh
    province_links = get_province_links()
    
    if not province_links:
        print("[LỖI CHÍNH] Không thể tìm thấy bất kỳ link tỉnh nào từ trang chủ. Dừng chương trình.")
        return

    print(f"Tìm thấy {len(province_links)} tỉnh/thành phố để crawl.")
    
    # Xóa file cũ nếu có để tránh trùng lặp dữ liệu
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        print(f"Đã xóa file cũ: {OUTPUT_FILE}")
    
    total_articles_crawled = 0

    # Mở file ở chế độ append (thêm vào cuối)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        for province_name, province_url in province_links:
            # Gọi hàm crawl_province để xử lý từng tỉnh. 
            # Giờ đây province_url đã là URL đầy đủ.
            articles_count = crawl_province(province_name, province_url, f)
            total_articles_crawled += articles_count
            time.sleep(SLEEP_TIME * 2) # Ngủ lâu hơn giữa các tỉnh/thành để giảm tải server

    print("\n--- KẾT THÚC TOÀN BỘ QUÁ TRÌNH CRAWL ---")
    print(f"Tổng số bài viết đã crawl và lưu vào file '{OUTPUT_FILE}': {total_articles_crawled}")

if __name__ == "__main__":
    main()