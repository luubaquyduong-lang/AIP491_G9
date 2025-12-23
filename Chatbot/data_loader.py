# ===== DATA LOADER MODULE =====
# Module này chịu trách nhiệm tải dữ liệu corpus từ file JSONL
# Corpus được sử dụng trong quá trình mở rộng ngữ cảnh (expand_context)

from datasets import load_dataset

def load_meta_corpus(file_path):
    """
    Tải toàn bộ corpus từ file JSONL để phục vụ cho context smoothing.
    
    Args:
        file_path (str): Đường dẫn tuyệt đối đến file JSONL chứa corpus
                        Mỗi dòng trong file là một JSON object với cấu trúc:
                        {"title": str, "passage": str, "doc_id": int, ...}
    
    Returns:
        List[Dict]: Danh sách các đoạn văn (passages) đã được sắp xếp theo doc_id
                   Mỗi phần tử là một dictionary chứa thông tin của một chunk:
                   - title: Tiêu đề bài viết/tài liệu
                   - passage: Nội dung văn bản của chunk
                   - doc_id: ID duy nhất của chunk trong corpus (0, 1, 2, ...)
                   
    Công dụng:
        - Hỗ trợ hàm expand_context để truy cập đoạn trước/sau dựa trên doc_id
        - Đảm bảo có thể lấy thêm ngữ cảnh từ các đoạn liền kề trong tài liệu gốc
    
    Ví dụ:
        >>> meta_corpus = load_meta_corpus("data/corpus.jsonl")
        >>> print(meta_corpus[0])
        {'title': 'Du lịch Hà Nội', 'passage': 'Hà Nội là thủ đô...', 'doc_id': 0}
    """
    # Sử dụng thư viện datasets của Hugging Face để load JSONL
    # split="train" đảm bảo load toàn bộ file thành một dataset duy nhất
    # .to_list() chuyển đổi dataset thành list để truy cập nhanh theo index
    return load_dataset("json", data_files=file_path, split="train").to_list()



