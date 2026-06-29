"""
================================================================================
TOOL CALLING AGENT - Du lịch Việt Nam
================================================================================
Framework hiện đại sử dụng LangChain @tool decorator để tạo một Agent hoàn chỉnh
với nhiều công cụ: RAG (du lịch), Thời tiết, Google Maps.

Cách sử dụng:
    from agent_with_tools import run_travel_agent
    run_travel_agent("Cho mình vị trí chính xác của Hồ Gươm trên Google Maps")
================================================================================
"""

import os
import json
import pickle
from typing import Any, Dict, List
from datetime import datetime
from pathlib import Path
import requests

# ========================= LANGCHAIN IMPORTS =========================
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# ========================= PROJECT IMPORTS =========================
from openai import OpenAI
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from smoonth_context import smooth_contexts
from data_loader import load_meta_corpus

# ========================= LOAD ENVIRONMENT =========================
_CURRENT_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=_CURRENT_DIR / ".env")
load_dotenv()

# ========================= CẤU HÌNH CONSTANTS =========================
CORPUS_PATH = r"D:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\AIP491_G9\Data\processed\data_final_train_v1\data_final_sort_v1_fisrt_se.jsonl"
DB_PATH = r"d:\ARTIFICIAL_INTELLIGENCE\KY_9\AIP491\data_store"
MODEL_PATH = r"duongluuba/AIP491_G9_Vietnam_tourism_data_bkai-foundation-fine-tuned-v1"

# ========================= KHỞI TẠO TÀI NGUYÊN GLOBAL =========================
print(">> [AGENT] Khởi tạo Embedding Model...")
EMB_MODEL = SentenceTransformer(MODEL_PATH)

print(">> [AGENT] Kết nối ChromaDB...")
chroma_client = PersistentClient(path=DB_PATH)
collection = chroma_client.get_collection(name="aip491_v1")

print(">> [AGENT] Tải Meta Corpus...")
META_CORPUS = load_meta_corpus(CORPUS_PATH)

# Global list to track which tools were used during a single agent run
USED_TOOLS: List[str] = []

# ========================= KHỞI TẠO LLM =========================
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7
)


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                          TOOL 1: RAG RETRIEVAL                            ║
# ╚════════════════════════════════════════════════════════════════════════════╝

@tool
def retrieve_tourism_info(query: str, language: str = "vi") -> str:
    """
    Truy xuất thông tin du lịch Việt Nam từ RAG database.
    
    Args:
        query: Câu hỏi về du lịch Việt Nam (tiếng Việt hoặc tiếng Anh)
        language: Ngôn ngữ trả lời ('vi' hoặc 'en')
    
    Returns:
        Thông tin du lịch từ database hoặc thông báo không tìm thấy
        
    Examples:
        retrieve_tourism_info("Hà Nội có những di tích nào nổi tiếng?")
        retrieve_tourism_info("What are the beaches in Da Nang?", language="en")
    """
    # Log tool usage
    USED_TOOLS.append("retrieve_tourism_info")
    try:
        # Embed query
        query_embedding = EMB_MODEL.encode(query, convert_to_tensor=False).tolist()
        
        # Truy vấn ChromaDB
        search_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=["documents", "distances", "metadatas"]
        )
        
        if not search_results["documents"] or not search_results["documents"][0]:
            return f"[RAG] Không tìm thấy thông tin liên quan đến: {query}"
        
        # Trích xuất và xử lý kết quả
        contexts = search_results["documents"][0]
        distances = search_results["distances"][0]
        metadatas = search_results["metadatas"][0]
        
        # Smooth context cho ngữ cảnh mịn mà hơn
        smoothed_contexts = smooth_contexts(contexts, META_CORPUS)
        
        # Format kết quả
        result_text = "\n".join(smoothed_contexts[:3])  # Top 3 kết quả
        
        return f"[RAG] Kết quả tìm kiếm:\n{result_text}"
        
    except Exception as e:
        return f"[RAG] Lỗi truy xuất: {str(e)}"


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                      TOOL 2: WEATHER INFORMATION                          ║
# ╚════════════════════════════════════════════════════════════════════════════╝

@tool
def get_weather_info(location: str, language: str = "vi") -> str:
    """
    Lấy thông tin thời tiết hiện tại của một địa điểm du lịch.
    
    Args:
        location: Tên địa điểm du lịch (vd: "Hà Nội", "Sapa", "Hạ Long")
        language: Ngôn ngữ ('vi' hoặc 'en')
    
    Returns:
        Thông tin thời tiết hoặc thông báo lỗi
        
    Examples:
        get_weather_info("Hà Nội")
        get_weather_info("Da Nang", language="en")
    """
    # Log tool usage
    USED_TOOLS.append("get_weather_info")

    try:
        # Tìm tọa độ thông qua Open-Meteo Geocoding API (miễn phí, không cần key)
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {
            "name": location.strip(),
            "count": 1,
            "language": language,
            "format": "json"
        }
        
        geo_response = requests.get(geo_url, params=geo_params, timeout=5)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        if "results" not in geo_data or not geo_data["results"]:
            return f"⚠️ [WEATHER] Không thể tìm thấy hoặc không hỗ trợ địa điểm: '{location}'. Vui lòng thử lại với tên tỉnh/thành phố rõ ràng hơn."
            
        city_info = geo_data["results"][0]
        lat = city_info["latitude"]
        lon = city_info["longitude"]
        city_name = city_info.get("name", location)
        
        # Sử dụng Open-Meteo API để lấy mốc thời tiết (miễn phí, không cần key)
        url = f"https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m",
            "timezone": "Asia/Ho_Chi_Minh"
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        current = data["current"]
        
        weather_code_map = {
            0: "☀️ Nắng quang",
            1: "🌤️ Hầu hết là nắng",
            2: "⛅ Một phần có mây",
            3: "☁️ Mây phủ kín",
            45: "🌫️ Sương mù",
            51: "🌦️ Mưa nhẹ",
            61: "🌧️ Mưa vừa",
            80: "⛈️ Mưa to",
        }
        
        weather_desc = weather_code_map.get(current["weather_code"], "Thời tiết bình thường")
        
        if language == "vi":
            result = f"""
🌤️ **THỜI TIẾT - {city_name.upper()}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌡️ Nhiệt độ: {current['temperature_2m']}°C
💨 Tốc độ gió: {current['wind_speed_10m']} km/h
💧 Độ ẩm: {current['relative_humidity_2m']}%
☁️ Điều kiện: {weather_desc}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """.strip()
        else:
            result = f"""
🌤️ **WEATHER - {city_name.upper()}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌡️ Temperature: {current['temperature_2m']}°C
💨 Wind Speed: {current['wind_speed_10m']} km/h
💧 Humidity: {current['relative_humidity_2m']}%
☁️ Conditions: {weather_desc}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """.strip()
        
        return result
        
    except requests.RequestException as e:
        return f"⚠️ [WEATHER] Không thể lấy dữ liệu thời tiết: {str(e)}"
    except Exception as e:
        return f"⚠️ [WEATHER] Lỗi xử lý: {str(e)}"


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                   TOOL 3: GOOGLE MAPS PRECISE LOCATION                    ║
# ╚════════════════════════════════════════════════════════════════════════════╝

@tool
def get_precise_location(destination: str, language: str = "vi") -> str:
    """
    Lấy vị trí chính xác của một địa điểm bằng Google Maps Geocoding API.
    
    Args:
        destination: Tên địa điểm cần tìm (ví dụ: "Hồ Gươm", "Bà Nà Hills")
        language: Ngôn ngữ ('vi' hoặc 'en')
    
    Returns:
        Địa chỉ chuẩn hoá, toạ độ và link Google Maps
        
    Examples:
        get_precise_location("Hồ Gươm")
        get_precise_location("Golden Bridge Da Nang", language="en")
    """

    # Log tool usage
    USED_TOOLS.append("get_precise_location")
    api_key = (
        os.getenv("GOOGLE_MAPS_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("GMAPS_API_KEY")
    )

    if not api_key:
        if language == "vi":
            return (
                "⚠️ [LOCATION] Chưa cấu hình API key Google Maps. "
                "Hãy thêm GOOGLE_MAPS_API_KEY vào Chatbot/.env và bật Geocoding API."
            )
        return (
            "⚠️ [LOCATION] Missing Google Maps API key. "
            "Please set GOOGLE_MAPS_API_KEY in Chatbot/.env and enable Geocoding API."
        )

    try:
        if not destination or not destination.strip():
            if language == "vi":
                return "⚠️ [LOCATION] Vui lòng cung cấp tên địa điểm cần tìm."
            return "⚠️ [LOCATION] Please provide a destination name."

        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": destination.strip(),
            "key": api_key,
            "language": "vi" if language == "vi" else "en",
            "region": "vn",
        }

        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()

        status = data.get("status", "UNKNOWN")
        results = data.get("results", [])
        error_message = data.get("error_message", "")

        if status == "ZERO_RESULTS":
            if language == "vi":
                return f"⚠️ [LOCATION] Không tìm thấy địa điểm '{destination}' trên Google Maps."
            return f"⚠️ [LOCATION] Could not find '{destination}' on Google Maps."
        if status != "OK" or not results:
            error_suffix = f" - {error_message}" if error_message else ""
            if language == "vi":
                return (
                    f"⚠️ [LOCATION] Google Maps API trả về trạng thái {status}{error_suffix}. "
                    "Vui lòng kiểm tra API key, billing và Geocoding API."
                )
            return (
                f"⚠️ [LOCATION] Google Maps API returned status {status}{error_suffix}. "
                "Please check API key, billing, and Geocoding API."
            )

        best_match = results[0]
        formatted_address = best_match.get("formatted_address", "N/A")
        geometry = best_match.get("geometry", {})
        coordinates = geometry.get("location", {})
        lat = coordinates.get("lat")
        lng = coordinates.get("lng")
        location_type = geometry.get("location_type", "UNKNOWN")
        place_id = best_match.get("place_id", "N/A")

        if lat is None or lng is None:
            if language == "vi":
                return f"⚠️ [LOCATION] Không lấy được toạ độ chính xác cho '{destination}'."
            return f"⚠️ [LOCATION] Unable to retrieve exact coordinates for '{destination}'."

        maps_pin_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        maps_place_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"

        if language == "vi":
            result = f"""
📍 **VỊ TRÍ CHÍNH XÁC - GOOGLE MAPS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Địa điểm tìm kiếm: {destination}
• Địa chỉ chuẩn hoá: {formatted_address}
• Tọa độ: {lat}, {lng}
• Mức chính xác geocoding: {location_type}
• Place ID: {place_id}
• Mở bản đồ (tọa độ): {maps_pin_url}
• Mở bản đồ (place_id): {maps_place_url}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                """.strip()
        else:
            result = f"""
📍 **PRECISE LOCATION - GOOGLE MAPS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Search query: {destination}
• Formatted address: {formatted_address}
• Coordinates: {lat}, {lng}
• Geocoding accuracy: {location_type}
• Place ID: {place_id}
• Open map (coordinates): {maps_pin_url}
• Open map (place_id): {maps_place_url}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                """.strip()
        
        return result
        
    except requests.RequestException as e:
        if language == "vi":
            return f"⚠️ [LOCATION] Không thể gọi Google Maps API: {str(e)}"
        return f"⚠️ [LOCATION] Failed to call Google Maps API: {str(e)}"
    except Exception as e:
        if language == "vi":
            return f"⚠️ [LOCATION] Lỗi xử lý dữ liệu vị trí: {str(e)}"
        return f"⚠️ [LOCATION] Location parsing error: {str(e)}"


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                        AGENT SETUP & EXECUTOR                             ║
# ╚════════════════════════════════════════════════════════════════════════════╝

def create_travel_agent():
    """
    Tạo Tool Calling Agent với các công cụ đã định nghĩa.
    """
    
    # Định nghĩa danh sách công cụ
    tools = [
        retrieve_tourism_info,
        get_weather_info,
        get_precise_location
    ]
    
    # Tạo system prompt cho agent
    system_prompt = """
Bạn là một trợ lý du lịch thông minh, am hiểu sâu sắc về du lịch Việt Nam.
Nhiệm vụ của bạn là giúp người dùng lập kế hoạch du lịch bằng cách sử dụng các công cụ có sẵn.

**Các công cụ của bạn:**
1. **retrieve_tourism_info**: Truy xuất thông tin du lịch từ database
2. **get_weather_info**: Lấy thông tin thời tiết của địa điểm
3. **get_precise_location**: Lấy vị trí chính xác địa điểm bằng Google Maps API

**Hướng dẫn sử dụng:**
- Khi người dùng hỏi về du lịch, hãy sử dụng retrieve_tourism_info để lấy dữ liệu.
- Khi người dùng hỏi về thời tiết, hãy sử dụng get_weather_info.
- Khi người dùng hỏi địa chỉ, tọa độ hoặc vị trí chính xác của điểm đến, hãy sử dụng get_precise_location.
- Kết hợp nhiều công cụ nếu cần thiết để trả lời toàn diện.
- Luôn thân thiện, nhiệt tình và cung cấp thông tin hữu ích.

**Quy tắc trả lời:**
- Trả lời bằng tiếng Việt trừ khi người dùng yêu cầu khác.
- Sử dụng emoji và formatting để làm cho câu trả lời dễ đọc hơn.
- Luôn kết thúc bằng lời khuyên hoặc gợi ý tiếp theo.
    """
    
    # Tạo prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Tạo agent
    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    # Tạo executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,  # Set thành True để debug
        max_iterations=10,
        handle_parsing_errors=True
    )
    
    return agent_executor


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                      MAIN INTERACTION FUNCTION                            ║
# ╚════════════════════════════════════════════════════════════════════════════╝

def run_travel_agent(user_query: str, language: str = "vi") -> str:
    """
    Chạy travel agent với câu hỏi từ người dùng.
    
    Args:
        user_query: Câu hỏi của người dùng
        language: Ngôn ngữ ('vi' hoặc 'en')
    
    Returns:
        Câu trả lời từ agent
    """
    
    try:
        # Khởi tạo agent nếu chưa có
        if not hasattr(run_travel_agent, "_agent"):
            print("🤖 Khởi tạo Agent...")
            run_travel_agent._agent = create_travel_agent()
        
        agent_executor = run_travel_agent._agent
        
        # Chạy agent
        print(f"\n👤 Người dùng: {user_query}")
        print("⏳ Agent đang xử lý...\n")
        
        response = agent_executor.invoke({
            "input": user_query,
            "language": language
        })
        # In ra danh sách công cụ đã sử dụng trong lần trả lời này
        print(f">> [TOOLS USED]: {', '.join(USED_TOOLS) if USED_TOOLS else 'None'}")
        # Xóa danh sách để chuẩn bị cho lần gọi tiếp theo
        USED_TOOLS.clear()

        return response["output"]
        
    except Exception as e:
        return f"❌ Lỗi: {str(e)}\n\nVui lòng thử lại hoặc liên hệ hỗ trợ."


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                           INTERACTIVE LOOP                                ║
# ╚════════════════════════════════════════════════════════════════════════════╝

def main():
    """
    Hàm main chạy chatbot du lịch tương tác.
    """
    print("\n" + "="*70)
    print("🌴 TRAVEL AGENT - Tool Calling Framework")
    print("="*70)
    print("Công cụ: RAG Database | Thời tiết | Vị trí Google Maps")
    print("Gõ 'exit' hoặc 'thoát' để kết thúc.\n")
    
    history = []
    
    while True:
        try:
            user_input = input("📍 Bạn: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit", "thoát", "e"]:
                print("\n👋 Cảm ơn bạn đã sử dụng Travel Agent. Hẹn gặp lại!")
                break
            
            # Chạy agent
            response = run_travel_agent(user_input, language="vi")
            print(f"\n🤖 Agent: {response}\n")
            
            # Lưu lịch sử
            history.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })
            history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
        except KeyboardInterrupt:
            print("\n\nĐã dừng chương trình.")
            break
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
            print("Vui lòng thử lại.\n")


if __name__ == "__main__":
    main()
