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
