# main.py

from data_loader import load_meta_corpus
from retriever import Retriever
from smooth_context import smooth_contexts
from chat import chatbot

# Load corpus
meta_corpus = load_meta_corpus("D:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\AIP491_G9\Data\\processed\data_final_sorted.jsonl")

# Initialize retriever
retriever = Retriever(
    corpus=meta_corpus,
    corpus_emb_path="D:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\\Embedding_data\\embeding_by_model_fine_e5.pkl",
    model_name="D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\Model_train\intfloat_multilingual_e5_base_fine_tuning"
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

