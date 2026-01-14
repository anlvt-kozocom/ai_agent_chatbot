import React from "react";

const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 text-white pt-10 pb-6 mt-10">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Col 1 */}
          <div>
            <h5 className="text-lg font-bold mb-4 flex items-center">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center mr-2">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4 w-4 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
                  />
                </svg>
              </div>
              MobileStore
            </h5>
            <p className="text-gray-400 text-sm leading-relaxed">
              Hệ thống bán lẻ điện thoại di động chính hãng uy tín hàng đầu. Cam
              kết chất lượng, giá cả cạnh tranh.
            </p>
          </div>

          {/* Col 2 */}
          <div>
            <h5 className="font-bold mb-4 text-gray-200">Về chúng tôi</h5>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>
                <a href="#" className="hover:text-blue-400 transition-colors">
                  Giới thiệu
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-blue-400 transition-colors">
                  Tuyển dụng
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-blue-400 transition-colors">
                  Chính sách bảo mật
                </a>
              </li>
            </ul>
          </div>

          {/* Col 3 */}
          <div>
            <h5 className="font-bold mb-4 text-gray-200">Hỗ trợ khách hàng</h5>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>
                <a href="#" className="hover:text-blue-400 transition-colors">
                  Tra cứu đơn hàng
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-blue-400 transition-colors">
                  Chính sách bảo hành
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-blue-400 transition-colors">
                  Hỏi đáp mua hàng
                </a>
              </li>
            </ul>
          </div>

          {/* Col 4 */}
          <div>
            <h5 className="font-bold mb-4 text-gray-200">Liên hệ</h5>
            <p className="text-gray-400 text-sm mb-2">Hotline: 1800.0000</p>
            <p className="text-gray-400 text-sm mb-4">Email: cskh@sigma.com</p>
            <div className="flex space-x-3">
              <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center hover:bg-blue-600 transition-colors cursor-pointer">
                <span className="font-bold text-xs">F</span>
              </div>
              <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center hover:bg-red-500 transition-colors cursor-pointer">
                <span className="font-bold text-xs">Y</span>
              </div>
              <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center hover:bg-pink-500 transition-colors cursor-pointer">
                <span className="font-bold text-xs">I</span>
              </div>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-800 pt-6 text-center">
          <p className="text-gray-500 text-xs">
            © 2025 Sigma. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
