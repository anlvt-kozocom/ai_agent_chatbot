import React, { useState, useEffect, useRef } from 'react';
import { ChatboxConfig, Message, MessageType, SenderType, AiResponseHandler, Product, Language } from '../../types';
import { ChatHeader } from './ChatHeader';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';
import { FloatingButton } from './FloatingButton';

interface ChatboxProps {
  config: ChatboxConfig;
  onGetAiResponse: AiResponseHandler;
}

// Helper to generate random thread ID
const generateThreadId = () => Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);

export const Chatbox: React.FC<ChatboxProps> = ({ config, onGetAiResponse }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isReady, setIsReady] = useState(false);
  const [threadId, setThreadId] = useState(generateThreadId());
  const [language, setLanguage] = useState<Language>('en');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      type: MessageType.TEXT,
      sender: SenderType.AI,
      content: config.welcomeMessage,
      timestamp: new Date()
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const activeRequestId = useRef(0);

  // Kích hoạt transition sau khi chatbox đã mount lần đầu để tránh lỗi slide ngang
  useEffect(() => {
    if (isOpen) {
      const timer = setTimeout(() => setIsReady(true), 50);
      return () => clearTimeout(timer);
    } else {
      setIsReady(false);
    }
  }, [isOpen]);

  useEffect(() => {
    if (scrollRef.current && isOpen) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isOpen, isLoading]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const requestId = ++activeRequestId.current;
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      type: MessageType.TEXT,
      sender: SenderType.USER,
      content: text,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Pass the threadId and language to the handler
      const responseResult = onGetAiResponse(text, threadId, language);
      
      // Xử lý Streaming (Async Generator)
      if (responseResult && typeof responseResult === 'object' && Symbol.asyncIterator in responseResult) {
        let fullContent = '';
        let hasStarted = false;
        const aiMsgId = `ai-${Date.now()}`;

        for await (const chunk of (responseResult as AsyncGenerator<string>)) {
          if (requestId !== activeRequestId.current) return;

          if (!hasStarted) {
            setMessages(prev => [...prev, {
              id: aiMsgId,
              type: MessageType.TEXT,
              sender: SenderType.AI,
              content: '',
              timestamp: new Date()
            }]);
            setIsLoading(false);
            hasStarted = true;
          }
          fullContent += chunk;
          setMessages(prev => prev.map(msg => 
            msg.id === aiMsgId ? { ...msg, content: fullContent } : msg
          ));
        }
      } 
      // Xử lý Promise (Static Response)
      else {
        const response = await responseResult;
        if (requestId !== activeRequestId.current) return;

        setIsLoading(false);
        const finalData = typeof response === 'string' 
          ? { text: response, products: undefined } 
          : (response as { text: string; products?: Product[] });
          
        setMessages(prev => [...prev, {
          id: `ai-${Date.now()}`,
          type: finalData.products ? MessageType.PRODUCT_LIST : MessageType.TEXT,
          sender: SenderType.AI,
          content: finalData.text,
          products: finalData.products,
          timestamp: new Date()
        }]);
      }
    } catch (err) {
      if (requestId !== activeRequestId.current) return;
      console.error("Chatbox Error:", err);
      setIsLoading(false);
      setMessages(prev => [...prev, {
        id: `err-${Date.now()}`,
        type: MessageType.TEXT,
        sender: SenderType.AI,
        content: "Hệ thống đang bận, vui lòng thử lại sau.",
        timestamp: new Date()
      }]);
    }
  };

  const handleResetChat = () => {
    activeRequestId.current++; // Hủy các request đang chạy
    setThreadId(generateThreadId()); // Tạo threadId mới ngẫu nhiên
    setMessages([{
      id: 'welcome',
      type: MessageType.TEXT,
      sender: SenderType.AI,
      content: config.welcomeMessage,
      timestamp: new Date()
    }]);
    setIsLoading(false);
    setIsExpanded(false);
  };

  const chatClasses = `
    fixed z-[99] overflow-hidden flex flex-col border border-white/40 shadow-2xl bg-white animate-chat-pop
    ${isReady ? 'transition-[width,height,border-radius,right,bottom] duration-300 ease-in-out' : ''}
    ${isExpanded 
      ? 'bottom-0 right-0 w-full h-full md:bottom-6 md:right-28 md:w-[850px] md:h-[85vh] rounded-none md:rounded-[32px]' 
      : 'bottom-0 right-0 w-full h-[80vh] md:bottom-6 md:right-28 md:w-[380px] md:h-[580px] rounded-t-[28px] md:rounded-[28px]'
    }
  `;

  return (
    <>
      <FloatingButton 
        isOpen={isOpen} 
        onClick={() => setIsOpen(!isOpen)} 
        primaryColor={config.primaryColor}
        className={isOpen ? 'hidden md:flex' : 'flex'}
      />

      {isOpen && (
        <div className={chatClasses} style={{ left: 'auto' }}>
          <ChatHeader 
            title={config.botName} 
            primaryColor={config.primaryColor} 
            onClose={() => setIsOpen(false)}
            onReset={handleResetChat}
            onToggleExpand={() => setIsExpanded(!isExpanded)}
            isExpanded={isExpanded}
            language={language}
            onLanguageChange={setLanguage}
          />

          <div className="flex-1 overflow-y-auto chat-scrollbar px-5 py-5 bg-slate-50/30" ref={scrollRef}>
             <ChatMessages 
                messages={messages} 
                isLoading={isLoading} 
                quickReplies={config.quickReplies}
                onQuickReply={(reply) => handleSendMessage(reply)}
                primaryColor={config.primaryColor}
                renderMarkdown={config.renderMarkdown}
              />
          </div>

          <div className="bg-white p-3 border-t border-slate-100">
            <ChatInput 
              placeholder={config.placeholder} 
              onSendMessage={handleSendMessage} 
              primaryColor={config.primaryColor}
            />
          </div>
        </div>
      )}
    </>
  );
};