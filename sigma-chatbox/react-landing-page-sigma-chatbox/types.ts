export interface Product {
  id: number;
  name: string;
  brand: string;
  brandId: string;
  price: number;
  originalPrice: number;
  image: string;
  rating: number;
  reviews: number;
  discount: number;
  description?: string;
  isHot?: boolean;
}

export interface BrandCategory {
  id: string;
  name: string;
  logo: string;
}

export interface Banner {
  id: number;
  image: string;
  title: string;
  subtitle: string;
}

export interface CartItem extends Product {
  quantity: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}
