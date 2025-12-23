// ===== VALIDATION SCHEMA CHO TIN NHẮN NGƯỜI DÙNG =====
// File: prompt-message-schema.ts
// Mô tả: Sử dụng Zod để validate dữ liệu tin nhắn trước khi xử lý
//        Đảm bảo dữ liệu đúng format và trong giới hạn cho phép

import { MESSAGE_TEXT_MAX_LENGTH } from "@/constants";
import z from "zod";

/**
 * Schema validation cho tin nhắn người dùng
 * 
 * Quy tắc:
 * - content: Bắt buộc phải có (min: 1 ký tự)
 * - content: Không vượt quá MESSAGE_TEXT_MAX_LENGTH (500 ký tự)
 * 
 * Sử dụng:
 *   const validatedMessage = promptMessageSchema.parse(message);
 *   // Throws error nếu không hợp lệ
 * 
 * Mục đích:
 * - Bảo vệ backend khỏi dữ liệu không hợp lệ
 * - Giới hạn độ dài tin nhắn để tránh spam
 * - Đảm bảo không gửi tin nhắn rỗng
 */
export const promptMessageSchema = z.object({
  content: z.string().min(1).max(MESSAGE_TEXT_MAX_LENGTH),
});
