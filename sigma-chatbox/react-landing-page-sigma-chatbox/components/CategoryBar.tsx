import React from "react";
import { BrandCategory } from "../types";

interface CategoryBarProps {
  brands: BrandCategory[];
  activeBrand: string;
  onSelectBrand: (brandId: string) => void;
}

const CategoryBar: React.FC<CategoryBarProps> = ({
  brands,
  activeBrand,
  onSelectBrand,
}) => {
  return (
    <div className="bg-white/95 backdrop-blur-sm border-b border-gray-100 sticky top-[64px] z-40 shadow-sm">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-start md:justify-center gap-4 md:gap-8 overflow-x-auto no-scrollbar py-1">
          {/* 'All' Option */}
          <div
            onClick={() => onSelectBrand("all")}
            className="flex flex-col items-center min-w-[72px] cursor-pointer group transition-all duration-300"
          >
            <div
              className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-2 shadow-sm border transition-all duration-300 group-hover:shadow-md group-hover:-translate-y-1 ${
                activeBrand === "all"
                  ? "bg-blue-600 border-blue-600 text-white shadow-blue-200 scale-105"
                  : "bg-gray-50 border-gray-200 text-gray-500 group-hover:border-blue-400 group-hover:text-blue-600"
              }`}
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
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </div>
          </div>

          {/* Brands */}
          {brands.map((brand) => (
            <div
              key={brand.id}
              onClick={() => onSelectBrand(brand.id)}
              className="flex flex-col items-center min-w-[72px] cursor-pointer group transition-all duration-300"
            >
              <div
                className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-2 shadow-sm border transition-all duration-300 group-hover:shadow-md group-hover:-translate-y-1 ${
                  activeBrand === brand.id
                    ? "bg-blue-600 border-blue-600 text-white shadow-blue-200 scale-105"
                    : "bg-white border-gray-200 text-gray-600 group-hover:border-blue-400 group-hover:text-blue-600"
                }`}
              >
                <span className="text-[10px] font-black uppercase text-center leading-tight tracking-wider">
                  {brand.name}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CategoryBar;
