import React from 'react';

interface FloatingButtonProps {
  isOpen: boolean;
  onClick: () => void;
  primaryColor: string;
  className?: string;
}

export const FloatingButton: React.FC<FloatingButtonProps> = ({ isOpen, onClick, primaryColor, className = '' }) => {
  return (
    <div className={`fixed bottom-4 right-4 md:bottom-6 md:right-6 z-[100] ${className}`}>
      <button 
        onClick={onClick}
        className={`w-12 h-12 bg-white rounded-2xl shadow-lg flex items-center justify-center border transition-all duration-300 overflow-hidden ${
          isOpen 
            ? 'border-indigo-500 ring-4 ring-indigo-50 scale-105 rotate-0' 
            : 'border-slate-100 hover:scale-110 hover:shadow-xl'
        }`}
      >
        <img 
          src="https://fptshop.com.vn/img/bitu/bitu-avatar.png" 
          className="w-10 h-10 object-contain" 
          alt="Bitu" 
          onError={(e) => (e.currentTarget.src = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png")}
        />
      </button>
    </div>
  );
};