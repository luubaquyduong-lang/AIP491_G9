"use client";

import { useRef, useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ThemeSwitch } from "@/components/ui/switch";
import { useChat } from "../hooks/use-chat";
import { UserButton } from "@clerk/nextjs";
import Link from "next/link";
import { TypingIndicator } from "@/components/TypingIndicator";
import {
  FolderIcon,
  PlusCircleIcon,
  SparklesIcon,
} from "@heroicons/react/24/solid";

export const Chat = () => {
  // Hook tùy chỉnh quản lý trạng thái chat
  const {
    theme,
    messages,
    input,
    handleSubmit,
    setInput,
    toggleTheme,
    handleSuggestionClick,
    toggleSidebar,
    sidebarOpen,
    startNewChat,
    isTyping,
    language,
    handleLanguageChange,
  } = useChat();

  // Tham chiếu đến container chứa tin nhắn để tự động scroll cuối
  const chatParent = useRef<HTMLUListElement>(null);

  // Gợi ý câu hỏi ban đầu tùy theo ngôn ngữ
  const faqSuggestions = [
    language === "Tiếng Việt"
      ? "Giới thiệu về thành phố Hà Nội"
      : "Introduction to Ha Noi City.",
    language === "Tiếng Việt"
      ? "Giới thiệu địa điểm du lịch tại thành phố Hồ Chí Minh ?"
      : "Introducing tourist destinations in Ho Chi Minh City ?",
  ];

  // Tự scroll xuống cuối khi danh sách message thay đổi
  useEffect(() => {
    const domNode = chatParent.current;
    if (domNode) {
      domNode.scrollTop = domNode.scrollHeight;
    }
  }, [messages]);

  // Cập nhật input tin nhắn
  const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(event.target.value);
  };

  return (
    <section
      className={`flex flex-col flex-grow ${theme === "light"
        ? "bg-white text-gray-800"
        : "bg-gradient-to-b from-slate-900 to-black text-gray-100"
        }`}
      style={{
        scrollbarColor: theme === "light"
          ? "#ea580c #fef3f2"
          : "#1e293b #0f172a",
        scrollbarWidth: "thin",
      }}
    >
      {/* HEADER */}
      <header className={`p-4 border-b flex justify-between items-center ${theme === "light"
        ? "border-orange-100 bg-gradient-to-r from-orange-50 to-white"
        : "border-slate-700 bg-gradient-to-r from-slate-800 to-slate-900"
        }`}>
        {/* Nút sidebar + New Chat (ẩn khi sidebar đang mở) */}
        {!sidebarOpen && (
          <div className="flex gap-4 items-center">
            {/* Nút mở sidebar */}
            <div className="relative group">
              <Button
                onClick={toggleSidebar}
                className={`p-2 rounded-full transition-all duration-200 shadow-sm ${theme === "light"
                  ? "bg-white hover:bg-orange-500 hover:text-white text-orange-600 border border-orange-200"
                  : "bg-slate-800 hover:bg-slate-600 text-cyan-400 border border-slate-600"
                  }`}
              >
                <FolderIcon className="w-8 h-8" />
              </Button>

              {/* Tooltip */}
              {/* <div className="absolute left-1/2 -translate-x-1/2 mt-2 w-max p-1 text-sm text-white bg-black rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                {language === "Tiếng Việt" ? "Mở thanh bên" : "Open sidebar"}
              </div> */}
            </div>

            {/* Nút tạo cuộc trò chuyện mới */}
            <div className="relative group">
              <Link href="/">
                <Button
                  onClick={startNewChat}
                  className={`p-2 rounded-full transition-all duration-200 shadow-sm ${theme === "light"
                    ? "bg-white hover:bg-orange-500 hover:text-white text-orange-600 border border-orange-200"
                    : "bg-slate-800 hover:bg-slate-600 text-cyan-400 border border-slate-600"
                    }`}
                >
                  <PlusCircleIcon className="w-8 h-8" />
                </Button>
              </Link>

              {/* Tooltip */}
              <div className={`absolute left-1/2 -translate-x-1/2 mt-2 w-max px-3 py-1 text-sm text-white rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 shadow-md ${theme === "light" ? "bg-orange-600" : "bg-slate-700"
                }`}>
                {language === "Tiếng Việt" ? "Cuộc trò chuyện mới" : "New Chat"}
              </div>
            </div>
          </div>
        )}

        {/* Tên chatbot */}
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-2xl shadow-md ${theme === "light"
            ? "bg-gradient-to-br from-orange-400 to-orange-600"
            : "bg-gradient-to-br from-cyan-500 to-blue-600"
            }`}>
            <SparklesIcon className="w-8 h-8 text-white" />
          </div>
          <h1 className={`text-3xl font-semibold bg-clip-text text-transparent ${theme === "light"
            ? "bg-gradient-to-r from-orange-600 to-orange-500"
            : "bg-gradient-to-r from-cyan-400 to-blue-500"
            }`}>
            {language === "Tiếng Việt"
              ? "Chatbot du lịch Việt Nam"
              : "Vietnam Travel"}
          </h1>
        </div>

        {/* ThemeSwitch + UserButton */}
        <div className="flex items-center gap-4">
          <ThemeSwitch theme={theme} toggleTheme={toggleTheme} />
          <UserButton />
        </div>
      </header>

      {/* PHẦN HIỂN THỊ TIN NHẮN */}
      <section
        className="flex-grow px-8 lg:px-32 xl:px-64 py-4 overflow-y-auto"
        ref={chatParent}
      >
        <div className="max-w-4xl mx-auto">
          {/* Nếu chưa có message → hiển thị gợi ý FAQ */}
          {messages.length === 0 ? (
            <div className="flex flex-col items-center space-y-6 mt-12">
              {/* <p className={`text-xl font-light ${theme === "light" ? "text-gray-600" : "text-gray-300"
                }`}>
                {language === "Tiếng Việt"
                  ? "Khám phá Việt Nam cùng chúng tôi"
                  : "Explore Vietnam with us"}
              </p> */}

              <ul className="space-y-3">
                {faqSuggestions.map((question, index) => (
                  <li key={index} className="text-center">
                    <Button
                      onClick={() => handleSuggestionClick(question)}
                      className={`inline-block px-6 py-3 rounded-full border-2 shadow-sm hover:shadow-md cursor-pointer transition-all duration-200 font-normal ${theme === "light"
                        ? "bg-white border-orange-300 text-orange-600 hover:bg-orange-500 hover:text-white hover:border-orange-500"
                        : "bg-slate-800 border-cyan-500 text-cyan-400 hover:bg-cyan-500 hover:text-black hover:border-cyan-400"
                        }`}
                    >
                      {question}
                    </Button>
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <ul>
              {/* Render danh sách tin nhắn */}
              {messages.map((m, index) => (
                <li
                  key={index}
                  className={`mb-6 ${m.role === "user" ? "text-right" : "text-left"}`}
                >
                  {m.role === "user" ? (
                    <div className={`inline-block px-5 py-3 rounded-3xl shadow-md max-w-2xl ${theme === "light"
                      ? "bg-gradient-to-br from-orange-500 to-orange-600 text-white"
                      : "bg-gradient-to-br from-slate-700 to-slate-800 text-gray-100 border border-slate-600"
                      }`}>
                      <p className="font-normal text-base leading-relaxed">
                        {m.content}
                      </p>
                    </div>
                  ) : (
                    <div className="inline-block max-w-3xl">
                      <div className="flex gap-3 items-start">
                        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-sm ${theme === "light"
                          ? "bg-gradient-to-br from-orange-400 to-orange-600"
                          : "bg-gradient-to-br from-cyan-500 to-blue-600"
                          }`}>
                          <SparklesIcon className="w-4 h-4 text-white" />
                        </div>
                        <div className={`flex-1 px-4 py-3 rounded-2xl rounded-tl-none shadow-sm ${theme === "light"
                          ? "bg-orange-50"
                          : "bg-slate-800 border border-slate-700"
                          }`}>
                          <p
                            className={`text-sm font-light leading-relaxed ${theme === "light" ? "text-gray-700" : "text-gray-300"
                              }`}
                            style={{ fontFamily: '"Inter", "SF Pro Display", -apple-system, sans-serif' }}
                            dangerouslySetInnerHTML={{
                              __html: m.content
                                .replace(
                                  /\*\*(.*?)\*\*/g,
                                  theme === "light"
                                    ? "<strong class='font-semibold text-orange-700'>$1</strong>"
                                    : "<strong class='font-semibold text-cyan-400'>$1</strong>"
                                )
                                .replace(/\n/g, "<br />")
                                .replace(
                                  /###\s(.*?):/g,
                                  theme === "light"
                                    ? "<h3 class='font-semibold text-orange-800 mt-3 mb-2 text-base'>$1:</h3>"
                                    : "<h3 class='font-semibold text-cyan-400 mt-3 mb-2 text-base'>$1:</h3>"
                                ),
                            }}
                          ></p>
                        </div>
                      </div>
                    </div>
                  )}
                </li>
              ))}

              {/* Hiển thị hoạt ảnh typing indicator */}
              {isTyping && (
                <li className="text-left inline-flex items-start max-w-fit">
                  <div className="flex gap-3 items-start">
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-sm ${theme === "light"
                      ? "bg-gradient-to-br from-orange-400 to-orange-600"
                      : "bg-gradient-to-br from-cyan-500 to-blue-600"
                      }`}>
                      <SparklesIcon className="w-4 h-4 text-white" />
                    </div>
                    <div className={`px-4 py-3 rounded-2xl rounded-tl-none shadow-sm ${theme === "light"
                      ? "bg-orange-50"
                      : "bg-slate-800 border border-slate-700"
                      }`}>
                      <TypingIndicator />
                    </div>
                  </div>
                </li>
              )}
            </ul>
          )}
        </div>
      </section>

      {/* KHUNG NHẬP TIN NHẮN */}
      <form
        onSubmit={handleSubmit}
        className={`p-6 border-t ${theme === "light"
          ? "bg-gradient-to-t from-orange-50 to-white border-orange-100"
          : "bg-gradient-to-t from-slate-900 to-slate-800 border-slate-700"
          }`}
      >
        <div className="max-w-4xl mx-auto w-full flex items-center gap-3">
          {/* Ô nhập nội dung */}
          <Input
            className={`flex-grow p-4 rounded-3xl border-2 shadow-sm ${theme === "light"
              ? "bg-white border-orange-200 focus:border-orange-400 text-gray-800 placeholder:text-gray-400"
              : "bg-slate-800 border-slate-600 focus:border-cyan-500 text-gray-100 placeholder:text-gray-500"
              }`}
            placeholder={
              language === "Tiếng Việt"
                ? "Nhập tin nhắn của bạn..."
                : "Type your message..."
            }
            value={input}
            onChange={handleInputChange}
            onEnterPress={() => {
              const form = document.querySelector('form');
              if (form) {
                form.requestSubmit();
              }
            }}
          />

          {/* Nút gửi */}
          <Button
            type="submit"
            className={`px-6 py-3 rounded-full font-medium shadow-md hover:shadow-lg transition-all duration-200 ${theme === "light"
              ? "bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white"
              : "bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white"
              }`}
          >
            {language === "Tiếng Việt" ? "Gửi" : "Send"}
          </Button>
        </div>
      </form>

      {/* Ghi chú cảnh báo cuối trang */}
      {/* <p className={`py-3 text-center flex-shrink-0 text-sm font-light ${theme === "light" ? "text-orange-400" : "text-slate-500"
        }`}>
        {language === "Tiếng Việt"
          ? "Chatbot có thể lỗi. Hãy kiểm tra những thông tin quan trọng."
          : "The chatbot may make errors. Please verify critical information."}
      </p> */}
    </section>
  );
};
