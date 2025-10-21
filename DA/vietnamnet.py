def crawl_to_csv(output_csv="vietnamnet_du_lich.csv", max_pages=10, max_articles=None):
    """Crawl nhiều trang du lịch của Vietnamnet"""
    all_articles = []

    for page in range(1, max_pages + 1):
        url = f"https://vietnamnet.vn/du-lich?p={page}"
        print(f"🕸️ Crawling page {page}: {url}")
        try:
            articles = get_article_list(url)
        except Exception as e:
            print("Error fetching list:", e)
            continue

        if not articles:
            print("No articles found, stopping.")
            break

        for title, link in articles:
            if max_articles and len(all_articles) >= max_articles:
                break
            try:
                art = get_article_content(link)
                if art and art["content"].strip():
                    all_articles.append(art)
                    print(f"✅ {art['title'][:60]}...")
                time.sleep(1)  # tránh bị chặn
            except Exception as e:
                print("Error fetching", link, e)
                continue

        # nếu đã đủ số lượng, dừng
        if max_articles and len(all_articles) >= max_articles:
            break

    # Lưu file CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "title", "time", "content"])
        writer.writeheader()
        writer.writerows(all_articles)

    print(f"🎉 Saved {len(all_articles)} articles to {output_csv}")
