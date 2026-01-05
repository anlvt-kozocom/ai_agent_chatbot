import { GoogleGenAI, Language } from "@google/genai";
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL;

// Cố vấn Sigma AI sử dụng Google Gemini API
// Đảm bảo export askSigmaAI để fix lỗi import trong AIAdvisor.tsx
export const askSigmaAI = async (message: string): Promise<string> => {
  try {
    // Luôn khởi tạo instance mới với API Key từ env
    const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

    // Sử dụng model gemini-3-flash-preview cho các tác vụ tư vấn văn bản
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: message,
      config: {
        systemInstruction:
          "Bạn là Sigma AI Advisor, một chuyên gia tư vấn chiến lược cho doanh nghiệp và thương mại điện tử. Hãy trả lời bằng tiếng Việt chuyên nghiệp, sáng tạo và thực tiễn. Giúp người dùng hiểu cách tối ưu hóa quy trình bán hàng và trải nghiệm khách hàng với Sigma.",
      },
    });

    // Truy cập .text trực tiếp từ response
    return (
      response.text ||
      "Tôi không thể đưa ra phản hồi lúc này. Vui lòng thử lại sau."
    );
  } catch (error) {
    console.error("Gemini API Error:", error);
    // Trả về phản hồi dự phòng thân thiện nếu có lỗi API
    return "Chào bạn! Hiện tại hệ thống tư vấn AI đang bận hoặc chưa được cấu hình khóa API. Sigma có thể giúp bạn tăng trưởng doanh thu bằng cách tự động hóa quy trình chăm sóc khách hàng và tối ưu hóa chuyển đổi.";
  }
};

export const mockResponse = (message: string) => {
  return "Chào bạn! Đây là phản hồi giả lập từ giao diện Sigma. Trong bản chính thức, tôi sẽ kết nối với AI để trả lời bạn.";
};

export const geminiService = {
  getChatResponseStream: async function* (
    userInput: string,
    threadId: string = "Thread_default",
    language: string = "en"
  ) {
    try {
      // Use relative path - Vite proxy will forward to API_BASE_URL
      const { data } = await axios.post(
        `/chat/stream`,
        { message: userInput, thread_id: threadId , language: language},
        { 
          responseType: "stream",
          adapter: "fetch"
        }
      );

      const reader = data.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          
          const content = line.substring(6).trim();
          if (content === "[DONE]") return;

          try {
            const parsed = JSON.parse(content);
            if (parsed.event === "on_chat_model_stream" && parsed.content) {
              yield parsed.content;
            }
          } catch {
            // Skip invalid JSON
          }
        }
      }
    } catch (error) {
      console.error("Lỗi kết nối:", error);
      yield "Đã có lỗi xảy ra khi kết nối với máy chủ.";
    }
  },
};
