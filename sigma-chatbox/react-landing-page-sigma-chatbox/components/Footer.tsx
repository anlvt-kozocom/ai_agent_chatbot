
import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-50 border-t border-slate-100 pt-24 pb-12">
      <div className="container mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-16 mb-20">
          <div className="lg:col-span-1">
            <div className="flex items-center space-x-2 mb-8">
              <div className="w-10 h-10 bg-gradient-to-tr from-rose-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg">
                <img src="https://api.dicebear.com/7.x/bottts/svg?seed=Sigma&backgroundColor=transparent" alt="Sigma Logo" className="w-7 h-7" />
              </div>
              <span className="font-black text-2xl text-slate-900">Sigma</span>
            </div>
            <p className="text-slate-500 font-medium mb-10 leading-relaxed">
              Dẫn đầu công nghệ AI Chat Box cho thương mại điện tử tại Đông Nam Á. 
              Sứ mệnh của chúng tôi là biến mọi cuộc trò chuyện thành một đơn hàng.
            </p>
            <div className="flex space-x-4">
              {['FB', 'TW', 'IN', 'GH'].map((social) => (
                <a key={social} href="#" className="w-12 h-12 rounded-2xl bg-white border border-slate-100 flex items-center justify-center text-slate-400 font-bold hover:bg-rose-600 hover:text-white transition-all shadow-sm">
                  {social}
                </a>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="font-black text-slate-900 mb-8 uppercase tracking-widest text-sm">Sản phẩm</h4>
            <ul className="space-y-4 text-slate-500 font-medium">
              <li><a href="#" className="hover:text-rose-600 transition">Sigma Core AI</a></li>
              <li><a href="#" className="hover:text-rose-600 transition">Sigma Widget SDK</a></li>
              <li><a href="#" className="hover:text-rose-600 transition">Sigma Analytics</a></li>
              <li><a href="#" className="hover:text-rose-600 transition">App Marketplace</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-black text-slate-900 mb-8 uppercase tracking-widest text-sm">Hỗ trợ</h4>
            <ul className="space-y-4 text-slate-500 font-medium">
              <li><a href="#" className="hover:text-rose-600 transition">Trung tâm trợ giúp</a></li>
              <li><a href="#" className="hover:text-rose-600 transition">Cộng đồng Dev</a></li>
              <li><a href="#" className="hover:text-rose-600 transition">Trạng thái hệ thống</a></li>
              <li><a href="#" className="hover:text-rose-600 transition">Liên hệ Support</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-black text-slate-900 mb-8 uppercase tracking-widest text-sm">Liên hệ</h4>
            <div className="space-y-4 text-slate-500 font-medium">
              <p>📍 Tầng 12, Tòa nhà Sigma, Quận 1, TP. HCM</p>
              <p>📞 1900 8888 (Hotline 24/7)</p>
              <p>✉️ hello@sigmaai.com</p>
            </div>
          </div>
        </div>
        
        <div className="pt-10 border-t border-slate-200 flex flex-col md:flex-row justify-between items-center text-slate-400 text-sm font-medium">
          <p>© 2024 Sigma Labs. Made with ❤️ in Vietnam.</p>
          <div className="mt-6 md:mt-0 flex items-center space-x-8">
            <a href="#" className="hover:text-rose-600 transition">Bảo mật</a>
            <a href="#" className="hover:text-rose-600 transition">Điều khoản</a>
            <div className="flex items-center gap-2 px-3 py-1 bg-green-50 text-green-600 rounded-full font-bold text-[10px] uppercase">
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
              All Systems Operational
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
