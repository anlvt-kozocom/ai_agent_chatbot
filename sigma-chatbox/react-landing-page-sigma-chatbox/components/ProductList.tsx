import React from "react";
import { Product } from "../types";

interface ProductListProps {
  products: Product[];
  activeBrand: string;
  getBrandName: (id: string) => string;
  onResetBrand: () => void;
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  onProductClick: (product: Product) => void;
}

const ProductList: React.FC<ProductListProps> = ({
  products,
  activeBrand,
  getBrandName,
  onResetBrand,
  currentPage,
  totalPages,
  onPageChange,
  onProductClick,
}) => {
  return (
    <section>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-2xl font-bold text-gray-800 border-l-4 border-blue-600 pl-3">
          {activeBrand === "all"
            ? "Điện Thoại Nổi Bật"
            : "Điện thoại " + getBrandName(activeBrand)}
        </h3>

        {activeBrand !== "all" ? (
          <button
            onClick={onResetBrand}
            className="text-gray-500 hover:text-blue-600 text-sm flex items-center"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4 mr-1"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            Quay lại tất cả
          </button>
        ) : (
          <a
            href="#"
            className="text-blue-600 text-sm font-semibold hover:underline flex items-center"
          >
            Xem tất cả
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4 ml-1"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9 5l7 7-7 7"
              />
            </svg>
          </a>
        )}
      </div>

      {/* Product Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 mb-8">
        {products.map((product) => (
          <div
            onClick={() => onProductClick(product)}
            key={product.id}
            className="bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100 overflow-hidden group flex flex-col relative h-full"
          >
            {/* Discount Badge */}
            {product.discount > 0 && (
              <div className="absolute top-2 left-2 z-10 bg-red-500 text-white text-[10px] font-bold px-2 py-1 rounded-full shadow-md">
                -{product.discount}%
              </div>
            )}
            {product.isHot && (
              <div className="absolute top-2 right-2 z-10 bg-yellow-400 text-blue-900 text-[10px] font-bold px-2 py-1 rounded-full shadow-md flex items-center">
                <span className="mr-1">🔥</span> HOT
              </div>
            )}

            {/* Product Image */}
            <div className="relative w-full pt-[100%] overflow-hidden bg-gray-50">
              <img
                src={product.image}
                alt={product.name}
                className="absolute inset-0 w-full h-full object-contain p-6 group-hover:scale-110 transition-transform duration-500 mix-blend-multiply"
              />
            </div>

            {/* Product Info */}
            <div className="p-4 flex flex-col flex-grow">
              <div className="mb-1">
                <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">
                  {product.brand}
                </span>
              </div>
              <h4 className="font-medium text-gray-800 text-sm md:text-base mb-2 line-clamp-2 min-h-[40px] group-hover:text-blue-600 transition-colors">
                {product.name}
              </h4>

              <div className="mt-auto">
                {/* Price */}
                <div className="flex flex-col mb-2">
                  <span className="text-red-600 font-bold text-base md:text-lg">
                    {new Intl.NumberFormat("vi-VN", {
                      style: "currency",
                      currency: "VND",
                    }).format(product.price)}
                  </span>
                  {product.discount > 0 && (
                    <span className="text-gray-400 text-xs line-through">
                      {new Intl.NumberFormat("vi-VN", {
                        style: "currency",
                        currency: "VND",
                      }).format(product.originalPrice)}
                    </span>
                  )}
                </div>

                {/* Rating */}
                <div className="flex items-center mb-3">
                  <div className="flex text-yellow-400 text-xs">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <svg
                        key={star}
                        xmlns="http://www.w3.org/2000/svg"
                        className={`h-3 w-3 ${
                          star > product.rating ? "text-gray-300" : ""
                        }`}
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                  </div>
                  <span className="text-xs text-gray-500 ml-1">
                    ({product.reviews})
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}

        {products.length === 0 && (
          <div className="col-span-full py-20 text-center">
            <p className="text-gray-500 text-lg">
              Không tìm thấy sản phẩm nào.
            </p>
          </div>
        )}
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex justify-center mt-8 gap-2">
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className={`px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
              currentPage === 1
                ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                : "bg-white text-gray-700 hover:bg-gray-50 hover:text-blue-600 border-gray-200"
            }`}
          >
            Trước
          </button>

          {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
            <button
              key={page}
              onClick={() => onPageChange(page)}
              className={`w-10 h-10 rounded-lg text-sm font-bold transition-all ${
                currentPage === page
                  ? "bg-blue-600 text-white shadow-blue-200 shadow-md transform scale-105"
                  : "bg-white text-gray-600 hover:bg-gray-50 border border-gray-200"
              }`}
            >
              {page}
            </button>
          ))}

          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className={`px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
              currentPage === totalPages
                ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                : "bg-white text-gray-700 hover:bg-gray-50 hover:text-blue-600 border-gray-200"
            }`}
          >
            Sau
          </button>
        </div>
      )}
    </section>
  );
};

export default ProductList;
