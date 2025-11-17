from ollama import chat
import os
from retriever import Retriever
from smooth_context import smooth_contexts
from data_loader import load_meta_corpus
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

# Nạp biến môi trường từ file .env (chứa API key, thông tin cấu hình)
load_dotenv()

# Lấy API key của OpenAI từ biến môi trường
api_key = os.getenv("OPENAI_API_KEY")
# Khởi tạo client để kết nối với API của OpenAI
client = OpenAI(api_key=api_key)

# Mẫu prompt hướng dẫn cách GPT trả lời câu hỏi dựa trên dữ liệu RAG
prompt_template = (
    """###Yêu cầu: Bạn là một trợ lý du lịch thông minh, chuyên cung cấp câu trả lời dựa trên thông tin được truy xuất từ hệ thống về du lịch Việt Nam. Khi nhận được dữ liệu truy xuất từ RAG, hãy:  

    1. Phân tích dữ liệu để trả lời đúng trọng tâm câu hỏi của người dùng. Chỉ trả lời dựa trên dữ liệu được cung cấp, không suy đoán hoặc tạo ra thông tin mới.
    2. Tóm tắt thông tin một cách rõ ràng, ngắn gọn nhưng vẫn đầy đủ ý nghĩa.  
    3. Trả lời với giọng điệu thân thiện và dễ tiếp cận.  
    4. Nếu dữ liệu truy xuất không có thông tin liên quan đến câu hỏi hoặc không có dữ liệu nào được truy xuất, hãy trả lời: "Xin lỗi, tôi không có thông tin phù hợp để trả lời câu hỏi này."  
    5. Nếu câu hỏi không liên quan đến chủ đề du lịch Việt Nam (out domain) hãy giới thiệu lịch sự về lĩnh vực của mình.
    6. Trả lời câu hỏi bằng ngôn ngữ: {language}

    ###Dựa vào một số ngữ cảnh truy xuất được dưới đây nếu bạn thấy nó có liên quan đến câu hỏi thì trả lời câu hỏi ở cuối. {input}
    ###Câu hỏi từ người dùng: {question}
    ###Nếu thấy ngữ cảnh có liên quan đến câu hỏi hãy trả lời chi tiết và đầy đủ dựa trên ngữ cảnh."""
)

# Hàm tạo prompt hoàn chỉnh cho mô hình GPT dựa trên ngữ cảnh và câu hỏi người dùng
def get_prompt(question, contexts, language):
    # Ghép các ngữ cảnh (context) thành chuỗi hiển thị đẹp
    context = "\n\n".join([f"Context [{i+1}]: {x['passage']}" for i, x in enumerate(contexts)])
    input = f"\n\n{context}\n\n"
    # Chèn dữ liệu vào mẫu prompt
    prompt = prompt_template.format(
        input=input,
        question=question, 
        language=language
    )
    return prompt

# Hàm phân loại xem câu hỏi có phải là small talk (trò chuyện phiếm) hay không
def classify_small_talk(input_sentence, language):
    prompt = f"""
    ###Yêu cầu: Bạn là một trợ lý hữu ích được thiết kế để phân loại các câu hỏi của người dùng trong ngữ cảnh của một chatbot du lịch Việt Nam. Nhiệm vụ của bạn là xác định liệu câu hỏi của người dùng có phải là "small talk" hay không"
    ###"Small talk" đề cập đến những chủ đề trò chuyện thông thường, không liên quan trực tiếp đến du lịch Việt Nam, chẳng hạn như chào hỏi, câu hỏi cá nhân, câu chuyện cười.
    Nếu câu hỏi không phải là small talk và liên quan đến du lịch, ẩm thực, điểm đến, hoạt động, bạn PHẢI có từ "no" trong câu trả lời và trả về "no."
    Nếu câu hỏi là small talk: Không trả lời câu hỏi mà hãy giới thiệu về chatbot tư vấn du lịch Việt Nam một cách ngắn gọn với giọng điệu cuốn hút bằng ngôn ngữ: {language}.

    ###Ví dụ:
    User query: "Chào bạn, hôm nay thế nào?"
    Response: "Cảm ơn bạn đã quan tâm! Mình là chatbot tư vấn du lịch Việt Nam, sẵn sàng hỗ trợ bạn khám phá các điểm đến tuyệt đẹp, món ăn hấp dẫn và nhiều hoạt động thú vị. Hãy hỏi mình bất cứ điều gì liên quan đến du lịch nhé! 😊"
    User query: "Ở đó có món gì ngon?"
    Response: "no"
    User query: "Bạn có thích đi du lịch không?"
    Response: "Mình là chatbot tư vấn du lịch Việt Nam, luôn sẵn sàng hỗ trợ bạn khám phá các điểm đến tuyệt vời, ẩm thực hấp dẫn và các hoạt động thú vị. Hãy hỏi tôi bất kỳ điều gì liên quan đến du lịch nhé! 😊"
    User query: "Hà Nội có món ăn nào ngon nhất?"
    Response: "no"
    User query: "Các địa điểm du lịch nổi tiếng ở Huế là gì?"
    Response: "no"
    User query: "Cảm ơn bạn"
    Response: "Cảm ơn bạn đã ghé thăm! Mình là chatbot tư vấn du lịch Việt Nam, luôn sẵn sàng giúp bạn khám phá các điểm đến tuyệt vời, ẩm thực phong phú và nhiều hoạt động thú vị. Hãy hỏi mình bất cứ điều gì liên quan đến du lịch nhé!"
    ###Dựa trên câu hỏi từ người dùng, hãy thực hiện đúng yêu cầu. Câu hỏi từ người dùng: {input_sentence}"""

    # Gọi API GPT để phân loại câu hỏi
    completion = client.chat.completions.create(
      model="gpt-4.0-mini",
      messages=[
        {"role": "user", "content": prompt}
      ]
    )

    # Lấy kết quả phân loại
    answer = completion.choices[0].message.content
    return answer.strip().lower()

# Hàm tạo prompt mới dựa trên lịch sử hội thoại
def create_new_prompt(prompt, chat_history, user_query, **kwargs):
    # Gộp prompt ban đầu với lịch sử hội thoại và câu hỏi hiện tại
    new_prompt = f"{prompt} lịch sử cuộc trò chuyện: {chat_history} câu hỏi của người dùng: {user_query}"
    # Thêm các tham số phụ khác (nếu có)
    for key, value in kwargs.items():
        new_prompt += f" {key}: {value}"
    return new_prompt

# Hàm chính điều phối toàn bộ quá trình chatbot
def chatbot(conversation_history: List[Dict[str, str]], language = "vi") -> str:
    # Lấy câu hỏi cuối cùng mà người dùng nhập vào
    user_query = conversation_history[-1]['content']

    # Tải dữ liệu corpus chứa thông tin du lịch đã được lưu
    meta_corpus = load_meta_corpus(r"D:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\AIP491_G9\Data\\processed\data_final_sorted.jsonl")

    # Khởi tạo bộ truy xuất dữ liệu (retriever) dùng BM25 + Bi-encoder
    retriever = Retriever(
        corpus=meta_corpus,
        corpus_emb_path=r"D:\ARTIFICIAL_INTELLIGENCE\\KY_9\AIP491\\Embedding_data\\embeding_by_model_fine_e5.pkl",
        model_name="D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\Model_train\intfloat_multilingual_e5_base_fine_tuning"
    )

    # Gọi hàm phân loại small talk để kiểm tra loại câu hỏi
    result = classify_small_talk(user_query, language)
    print("result classify small talk:", result)

    # Nếu là small talk -> trả về lời giới thiệu ngắn gọn
    if "no" not in result:
        return result

    # Nếu không phải small talk -> xử lý theo pipeline RAG
    elif "no" in result:
        # Prompt yêu cầu GPT chuyển câu hỏi thành dạng độc lập (nếu có tham chiếu)
        prompt = """Dựa trên lịch sử cuộc trò chuyện và câu hỏi mới nhất của người dùng, có thể tham chiếu đến ngữ cảnh trong lịch sử trò chuyện, 
            hãy tạo thành một câu hỏi độc lập có thể hiểu được mà không cần lịch sử cuộc trò chuyện. 
            KHÔNG trả lời câu hỏi, chỉ cần điều chỉnh lại nếu cần, nếu không thì giữ nguyên. 
            Nếu câu hỏi bằng tiếng Anh, sau khi tinh chỉnh, hãy dịch câu hỏi đó sang tiếng Việt."""

        # Tạo prompt mới kết hợp với lịch sử hội thoại
        new_prompt = create_new_prompt(
            prompt=prompt,
            chat_history=conversation_history,
            user_query=user_query,
        )

        # Gọi GPT để tinh chỉnh lại câu hỏi người dùng
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": new_prompt}
            ]
        )

        # Lấy câu hỏi đã tinh chỉnh
        answer = completion.choices[0].message.content
        print("Câu hỏi mới: ", answer)
        question = answer

        # Truy xuất top 10 đoạn văn bản có liên quan nhất từ corpus
        top_passages = retriever.retrieve(question, topk=10)
        print("topK:", top_passages)

        # Làm mượt ngữ cảnh (gộp hoặc lọc bớt phần trùng lặp)
        smoothed_contexts = smooth_contexts(top_passages, meta_corpus)
        print("Smooth context: ", smoothed_contexts)

        # Tạo prompt hoàn chỉnh cho GPT với ngữ cảnh và câu hỏi
        prompt = get_prompt(question, smoothed_contexts, language)
    
        # Gọi GPT để sinh câu trả lời cuối cùng dựa trên ngữ cảnh
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Lấy câu trả lời cuối cùng
        answer = completion.choices[0].message.content
        return answer

    # Trường hợp lỗi không mong muốn
    else:
        print("Unexpected response from the model.")
        return "Xin lỗi, hệ thống không xử lý được."
    
    # Kết thúc hàm chatbot
#   
def main():
    print(" Chatbot du lịch Việt Nam sẵn sàng! (gõ 'exit' để thoát)\n")
    # Tạo lịch sử hội thoại ban đầu
    conversation_history = []
    language = "vi"

    while True:
        user_query = input(" Bạn: ").strip()
        if user_query.lower() in ["exit", "quit", "bye", "thoát","e"]:
            print(" Tạm biệt! Chúc bạn có chuyến đi vui vẻ!")
            break

        # Thêm câu hỏi vào lịch sử
        conversation_history.append({"role": "user", "content": user_query})

        # Gọi chatbot xử lý
        try:
            result = chatbot(conversation_history, language)
            print(f" Chatbot: {result}\n")
            # Lưu phản hồi vào lịch sử hội thoại
            conversation_history.append({"role": "assistant", "content": result})
        except Exception as e:
            print(" Lỗi khi xử lý:", e)
            break


if __name__ == "__main__":
    main()
