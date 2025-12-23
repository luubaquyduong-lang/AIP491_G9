import json
import re

MAX_LEN = 150  # tối đa từ mỗi chunk
MIN_LEN = 50   # tối thiểu từ mỗi chunk (nếu < 50 thì sẽ mượn/gộp)

# --- Tách câu (có hỗ trợ …) ---
SENT_SPLIT_RE = re.compile(r'(?<=[\.\!\?…])\s+')

def count_words(s: str) -> int:
    return len(s.split())

def first_sentence(text: str) -> str:
    """Lấy câu đầu tiên của đoạn gốc."""
    text = text.strip()
    if not text:
        return ""
    parts = SENT_SPLIT_RE.split(text)
    return parts[0].strip() if parts else text

def split_text_by_sentence_balanced(text: str, max_words: int, min_words: int) -> list[str]:
    """
    Chia văn bản thành các chunk theo CÂU, mỗi chunk <= max_words.
    Sau đó cân bằng để tránh chunk < min_words bằng cách mượn/gộp từ chunk trước.
    """
    text = text.strip()
    if not text:
        return []

    # ===== BƯỚC 1: TÁCH CÂU =====
    # Tách văn bản thành danh sách các câu riêng biệt
    # VD: "Hà Nội đẹp. Đà Nẵng đẹp." → ["Hà Nội đẹp", "Đà Nẵng đẹp"]
    sentences = [s.strip() for s in SENT_SPLIT_RE.split(text) if s.strip()]

    # ===== BƯỚC 2: GOM CÂU THÀNH CHUNK (≤ max_words) =====
    # Gom các câu liền kề thành 1 chunk, đảm bảo tổng số từ ≤ max_words (150)
    chunks_sent = []  
    cur_sent_list, cur_len = [], 0  
    
    for s in sentences:
        sw = count_words(s)  

        # TRƯỜNG HỢP 1: Câu dài hơn max_words → Tách riêng thành 1 chunk
        if sw > max_words:
            if cur_sent_list:  
                chunks_sent.append(cur_sent_list)
                cur_sent_list, cur_len = [], 0
            chunks_sent.append([s])  
            continue

        # TRƯỜNG HỢP 2: Thêm câu này vào chunk hiện tại sẽ vượt max_words
        # → Kết thúc chunk hiện tại, bắt đầu chunk mới
        if cur_len + sw > max_words and cur_sent_list:
            chunks_sent.append(cur_sent_list)  
            cur_sent_list, cur_len = [s], sw   
        else:
            # TRƯỜNG HỢP 3: Thêm câu này vào chunk hiện tại vẫn ≤ max_words
            cur_sent_list.append(s)
            cur_len += sw

    # Lưu chunk cuối cùng (nếu có)
    if cur_sent_list:
        chunks_sent.append(cur_sent_list)

    # ===== BƯỚC 3: CÂN BẰNG CHUNK (tránh < min_words) =====
    # Nếu chunk nào < min_words (50 từ) → Mượn câu từ chunk trước hoặc gộp luôn
    
    def chunk_len(sent_list):
        """Tính tổng số từ trong 1 chunk (list các câu)"""
        return sum(count_words(x) for x in sent_list)

    i = 1  # Bắt đầu từ chunk thứ 2 (chunk 0 không thể mượn từ ai)
    while i < len(chunks_sent):
        cur_len = chunk_len(chunks_sent[i])
        
        #  Chunk đủ dài (≥ min_words) → Bỏ qua, kiểm tra chunk tiếp theo
        if cur_len >= min_words:
            i += 1
            continue

        #  Chunk quá ngắn (< min_words) → CẦN XỬ LÝ
        prev = chunks_sent[i-1] 
        cur = chunks_sent[i]     

        # --- CƠ CHẾ MƯỢN CÂU ---
        # Lần lượt lấy câu cuối của chunk trước cho vào đầu chunk hiện tại
        # Cho đến khi chunk hiện tại đủ min_words HOẶC chunk trước hết câu
        while chunk_len(cur) < min_words and len(prev) > 0:
            last_sentence = prev[-1]  
            
            # Kiểm tra: Nếu lấy câu này thì chunk trước còn đủ min_words không?
            # Nếu chunk trước chỉ có 1 câu VÀ sau khi lấy sẽ < min_words → DỪNG MƯỢN
            if chunk_len(prev) - count_words(last_sentence) < min_words and len(prev) == 1:
                break
            
            # Mượn: Lấy câu cuối của prev, thêm vào đầu cur
            cur.insert(0, prev.pop())  

        # Sau khi mượn hết, kiểm tra lại:
        # Nếu chunk hiện tại VẪN < min_words → GỘP LUÔN 2 chunks
        if chunk_len(cur) < min_words:
            chunks_sent[i-1] = prev + cur  # Gộp prev và cur thành 1
            del chunks_sent[i]             # Xóa chunk i (đã gộp vào i-1)
            # Không tăng i (vì đã xóa chunk i, chunk tiếp theo trở thành i)
        else:
            # Chunk đã đủ min_words sau khi mượn → Chuyển sang chunk tiếp theo
            i += 1

    # ===== BƯỚC 4: CHUYỂN TỪ LIST CÂU THÀNH CHUỖI =====
    # Mỗi chunk từ list các câu → 1 chuỗi văn bản hoàn chỉnh
    chunks = [" ".join(slist) for slist in chunks_sent if slist]
    return chunks


# ==========================
# MAIN - XỬ LÝ FILE INPUT
# ==========================
input_file  = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\data_final_train_v2\data_final_sort_v2_output.txt"
output_file = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\data_final_train_v1\data_final_sort_v1_fisrt_se.jsonl"

output = []
line_id = 0  # ID duy nhất cho mỗi passage

# Đọc từng dòng từ file input
with open(input_file, 'r', encoding='utf-8') as f:
    for line_num, raw in enumerate(f, start=1):
        line = raw.strip()
        if not line:
            continue

        # Bỏ qua các dòng header kiểu "===== Huế ====="
        if line.startswith("=====") and line.endswith("====="):
            continue

        # Tạo title dựa trên số dòng (mỗi dòng là 1 đoạn văn độc lập)
        title = f"output_paragraph_{line_num}"

        # Lấy câu đầu tiên của đoạn gốc (để tham chiếu)
        first_sent = first_sentence(line)

        # Chia đoạn văn thành các chunks cân bằng (50-150 từ)
        chunks = split_text_by_sentence_balanced(line, MAX_LEN, MIN_LEN)

        # Tạo 1 object JSON cho mỗi chunk
        for chunk in chunks:
            obj = {
                "title": title,                    # Tiêu đề đoạn gốc
                "line_first_sentence": first_sent, # Câu đầu tiên của đoạn gốc
                "passage": chunk,                  # Nội dung chunk
                "id": line_id,                     # ID duy nhất
                "len": len(chunk.split()),         # Số từ trong chunk
            }
            output.append(obj)
            line_id += 1

# Ghi tất cả ra file JSONL (mỗi dòng là 1 JSON object)
with open(output_file, 'w', encoding='utf-8') as f:
    for item in output:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f" Đã xử lý xong và xuất {len(output)} đoạn vào {output_file}")

