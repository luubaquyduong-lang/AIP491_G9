// ===== ĐỊNH NGHĨA TYPES CHO MESSAGE VÀ CHAT =====
// File: message.ts
// Mô tả: Định nghĩa các interface TypeScript cho message và chat
//        Loại bỏ các trường không cần thiết khi gửi giữa client-server

import { Chat, Message } from "@prisma/client";

/**
 * MessageClient - Interface cho tin nhắn ở phía client
 * 
 * Loại bỏ các trường:
 * - id: Server tự sinh khi lưu vào DB
 * - chatId: Server tự gán dựa vào context
 * - createdAt, updatedAt: Server tự động quản lý timestamps
 * 
 * Giữ lại:
 * - role: "user" hoặc "assistant"
 * - content: Nội dung tin nhắn
 */
export interface MessageClient
  extends Omit<Message, "id" | "chatId" | "createdAt" | "updatedAt"> { }

/**
 * ChatClient - Interface cho cuộc hội thoại ở phía client
 * 
 * Loại bỏ các trường:
 * - userId: Không cần gửi lên (server lấy từ session)
 * - createdAt, updatedAt: Server tự động quản lý timestamps
 * 
 * Giữ lại:
 * - id: ID của cuộc chat
 * - title: Tiêu đề cuộc chat (thường là câu hỏi đầu tiên)
 */
export interface ChatClient
  extends Omit<Chat, "userId" | "createdAt" | "updatedAt"> { }
