
import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage } from '../types';

const SigmaChatPreview: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: 'Chào bạn, mình là trợ lý AI của Sigma Shop! Bạn cần hỗ trợ gì hoặc có thể chọn một trong các chủ đề dưới đây nhé.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSimulatedSubmit = (text?: string) => {
    const userMsg = text || input.trim();
    if (!userMsg || isLoading) return;

    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsLoading(true);

    // Giả lập phản hồi sau 1 giây
    setTimeout(() => {
      const responses: Record<string, string> = {
        "Chính sách bảo hành": "Chính sách bảo hành của Sigma là 1 đổi 1 trong vòng 12 tháng đối với lỗi nhà sản xuất bạn nhé! ✨",
        "Tra cứu đơn hàng": "Vui lòng nhập mã đơn hàng (ví dụ: SIG123) để mình kiểm tra giúp bạn.",
        "Khuyến mãi HOT": "Hiện tại đang có chương trình giảm giá 20% cho khách hàng mới đấy!",
        "default": "Cảm ơn bạn đã quan tâm! Đây là bản demo giao diện của Sigma Chat Box."
      };
      
      const reply = responses[userMsg] || responses["default"];
      setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
      setIsLoading(false);
    }, 1000);
  };

  const quickActions = ["Chính sách bảo hành", "Tra cứu đơn hàng", "Khuyến mãi HOT", "Tìm cửa hàng"];

  return (
    <div className="w-full max-w-[400px] h-[580px] bg-[#FDE8E9] rounded-[32px] shadow-2xl overflow-hidden border border-white/40 flex flex-col relative font-sans">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#FF4D5E] to-[#FF758C] p-4 flex items-center justify-between text-white">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
             <img src="https://api.dicebear.com/7.x/bottts/svg?seed=Sigma&backgroundColor=transparent" alt="Mascot" className="w-6 h-6" />
          </div>
          <span className="font-semibold text-sm">Trợ lý AI - Sigma ✨</span>
        </div>
        <div className="flex gap-3">
           <div className="w-5 h-5 opacity-80 cursor-pointer">🔄</div>
           <div className="w-5 h-5 opacity-80 cursor-pointer">⛶</div>
           <div className="w-5 h-5 opacity-80 cursor-pointer">✕</div>
        </div>
      </div>

      {/* Content Area */}
      <div ref={scrollRef} className="flex-grow overflow-y-auto p-4 space-y-5 scroll-smooth no-scrollbar">
        <div className="flex flex-col items-center py-4">
          <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg mb-2 border-2 border-pink-100 overflow-hidden">
             <img src="https://api.dicebear.com/7.x/bottts/svg?seed=Sigma&backgroundColor=b6e3f4" alt="Sigma" />
          </div>
          <h3 className="text-lg font-bold text-[#333]">Sigma<span className="bg-[#FF4D5E] text-white text-[10px] px-1 rounded ml-1">AI</span></h3>
          <p className="text-center text-[12px] text-gray-500 font-medium px-4">
            <b>Sigma - Biết tuốt</b> hỗ trợ bạn tra cứu nhanh sản phẩm và đơn hàng.
          </p>
        </div>

        {messages.map((msg, i) => (
          <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            {msg.role === 'assistant' && (
               <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center shadow-sm mb-1 overflow-hidden">
                 <img src="https://api.dicebear.com/7.x/bottts/svg?seed=Sigma" alt="AI" />
               </div>
            )}
            <div className={`max-w-[85%] px-4 py-3 text-[13.5px] leading-relaxed shadow-sm ${
              msg.role === 'user' 
                ? 'bg-[#FF4D5E] text-white rounded-2xl rounded-tr-none' 
                : 'bg-white text-[#333] rounded-2xl rounded-tl-none border border-white'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex flex-col items-start animate-pulse">
            <div className="bg-white px-4 py-3 rounded-2xl rounded-tl-none shadow-sm">
               <div className="flex gap-1">
                 <div className="w-1.5 h-1.5 bg-pink-300 rounded-full animate-bounce"></div>
                 <div className="w-1.5 h-1.5 bg-pink-300 rounded-full animate-bounce [animation-delay:-0.1s]"></div>
                 <div className="w-1.5 h-1.5 bg-pink-300 rounded-full animate-bounce [animation-delay:-0.2s]"></div>
               </div>
            </div>
          </div>
        )}

        <div className="flex overflow-x-auto gap-2 py-2 no-scrollbar">
          {quickActions.map((action, idx) => (
            <button 
              key={idx}
              onClick={() => handleSimulatedSubmit(action)}
              className="whitespace-nowrap bg-white text-[#FF4D5E] border border-[#FF4D5E]/20 px-4 py-2 rounded-full text-[11px] font-bold hover:bg-[#FF4D5E] hover:text-white transition-all shadow-sm"
            >
              {action}
            </button>
          ))}
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white p-4 border-t border-pink-50">
        <div className="flex items-center bg-[#F4F6F9] rounded-2xl px-4 py-1.5">
          <input 
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSimulatedSubmit()}
            placeholder="Bạn cần hỗ trợ gì?"
            className="flex-grow bg-transparent border-none focus:ring-0 text-[13px] py-2 text-[#333]"
          />
          <button 
            onClick={() => handleSimulatedSubmit()}
            className="ml-2 w-8 h-8 bg-[#E5E7EB] text-[#333] rounded-full flex items-center justify-center hover:bg-[#FF4D5E] hover:text-white transition-all"
          >
            <svg className="w-4 h-4 rotate-90" fill="currentColor" viewBox="0 0 20 20"><path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"></path></svg>
          </button>
        </div>
        <p className="text-[9px] text-center text-gray-400 mt-2 uppercase tracking-tighter">
          Demo UI Interface • Sigma Labs
        </p>
      </div>
    </div>
  );
};

export default SigmaChatPreview;
