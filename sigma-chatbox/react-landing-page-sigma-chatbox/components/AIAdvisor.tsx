
import React, { useState, useRef, useEffect } from 'react';
// Fix: Import askSigmaAI instead of non-existent askAIAdvisor
import { askSigmaAI } from '../services/geminiService';
import { ChatMessage } from '../types';

const AIAdvisor: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: 'Chào bạn! Tôi là Sigma AI Advisor. Bạn cần tư vấn gì cho doanh nghiệp của mình hôm nay?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsLoading(true);

    // Fix: Use the available askSigmaAI service
    const response = await askSigmaAI(userMsg);
    setMessages(prev => [...prev, { role: 'assistant', content: response }]);
    setIsLoading(false);
  };

  return (
    <div className="container mx-auto px-6">
      <div className="flex flex-col lg:flex-row items-center gap-16">
        <div className="lg:w-1/2">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-6">
            Cố vấn chiến lược <br />
            <span className="text-indigo-600">Luôn sẵn sàng 24/7</span>
          </h2>
          <p className="text-slate-600 mb-8 text-lg">
            Thử trò chuyện với AI của chúng tôi ngay tại đây. Nó có thể giúp bạn giải đáp các thắc mắc về quản trị, xu hướng thị trường hoặc đơn giản là hướng dẫn bạn cách sử dụng Sigma hiệu quả nhất.
          </p>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center text-white">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path></svg>
              </div>
              <span className="font-medium">Tư vấn cá nhân hóa</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center text-white">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path></svg>
              </div>
              <span className="font-medium">Phản hồi tức thì</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center text-white">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path></svg>
              </div>
              <span className="font-medium">Bảo mật thông tin trao đổi</span>
            </div>
          </div>
        </div>
        
        <div className="lg:w-1/2 w-full max-w-xl">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-100 flex flex-col h-[500px]">
            <div className="p-4 border-bottom bg-slate-50 rounded-t-3xl flex items-center gap-3">
              <div className="w-3 h-3 bg-red-400 rounded-full"></div>
              <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
              <div className="w-3 h-3 bg-green-400 rounded-full"></div>
              <span className="ml-2 font-semibold text-slate-500 text-sm">Sigma AI Consulting</span>
            </div>
            
            <div 
              ref={scrollRef}
              className="flex-grow overflow-y-auto p-6 space-y-4 bg-white"
            >
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-slate-100 text-slate-800 rounded-bl-none'}`}>
                    {msg.content}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-slate-100 px-4 py-3 rounded-2xl rounded-bl-none">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            <form onSubmit={handleSubmit} className="p-4 border-t border-slate-100 flex gap-2">
              <input 
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Hỏi AI về chiến lược kinh doanh..."
                className="flex-grow px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
              />
              <button 
                type="submit"
                disabled={isLoading}
                className="bg-indigo-600 text-white p-2 rounded-xl hover:bg-indigo-700 transition disabled:opacity-50"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAdvisor;
