import { PrismaClient } from "@prisma/client";

// Prisma client singleton cho ứng dụng Next.js.
// - Sử dụng biến môi trường `DATABASE_URL` (xem Code/Frontend/.env)
// - Datasource được cấu hình để sử dụng MongoDB trong prisma/schema.prisma
// - Sử dụng `prisma` để truy cập các model `Chat` và `Message` từ
//   các API route hoặc server component.
export const prisma = new PrismaClient();
