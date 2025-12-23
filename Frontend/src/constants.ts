// ===== HẰNG SỐ TOÀN CỤC =====
// File: constants.ts
// Mô tả: Định nghĩa các hằng số dùng chung trong toàn bộ ứng dụng

/**
 * MESSAGE_TEXT_MAX_LENGTH - Độ dài tối đa của tin nhắn
 * 
 * Giới hạn: 500 ký tự
 * 
 * Mục đích:
 * - Ngăn chặn spam/tin nhắn quá dài
 * - Đảm bảo hiệu suất xử lý
 * - Giới hạn kích thước request gửi lên server
 * 
 * Sử dụng trong:
 * - Validation schema (Zod)
 * - UI input validation
 * - Backend validation
 */
export const MESSAGE_TEXT_MAX_LENGTH = 500;
