from copy import deepcopy
from underthesea import sent_tokenize

# Hàm tách danh sách các số thành các nhóm liên tiếp nhau
def extract_consecutive_subarray(numbers):
    subarrays = []
    current_subarray = []
    for num in numbers:
        # Nếu danh sách hiện tại trống hoặc số hiện tại nối tiếp số trước đó
        if not current_subarray or num == current_subarray[-1] + 1:
            current_subarray.append(num)
        else:
            # Nếu không liên tiếp thì lưu nhóm hiện tại và bắt đầu nhóm mới
            subarrays.append(current_subarray)
            current_subarray = [num]
    subarrays.append(current_subarray)  # Thêm nhóm cuối cùng
    return subarrays

# Hàm gộp các đoạn (passage) có ID liên tiếp trong cùng một tài liệu
def merge_contexts(passages):
    # Sắp xếp danh sách passage theo ID tăng dần
    passages_sorted_by_id = sorted(passages, key=lambda x: x["id"], reverse=False)

    # Lấy danh sách ID và chia thành các nhóm ID liên tiếp
    psg_ids = [x["id"] for x in passages_sorted_by_id]
    consecutive_ids = extract_consecutive_subarray(psg_ids)

    merged_contexts = []
    b = 0
    for ids in consecutive_ids:
        # Lấy ra các passage có ID liên tiếp
        psgs = passages_sorted_by_id[b:b+len(ids)]

        # Lấy nội dung của các passage, loại bỏ tiêu đề trùng lặp
        psg_texts = [x["passage"].strip("Title: ").strip(x["title"]).strip() for x in psgs]

        # Gộp lại thành một đoạn duy nhất với tiêu đề chung
        merged = f"Title: {psgs[0]['title']}\n\n" + " ".join(psg_texts)
        b = b + len(ids)

        # Tạo một dict mới chứa thông tin của đoạn đã gộp
        merged_contexts.append(dict(
            title=psgs[0]['title'], 
            passage=merged,
            score=max([x["combined_score"] for x in psgs]),  # Lấy điểm cao nhất trong nhóm
            merged_from_ids=ids  # Lưu lại ID các đoạn gộp
        ))
    return merged_contexts

# Hàm loại bỏ các đoạn có điểm thấp (lọc bớt ngữ cảnh yếu)
def discard_contexts(passages):
    # Sắp xếp theo điểm từ thấp đến cao
    sorted_passages = sorted(passages, key=lambda x: x["score"], reverse=False)

    # Nếu chỉ có 1 đoạn thì giữ nguyên
    if len(sorted_passages) == 1:
        return sorted_passages
    else:
        shortened = deepcopy(sorted_passages)
        # Duyệt qua từng cặp liên tiếp để xác định ngưỡng loại bỏ
        for i in range(len(sorted_passages) - 1):
            current, next = sorted_passages[i], sorted_passages[i+1]
            # Nếu chênh lệch điểm >= 0.05 thì chỉ giữ lại các đoạn có điểm cao hơn
            if next["score"] - current["score"] >= 0.05:
                shortened = sorted_passages[i+1:]
        return shortened

# Hàm mở rộng ngữ cảnh xung quanh một đoạn (thêm câu trước và sau)
def expand_context(passage, meta_corpus, word_window=60, n_sent=3):
    merged_from_ids = passage["merged_from_ids"]
    title = passage["title"]
    prev_id = merged_from_ids[0] - 1
    next_id = merged_from_ids[-1] + 1

    # Hàm loại bỏ phần tiêu đề trong đoạn
    strip_title = lambda x: x["passage"].strip(f"Title: {x['title']}\n\n")
    
    texts = []

    # Thêm phần trước (nếu cùng tiêu đề)
    if prev_id in range(0, len(meta_corpus)):
        prev_psg = meta_corpus[prev_id]
        if prev_psg["title"] == title: 
            prev_text = strip_title(prev_psg)
            prev_text = " ".join(sent_tokenize(prev_text)[-n_sent:])  # Lấy n câu cuối
            texts.append(prev_text)
            
    # Thêm đoạn chính
    texts.append(strip_title(passage))
    
    # Thêm phần sau (nếu cùng tiêu đề)
    if next_id in range(0, len(meta_corpus)):
        next_psg = meta_corpus[next_id]
        if next_psg["title"] == title: 
            next_text = strip_title(next_psg)
            next_text = " ".join(sent_tokenize(next_text)[:n_sent])  # Lấy n câu đầu
            texts.append(next_text)

    # Gộp tất cả lại thành một đoạn văn mới
    expanded_text = " ".join(texts)
    expanded_text = f"Title: {title}\n{expanded_text}"

    # Trả về một bản sao passage có nội dung mở rộng
    new_passage = deepcopy(passage)
    new_passage["passage"] = expanded_text
    return new_passage

# Hàm mở rộng ngữ cảnh cho danh sách các passage
def expand_contexts(passages, meta_corpus, word_window=60, n_sent=3):
    new_passages = [expand_context(passage, meta_corpus, word_window, n_sent) for passage in passages]
    return new_passages

# Hàm giữ lại đoạn tốt nhất cho mỗi tiêu đề
def collapse(passages):
    new_passages = deepcopy(passages)
    titles = {}

    # Gom các đoạn theo tiêu đề
    for passage in new_passages:
        title = passage["title"]
        if not titles.get(title):
            titles[title] = [passage]
        else:
            titles[title].append(passage)

    best_passages = []
    # Lấy đoạn có điểm cao nhất trong mỗi nhóm tiêu đề
    for k, v in titles.items():
        best_passage = max(v, key=lambda x: x["score"])
        best_passages.append(best_passage)
    return best_passages

# Hàm chính để làm mượt danh sách ngữ cảnh (context smoothing)
def smooth_contexts(passages, meta_corpus):
    merged_contexts = merge_contexts(passages)           # Gộp các đoạn liên tiếp
    shortlisted_contexts = discard_contexts(merged_contexts)  # Loại bỏ đoạn yếu
    expanded_contexts = expand_contexts(shortlisted_contexts, meta_corpus)  # Mở rộng ngữ cảnh
    collapsed_contexts = collapse(expanded_contexts)     # Giữ lại đoạn tốt nhất mỗi tiêu đề
    return collapsed_contexts
