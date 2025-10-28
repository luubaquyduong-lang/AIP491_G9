# main.py

from data_loader import load_meta_corpus
from retriever import Retriever
from smooth_context import smooth_contexts
from chat import chatbot

# Load corpus
meta_corpus = load_meta_corpus("D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\corpus_chunks.jsonl")

# Initialize retriever
retriever = Retriever(
    corpus=meta_corpus,
    corpus_emb_path="D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\corpus_embedding_w150.pkl",
    # corpus_emb_path="D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\Train_model\corpus_embedding_ft.pkl",
    # model_name="bkai-foundation-models/vietnamese-bi-encoder"
    model_name="D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\Train_model\fine_tuned_biencoder"
)

# Query example
question = "Địa điểm du lịch nổi tiếng ở miền Bắc là gì?"
top_results = retriever.retrieve(question, topk=10)

# Smooth contexts
smoothed_contexts = smooth_contexts(top_results, meta_corpus)

# Display results
# for context in smoothed_contexts:
#     print(context["passage"], context["score"])
# {"role": "user", "content": "Địa điểm du lịch ở An Giang?"},
#                 {"role": "system", "content": "An Giang có nhiều điểm du lịch thú vị."},
# Chatbot interaction
conversation_history = [
                {"role": "user", "content": "Chào bạn, bạn thích đi du lịch chứ?"}]
response = chatbot(conversation_history, "Tiếng Việt")
print(response)