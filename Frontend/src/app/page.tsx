"use client";
// Cho biết đây là Client Component. Cần thiết để sử dụng các hook như useAuth, useEffect.

import { redirect } from "next/navigation";
// Hàm dùng để chuyển hướng người dùng sang trang khác.

import { useAuth } from "@clerk/nextjs";
// Hook của Clerk giúp lấy trạng thái đăng nhập (isLoaded, isSignedIn).

import { ChatProvider } from "../features/chat/hooks/use-chat";
// Provider quản lý toàn bộ state và logic của hệ thống chat.

import { Sidebar } from "../features/chat/components/sidebar";
// Component hiển thị thanh bên trái (danh sách cuộc trò chuyện, menu, v.v.)

import { Chat } from "../features/chat/components/chat";
// Component hiển thị khung trò chuyện chính.

import { useEffect } from "react";
// Hook dùng để chạy logic mỗi khi isLoaded hoặc isSignedIn thay đổi.


export default function Page() {
  // Lấy trạng thái đăng nhập từ Clerk
  const { isLoaded, isSignedIn } = useAuth();

  useEffect(() => {
    // Khi Clerk đã tải xong nhưng người dùng chưa đăng nhập → chuyển hướng về trang login
    if (isLoaded && !isSignedIn) {
      redirect("/login");
    }
  }, [isLoaded, isSignedIn]);

  // Khi Clerk chưa tải xong dữ liệu xác thực → hiển thị thông báo tạm
  if (!isLoaded) {
    return <p>Đang kiểm tra trạng thái đăng nhập...</p>;
  }

  // Khi biết chắc chắn là người dùng chưa đăng nhập → không hiển thị nội dung trang
  if (!isSignedIn) {
    return null;
  }

  // Khi người dùng đã đăng nhập → hiển thị giao diện chat
  return (
    <ChatProvider>
      <div className="flex w-full h-screen">
        <Sidebar />
        <Chat />
      </div>
    </ChatProvider>
  );
}
