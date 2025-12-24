from copy import deepcopy
# Sử dụng sent_tokenize để chia văn bản thành câu (từ thư viện underthesea)
from underthesea import sent_tokenize 
from typing import List, Dict

def extract_consecutive_subarray(numbers: List[int]) -> List[List[int]]:
    """
    Tách danh sách các ID số nguyên thành các nhóm liên tiếp nhau.
    Ví dụ: [1, 2, 3, 5, 6, 9] -> [[1, 2, 3], [5, 6], [9]]
    """
    if not numbers:
        return []
    subarrays = []
    current_subarray = [numbers[0]]

    for i in range(1, len(numbers)):
        # Nếu số hiện tại nối tiếp số trước đó
        if numbers[i] == numbers[i-1] + 1:
            current_subarray.append(numbers[i])
        else:
            # Kết thúc nhóm hiện tại và bắt đầu nhóm mới
            subarrays.append(current_subarray)
            current_subarray = [numbers[i]]

    # Thêm nhóm cuối cùng
    subarrays.append(current_subarray)
    return subarrays

# --- HÀM SMOOTHING CHÍNH ---

def merge_contexts(retrieved_passages: List[Dict]) -> List[Dict]:
    """
    Gộp các đoạn (passage) có ID liên tiếp (tức là nằm cạnh nhau trong tài liệu gốc) 
    và thuộc cùng một Tiêu đề (title) trong danh sách truy xuất.
    """
    # 1. Sắp xếp danh sách passage theo ID tài liệu gốc
    # Đảm bảo các đoạn được truy xuất cùng một tài liệu gốc được nhóm lại
    passages_sorted = sorted(retrieved_passages, key=lambda x: (x["title"], x["doc_id"]), reverse=False)

    if not passages_sorted:
        return []
    
    # 2. Tạo một danh sách các nhóm passage dựa trên tiêu đề
    grouped_by_title = {}
    for psg in passages_sorted:
        title = psg["title"]
        if title not in grouped_by_title:
            grouped_by_title[title] = []
        grouped_by_title[title].append(psg)

    final_merged_contexts = []

    # 3. Duyệt qua từng nhóm tiêu đề để gộp các ID liên tiếp
    for title, passages_by_title in grouped_by_title.items():
        # Lấy danh sách ID gốc của các đoạn trong nhóm tiêu đề hiện tại
        psg_ids = [x["doc_id"] for x in passages_by_title]
        # Tạo ánh xạ ID -> passage để truy cập nhanh
        id_to_passage = {x["doc_id"]: x for x in passages_by_title}
        
        # Chia ID thành các nhóm liên tiếp
        consecutive_id_groups = extract_consecutive_subarray(psg_ids)

        for id_group in consecutive_id_groups:
            # Lấy các passage tương ứng với nhóm ID liên tiếp này
            psgs_to_merge = [id_to_passage[doc_id] for doc_id in id_group]

            # Lấy nội dung của các passage để gộp
            # Dùng passage_content thay vì passage gốc (đã bao gồm tiêu đề)
            psg_texts = [p["passage"] for p in psgs_to_merge]
            
            # Gộp lại thành một đoạn duy nhất
            # merged_passage_text = f"Title: {title}\n" + " ".join(psg_texts)
            merged_passage_text = " ".join(psg_texts)
            # Tạo một dict mới chứa thông tin của đoạn đã gộp
            final_merged_contexts.append(dict(
                title=title, 
                passage=merged_passage_text,
                # Lấy điểm cao nhất trong nhóm đã gộp
                score=max([x["score"] for x in psgs_to_merge]),  # Lấy điểm cao nhất trong nhóm đã gộp
                # Lưu lại ID gốc của các đoạn đã gộp
                merged_from_ids=id_group, 
                # Lưu lại ID gốc của đoạn đầu tiên trong chuỗi gộp
                doc_id=id_group[0] 
            ))

    # Sắp xếp lại theo điểm để đảm bảo thứ tự
    return sorted(final_merged_contexts, key=lambda x: x["score"], reverse=True)

def discard_contexts(passages: List[Dict], threshold: float = 0.1) -> List[Dict]:
    """
    Loại bỏ các đoạn có điểm thấp dựa trên sự chênh lệch điểm 
    so với đoạn kế tiếp (đã sắp xếp).
    Giúp lọc bớt ngữ cảnh yếu, không liên quan đến truy vấn.
    """
    # 1. Sắp xếp theo điểm từ thấp đến cao (cần cho logic lọc chênh lệch)
    sorted_passages = sorted(passages, key=lambda x: x["score"], reverse=False)

    if len(sorted_passages) <= 1:
        return sorted_passages
    
    # 2. Tìm điểm ngắt
    # Lọc các đoạn có điểm thấp hơn so với đoạn kế tiếp một khoảng đáng kể (>= threshold)
    start_index = 0
    for i in range(len(sorted_passages) - 1):
        current = sorted_passages[i]
        next_psg = sorted_passages[i+1]
        
        # Nếu chênh lệch điểm lớn hơn ngưỡng, cắt bỏ các đoạn phía dưới
        if next_psg["score"] - current["score"] >= threshold:
            start_index = i + 1
            break
            
    # 3. Trả về danh sách đã lọc (từ điểm ngắt trở lên)
    return sorted_passages[start_index:]

def expand_context(passage: Dict, meta_corpus: List[Dict], n_sent: int = 3) -> Dict:
    """
    Mở rộng ngữ cảnh của một đoạn (đã gộp) bằng cách thêm n_sent câu 
    từ đoạn trước và sau trong tài liệu gốc (nếu cùng tiêu đề).
    """
    # Tạo bản sao sâu để tránh thay đổi dữ liệu gốc
    new_passage = deepcopy(passage) 
    merged_from_ids = new_passage["merged_from_ids"]
    title = new_passage["title"]
    
    # ID của đoạn liền kề (trước và sau) trong meta_corpus
    prev_id = merged_from_ids[0] - 1
    next_id = merged_from_ids[-1] + 1

    texts = []
    
    # 1. Thêm phần trước (nếu ID hợp lệ và cùng tiêu đề)
    if 0 <= prev_id < len(meta_corpus):
        prev_psg = meta_corpus[prev_id]
        if prev_psg.get("title") == title: 
            # Lấy nội dung đoạn trước
            prev_text = prev_psg["passage"]
            # Tách câu và lấy n_sent câu cuối cùng
            sentences = sent_tokenize(prev_text)
            prev_context = " ".join(sentences[-n_sent:])
            texts.append(prev_context)
            
    # 2. Thêm đoạn chính (đã gộp)
    # Lấy nội dung gốc của đoạn đã gộp (đã bao gồm tiêu đề)
    texts.append(new_passage["passage"])
    
    # 3. Thêm phần sau (nếu ID hợp lệ và cùng tiêu đề)
    if 0 <= next_id < len(meta_corpus):
        next_psg = meta_corpus[next_id]
        if next_psg.get("title") == title: 
            # Lấy nội dung đoạn sau
            next_text = next_psg["passage"]
            # Tách câu và lấy n_sent câu đầu tiên
            sentences = sent_tokenize(next_text)
            next_context = " ".join(sentences[:n_sent])
            texts.append(next_context)

    # Gộp tất cả lại
    # Gộp nội dung (đoạn chính đã có tiêu đề, nên không cần thêm tiêu đề nữa)
    expanded_text = "\n\n".join(texts)

    # Cập nhật nội dung mở rộng vào bản sao
    new_passage["passage"] = expanded_text
    return new_passage

def expand_contexts(passages: List[Dict], meta_corpus: List[Dict], n_sent: int = 3) -> List[Dict]:
    """
    Áp dụng hàm mở rộng ngữ cảnh cho toàn bộ danh sách các passage.
    """
    new_passages = [expand_context(passage, meta_corpus, n_sent) for passage in passages]
    return new_passages

def collapse(passages: List[Dict]) -> List[Dict]:
    """
    Giữ lại đoạn có điểm cao nhất cho mỗi Tiêu đề (title) duy nhất 
    trong danh sách đã mở rộng. Giúp tránh lặp nội dung.
    """
    new_passages = deepcopy(passages)
    titles = {}

    # Gom các đoạn theo tiêu đề (title)
    for passage in new_passages:
        title = passage["title"]
        if title not in titles:
            titles[title] = []
        titles[title].append(passage)

    best_passages = []
    # Lấy đoạn có điểm cao nhất (best_passage) trong mỗi nhóm tiêu đề
    for _, v in titles.items():
        best_passage = max(v, key=lambda x: x["score"])
        best_passages.append(best_passage)
        
    # Sắp xếp lại theo điểm cuối cùng trước khi trả về
    return sorted(best_passages, key=lambda x: x["score"], reverse=True)


def smooth_contexts(passages: List[Dict], meta_corpus: List[Dict]) -> List[Dict]:
    """
    Hàm chính để làm mượt danh sách ngữ cảnh (context smoothing) theo các bước:
    1. Gộp các đoạn liên tiếp (cùng tiêu đề và ID liền kề).
    2. Loại bỏ các đoạn có điểm quá thấp.
    3. Mở rộng ngữ cảnh bằng cách thêm câu trước và sau từ tài liệu gốc.
    4. Gọn lại (collapse) để mỗi tiêu đề chỉ có một đoạn tốt nhất.
    """
    # 1. Gộp các đoạn liên tiếp
    merged_contexts = merge_contexts(passages) 
    
    # 2. Loại bỏ các đoạn yếu (chỉ giữ lại những đoạn có điểm cao)
    shortlisted_contexts = discard_contexts(merged_contexts) 
    
    # 3. Mở rộng ngữ cảnh
    expanded_contexts = expand_contexts(shortlisted_contexts, meta_corpus) 
    
    # 4. Giữ lại đoạn tốt nhất mỗi tiêu đề
    collapsed_contexts = collapse(expanded_contexts) 
    
    return collapsed_contexts