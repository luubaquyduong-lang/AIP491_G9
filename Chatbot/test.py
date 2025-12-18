# # main.py

# from data_loader import load_meta_corpus
# from retriever import Retriever
# from smooth_context import smooth_contexts
# from chat import chatbot

# # Load corpus
# meta_corpus = load_meta_corpus("D:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\AIP491_G9\Data\\processed\data_final_sorted.jsonl")

# # Initialize retriever
# retriever = Retriever(
#     corpus=meta_corpus,
#     corpus_emb_path="D:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\\Embedding_data\\embeding_by_model_fine_e5.pkl",
#     model_name="D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\Model_train\intfloat_multilingual_e5_base_fine_tuning"
# )

# # Query example
# question = "Địa điểm du lịch nổi tiếng ở miền Bắc là gì?"
# top_results = retriever.retrieve(question, topk=10)

# # Smooth contexts
# smoothed_contexts = smooth_contexts(top_results, meta_corpus)

# # Display results
# # for context in smoothed_contexts:
# #     print(context["passage"], context["score"])
# # {"role": "user", "content": "Địa điểm du lịch ở An Giang?"},
# #                 {"role": "system", "content": "An Giang có nhiều điểm du lịch thú vị."},
# # Chatbot interaction
# conversation_history = [
#                 {"role": "user", "content": "Chào bạn, bạn thích đi du lịch chứ?"}]
# response = chatbot(conversation_history, "Tiếng Việt")
# print(response)






# test_chroma_query.py
import chromadb
import numpy as np
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import pprint

CHROMA_PATH = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data_store"
COLLECTION_NAME = "aip491_v1"
MODEL = r"d:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\model_train\bkai_foundation_models_fine_tuning"

pp = pprint.PrettyPrinter(indent=2)

# 1) Connect tới Chroma
client = chromadb.PersistentClient(path=CHROMA_PATH, settings=Settings(anonymized_telemetry=False))
collection = client.get_collection(COLLECTION_NAME)

# 2) In metadata collection (đã thấy bạn có cosine)
print("Collection metadata:", collection.metadata)

# 3) Chuẩn bị query embedding (hoặc dùng query_text nếu collection có embedding_function)
embedder = SentenceTransformer(MODEL)
query_text = "du lịch phú quốc nên đi mùa nào"
query_emb = embedder.encode([query_text]).tolist()

# 4) Query — KHÔNG đưa "ids" vào include vì gây lỗi
res = collection.query(
    query_embeddings=query_emb,
    n_results=5,
    include=["documents", "metadatas", "distances"]  # hợp lệ
)

# 5) In cấu trúc trả về để xem keys
print("\nResponse keys:", list(res.keys()))
pp.pprint(res)

# 6) Duyệt kết quả và in thông tin hữu ích
def safe_get_doc_id(meta):
    # nếu bạn đã lưu doc_id trong metadata (recommended) -> lấy ra
    return meta.get("doc_id") if isinstance(meta, dict) else None

for rank, (doc, meta, dist) in enumerate(zip(res["documents"][0], res["metadatas"][0], res["distances"][0]), start=1):
    doc_id = safe_get_doc_id(meta) or f"(no doc_id in metadata, rank {rank})"
    print(f"\nRank {rank} | doc_id={doc_id} | distance={dist}")
    print("Metadata snippet:", {k: meta.get(k) for k in ("title","line_first_sentence") if k in meta})
    print("Document snippet:", (doc[:300] + "...") if len(doc) > 300 else doc)

# 7) Nếu bạn đã lưu embedding trong metadata (ví dụ meta['embedding']), ta có thể tính cosine similarity:
def cosine_sim(a, b):
    a = np.array(a); b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

if "embedding" in res["metadatas"][0][0]:
    print("\nEmbeddings có trong metadata — tính cosine similarity cho từng result:")
    for i, meta in enumerate(res["metadatas"][0]):
        sim = cosine_sim(query_emb[0], meta["embedding"])
        print(f"  rank {i+1} cosine_sim = {sim:.4f}")
else:
    print("\nKhông tìm thấy field 'embedding' trong metadata — không thể tính cosine similarity trực tiếp.")
