
import React from 'react';
import { Message, MessageType, SenderType } from '../../types';
import { ProductCard } from './ProductCard';

interface ChatMessagesProps {
  messages: Message[];
  isLoading: boolean;
  quickReplies: string[];
  onQuickReply: (reply: string) => void;
  primaryColor: string;
  renderMarkdown?: boolean;
}

const parseInlineMarkdown = (text: string): React.ReactNode[] => {
  const regex = /(\*\*.*?\*\*|\[.*?\]\(.*?\))/g;
  const parts = text.split(regex);

  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      const content = part.slice(2, -2);
      return <strong key={i} className="font-bold text-gray-900">{content}</strong>;
    }
    
    const linkMatch = part.match(/\[(.*?)\]\((.*?)\)/);
    if (linkMatch) {
      const [_, linkText, url] = linkMatch;
      return (
        <a 
          key={i} 
          href={url} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="text-blue-600 hover:underline break-all font-semibold"
        >
          {linkText}
        </a>
      );
    }

    return part;
  });
};

const MarkdownLite: React.FC<{ text: string }> = ({ text }) => {
  const lines = text.split('\n');
  
  return (
    <div className="markdown-body space-y-1.5">
      {lines.map((line, idx) => {
        const trimmedLine = line.trim();
        
        const headerMatch = trimmedLine.match(/^(#{1,4})\s+(.*)$/);
        if (headerMatch) {
          const level = headerMatch[1].length;
          const content = headerMatch[2];
          const className = level === 1 ? 'text-lg font-bold mb-3 mt-1' : 
                            level === 2 ? 'text-md font-bold mb-2 mt-1' : 
                            'text-[14px] font-bold mb-1.5 mt-0.5 text-gray-900 uppercase tracking-wide';
          return <div key={idx} className={className}>{parseInlineMarkdown(content)}</div>;
        }

        const bulletMatch = trimmedLine.match(/^[*+-]\s+(.*)$/);
        if (bulletMatch) {
          const content = bulletMatch[1];
          return (
            <div key={idx} className="flex gap-2.5 pl-1 mb-2 items-start">
              <span className="text-gray-400 flex-shrink-0 mt-1.5 w-1 h-1 bg-gray-400 rounded-full"></span>
              <div className="flex-1 leading-relaxed text-gray-800">{parseInlineMarkdown(content)}</div>
            </div>
          );
        }

        if (trimmedLine === '') {
          return <div key={idx} className="h-3" />;
        }

        return (
          <div key={idx} className="mb-1 leading-relaxed text-gray-800">
            {parseInlineMarkdown(line)}
          </div>
        );
      })}
    </div>
  );
};

export const ChatMessages: React.FC<ChatMessagesProps> = ({ 
  messages, 
  isLoading, 
  quickReplies, 
  onQuickReply,
  primaryColor,
  renderMarkdown = false
}) => {
  const botAvatar = "https://fptshop.com.vn/img/bitu/bitu-avatar.png";
  const fallbackAvatar = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png";

  return (
    <div className="flex flex-col gap-8 pb-4">
      <div className="flex flex-col items-center justify-center py-8 text-center animate-msg">
        <div className="relative mb-5">
          <div className="w-24 h-24 flex items-center justify-center">
             <img 
               src={botAvatar} 
               onError={(e) => (e.currentTarget.src = fallbackAvatar)}
               className="w-full h-full object-contain" 
               alt="Sigma AI Hero"
             />
          </div>
        </div>
        <h2 className="text-xl font-bold text-[#1a2b56] flex items-center justify-center gap-1">
          Sigma <span className="bg-indigo-600 text-white text-[10px] px-1.5 py-0.5 rounded-md leading-none ml-1 uppercase font-bold tracking-tight">AI</span>
        </h2>
        <div className="text-[14px] text-gray-600 mt-3 leading-relaxed px-4">
          <p><span className="font-bold text-gray-800">Sigma Assistant</span> hỗ trợ bạn mọi lúc mọi nơi</p>
          <p>Tăng cường hiệu suất với AI thông minh</p>
        </div>
      </div>

      {messages.map((msg, index) => (
        <div 
          key={msg.id} 
          className={`flex flex-col animate-msg ${msg.sender === SenderType.USER ? 'items-end' : 'items-start'}`}
          style={{ animationDelay: `${index * 0.05}s` }}
        >
          {msg.sender === SenderType.AI && (
            <div className="flex items-center gap-1.5 mb-2 ml-1">
               <img 
                src={botAvatar} 
                onError={(e) => (e.currentTarget.src = fallbackAvatar)}
                className="w-4 h-4 object-contain" 
                alt="AI"
               />
               <span className="text-[11px] font-bold text-gray-400 uppercase tracking-widest">AI Agent</span>
            </div>
          )}
          
          <div className={`flex flex-col ${msg.sender === SenderType.USER ? 'items-end' : 'items-start'} max-w-[94%]`}>
            <div 
              className={`px-4 py-3 rounded-[18px] text-[14px] shadow-sm border border-black/[0.03] ${
                msg.sender === SenderType.USER 
                  ? 'bg-indigo-600 text-white rounded-tr-none whitespace-pre-line shadow-indigo-100' 
                  : 'bg-white text-gray-800 border-none rounded-tl-none'
              } ${!renderMarkdown || msg.sender === SenderType.USER ? 'whitespace-pre-line' : ''}`}
            >
              {renderMarkdown && msg.sender === SenderType.AI ? (
                <MarkdownLite text={msg.content} />
              ) : (
                msg.content
              )}
            </div>

            {msg.type === MessageType.PRODUCT_LIST && msg.products && (
              <div className="w-full mt-4 flex gap-4 overflow-x-auto pb-4 pt-1 no-scrollbar snap-x">
                {msg.products.map(product => (
                  <div key={product.id} className="product-card-snap">
                    <ProductCard product={product} primaryColor={primaryColor} />
                  </div>
                ))}
              </div>
            )}

            {index === 0 && messages.length === 1 && msg.sender === SenderType.AI && (
              <div className="mt-5 flex flex-wrap gap-2.5 w-full">
                {quickReplies.map((reply, i) => (
                  <button
                    key={i}
                    onClick={() => onQuickReply(reply)}
                    className="px-4 py-2 rounded-full text-[13px] font-semibold border border-transparent bg-white text-gray-600 hover:text-indigo-600 hover:border-indigo-100 transition-all duration-200 shadow-sm active:scale-95"
                  >
                    {reply}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex flex-col gap-1.5 items-start animate-msg">
          <div className="flex items-center gap-1.5 ml-1">
            <img 
              src={botAvatar} 
              onError={(e) => (e.currentTarget.src = fallbackAvatar)}
              className="w-4 h-4 object-contain" 
              alt="AI Loading"
            />
          </div>
          <div className="flex gap-1.5 bg-white px-4 py-3 rounded-[18px] rounded-tl-none border-none shadow-sm">
            <span className="w-2 h-2 bg-indigo-300 rounded-full animate-sigma-bounce"></span>
            <span className="w-2 h-2 bg-indigo-300 rounded-full animate-sigma-bounce [animation-delay:0.2s]"></span>
            <span className="w-2 h-2 bg-indigo-300 rounded-full animate-sigma-bounce [animation-delay:0.4s]"></span>
          </div>
        </div>
      )}
    </div>
  );
};