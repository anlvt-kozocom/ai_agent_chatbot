
import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Features from './components/Features';
import Footer from './components/Footer';
import AIAdvisor from './components/AIAdvisor';
import { Chatbox } from 'react-sigma-chatbox';
import 'react-sigma-chatbox/dist/react-sigma-chatbox.css'; 
import { geminiService } from './services/geminiService';


const App: React.FC = () => {
  const [scrolled, setScrolled] = useState(false);

  const config = {
    primaryColor: '#6366f1',
    botName: 'Sigma Assistant',
    welcomeMessage: 'Chào bạn! Tôi có thể giúp gì cho bạn?',
    quickReplies: ['Giá iPhone 15', 'Chính sách bảo hành'],
    placeholder: 'Nhập tin nhắn...',
    avatarUrl: 'https://api.dicebear.com/7.x/bottts/svg?seed=Sigma',
    renderMarkdown: true
  };

  const handleAiResponse = (input, threadId, language) => geminiService.getChatResponseStream(input, threadId, language);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <>
      <div className="min-h-screen flex flex-col bg-white">
        <Navbar scrolled={scrolled} />

        <main className="flex-grow">
          <section id="hero">
            <Hero />
          </section>

          <section id="features" className="py-24 bg-slate-50">
            <Features />
          </section>

          {/* AI Advisor Section */}
          <section id="advisor" className="py-24 bg-white">
            <AIAdvisor />
          </section>

          {/* CTA Section */}
          <section
            id="cta"
            className="py-24 bg-rose-600 overflow-hidden relative"
          >
            <div className="absolute top-0 right-0 w-96 h-96 bg-rose-500 rounded-full blur-[100px] opacity-50 -mr-48 -mt-48"></div>
            <div className="absolute bottom-0 left-0 w-96 h-96 bg-rose-400 rounded-full blur-[100px] opacity-30 -ml-48 -mb-48"></div>

            <div className="container mx-auto px-6 text-center relative z-10">
              <h2 className="text-4xl md:text-6xl font-black text-white mb-8">
                Bạn đã sẵn sàng để bùng nổ?
              </h2>
              <p className="text-rose-100 text-xl mb-12 max-w-2xl mx-auto leading-relaxed">
                Gia nhập cùng cộng đồng doanh nghiệp hiện đại. Sigma giúp bạn
                tối ưu hóa tỷ lệ chuyển đổi ngay lập tức.
              </p>
              <div className="flex flex-col sm:flex-row justify-center gap-6">
                <button className="bg-white text-rose-600 px-12 py-5 rounded-2xl font-black text-xl hover:shadow-2xl transition-all hover:-translate-y-1">
                  Bắt đầu Miễn phí
                </button>
                <button className="bg-rose-700 text-white px-12 py-5 rounded-2xl font-bold text-xl hover:bg-rose-800 transition-all">
                  Xem Tài liệu SDK
                </button>
              </div>
            </div>
          </section>
        </main>

        <Footer />
      </div>
      <Chatbox config={config} onGetAiResponse={handleAiResponse} />
    </>
  );
};

export default App;
