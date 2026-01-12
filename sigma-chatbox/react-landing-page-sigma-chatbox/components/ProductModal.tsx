import React from "react";
import { Product } from "../types";

interface ProductModalProps {
  product: Product | null;
  onClose: () => void;
}

const ProductModal: React.FC<ProductModalProps> = ({ product, onClose }) => {
  if (!product) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center m-5 p-4 max-h-[90vh] overflow-y-auto"
      aria-labelledby="modal-title"
      role="dialog"
      aria-modal="true"
    >
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 transition-opacity backdrop-blur-sm"
        onClick={onClose}
      ></div>

      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl overflow-hidden transform transition-all flex  md:flex-row animate-fadeIn max-h-[90vh]">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 p-2 bg-white/80 rounded-full hover:bg-gray-100 transition-colors shadow-sm"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6 text-gray-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        <div className="w-full md:w-1/2 bg-gray-50 p-6 flex items-center justify-center relative">
          <div className="absolute inset-0 bg-blue-50/50 rounded-full scale-75 blur-3xl opacity-50"></div>
          <img
            src={product.image}
            alt={product.name}
            className="relative z-10 w-full max-w-[240px] md:max-w-xs object-contain mix-blend-multiply hover:scale-110 transition-transform duration-500"
          />
        </div>

        {/* Content Section */}
        <div className="w-full md:w-1/2 p-5 md:p-6 flex flex-col max-h-[90vh] overflow-y-auto">
          <div className="mb-4">
            <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 text-[10px] md:text-xs font-bold rounded-full uppercase tracking-wide mb-2">
              {product.brand}
            </span>
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900 leading-tight mb-2">
              {product.name}
            </h2>

            {/* Rating in Modal */}
            <div className="flex items-center mb-4">
              <div className="flex text-yellow-400">
                {[1, 2, 3, 4, 5].map((star) => (
                  <svg
                    key={star}
                    xmlns="http://www.w3.org/2000/svg"
                    className={`h-5 w-5 ${
                      star > product.rating ? "text-gray-300" : ""
                    }`}
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}
              </div>
              <span className="text-gray-500 text-sm ml-2">
                ({product.reviews} đánh giá)
              </span>
            </div>

            {/* Price */}
            <div className="flex items-end gap-3 mb-6">
              <span className="text-3xl font-bold text-red-600">
                {new Intl.NumberFormat("vi-VN", {
                  style: "currency",
                  currency: "VND",
                }).format(product.price)}
              </span>
              {product.discount > 0 && (
                <>
                  <span className="text-lg text-gray-400 line-through mb-1">
                    {new Intl.NumberFormat("vi-VN", {
                      style: "currency",
                      currency: "VND",
                    }).format(product.originalPrice)}
                  </span>
                  <span className="text-sm font-bold text-red-500 mb-2 bg-red-50 px-2 py-0.5 rounded">
                    -{product.discount}%
                  </span>
                </>
              )}
            </div>

            <p className="text-gray-600 mb-6 leading-relaxed text-sm">
              {product.description ||
                `Sản phẩm chính hãng ${product.brand}. Thiết kế sang trọng, hiệu năng mạnh mẽ. Bảo hành 12 tháng chính hãng. 1 đổi 1 trong 30 ngày đầu nếu có lỗi nhà sản xuất.`}
            </p>

            {/* Mock Specs */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8 text-sm text-gray-600 bg-gray-50 p-4 rounded-xl border border-gray-100">
              <div className="flex items-center gap-2">
                <svg
                  className="w-5 h-5 text-blue-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
                  />
                </svg>
                <span>Chipset hiệu năng cao</span>
              </div>
              <div className="flex items-center gap-2">
                <svg
                  className="w-5 h-5 text-green-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
                  />
                </svg>
                <span>Pin 5000 mAh</span>
              </div>
              <div className="flex items-center gap-2">
                <svg
                  className="w-5 h-5 text-purple-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
                <span>Camera AI sắc nét</span>
              </div>
              <div className="flex items-center gap-2">
                <svg
                  className="w-5 h-5 text-orange-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <span>Bảo hành 12 tháng</span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-auto flex gap-3 md:gap-4 flex-col sm:flex-row">
            <button className="flex-1 bg-white border-2 border-blue-600 text-blue-600 hover:bg-blue-50 font-bold py-3 px-6 rounded-xl transition-colors flex items-center justify-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
                />
              </svg>
              Thêm vào giỏ
            </button>
            <button className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold py-3 px-6 rounded-xl shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all flex items-center justify-center gap-2">
              Mua ngay
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M13 7l5 5m0 0l-5 5m5-5H6"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductModal;
