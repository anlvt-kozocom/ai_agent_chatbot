
import React from 'react';

interface NavbarProps {
  scrolled: boolean;
}

const Navbar: React.FC<NavbarProps> = ({ scrolled }) => {
  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'bg-white/90 backdrop-blur-md shadow-sm py-3' : 'bg-transparent py-5'}`}>
      <div className="container mx-auto px-6 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-10 h-10 bg-gradient-to-tr from-rose-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg shadow-rose-200">
             <img src="https://api.dicebear.com/7.x/bottts/svg?seed=Sigma&backgroundColor=transparent" alt="Sigma Logo" className="w-7 h-7" />
          </div>
          <span className={`font-black text-2xl tracking-tight text-slate-900`}>Sigma</span>
        </div>
        
        <div className="hidden md:flex items-center space-x-10">
          <a href="#features" className="text-slate-600 hover:text-rose-600 font-bold transition text-sm uppercase tracking-wider">Tính năng</a>
          <a href="#" className="text-slate-600 hover:text-rose-600 font-bold transition text-sm uppercase tracking-wider">Hệ sinh thái</a>
          <a href="#" className="text-slate-600 hover:text-rose-600 font-bold transition text-sm uppercase tracking-wider">Cộng đồng</a>
          <button className="bg-slate-900 text-white px-8 py-3 rounded-xl font-bold hover:bg-rose-600 transition shadow-md hover:shadow-rose-200">
            Dùng thử ngay
          </button>
        </div>

        <button className="md:hidden text-slate-900">
          <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7"></path></svg>
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
