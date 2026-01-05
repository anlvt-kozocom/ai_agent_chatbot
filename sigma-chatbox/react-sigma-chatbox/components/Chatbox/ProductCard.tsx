
import React from 'react';
import { Product } from '../../types';

interface ProductCardProps {
  product: Product;
  primaryColor: string;
}

export const ProductCard: React.FC<ProductCardProps> = ({ product, primaryColor }) => {
  return (
    <div className="min-w-[170px] max-w-[170px] bg-white rounded-xl border border-gray-50 shadow-sm overflow-hidden flex flex-col hover:shadow-lg transition-all duration-300 group">
      <div className="relative h-32 w-full bg-white flex items-center justify-center p-2">
        <img 
          src={product.image} 
          alt={product.name} 
          className="h-full w-full object-contain group-hover:scale-105 transition-transform duration-500"
        />
        {product.discount && (
          <div className="absolute top-2 left-2 bg-red-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded-md shadow-sm">
            {product.discount}
          </div>
        )}
      </div>
      <div className="p-3 flex-1 flex flex-col justify-between border-t border-gray-50">
        <div>
          <h4 className="text-[11px] font-bold text-gray-800 line-clamp-2 min-h-[30px] mb-1.5 group-hover:text-red-600 transition-colors">
            {product.name}
          </h4>
          <div className="mb-2">
            <span className="text-red-600 font-extrabold text-[13px]">{product.price}</span>
            {product.oldPrice && (
              <span className="text-[10px] text-gray-400 line-through ml-1 block opacity-60">{product.oldPrice}</span>
            )}
          </div>
        </div>
        <button 
          className="w-full py-1.5 rounded-lg text-[11px] font-bold border transition-all duration-300 active:scale-95 shadow-sm"
          style={{ borderColor: primaryColor, color: primaryColor }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = primaryColor;
            e.currentTarget.style.color = 'white';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
            e.currentTarget.style.color = primaryColor;
          }}
        >
          Chọn mua
        </button>
      </div>
    </div>
  );
};