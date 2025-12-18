# # upsert_chroma_with_first_sentence.py
# import json
# import os
# import re
# import pickle
# from typing import List, Dict
# from sentence_transformers import SentenceTransformer
# import chromadb
# from chromadb.config import Settings

# # ================= CONFIG - sửa theo môi trường bạn =================
# INPUT_JSONL = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\data_final_train_v1\data_final_sort_v1_fisrt_se.jsonl"   # <-- file jsonl của bạn
# EMBED_PKL   = r"d:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\embedding_data\embeding_by_model_fine_bkai_v1.pkl"                        # <-- nếu có embeddings sẵn: path tới .pkl (để trống nếu muốn compute)
# CHROMA_PATH = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data_store"                                              # nơi lưu chroma persistent
# COLLECTION_NAME = "aip491_v1"
# EMBED_MODEL = "d:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\model_train\bkai_foundation_models_fine_tuning"  # hoặc path tới model fine-tuned
# BATCH = 256
# # ===================================================================

# def load_jsonl(path: str) -> List[Dict]:
#     out = []
#     with open(path, "r", encoding="utf-8") as f:
#         for i, line in enumerate(f):
#             line = line.strip()
#             if not line:
#                 continue
#             try:
#                 obj = json.loads(line)
#             except json.JSONDecodeError:
#                 # bỏ dòng không phải JSON
#                 continue

#             passage = obj.get("passage", "") or obj.get("text", "")
#             title = obj.get("title", "")
#             doc_id = obj.get("id", i)
#             length = obj.get("len", len(passage.split()))
#             line_first = obj.get("line_first_sentence", "")  # <-- giữ nếu có
#             out.append({
#                 "title": title,
#                 "passage": passage,
#                 "id": str(doc_id),
#                 "len": length,
#                 "line_first_sentence": line_first
#             })
#     print(f"Loaded {len(out)} docs from {path}")
#     return out

# def ensure_list_of_floats(vec):
#     try:
#         v = list(vec)
#     except Exception:
#         v = vec
#     return [float(x) for x in v]

# def main():
#     corpus = load_jsonl(INPUT_JSONL)
#     n = len(corpus)

#     # Load embeddings nếu có sẵn
#     embeddings = None
#     if EMBED_PKL and os.path.exists(EMBED_PKL):
#         with open(EMBED_PKL, "rb") as f:
#             embeddings = pickle.load(f)
#         print("Loaded embeddings from", EMBED_PKL, "len=", len(embeddings))
#         if len(embeddings) != n:
#             raise ValueError("Số lượng embeddings và corpus không khớp!")

#     # Nếu không có embeddings thì chuẩn bị model để compute
#     embedder = None
#     if embeddings is None:
#         print("No embedding file → sẽ compute embeddings bằng model:", EMBED_MODEL)
#         embedder = SentenceTransformer(EMBED_MODEL)

#     ids: List[str] = []
#     documents: List[str] = []
#     metadatas: List[Dict] = []
#     embs: List[List[float]] = []

#     for i, doc in enumerate(corpus):
#         doc_id = str(doc["id"])
#         text = doc["passage"] or ""
#         title = doc.get("title", "").strip()
#         line_first = doc.get("line_first_sentence", "")

#         meta = {
#             "doc_id": doc_id,
#             "title": title,
#             "line_first_sentence": line_first,  # <-- giữ trường này trong metadata
#             "len": doc.get("len", 0),
#             "chunk_index": i
#         }

#         ids.append(doc_id)
#         documents.append(text)
#         metadatas.append(meta)

#         if embeddings is not None:
#             e = embeddings[i]
#             ems = ensure_list_of_floats(e)
#             embs.append(ems)

#     # nếu chưa có embedding: compute in batches
#     if embeddings is None:
#         print("Computing embeddings on the fly in batches...")
#         embs = []
#         for i in range(0, n, BATCH):
#             j = min(n, i + BATCH)
#             texts_batch = documents[i:j]
#             batch_emb = embedder.encode(texts_batch, show_progress_bar=True)
#             for be in batch_emb:
#                 embs.append(ensure_list_of_floats(be))
#         print("Computed all embeddings, total:", len(embs))

#     # ================= Create / connect to persistent Chroma =================
#     print("Creating/connecting to Chroma at:", CHROMA_PATH)
#     client = chromadb.PersistentClient(path=CHROMA_PATH, settings=Settings(anonymized_telemetry=False))

#     # get or create collection
#     try:
#         collection = client.get_or_create_collection(name=COLLECTION_NAME)
#     except Exception:
#         # fallback
#         try:
#             collection = client.get_collection(name=COLLECTION_NAME)
#         except Exception:
#             collection = client.create_collection(name=COLLECTION_NAME)

#     # Add to chroma in batches
#     print("Adding to Chroma collection:", COLLECTION_NAME)
#     for i in range(0, n, BATCH):
#         j = min(n, i + BATCH)
#         collection.add(
#             ids=ids[i:j],
#             documents=documents[i:j],
#             metadatas=metadatas[i:j],
#             embeddings=embs[i:j]
#         )
#         print(f"  Added {j}/{n}")

#     print("✅ Done. Data upserted into Chroma collection:", COLLECTION_NAME)

# if __name__ == "__main__":
#     main()



# Mục đích: tải dữ liệu từ file JSONL, (tuỳ chọn) load embeddings có sẵn, hoặc compute embeddings bằng SentenceTransformer rồi upsert (thêm) vào ChromaDB.
# Ghi chú: file đã được chú thích chi tiết từng phần để bạn dễ hiểu và maintain.

import json
import os
import pickle
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# ======================= CẤU HÌNH (sửa theo môi trường của bạn) =======================
# Đường dẫn tới file JSONL chứa dữ liệu (mỗi dòng 1 JSON object)
INPUT_JSONL = r"D:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\AIP491_G9\Data\processed\data_final_train_v2\data_final_sort_v2_fisrt_se.jsonl"

# Nếu bạn đã có embeddings tính sẵn, để đường dẫn file .pkl vào đây.
# Nếu để chuỗi rỗng hoặc file không tồn tại -> script sẽ tự compute embedding bằng model.
EMBED_PKL   = r"d:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\embedding_data\embeding_by_model_fine_bkai_v2.pkl"

# Thư mục lưu Chroma persistent (local)
CHROMA_PATH = r"D:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\AIP491_G9\Data\data_store"

# Tên collection trong Chroma
COLLECTION_NAME = "aip491_v2"

# Đường dẫn/tên model để compute embedding nếu không có EMBED_PKL
EMBED_MODEL = r"d:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\\model_train\bkai_foundation_models_fine_tuning_v2"

# Kích thước batch khi compute embedding hoặc khi upsert vào Chroma
# (tăng để nhanh hơn nhưng cần nhiều RAM/GPU hơn)
BATCH = 256
# ======================================================================================


def load_jsonl(path: str) -> List[Dict]:
    """
    Đọc file JSONL và trả về list các document (dạng dict).
    Chuẩn hóa các trường quan trọng:
      - 'passage' hoặc 'text' -> nội dung chính
      - 'title' -> tiêu đề (nếu có)
      - 'doc_id' -> id tài liệu (dùng id trong file nếu có, ngược lại dùng index)
      - 'len' -> số từ (nếu file có trường len thì dùng, nếu không thì tính cơ bản)
      - 'line_first_sentence' -> câu đầu (nếu đã precompute)
    Trả về: list các dict dạng { "title", "passage", "doc_id", "len", "line_first_sentence" }
    """
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                # Nếu dòng không phải JSON hợp lệ thì bỏ qua (chống lỗi file)
                continue

            passage = obj.get("passage", "") or obj.get("text", "")
            title = obj.get("title", "")
            # Lấy id từ file nếu có (giữ nguyên kiểu), nếu không => dùng index i
            doc_id = obj.get("id", i)
            # Độ dài: nếu file có trường 'len' thì dùng, nếu không thì tính sơ bằng .split()
            length = obj.get("len", len(passage.split()))
            # Câu đầu tiên đã precompute (nếu có)
            line_first = obj.get("line_first_sentence", "")

            out.append({
                "title": title,
                "passage": passage,
                "doc_id": doc_id,
                "len": length,
                "line_first_sentence": line_first
            })

    print(f"Loaded {len(out)} docs from {path}")
    return out


def ensure_list_of_floats(vec):
    """
    Đảm bảo embedding là list các float (Chroma yêu cầu list[float]).
    Nếu đầu vào là numpy array hoặc tensor, chuyển sang list float.
    """
    try:
        v = list(vec)
    except Exception:
        v = vec
    return [float(x) for x in v]


def main():
    # ------------------ 1. Load corpus ------------------
    corpus = load_jsonl(INPUT_JSONL)
    n = len(corpus)

    # ------------------ 2. Load embeddings nếu có ------------------
    # embeddings dự kiến là list/np.array kích thước n x dim
    embeddings = None
    if EMBED_PKL and os.path.exists(EMBED_PKL):
        with open(EMBED_PKL, "rb") as f:
            embeddings = pickle.load(f)
        print("Loaded embeddings from", EMBED_PKL, "len=", len(embeddings))

        # Kiểm tra cơ bản: số lượng embedding có khớp số document không
        if len(embeddings) != n:
            raise ValueError("Số lượng embeddings và corpus không khớp!")

    # ------------------ 3. Chuẩn bị embedder (nếu cần compute) ------------------
    embedder = None
    if embeddings is None:
        # Nếu không có file embeddings thì cần model để tính embedding
        print("No embedding file → sẽ compute embeddings bằng model:", EMBED_MODEL)
        embedder = SentenceTransformer(EMBED_MODEL)

    # ------------------ 4. Build lists để upsert ------------------
    # ids: list[str] dùng làm id chính khi add vào Chroma (chuẩn hoá sang string)
    # documents: list[str] nội dung text
    # metadatas: list[dict] metadata cho mỗi doc (dùng khi query để hiểu nguồn)
    # embs: list[list[float]] embeddings
    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict] = []
    embs: List[List[float]] = []

    for i, doc in enumerate(corpus):
        # Chuẩn hoá doc_id thành string (chroma id nên là string để tránh trùng kiểu)
        doc_id = str(doc["doc_id"])
        text = doc["passage"] or ""
        title = doc.get("title", "").strip()
        line_first = doc.get("line_first_sentence", "")

        # Tạo metadata cho document -> lưu các thông tin hữu ích cho filtering / trace
        # Bạn có thể thêm fields khác như 'province', 'category', 'source', 'published_at'...
        meta = {
            "doc_id": doc_id,
            "title": title,
            "line_first_sentence": line_first,
            "len": doc.get("len", 0),
            "chunk_index": i
        }

        ids.append(doc_id)
        documents.append(text)
        metadatas.append(meta)

        # Nếu đã load embeddings từ file .pkl thì chèn vào list embs tương ứng
        if embeddings is not None:
            e = embeddings[i]
            ems = ensure_list_of_floats(e)
            embs.append(ems)

    # ------------------ 5. Compute embedding nếu chưa có ------------------
    if embeddings is None:
        print("Computing embeddings theo batch...")
        embs = []
        for i in range(0, n, BATCH):
            j = min(n, i + BATCH)
            texts_batch = documents[i:j]

            # Tính batch embedding (show_progress_bar=True để thấy tiến trình)
            batch_emb = embedder.encode(texts_batch, show_progress_bar=True)

            # Chuyển từng embedding về list[float] và append
            for be in batch_emb:
                embs.append(ensure_list_of_floats(be))

        print("Tính embedding xong. Tổng embeddings:", len(embs))

    # ------------------ 6. Kết nối tới Chroma (persistent) ------------------
    print("Kết nối tới Chroma Persistent:", CHROMA_PATH)
    client = chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=Settings(anonymized_telemetry=False)
    )

    # ------------------ 7. (Tuỳ chọn) Xóa collection cũ nếu muốn build lại ------------------
    # Nếu bạn muốn rebuild hoàn toàn (ví dụ: đổi model embedding) -> mở comment phần này.
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Đã xoá collection cũ (nếu tồn tại):", COLLECTION_NAME)
    except Exception:
        # Nếu không có collection cũ thì sẽ ném ngoại lệ, ta bỏ qua
        print("Collection không tồn tại hoặc đã xoá từ trước.")

    # ------------------ 8. Tạo hoặc lấy collection mới ------------------
    # Khi tạo collection, ta đặt metadata {"hnsw:space": "cosine"} để dùng cosine distance
    try:
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}  # đặt metric tìm kiếm là cosine
        )
        print("Tạo/Lấy Chroma Collection:", COLLECTION_NAME)
    except Exception:
        # fallback nếu api khác version
        try:
            collection = client.get_collection(name=COLLECTION_NAME)
        except Exception:
            collection = client.create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"} # Cosine Distance
            )

    # ------------------ 9. Add/Upsert dữ liệu vào Chroma theo batch ------------------
    # Lưu ý: nếu ids trùng (same id) thì hành vi có thể là duplicate hoặc replace tùy version chroma.
    # Nếu muốn an toàn, hãy đảm bảo ids unique trước khi add.
    print("Bắt đầu add dữ liệu vào Chroma Collection:", COLLECTION_NAME)

    for i in range(0, n, BATCH):
        j = min(n, i + BATCH)

        collection.add(
            ids=ids[i:j],
            documents=documents[i:j],
            metadatas=metadatas[i:j],
            embeddings=embs[i:j]
        )

        # In tiến trình để bạn biết đã upsert tới đâu
        print(f"  → Đã thêm documents {i+1}..{j} / {n}")

    print("DONE! Dữ liệu đã được upsert vào collection:", COLLECTION_NAME)


if __name__ == "__main__":
    main()
