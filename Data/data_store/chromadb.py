from datasets import load_dataset


import re

def extract_first_sentence(text: str) -> str:
    """
    Lấy câu đầu tiên trong đoạn text.
    Cắt theo dấu . ? ! : đầu tiên.
    """
    text = text.strip()
    if not text:
        return ""

    parts = re.split(r'(?<=[\.!\?:])\s+', text, maxsplit=1)
    return parts[0].strip()

import json
import pickle
from datasets import load_dataset

# ===== 1) Load JSONL thành list[dict] =====
def load_meta_corpus(file_path: str):
    return load_dataset("json", data_files=file_path, split="train").to_list()

json_path = r"C:\Users\Acer\Downloads\data_final_sorted.jsonl"
meta_corpus = load_meta_corpus(json_path)
print("Số dòng corpus:", len(meta_corpus))

# ===== 2) Load embeddings (pkl) =====
corpus_emb_path = r"d:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\Embedding_data\embeding_by_model_fine_e5.pkl"

with open(corpus_emb_path, "rb") as f:
    corpus_embeddings = pickle.load(f)

print("Số embedding:", len(corpus_embeddings))

assert len(meta_corpus) == len(corpus_embeddings), "❌ Số dòng corpus != số embedding!"

ids = []
documents = []
metadatas = []
embeddings = []

# Lưu section_title lần đầu cho mỗi output_paragraph_x
title2section = {}

for i, row in enumerate(meta_corpus):
    title   = row["title"]        # vd: "output_paragraph_15"
    passage = row["passage"]
    row_id  = row.get("id", i)    # phòng khi không có field id

    # Nếu lần đầu gặp title này → trích câu đầu
    if title not in title2section:
        section_title = extract_first_sentence(passage)
        title2section[title] = section_title
    else:
        section_title = title2section[title]

    # ID duy nhất cho từng chunk (string)
    doc_id = f"doc_{row_id}"

    ids.append(doc_id)
    documents.append(passage)
    metadatas.append({
        "section_title": section_title,  # câu đầu của đoạn gốc
        "paragraph_id": title,           # output_paragraph_x
        "len": row.get("len", None),
        # nếu trong data_final_sorted.jsonl có province thì thêm:
        # "province": row.get("province"),
        # "source": row.get("source"),
    })
    # embedding thứ i
    emb = corpus_embeddings[i]
    # nếu là numpy array / torch tensor thì chuyển sang list
    try:
        emb = emb.tolist()
    except AttributeError:
        pass
    embeddings.append(emb)

import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(
    path="D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data_store\chroma_store",
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_or_create_collection(
    name="vietnam_tourism_e5_finetuned",
)

BATCH = 256
n = len(documents)

for start in range(0, n, BATCH):
    end = start + BATCH
    collection.add(
        ids=ids[start:end],
        documents=documents[start:end],
        metadatas=metadatas[start:end],
        embeddings=embeddings[start:end],
    )
    print(f"✅ Đã add {end}/{n}")
test_query = "Đi An Giang thì có thể tham quan chùa chiền, núi non ở đâu?"
# embed_query = ... (dùng đúng model e5 bạn đã fine-tune)
# ví dụ:
# embed_query = model.encode([test_query]).tolist()

res = collection.query(
    query_embeddings=embed_query,
    n_results=3
)

for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
    print("====")
    print("section_title:", meta["section_title"])
    print("paragraph_id :", meta["paragraph_id"])
    print("len          :", meta["len"])
    print("passage      :", doc[:200], "...")
