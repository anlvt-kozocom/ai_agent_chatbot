import React from "react";
import { CartItem } from "../types";

interface CartDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  items: CartItem[];
  onRemove: (id: number) => void;
  onUpdateQuantity: (id: number, change: number) => void;
  total: number;
}

const CartDrawer: React.FC<CartDrawerProps> = ({
  isOpen,
  onClose,
  items,
  onRemove,
  onUpdateQuantity,
  total,
}) => {
  return (
    <div
      className={`fixed inset-0 z-[100] overflow-hidden transition-all duration-300 ${
        isOpen ? "visible" : "invisible"
      }`}
    >
      {/* Overlay */}
      <div
        className={`absolute inset-0 bg-black/50 transition-opacity duration-300 ${
          isOpen ? "opacity-100" : "opacity-0"
        }`}
        onClick={onClose}
      ></div>

      {/* Drawer */}
      <div
        className={`absolute inset-y-0 right-0 max-w-md w-full bg-white shadow-2xl transform transition-transform duration-300 flex flex-col ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Cart Header */}
        <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50">
          <h2 className="text-xl font-bold text-gray-800 flex items-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 mr-2 text-blue-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
              />
            </svg>
            Giỏ hàng ({items.reduce((acc, item) => acc + item.quantity, 0)})
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-red-500 transition-colors rounded-full hover:bg-red-50"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
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
        </div>

        {/* Cart Items */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {items.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 space-y-4">
              <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-12 w-12 text-gray-300"
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
              </div>
              <p>Giỏ hàng của bạn đang trống.</p>
              <button
                onClick={onClose}
                className="text-blue-600 font-bold hover:underline"
              >
                Tiếp tục mua sắm
              </button>
            </div>
          ) : (
            items.map((item) => (
              <div
                key={item.id}
                className="flex gap-3 items-start p-3 bg-white border border-gray-100 rounded-lg shadow-sm"
              >
                <div className="w-16 h-16 flex-shrink-0 bg-gray-50 rounded-md overflow-hidden p-2">
                  <img
                    src={item.image}
                    alt={item.name}
                    className="w-full h-full object-contain mix-blend-multiply"
                  />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-gray-900 line-clamp-2">
                    {item.name}
                  </h4>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-red-600 font-bold text-sm">
                      {new Intl.NumberFormat("vi-VN", {
                        style: "currency",
                        currency: "VND",
                      }).format(item.price)}
                    </span>
                    <div className="flex items-center border border-gray-200 rounded-lg">
                      <button
                        onClick={() => onUpdateQuantity(item.id, -1)}
                        className="w-7 h-7 flex items-center justify-center text-gray-500 hover:bg-gray-100 transition-colors text-sm"
                      >
                        -
                      </button>
                      <span className="w-8 text-center text-xs font-bold">
                        {item.quantity}
                      </span>
                      <button
                        onClick={() => onUpdateQuantity(item.id, 1)}
                        className="w-7 h-7 flex items-center justify-center text-gray-500 hover:bg-gray-100 transition-colors text-sm"
                      >
                        +
                      </button>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => onRemove(item.id)}
                  className="text-gray-400 hover:text-red-500 p-1"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </div>
            ))
          )}
        </div>

        {/* Cart Footer */}
        {items.length > 0 && (
          <div className="p-4 bg-white border-t border-gray-100 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)]">
            <div className="flex justify-between items-center mb-4">
              <span className="text-gray-600">Tổng tiền:</span>
              <span className="text-xl font-bold text-red-600">
                {new Intl.NumberFormat("vi-VN", {
                  style: "currency",
                  currency: "VND",
                }).format(total)}
              </span>
            </div>
            <button className="w-full bg-blue-600 text-white font-bold py-3 rounded-xl hover:bg-blue-700 transition-colors shadow-lg shadow-blue-200">
              Thanh Toán
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CartDrawer;
