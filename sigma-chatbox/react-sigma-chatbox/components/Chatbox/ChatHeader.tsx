import React from 'react';
import { Language } from '../../types';

interface ChatHeaderProps {
  title: string;
  primaryColor: string;
  onClose: () => void;
  onReset: () => void;
  onToggleExpand: () => void;
  isExpanded: boolean;
  language: Language;
  onLanguageChange: (lang: Language) => void;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({ 
  title, 
  primaryColor, 
  onClose, 
  onReset, 
  onToggleExpand,
  isExpanded,
  language,
  onLanguageChange
}) => {
  const languages: { value: Language; label: string }[] = [
    { value: 'en', label: 'EN' },
    { value: 'vi', label: 'VI' },
    { value: 'ja', label: 'JA' }
  ];

  return (
    <div 
      className="px-4 py-3 flex items-center justify-between border-b border-red-50/50 sticky top-0 z-10 bg-[#fff1f2]/90 backdrop-blur-sm"
    >
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full overflow-hidden bg-white p-0.5 shadow-sm">
           <img 
             src="https://fptshop.com.vn/img/bitu/bitu-avatar.png" 
             onError={(e) => (e.currentTarget.src = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png")}
             className="w-full h-full object-contain" 
             alt="Bot Icon"
           />
        </div>
        <div className="flex flex-col">
          <h3 className="font-bold text-[#1a2b56] text-[14px] leading-tight tracking-tight flex items-center gap-1">
            {title} <span className="text-red-400 text-[10px]">✨</span>
          </h3>
          <span className="text-[10px] text-green-500 font-medium flex items-center gap-1">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
            Online
          </span>
        </div>
      </div>
      
      <div className="flex items-center gap-1">
        {/* Language Select Box */}
        <div className="relative group mr-1">
          <select 
            value={language}
            onChange={(e) => onLanguageChange(e.target.value as Language)}
            className="appearance-none bg-white/50 border border-gray-200 rounded-lg px-2 pr-5 py-1 text-[10px] font-black text-indigo-600 cursor-pointer hover:bg-white transition-all focus:outline-none focus:ring-2 focus:ring-indigo-100 uppercase"
            title="Select language"
          >
            {languages.map((lang) => (
              <option key={lang.value} value={lang.value} className="font-sans font-bold">
                {lang.label}
              </option>
            ))}
          </select>
          <div className="absolute right-1.5 top-1/2 -translate-y-1/2 pointer-events-none text-indigo-400">
            <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6"/></svg>
          </div>
        </div>

        <button 
          onClick={onReset} 
          className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/60 text-gray-500 hover:text-indigo-600 transition-all"
          title="Reset chat"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path><path d="M21 3v5h-5"></path><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path><path d="M8 16H3v5"></path></svg>
        </button>

        <button 
          onClick={onToggleExpand}
          className="w-8 h-8 hidden md:flex items-center justify-center rounded-lg hover:bg-white/60 text-gray-500 hover:text-indigo-600 transition-all" 
          title={isExpanded ? "Collapse" : "Expand"}
        >
          {isExpanded ? (
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M4 14h6v6"></path><path d="M20 10h-6V4"></path><path d="M14 10l7-7"></path><path d="M10 14l-7 7"></path></svg>
          ) : (
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M15 3h6v6"></path><path d="M9 21H3v-6"></path><path d="M21 3l-7 7"></path><path d="M3 21l7-7"></path></svg>
          )}
        </button>

        <button 
          onClick={onClose} 
          className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-red-50 text-gray-500 hover:text-red-500 transition-all"
          title="Close"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"></path><path d="M6 6l12 12"></path></svg>
        </button>
      </div>
    </div>
  );
};