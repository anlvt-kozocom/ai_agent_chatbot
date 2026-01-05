
import React from 'react';
import SigmaChatPreview from './SigmaChatPreview';

const Hero: React.FC = () => {
  return (
    <div className="relative pt-32 pb-20 lg:pt-40 lg:pb-32 overflow-hidden bg-white">
      {/* Background blobs */}
      <div className="absolute top-0 right-0 -z-10 w-1/2 h-1/2 bg-rose-50 blur-[120px] rounded-full opacity-60"></div>
      <div className="absolute bottom-0 left-0 -z-10 w-1/3 h-1/3 bg-pink-100 blur-[100px] rounded-full opacity-40"></div>

      <div className="container mx-auto px-6">
        <div className="flex flex-col lg:flex-row items-center justify-between gap-12 lg:gap-24">
          <div className="lg:w-1/2 text-center lg:text-left">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 mb-8 text-sm font-bold tracking-wide text-rose-600 uppercase bg-rose-50 rounded-full border border-rose-100">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
              </span>
              Sáng tạo bởi Sigma Labs
            </div>
            <h1 className="text-5xl md:text-7xl font-black text-slate-900 leading-tight mb-8">
              Bán hàng <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-rose-600 to-pink-500">Thần tốc với AI</span>
            </h1>
            <p className="text-xl text-slate-600 mb-10 max-w-xl mx-auto lg:mx-0 leading-relaxed">
              Sigma Chat Box giúp khách hàng của bạn chốt đơn ngay trong khung chat. 
              Tra cứu sản phẩm, kiểm tra đơn hàng và tư vấn kỹ thuật chỉ trong 1 nốt nhạc.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 mb-12">
              <button className="w-full sm:w-auto px-10 py-5 bg-[#FF4D5E] text-white rounded-2xl font-black text-xl hover:bg-rose-600 transition shadow-xl hover:shadow-rose-200 hover:-translate-y-1">
                Dùng thử Sigma ngay
              </button>
              <button className="w-full sm:w-auto px-10 py-5 bg-white text-slate-700 border-2 border-slate-100 rounded-2xl font-bold text-lg hover:bg-slate-50 transition">
                Tài liệu API
              </button>
            </div>
            
            <div className="grid grid-cols-3 gap-8 pt-8 border-t border-slate-100">
               <div>
                  <p className="text-3xl font-black text-slate-900">98%</p>
                  <p className="text-sm text-slate-500 font-medium">Khách hài lòng</p>
               </div>
               <div>
                  <p className="text-3xl font-black text-slate-900">2s</p>
                  <p className="text-sm text-slate-500 font-medium">Phản hồi trung bình</p>
               </div>
               <div>
                  <p className="text-3xl font-black text-slate-900">50+</p>
                  <p className="text-sm text-slate-500 font-medium">Tích hợp Platform</p>
               </div>
            </div>
          </div>
          
          <div className="lg:w-1/2 flex justify-center lg:justify-end relative">
             <div className="relative z-10 scale-100 lg:scale-110">
                <SigmaChatPreview />
                {/* Decorative floating icon */}
                <div className="absolute -left-12 bottom-20 bg-white p-4 rounded-3xl shadow-2xl animate-bounce hidden md:block border border-slate-100">
                   <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-rose-100 rounded-2xl flex items-center justify-center text-rose-600 font-bold">🛒</div>
                      <div>
                         <p className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Mới đặt hàng</p>
                         <p className="text-xs font-black text-slate-900">iPhone 15 Pro Max</p>
                      </div>
                   </div>
                </div>
             </div>
             {/* Background glow */}
             <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-rose-500/10 blur-[100px] -z-10 rounded-full"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Hero;
