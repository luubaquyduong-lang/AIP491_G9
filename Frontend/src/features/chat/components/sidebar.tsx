"use client";

import { FolderIcon, PlusCircleIcon, ArrowLeftIcon, ChatBubbleBottomCenterTextIcon } from "@heroicons/react/24/solid";
import { useChat } from "../hooks/use-chat";
import Link from "next/link";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
export const Sidebar = () => {
  const {
    theme,
    setHistory,
    history,
    selectedChat,
    startNewChat,
    toggleSidebar,
    sidebarOpen,
    language,
  } = useChat();

  // Lấy danh sách lịch sử từ backend
  useEffect(() => {
    fetch("/api/chats")
      .then((res) => res.json())

      .then((data) => {
        setHistory(data);
        console.log("DATA FROM API:", data);
        console.log("IS ARRAY?", Array.isArray(data));
        setHistory(Array.isArray(data) ? data : []);
      })
      .catch((err) => console.error("Error fetching chat history:", err));
  }, []);
  return (
    <>
      {sidebarOpen && (
        <aside
          className={`relative flex-shrink-0 max-w-xs border-r p-4 pt-10 overflow-visible ${theme === "light"
              ? "border-orange-200 bg-gradient-to-b from-orange-50 to-white text-gray-800"
              : "border-slate-700 bg-gradient-to-b from-slate-900 to-slate-950 text-gray-100"
            }`}
          style={{
            lineHeight: "30px",
            fontSize: "17.5px",
            tabSize: "4",
            width: "600px",
            overflow: "hidden",
            overflowY: "auto",
            scrollbarColor: theme === "light" ? "#ea580c #fef3f2" : "#1e293b #0f172a",
            scrollbarWidth: "thin",
          }}
        >
          {/* Container cho các nút */}
          <div className="absolute top-4 left-4 right-4 z-10 flex justify-between items-center overflow-visible">
            {/* Nút New Chat */}
            <div className="relative group overflow-visible">
              <Button
                onClick={startNewChat}
                className={`p-2 rounded-full border transition-all duration-200 shadow-sm ${theme === "light"
                    ? "bg-white hover:bg-orange-500 hover:text-white text-orange-600 border-orange-200"
                    : "bg-slate-800 hover:bg-slate-600 text-cyan-400 border-slate-600"
                  }`}
              >
                <PlusCircleIcon className="w-8 h-8" />
              </Button>

              {/* Tooltip */}
              <div className={`absolute left-1/2 -translate-x-1/2 mt-2 w-max px-3 py-1 text-sm text-white rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 overflow-visible shadow-md ${theme === "light" ? "bg-orange-600" : "bg-slate-700"
                }`}>
                {language === "Tiếng Việt" ? "Cuộc trò chuyện mới" : "New Chat"}
              </div>
            </div>

            {/* Nút Close Sidebar */}
            <div className="relative group">
              <Button
                onClick={toggleSidebar}
                className={`p-2 rounded-full border transition-all duration-200 shadow-sm overflow-visible ${theme === "light"
                    ? "bg-white hover:bg-orange-500 hover:text-white text-orange-600 border-orange-200"
                    : "bg-slate-800 hover:bg-slate-600 text-cyan-400 border-slate-600"
                  }`}
              >
                <ArrowLeftIcon className="w-7 h-7" />
              </Button>

              {/* Tooltip */}
              <div className={`absolute top-full right-1/2 translate-x-1/2 translate-y-2 w-max px-3 py-1 text-sm text-white rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 shadow-md z-20 overflow-visible ${theme === "light" ? "bg-orange-600" : "bg-slate-700"
                }`}>
                {language === "Tiếng Việt" ? "Đóng thanh bên" : "Close Sidebar"}
              </div>
            </div>
          </div>

          {/* button new chat */}
          <Link href="/">
            <Button
              onClick={startNewChat}
              className={`group w-full max-w-sm px-5 py-3 mb-4 mt-14 rounded-full flex items-center justify-between gap-2 text-lg font-medium shadow-md hover:shadow-lg transition-all duration-200 ${theme === "light"
                  ? "bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white"
                  : "bg-gradient-to-r from-slate-700 to-slate-800 hover:from-slate-600 hover:to-slate-700 text-cyan-400 border border-slate-600"
                }`}
            >
              <div className="flex items-center gap-3">
                <ChatBubbleBottomCenterTextIcon className="w-7 h-7" />
                {language === "Tiếng Việt" ? "Trò chuyện ngay!" : "Chat now!"}
              </div>
              {/* Icon hiển thị khi hover */}
              <PlusCircleIcon className="w-6 h-6 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
            </Button>
          </Link>
          {/* chat history */}
          <h1 className={`max-w-sm mb-4 mt-7 text-lg font-semibold flex items-center gap-2 ${theme === "light" ? "text-orange-700" : "text-cyan-400"
            }`}>
            <FolderIcon className="w-5 h-5" />
            {language === "Tiếng Việt" ? "Lịch sử trò chuyện" : "Chat history"}
          </h1>


          {history.length === 0 ? (
            <p className={`text-center font-light ${theme === "light" ? "text-orange-400" : "text-slate-500"
              }`}>
              Không tồn tại lịch sử trò chuyện
            </p>
          ) : (
            <ul>
              {history.slice().reverse().map((chat) => (
                <Link href={`/chat/${chat.id}`} key={chat.id}>
                  <li
                    className={`p-3 mb-2 rounded-2xl cursor-pointer transition-all duration-200 border-l-4 ${selectedChat === chat.id
                        ? theme === "light"
                          ? "bg-orange-100 border-orange-500 shadow-sm"
                          : "bg-slate-800 border-cyan-500 shadow-sm"
                        : theme === "light"
                          ? "bg-white hover:bg-orange-50 border-transparent hover:border-orange-300"
                          : "bg-slate-900 hover:bg-slate-800 border-transparent hover:border-cyan-600"
                      }`}
                    style={{
                      display: "block",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "clip",
                      maxWidth: "590px",
                      maskImage: "linear-gradient(to right, black 80%, transparent)",
                      WebkitMaskImage: "linear-gradient(to right, black 80%, transparent)",
                    }}
                  >
                    <span className={`font-normal ${theme === "light" ? "text-gray-700" : "text-gray-300"
                      }`}>{chat.title}</span>
                  </li>
                </Link>
              ))}
            </ul>
          )}
        </aside>
      )}
    </>
  );
};
