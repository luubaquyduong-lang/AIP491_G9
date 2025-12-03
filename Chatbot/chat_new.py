# import os
# from openai import OpenAI
# from chromadb import PersistentClient
# from sentence_transformers import SentenceTransformer
# from dotenv import load_dotenv
# from ollama import chat

# from retriever import Retriever
# from smooth_context import smooth_contexts
# from data_loader import load_meta_corpus
# from typing import List, Dict
# from openai import OpenAI
# load_dotenv()

# # ------------------------- INIT GLOBAL RESOURCES -------------------------
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # Load embedding model (fine-tuned)
# EMB_MODEL = SentenceTransformer(
#     r"d:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\model_train\bkai_foundation_models_fine_tuning"
# )

# # Load ChromaDB
# chroma_client = PersistentClient(
#     path=r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\data_store"
# )
# collection = chroma_client.get_collection(name="aip491_v1")


# # ------------------------- FUNCTION: CLASSIFY SMALL TALK -------------------------
# def classify_small_talk(user_input, language="vi"):
#     prompt = f"""
#     Hãy phân loại câu sau có phải small talk không.

#     - Nếu là small talk → trả lời một đoạn giới thiệu chatbot du lịch Việt Nam.
#     - Nếu KHÔNG phải small talk → trả về đúng chữ: "no".

#     Câu hỏi: {user_input}
#     """

#     res = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": prompt}]
#     )

#     ans = res.choices[0].message.content.strip().lower()

#     # Chỉ hợp lệ khi trả về EXACT "no"
#     if ans == "no":
#         return "no"
#     else:
#         return ans  # small talk reply


# # ------------------------- FUNCTION: REWRITE QUESTION -------------------------
# def rewrite_question(history):
#     text_history = "\n".join([f"{m['role']}: {m['content']}" for m in history])

#     prompt = f"""
#     Hãy biến câu hỏi cuối cùng thành câu hỏi độc lập, có thể hiểu mà không cần lịch sử hội thoại.

#     Không trả lời câu hỏi.
#     Chỉ viết lại, nếu tiếng Anh thì dịch sang tiếng Việt.

#     Lịch sử hội thoại:
#     {text_history}
#     """

#     res = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": prompt}]
#     )
#     return res.choices[0].message.content.strip()


# # ------------------------- FUNCTION: RETRIEVE USING CHROMADB -------------------------
# def chroma_retrieve(query, topk=8):

#     # Convert query → embedding
#     q_emb = EMB_MODEL.encode([query]).tolist()

#     # Query Chroma
#     result = collection.query(
#         query_embeddings=q_emb,
#         n_results=topk,
#         include=["documents", "metadatas"]
#     )

#     contexts = []
#     for i in range(len(result["documents"][0])):
#         contexts.append({
#             "text": result["documents"][0][i],
#             "meta": result["metadatas"][0][i]
#         })

#     return contexts


# # ------------------------- FUNCTION: BUILD PROMPT -------------------------
# def build_prompt(question, contexts):
#     ctx_text = "\n\n".join(
#         [f"Context {i+1}: {c['text']}" for i, c in enumerate(contexts)]
#     )

#     prompt = f"""
#     Bạn là trợ lý du lịch Việt Nam. Chỉ trả lời dựa trên context.

#     {ctx_text}

#     Câu hỏi: {question}

#     Nếu không thấy thông tin phù hợp → trả lời:
#     "Xin lỗi, tôi không có thông tin phù hợp để trả lời câu hỏi này."
#     """

#     return prompt


# # ------------------------- FUNCTION: CHATBOT MAIN -------------------------
# def chatbot(history, language="vi"):
#     user_query = history[-1]["content"]

#     # 1. check small talk
#     st = classify_small_talk(user_query, language)
#     if st != "no":
#         return st

#     # 2. rewrite question
#     new_q = rewrite_question(history)

#     # 3. retrieve from ChromaDB
#     ctxs = chroma_retrieve(new_q, topk=8)

#     # 4. build prompt
#     prompt = build_prompt(new_q, ctxs)

#     # 5. GPT answer
#     res = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": prompt}]
#     )

#     return res.choices[0].message.content.strip()


# # ------------------------- MAIN LOOP -------------------------
# def main():
#     print("Chatbot du lịch Việt Nam (ChromaDB version)\n")
#     history = []

#     while True:
#         q = input("Bạn: ").strip()
#         if q in ["exit", "quit", "bye", "e"]:
#             print("Tạm biệt!")
#             break

#         history.append({"role": "user", "content": q})
#         reply = chatbot(history)
#         print("Bot:", reply)
#         history.append({"role": "assistant", "content": reply})


# if __name__ == "__main__":
#     main()
