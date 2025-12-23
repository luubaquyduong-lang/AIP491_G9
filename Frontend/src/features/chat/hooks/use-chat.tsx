// ===== CUSTOM HOOK: USE CHAT =====
// File: use-chat.tsx
// Mô tả: React Context và Hook quản lý toàn bộ state của chatbot
//        Bao gồm: messages, input, history, theme, language, sidebar...
//        Cung cấp các hàm xử lý: gửi tin nhắn, tạo chat mới, đổi ngôn ngữ...

"use client";

import { Chat, Message, Prisma } from "@prisma/client";
import { MessageClient, ChatClient } from "../types/message";

import React, {
  createContext,
  useContext,
  useState,
  ReactNode,
  FormEvent,
  useEffect,
} from "react";

// ===== TYPE DEFINITIONS =====

/**
 * WithMessagesChat - Kiểu dữ liệu Chat kèm theo danh sách messages
 * Sử dụng Prisma's Payload type để include messages relation
 */
type WithMessagesChat = Prisma.ChatGetPayload<{ include: { messages: true } }>;

/**
 * ChatContextType - Interface định nghĩa toàn bộ state và methods của chat context
 * 
 * State management:
 * - messages: Danh sách tin nhắn trong cuộc chat hiện tại
 * - input: Giá trị input box người dùng đang gõ
 * - history: Danh sách tất cả cuộc chat của user
 * - selectedChat: ID của chat đang được chọn
 * - sidebarOpen: Trạng thái đóng/mở sidebar
 * - isTyping: Bot đang typing hay không
 * - theme: Chế độ sáng/tối
 * - language: Ngôn ngữ hiện tại (Tiếng Việt/English)
 * 
 * Methods:
 * - handleSubmit: Xử lý gửi tin nhắn
 * - startNewChat: Tạo cuộc chat mới
 * - toggleTheme: Chuyển đổi theme
 * - toggleSidebar: Đóng/mở sidebar
 * - handleLanguageChange: Thay đổi ngôn ngữ
 * - handleSuggestionClick: Xử lý click vào câu hỏi gợi ý
 */
interface ChatContextType {
  messages: MessageClient[];
  setMessages: React.Dispatch<React.SetStateAction<MessageClient[]>>;
  input: string;
  setInput: React.Dispatch<React.SetStateAction<string>>;
  history: ChatClient[];
  setHistory: React.Dispatch<React.SetStateAction<ChatClient[]>>;
  selectedChat: string | null;
  setSelectedChat: React.Dispatch<React.SetStateAction<string | null>>;
  sidebarOpen: true | false;
  setSidebarOpen: React.Dispatch<React.SetStateAction<true | false>>;
  isTyping: true | false;
  setIsTyping: React.Dispatch<React.SetStateAction<true | false>>;
  theme: "light" | "dark";
  language: "Tiếng Việt" | "English";
  setLanguage: React.Dispatch<React.SetStateAction<"Tiếng Việt" | "English">>;
  handleLanguageChange: (event: React.ChangeEvent<HTMLSelectElement>) => void;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  startNewChat: () => void;
  handleSubmit: (event: FormEvent) => Promise<void>;
  handleSuggestionClick: (question: string) => void;
}

// Tạo Context
const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider = ({
  chat,
  children,
}: {
  chat?: WithMessagesChat;
  children: ReactNode;
}) => {
  // Danh sách message trong cuộc trò chuyện hiện tại
  const [messages, setMessages] = useState<MessageClient[]>([]);

  // Nội dung người dùng đang nhập
  const [input, setInput] = useState("");

  // Lịch sử các cuộc chat đã lưu
  const [history, setHistory] = useState<ChatClient[]>([]);

  // ID của cuộc chat đang được mở
  const [selectedChat, setSelectedChat] = useState<string | null>(null);

  // Trạng thái mở/đóng sidebar trái
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Trạng thái "bot đang gõ"
  const [isTyping, setIsTyping] = useState(false);

  // Ngôn ngữ UI
  const [language, setLanguage] = useState<"Tiếng Việt" | "English">("Tiếng Việt");

  // Theme UI (dark / light), đồng thời lưu vào localStorage
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    if (typeof window !== "undefined") {
      const savedTheme = localStorage.getItem("theme");
      return savedTheme ? (savedTheme as "light" | "dark") : "light";
    }
    return "light";
  });

  // Load dữ liệu cuộc chat đang chọn (nếu có)
  useEffect(() => {
    if (chat) {
      setMessages(chat.messages);
      setSelectedChat(chat.id);
    }
  }, [chat]);

  // Toggle sáng/tối và lưu vào localStorage
  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);

    if (typeof window !== "undefined") {
      localStorage.setItem("theme", newTheme);
    }
  };

  // Toggle sidebar
  const toggleSidebar = () => {
    setSidebarOpen((prev) => !prev);
  };

  // Tạo một cuộc trò chuyện mới
  const startNewChat = () => {
    setSelectedChat(null);
    setMessages([]);
  };

  // Gửi tin nhắn khi người dùng submit form
  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!input.trim()) return;

    // Tạo message user
    const newMessage: MessageClient = { role: "user", content: input };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setInput("");
    setIsTyping(true);

    // Nếu có chatId → gửi vào chat cũ, nếu không → tạo chat mới
    const url = selectedChat
      ? `/api/messages?chatId=${selectedChat}`
      : `/api/messages`;

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: newMessage, language }),
      });

      if (!response.ok) throw new Error("Failed to fetch from API");

      const { content, chatId } = await response.json();

      // Tin nhắn bot trả về
      const botMessage: MessageClient = { role: "assistant", content };

      setIsTyping(false);
      setMessages((prevMessages) => [...prevMessages, botMessage]);

      // Cập nhật selectedChat nếu đây là chat mới
      if (!selectedChat && chatId) {
        setSelectedChat(chatId);
      }

      // Cập nhật lịch sử chat
      setHistory((prevHistory) => {
        const updatedHistory = prevHistory.map((chat) =>
          chat.id === chatId ? { ...chat } : chat,
        );

        // Nếu cuộc chat chưa tồn tại → thêm vào history
        if (!prevHistory.find((chat) => chat.id === chatId)) {
          updatedHistory.push({
            id: chatId,
            title: newMessage.content,
            messages: [newMessage, botMessage],
          } as ChatClient);
        }
        return updatedHistory;
      });
    } catch (error) {
      console.error("Error occurred:", error);
    }
  };

  // Khi người dùng click vào câu hỏi gợi ý
  const handleSuggestionClick = async (question: string) => {
    if (!question.trim()) return;

    const newMessage: MessageClient = { role: "user", content: question };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setInput("");
    setIsTyping(true);

    try {
      const response = await fetch("/api/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: newMessage, language }),
      });

      if (!response.ok) throw new Error("Failed to fetch from API");

      const { content, chatId } = await response.json();
      const botMessage: MessageClient = { role: "assistant", content };

      setIsTyping(false);
      setMessages((prevMessages) => [...prevMessages, botMessage]);

      // Cập nhật selectedChat nếu đây là chat mới
      if (!selectedChat && chatId) {
        setSelectedChat(chatId);
      }

      // Cập nhật lịch sử chat
      setHistory((prevHistory) => {
        const updatedHistory = prevHistory.map((chat) =>
          chat.id == chatId ? { ...chat } : chat,
        );

        updatedHistory.push({
          id: chatId,
          title: newMessage.content,
          messages: [newMessage, botMessage],
        } as ChatClient);

        return updatedHistory;
      });
    } catch (error) {
      console.error("Error occurred:", error);
    }
  };

  // Xử lý đổi ngôn ngữ UI
  const handleLanguageChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedLanguage = event.target.value as "Tiếng Việt" | "English";
    setLanguage(selectedLanguage);
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        setMessages,
        input,
        setInput,
        history,
        setHistory,
        selectedChat,
        setSelectedChat,
        theme,
        toggleTheme,
        startNewChat,
        handleSuggestionClick,
        handleSubmit,
        toggleSidebar,
        sidebarOpen,
        setSidebarOpen,
        isTyping,
        setIsTyping,
        language,
        setLanguage,
        handleLanguageChange,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

// Hook để dùng ChatContext
export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
};
