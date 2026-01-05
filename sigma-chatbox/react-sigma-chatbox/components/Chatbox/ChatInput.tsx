import React, { useState } from 'react';

interface ChatInputProps {
  placeholder: string;
  onSendMessage: (text: string) => void;
  primaryColor: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({ placeholder, onSendMessage, primaryColor }) => {
  const [text, setText] = useState('');

  const handleSend = () => {
    if (text.trim()) {
      onSendMessage(text);
      setText('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="p-1">
      <div className="relative flex items-center bg-gray-50/50 rounded-2xl border border-gray-100 focus-within:border-indigo-100 focus-within:bg-white transition-all duration-200 pr-2 pl-3 py-1">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          rows={1}
          className="w-full bg-transparent border-none outline-none focus:ring-0 text-[14px] text-gray-700 font-normal py-3 px-1 resize-none chat-scrollbar min-h-[44px] max-h-[120px] leading-relaxed placeholder:text-gray-400"
          style={{ fontWeight: 400 }}
        />
        <button 
          onClick={handleSend}
          disabled={!text.trim()}
          className={`w-9 h-9 rounded-xl flex-shrink-0 flex items-center justify-center transition-all duration-300 shadow-sm ${
            text.trim() 
              ? 'bg-indigo-600 text-white hover:bg-indigo-700 active:scale-95' 
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          }`}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="m5 12 7-7 7 7"></path><path d="M12 19V5"></path></svg>
        </button>
      </div>
    </div>
  );
};