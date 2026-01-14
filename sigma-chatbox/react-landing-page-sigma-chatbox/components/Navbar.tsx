import React, { useState } from "react";
import { BrandCategory } from "../types";

interface NavbarProps {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  onResetBrand: () => void;
  cartCount: number;
  onToggleCart: () => void;
}

const Navbar: React.FC<NavbarProps> = ({
  searchQuery,
  setSearchQuery,
  onResetBrand,
  cartCount,
  onToggleCart,
}) => {
  return (
    <header className="sticky top-0 z-50 bg-blue-600 shadow-lg">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between gap-4">
          <div
            onClick={onResetBrand}
            className="flex items-center cursor-pointer group select-none"
          >
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center mr-2 shadow-sm group-hover:rotate-12 transition-transform">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6 text-blue-600"
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
            <span className="text-white font-bold text-xl tracking-tight sm:block">
              MobileStore
            </span>
          </div>

          <div className="flex-1 max-w-xl relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm kiếm điện thoại, phụ kiện..."
              className="w-full py-2.5 pl-4 pr-10 rounded-lg border-none focus:ring-2 focus:ring-yellow-400 outline-none text-sm transition-shadow shadow-sm"
            />
            <button className="absolute right-2 top-1/2 transform -translate-y-1/2 text-blue-600 bg-yellow-400 p-1.5 rounded-md hover:bg-yellow-300 transition-colors">
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
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </button>
          </div>

          {/* Icons Actions */}
          <div className="flex items-center space-x-4 text-white">
            <div className="hidden md:flex flex-col items-center cursor-pointer hover:text-yellow-300 transition-colors">
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
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
              <span className="text-xs mt-1">Tài khoản</span>
            </div>
            <div
              onClick={onToggleCart}
              className="flex flex-col items-center cursor-pointer hover:text-yellow-300 transition-colors relative"
            >
              <div className="relative">
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
                    d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
                  />
                </svg>
                {cartCount > 0 && (
                  <span className="absolute -top-2 -right-2 bg-yellow-400 text-blue-800 text-[10px] font-bold px-1.5 py-0.5 rounded-full animate-bounce">
                    {cartCount}
                  </span>
                )}
              </div>
              <span className="text-xs mt-1 hidden sm:block">Giỏ hàng</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
