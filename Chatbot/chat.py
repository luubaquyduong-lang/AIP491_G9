import os
import pickle
from typing import List, Dict

# --- Thư viện bên thứ 3 ---
from openai import OpenAI
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pyvi.ViTokenizer import tokenize
# --- Import Module Nội Bộ ---
from smoonth_context import smooth_contexts
from data_loader import load_meta_corpus 
load_dotenv()

# ========================= CẤU HÌNH ĐƯỜNG DẪN =========================
CORPUS_PATH = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\data_final_train_v1\data_final_sort_v1_fisrt_se.jsonl"
DB_PATH = r"d:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\data_store"
MODEL_PATH = r"duongluuba/AIP491_G9_Vietnam_tourism_data_bkai-foundation-fine-tuned-v1"
# ========================d:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\\model_train\bkai_foundation_models_fine_tuning= KHỞI TẠO TÀI NGUYÊN =========================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print(">> Loading Embedding Model...")
EMB_MODEL = SentenceTransformer(MODEL_PATH)

print(">> Connecting to ChromaDB...")
chroma_client = PersistentClient(path=DB_PATH)
collection = chroma_client.get_collection(name="aip491_v1")

print(">> Loading Meta Corpus (cho smooth context)...")
META_CORPUS = load_meta_corpus(CORPUS_PATH) 

# ========================= PROMPT TEMPLATE =========================
# PROMPT_TEMPLATE = (
#     """###Yêu cầu: Bạn là một trợ lý du lịch thông minh, chuyên cung cấp câu trả lời dựa trên thông tin được truy xuất từ hệ thống về du lịch Việt Nam. Khi nhận được dữ liệu truy xuất từ RAG, hãy:  
#     1. Phân tích dữ liệu để trả lời đúng trọng tâm câu hỏi của người dùng. Chỉ trả lời dựa trên dữ liệu được cung cấp, không suy đoán hoặc tạo ra thông tin mới.
#     2. Tóm tắt thông tin một cách rõ ràng, ngắn gọn nhưng vẫn đầy đủ ý nghĩa.  
#     3. Trả lời với giọng điệu thân thiện và dễ tiếp cận.  
#     4. Nếu dữ liệu truy xuất không có thông tin liên quan đến câu hỏi hoặc không có dữ liệu nào được truy xuất, hãy trả lời: "Xin lỗi, tôi không có thông tin phù hợp để trả lời câu hỏi này."  
#     5. Nếu câu hỏi không liên quan đến chủ đề du lịch Việt Nam (out domain) hãy giới thiệu lịch sự về lĩnh vực của mình.
#     6. Trả lời câu hỏi bằng ngôn ngữ: {language}

#     ###Dựa vào một số ngữ cảnh truy xuất được dưới đây nếu bạn thấy nó có liên quan đến câu hỏi thì trả lời câu hỏi ở cuối. {input}
#     ###Câu hỏi từ người dùng: {question}
#     ###Nếu thấy ngữ cảnh có liên quan đến câu hỏi hãy trả lời chi tiết và đầy đủ dựa trên ngữ cảnh."""
# )
PROMPT_TEMPLATE = (
    """###Vai trò: Bạn là trợ lý du lịch ảo thông minh, am hiểu sâu sắc về du lịch Việt Nam. Nhiệm vụ của bạn là hỗ trợ du khách dựa trên thông tin được cung cấp.

    ###Nguyên tắc trả lời:
    1. **Phân tích sâu:** Hãy đọc kỹ các ngữ cảnh được cung cấp (context). Đừng chỉ tìm từ khóa chính xác, hãy tìm các ý liên quan, đồng nghĩa hoặc suy luận logic từ ngữ cảnh để trả lời câu hỏi.
    2. **Trả lời linh hoạt:** - Nếu ngữ cảnh chứa đầy đủ thông tin: Trả lời chi tiết, chính xác.
       - Nếu ngữ cảnh chỉ chứa một phần thông tin: Hãy trả lời dựa trên những gì có trong ngữ cảnh và nói rõ rằng hệ thống chưa có thông tin chi tiết cho phần còn lại. Đừng từ chối toàn bộ câu hỏi.
    3. **Phong cách:** Thân thiện, nhiệt tình như một hướng dẫn viên du lịch bản địa.
    4. **Xử lý thiếu tin:** Chỉ khi ngữ cảnh HOÀN TOÀN KHÔNG LIÊN QUAN đến câu hỏi, bạn mới được phép trả lời: "Hiện tại cơ sở dữ liệu của tôi chưa cập nhật thông tin chính xác về vấn đề này, bạn có thể thử hỏi về các địa điểm khác như [gợi ý dựa trên ngữ cảnh] không?".
    5. **Ngôn ngữ:** Trả lời bằng ngôn ngữ: {language}

    ###Dữ liệu được truy xuất:
    {input}

    ###Câu hỏi của người dùng: {question}
    
    ###Câu trả lời của bạn:"""
)
# ========================= CÁC HÀM XỬ LÝ (UTILS) =========================

def classify_small_talk(user_input, language="vi"):
    """
    Phân loại Small Talk dùng Prompt chi tiết
    """
    prompt = f"""
    ###Yêu cầu: Bạn là một trợ lý hữu ích được thiết kế để phân loại các câu hỏi của người dùng trong ngữ cảnh của một chatbot du lịch Việt Nam. Nhiệm vụ của bạn là xác định liệu câu hỏi của người dùng có phải là "small talk" hay không"
    ###"Small talk" đề cập đến những chủ đề trò chuyện thông thường, không liên quan trực tiếp đến du lịch Việt Nam, chẳng hạn như chào hỏi, câu hỏi cá nhân, câu chuyện cười.
    
    Quy tắc:
    1. Nếu câu hỏi KHÔNG phải là small talk (liên quan đến du lịch, ẩm thực, địa điểm...) -> Trả về đúng chữ: "no".
    2. Nếu câu hỏi là small talk -> Không trả lời câu hỏi mà hãy giới thiệu về chatbot tư vấn du lịch Việt Nam một cách ngắn gọn, cuốn hút bằng ngôn ngữ: {language}.

    ###Ví dụ:
    User query: "Chào bạn, hôm nay thế nào?"
    Response: "Cảm ơn bạn đã quan tâm! Mình là chatbot tư vấn du lịch Việt Nam, sẵn sàng hỗ trợ bạn khám phá các điểm đến tuyệt đẹp. Hãy hỏi mình bất cứ điều gì liên quan đến du lịch nhé!"
    
    User query: "Ở đó có món gì ngon?"
    Response: "no"
    
    User query: "Hà Nội có món ăn nào ngon nhất?"
    Response: "no"
    
    User query: "Cảm ơn bạn"
    Response: "Cảm ơn bạn đã ghé thăm! Mình là chatbot tư vấn du lịch Việt Nam, luôn sẵn sàng giúp bạn khám phá các điểm đến tuyệt vời, ẩm thực phong phú và nhiều hoạt động thú vị. Hãy hỏi mình bất cứ điều gì liên quan đến du lịch nhé!"

    ###Dựa trên câu hỏi từ người dùng, hãy thực hiện đúng yêu cầu. 
    Câu hỏi từ người dùng: {user_input}
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = completion.choices[0].message.content.strip()
        # Logic check để đảm bảo trả về "no" đúng định dạng
        if "no" in answer.lower() and len(answer) < 10:
            return "no"
        return answer
    except Exception:
        return "no"

def rewrite_question(history):
    """
    Viết lại câu hỏi dựa trên lịch sử hội thoại (Chỉ nhận 1 tham số history).
    Logic: Lấy câu cuối cùng làm câu hỏi hiện tại, các câu trước đó làm ngữ cảnh.
    """
    # 1. Kiểm tra an toàn
    if not history:
        return ""
    
    # 2. Tách câu hỏi hiện tại và lịch sử
    current_question = history[-1]['content'] # Câu cuối cùng là câu hỏi mới
    
    # Lấy 6 câu trước đó làm ngữ cảnh (loại trừ câu cuối)
    prev_turns = history[:-1][-6:] 
    print(prev_turns)
    # Nếu không có lịch sử trước đó thì không cần viết lại (trả về câu gốc)
    if not prev_turns:
        return current_question

    text_history = "\n".join([f"{m['role']}: {m['content']}" for m in prev_turns])
    # print("text_history ", text_history)
    # 3. Prompt Tối ưu (Few-Shot)
    prompt = f"""
    ### Vai trò:
    Bạn là chuyên gia "Query Rewriting". Nhiệm vụ là viết lại [Câu hỏi hiện tại] dựa trên [Lịch sử hội thoại] để tạo thành câu hỏi độc lập (Standalone Question).

    ### Quy tắc BẮT BUỘC:
    1. Thay thế đại từ (nó, đó, ở đây...) bằng danh từ cụ thể trong lịch sử.
    2. Bổ sung chủ ngữ/vị ngữ nếu câu hỏi bị cụt lủn dựa trên ngữ cảnh trước đó.
    3. Nếu câu hỏi đã rõ ràng hoặc ĐỔI CHỦ ĐỀ MỚI -> Giữ nguyên câu hỏi gốc.
    4. KHÔNG trả lời câu hỏi, chỉ viết lại.
    5. Giữ nguyên ngôn ngữ Tiếng Việt.

    ### Ví dụ mẫu (Học theo cách xử lý này):
    
    Lịch sử: 
    user: Vịnh Hạ Long ở đâu?
    assistant: Ở Quảng Ninh.
    Câu hiện tại: Vé ở đó bao nhiêu?
    -> Output: Vé tham quan Vịnh Hạ Long bao nhiêu tiền?

    Lịch sử:
    user: Món ngon Hà Nội?
    assistant: Phở, bún chả.
    Câu hiện tại: Sài Gòn có gì vui?
    -> Output: Sài Gòn có gì vui? (Giữ nguyên vì đổi chủ đề)

    ### Input thực tế:
    [Lịch sử hội thoại]:
    {text_history}

    [Câu hỏi hiện tại]:
    {current_question}

    ### Output (Chỉ trả về câu hỏi đã viết lại):
    """

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, # Giảm nhiệt độ để model tập trung vào tính chính xác
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        print(f"Lỗi rewrite: {e}")
        return current_question # Fallback về câu gốc nếu lỗi

def chroma_retrieve_formatted(query, topk = 10):
    """
    Lấy dữ liệu từ Chroma và format chuẩn cho smooth_contexts
    """
    # seg_query = tokenize(query)
    # print('seg_query', seg_query)
    # q_emb = EMB_MODEL.encode([seg_query]).tolist()
    q_emb = EMB_MODEL.encode([query]).tolist()
    result = collection.query(
        query_embeddings=q_emb,
        n_results=topk,
        include=["documents", "metadatas", "distances"]
    )
    
    formatted_contexts = []
    if result["documents"]:
        for i in range(len(result["documents"][0])):
            meta = result["metadatas"][0][i]
            dist = result["distances"][0][i]  # Cosine Distance
            
            # công thức chuyển nó thành Cosine Similarity
            score = 1 - dist

            formatted_contexts.append({
                "doc_id": int(meta["doc_id"]),     
                "title": meta.get("title", ""),
                "passage": result["documents"][0][i],
                "score": score,             
            })
    # print(formatted_contexts)        
    return formatted_contexts

def get_prompt(question, contexts, language):
    """
    Tạo prompt cuối cùng gửi cho LLM dựa trên Template
    """
    if not contexts:
        input_str = "Không tìm thấy dữ liệu liên quan."
    else:
        # Ghép các ngữ cảnh
        context_list = [f"Context [{i+1}]: {c['passage']}" for i, c in enumerate(contexts)]
        input_str = "\n\n".join(context_list)
        input_str = f"\n\n{input_str}\n\n"
    print(f"input_str: {input_str}")
    # Chèn dữ liệu vào mẫu prompt
    prompt = PROMPT_TEMPLATE.format(
        input=input_str,
        question=question, 
        language=language
    )
    return prompt

def chatbot(history, language="vi"):
    """
    RAG pipeline
    """
    # 1. Lấy câu gốc để check small talk và làm ngữ cảnh
    # Copy để đảm bảo không sửa nhầm, dù list slicing trả về copy nhưng cẩn thận vẫn hơn
    original_q = history[-1]['content'] 
    
    # 2. Check Small Talk (Dùng câu GỐC)
    st = classify_small_talk(original_q, language)
    if st != "no":
        return st # Trả về luôn nếu là small talk

    # 3. Query Rewriting
    try:
        # Hàm này dùng history để hiểu ngữ cảnh, trả về câu hỏi rõ nghĩa
        rewritten_q = rewrite_question(history) 
        print(f"Rewritten Query: {rewritten_q}")
    except Exception as e:
        print(f"Warning: rewrite_question failed: {e}")
        rewritten_q = original_q # Fallback về câu gốc nếu lỗi
    
    
    # 4. Retrieve (Dùng câu ĐÃ VIẾT LẠI)
    raw_contexts = chroma_retrieve_formatted(rewritten_q, topk=10)
    
    # in ra title và doc_id của các chunk được lấy
    print(f"\n--- Retrieved {len(raw_contexts)} chunks ---")
    for idx, ctx in enumerate(raw_contexts, 1):
        word_count = len(ctx['passage'].split())
        print(f"  [{idx}] Title: {ctx['title']} | doc_id: {ctx['doc_id']} | score: {ctx['score']:.4f} | words: {word_count}")

    
    # 5. Smooth Contexts
    if raw_contexts:
        final_contexts = smooth_contexts(raw_contexts, META_CORPUS)
    else:
        final_contexts = []
    # in ra title và doc_id của các chunk được lấy
    print(f"\n--- Smooth Contexts {len(final_contexts)} chunks ---")
    for idx, ctx in enumerate(final_contexts, 1):
        word_count = len(ctx['passage'].split())
        print(f"  [{idx}] Title: {ctx['title']} | doc_id: {ctx['doc_id']} | score: {ctx['score']:.4f} | len: {word_count}")
    # print(f"final_contexts: {final_contexts}")
    # 6. Build Prompt 
    prompt = get_prompt(rewritten_q, final_contexts, language)
    
    # 7. Generate Answer
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = res.choices[0].message.content.strip()
        return answer
    except Exception as e:
        print(f"Generation error: {e}")
        return "Xin lỗi, đã xảy ra lỗi khi tạo câu trả lời."
# ========================= VÒNG LẶP CHÍNH =========================
def main():
    print("\n" + "="*50)
    print("Chatbot Du lịch Việt Nam (RAG Complete Version)")
    print("="*50 + "\n")
    history = []
    current_lang = "vi" 
    while True:
        try:
            query = input("Bạn: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "bye", "e", "thoát"]:
                print("Tạm biệt! Hẹn gặp lại.")
                break
            #  
            history.append({"role": "user", "content": query})

            #  
            reply = chatbot(history, language=current_lang)

            print(f"Bot: {reply}\n")
            history.append({"role": "assistant", "content": reply})
            # print(history)
        except KeyboardInterrupt:
            print("\nĐã dừng chương trình.")
            break
        except Exception as e:
            print(f"Lỗi hệ thống: {e}")
if __name__ == "__main__":
    main()
    
    
    