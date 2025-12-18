import { promptMessageSchema } from "@/features/chat/schemas/prompt-message-schema";
import { prisma } from "@/lib/prisma";
import { auth } from "@clerk/nextjs/server";
import { notFound, redirect } from "next/navigation";
import { NextRequest, NextResponse } from "next/server";
import _ from "lodash";

// ============================
// 🚀 API POST /api/messages
// ============================
export async function POST(req: NextRequest) {
  // Lấy URL để đọc query params (chatId)
  const url = new URL(req.url);
  const chatId = url.searchParams.get("chatId");

  // Lấy body JSON gửi từ frontend
  const { message, language } = await req.json();
  console.log("message: ", message);

  try {
    // ============================
    // 🔐 Kiểm tra user đã login chưa (Clerk)
    // ============================
    const { userId } = await auth();

    if (!userId) {
      // Nếu chưa login → redirect
      redirect("/login");
    }

    // ============================
    // 🧹 Validate message theo schema Zod
    // ============================
    const validatedMessage = promptMessageSchema.parse(message);
    console.log("validateM: ", validatedMessage);

    // ============================
    // 💬 Nếu có chatId → load cuộc chat cũ
    // Nếu không → tạo chat mới
    // ============================
    const chat = chatId
      ? await prisma.chat.findUnique({
        where: { id: chatId },
        include: { messages: true },
      })
      : await prisma.chat.create({
        data: {
          userId,
          title: validatedMessage.content, // đặt tiêu đề chat bằng câu user hỏi
        },
        include: { messages: true },
      });

    if (!chat) {
      notFound(); // trả lỗi 404 nếu không tìm thấy
    }

    // ============================
    //  Lưu tin nhắn của user vào DB
    // ============================
    const userMessage = await prisma.message.create({
      data: {
        chatId: chat.id,
        role: "user",
        ...validatedMessage,
      },
    });

    console.log("user mess: ", userMessage);

    // Danh sách tin nhắn trong cuộc trò chuyện
    const messages = chat.messages.concat(userMessage);
    console.log(language);

    // ============================
    //  Gửi request sang Python FastAPI backend
    // ============================
    const response = await fetch("http://127.0.0.1:8000/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: messages.map((m) => ({
          role: m.role,
          content: m.content,
        })),
        language: language,
      }),
    });

    // Nếu FastAPI trả lỗi
    if (!response.ok) {
      throw new Error("Failed to fetch from chatbot API");
    }

    // Lấy câu trả lời chatbot
    const { answer } = await response.json();

    // ============================
    //  Lưu lại response của chatbot vào DB
    // ============================
    const botMessage = await prisma.message.create({
      data: {
        chatId: chat.id,
        role: "assistant",
        content: answer,
      },
    });

    // Trả JSON về frontend
    return NextResponse.json(botMessage);

  } catch (error) {
    // Nếu có bất kỳ lỗi nào
    console.log(error);
    return NextResponse.json({ error }, { status: 500 });
  }
}
