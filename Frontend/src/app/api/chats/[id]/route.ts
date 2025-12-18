import { prisma } from "@/lib/prisma";
import { auth } from "@clerk/nextjs/server";
import { notFound, redirect } from "next/navigation";
import { NextRequest, NextResponse } from "next/server";

// GET /api/chats/[id]
// Mô tả (tiếng Việt):
// - Trả về một document `Chat` theo `id`, kèm theo danh sách `messages` của nó.
// - Yêu cầu đăng nhập (Clerk). Nếu chưa login sẽ redirect về `/login`.
// - Kiểm tra phân quyền: chỉ trả chat khi `chat.userId` trùng với user hiện tại.
export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } },
) {
  const id = params.id;

  try {
    // Xác thực user (Clerk)
    const { userId } = await auth();

    if (!userId) {
      // Nếu chưa đăng nhập → chuyển hướng đến trang login
      redirect("/login");
    }

    // Tải chat kèm messages. `id` là chuỗi ObjectId trong Prisma/MongoDB.
    const chat = await prisma.chat.findUnique({
      where: { id },
      include: {
        messages: true,
      },
    });

    // Nếu không tìm thấy hoặc chat không thuộc user hiện tại → trả 404
    if (!chat || chat.userId !== userId) {
      notFound();
    }

    // Trả về đối tượng chat (JSON)
    return NextResponse.json(chat);
  } catch (error) {
    return NextResponse.json({ error }, { status: 500 });
  }
}
