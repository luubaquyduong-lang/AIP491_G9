from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
import os
from urllib.parse import urljoin

BASE_URL = "https://csdl.vietnamtourism.gov.vn"
LIST_URL = f"{BASE_URL}/dest"

def get_driver():
	chrome_options = Options()
	chrome_options.add_argument("--headless=new")
	chrome_options.add_argument("--no-sandbox")
	chrome_options.add_argument("--disable-dev-shm-usage")
	return webdriver.Chrome(service = Service(), options = chrome_options)

def extract_detail_links(html: str) -> set:
	soup = BeautifulSoup(html, 'html.parser')
	# Hỗ trợ 2 dạng link: /dest-<slug>-<id>.html và /dest/?item=<id>
	pattern_slug = re.compile(r'^(?:https?://csdl\.vietnamtourism\.gov\.vn)?/dest-[a-z0-9\-]+-\d+\.html$', re.IGNORECASE)
	pattern_item = re.compile(r'^(?:https?://csdl\.vietnamtourism\.gov\.vn)?/dest/\?item=\d+$', re.IGNORECASE)
	links = set()
	for a in soup.find_all('a', href=True):
		href = a['href'].strip()
		if not href:
			continue
		absolute = urljoin(BASE_URL, href)
		as_path = absolute.replace(BASE_URL, '')
		if pattern_slug.match(as_path) or pattern_item.match(as_path):
			links.add(absolute)
	return links

def discover_pagination_links(html: str) -> list:
	"""Tìm tất cả các trang pagination từ HTML"""
	soup = BeautifulSoup(html, 'html.parser')
	page_urls = set([LIST_URL])
	
	# Tìm tất cả link pagination
	pagination_links = soup.find_all('a', href=True)
	
	for a in pagination_links:
		href = a['href']
		if not href:
			continue
			
		# Chuyển đổi thành URL tuyệt đối
		abs_url = urljoin(BASE_URL, href)
		
		# Kiểm tra nếu là link pagination
		if (abs_url.startswith(LIST_URL) and 
			("?page=" in abs_url or "&page=" in abs_url)):
			page_urls.add(abs_url)
	
	# Sắp xếp theo số trang
	def page_key(u: str) -> int:
		m = re.search(r'[?&]page=(\d+)', u)
		return int(m.group(1)) if m else 1
	
	return sorted(page_urls, key=page_key)

def get_max_page_from_pagination(html: str) -> int:
	"""Tìm số trang tối đa từ pagination"""
	soup = BeautifulSoup(html, 'html.parser')
	max_page = 1
	
	# Tìm nút "Cuối cùng" hoặc số trang cao nhất
	pagination_links = soup.find_all('a', href=True)
	
	for a in pagination_links:
		href = a['href']
		text = a.get_text(strip=True)
		
		# Nếu có nút "Cuối cùng", tìm URL của nó
		if text == "Cuối cùng" and href:
			abs_url = urljoin(BASE_URL, href)
			match = re.search(r'[?&]page=(\d+)', abs_url)
			if match:
				max_page = max(max_page, int(match.group(1)))
		
		# Tìm số trang cao nhất từ các link khác
		if href and ("?page=" in href or "&page=" in href):
			match = re.search(r'[?&]page=(\d+)', href)
			if match:
				max_page = max(max_page, int(match.group(1)))
	
	return max_page

def crawl_all_links() -> set:
	"""Crawl tất cả links từ tất cả các trang"""
	driver = get_driver()
	print(f'driver{driver}')
	try:
		# Truy cập trang đầu tiên
		print(f"Truy cập trang đầu tiên: {LIST_URL}")
		driver.get(LIST_URL)
		time.sleep(3)

		first_html = driver.page_source
		# Tìm tất cả các trang pagination
		all_pages = discover_pagination_links(first_html)
		print(f'all_pages{all_pages}')
		# Nếu không tìm thấy pagination, chỉ crawl trang đầu
		if not all_pages:
			all_pages = [LIST_URL]
		# Tìm số trang tối đa để xác nhận
		max_page = get_max_page_from_pagination(first_html)
		print(f"Tìm thấy {len(all_pages)} trang, trang cuối cùng: {max_page}")
		for i in range(1, max_page + 1):
			all_pages.append(f"{LIST_URL}?page={i}")
			
		collected = set()
		# Crawl từng trang
		for i, page_url in enumerate(all_pages, 1):
			print(f"Crawling trang {i}/{len(all_pages)}: {page_url}")
			
			try:
				driver.get(page_url)
				time.sleep(2)
				html = driver.page_source
				page_links = extract_detail_links(html)
				collected |= page_links
				
				print(f"  - Thu thập được {len(page_links)} links từ trang này")
				
			except Exception as e:
				print(f"  - Lỗi khi crawl trang {page_url}: {e}")
				continue
		
		print(f"Tổng cộng thu thập được {len(collected)} links")
		return collected
		
	finally:
		driver.quit()

if __name__ == "__main__":
	crawl_links = []
	links = crawl_all_links()
	for link in sorted(links):
		print(link)

	out_path = os.path.join(os.path.dirname(__file__), 'vietnamtourism_link.txt')
	with open(out_path, 'w', encoding='utf-8') as f:
		for link in sorted(links):
			f.write(link + '\n')