import React, { useState, useMemo } from "react";
import Navbar from "./components/Navbar";
import CategoryBar from "./components/CategoryBar";
import BannerCarousel from "./components/BannerCarousel";
import ProductList from "./components/ProductList";
import Footer from "./components/Footer";
import { Chatbox } from "react-sigma-chatbox";
import "react-sigma-chatbox/dist/react-sigma-chatbox.css";
import { geminiService } from "./services/geminiService";
import { BrandCategory, Banner, Product } from "./types";

const App: React.FC = () => {
  // State
  const [activeBrand, setActiveBrand] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Data mocks from Sample.tsx
  const [brands] = useState<BrandCategory[]>([
    { id: "apple", name: "Apple", logo: "" },
    { id: "samsung", name: "Samsung", logo: "" },
    { id: "xiaomi", name: "Xiaomi", logo: "" },
    { id: "oppo", name: "OPPO", logo: "" },
    { id: "vivo", name: "Vivo", logo: "" },
    { id: "realme", name: "Realme", logo: "" },
    { id: "asus", name: "Asus", logo: "" },
    { id: "nokia", name: "Nokia", logo: "" },
  ]);

  const [banners] = useState<Banner[]>([
    {
      id: 1,
      image:
        "https://images.unsplash.com/photo-1556656793-02715d8dd660?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
      title: "iPhone 15 Pro Max",
      subtitle: "Thiết kế Titan. Hiệu năng vượt trội.",
    },
    {
      id: 2,
      image:
        "https://images.unsplash.com/photo-1610945265078-386f3b58d86f?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
      title: "Samsung Galaxy S24 Ultra",
      subtitle: "Quyền năng AI trong tay bạn.",
    },
    {
      id: 3,
      image:
        "https://images.unsplash.com/photo-1519389950473-47ba0277781c?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
      title: "Tuần Lễ Công Nghệ",
      subtitle: "Giảm đến 40% cho các sản phẩm Laptop & Tablet",
    },
  ]);

  const [products] = useState<Product[]>([
    {
      id: 1,
      name: "iPhone 15 Pro Max 256GB",
      brand: "Apple",
      brandId: "apple",
      price: 28990000,
      originalPrice: 34990000,
      image:
        "https://images.unsplash.com/photo-1695046058804-1913c12140dd?w=500&auto=format&fit=crop&q=60",
      rating: 5,
      reviews: 128,
      discount: 17,
      isHot: true,
    },
    {
      id: 2,
      name: "Samsung Galaxy S24 Ultra 5G",
      brand: "Samsung",
      brandId: "samsung",
      price: 29990000,
      originalPrice: 33990000,
      image:
        "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500&auto=format&fit=crop&q=60",
      rating: 4.8,
      reviews: 85,
      discount: 12,
      isHot: true,
    },
    {
      id: 3,
      name: "Xiaomi 14 5G 12GB/256GB",
      brand: "Xiaomi",
      brandId: "xiaomi",
      price: 19990000,
      originalPrice: 22990000,
      image:
        "https://images.unsplash.com/photo-1598327105666-5b89351aff70?w=500&auto=format&fit=crop&q=60",
      rating: 4.5,
      reviews: 42,
      discount: 13,
    },
    {
      id: 4,
      name: "OPPO Reno10 Pro+ 5G",
      brand: "OPPO",
      brandId: "oppo",
      price: 13990000,
      originalPrice: 15490000,
      image:
        "https://images.unsplash.com/photo-1592899677712-a170135c7993?w=500&auto=format&fit=crop&q=60",
      rating: 4.6,
      reviews: 30,
      discount: 10,
    },
    {
      id: 5,
      name: "iPhone 13 128GB VN/A",
      brand: "Apple",
      brandId: "apple",
      price: 13990000,
      originalPrice: 16990000,
      image:
        "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=500&auto=format&fit=crop&q=60",
      rating: 4.9,
      reviews: 1240,
      discount: 18,
    },
    {
      id: 6,
      name: "Samsung Galaxy A55 5G",
      brand: "Samsung",
      brandId: "samsung",
      price: 9690000,
      originalPrice: 10690000,
      image:
        "https://images.unsplash.com/photo-1533228122081-3853f86e6ba5?w=500&auto=format&fit=crop&q=60",
      rating: 4.2,
      reviews: 15,
      discount: 9,
    },
    {
      id: 7,
      name: "Realme 11 Pro+ 5G",
      brand: "Realme",
      brandId: "realme",
      price: 8990000,
      originalPrice: 9990000,
      image:
        "https://images.unsplash.com/photo-1589492477829-5e65395b66cc?w=500&auto=format&fit=crop&q=60",
      rating: 4.0,
      reviews: 12,
      discount: 10,
    },
    {
      id: 8,
      name: "Xiaomi Redmi Note 13",
      brand: "Xiaomi",
      brandId: "xiaomi",
      price: 4590000,
      originalPrice: 5290000,
      image:
        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&auto=format&fit=crop&q=60",
      rating: 4.7,
      reviews: 320,
      discount: 13,
      isHot: true,
    },
  ]);

  const config = {
    primaryColor: "#6366f1",
    botName: "Sigma Assistant",
    welcomeMessage: {
      vi: "Chào bạn! Tôi có thể giúp gì cho bạn?",
      en: "Hello! How can I help you today?",
      ja: "こんにちは！今日はどのようなお手伝いができますか？",
    },
    placeholder: {
      vi: "Nhập tin nhắn...",
      en: "Type a message...",
      ja: "メッセージを入力してください...",
    },
    quickReplies: {
      vi: ["Giá iPhone 15", "Bảo hành"],
      en: ["iPhone 15 Price", "Warranty"],
      ja: ["iPhone 15の価格", "保証"],
    },
    description: {
      vi: '**Sigma Assistant** hỗ trợ bạn mọi lúc mọi nơi',
      en: '**Sigma Assistant** supports you anytime, anywhere',
      ja: '**Sigma Assistant** はいつでもどこでもあなたをサポートします',
    },
    avatarUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=Sigma",
    renderMarkdown: true,
  };

  const handleAiResponse = (
    input: string,
    threadId: string,
    language: string
  ) => geminiService.getChatResponseStream(input, threadId, language);

  const handleResetBrand = () => {
    setActiveBrand("all");
  };

  const getBrandName = (id: string) => {
    return brands.find((b) => b.id === id)?.name || "";
  };

  // Filter logic
  const filteredProducts = useMemo(() => {
    const query = searchQuery.toLowerCase();
    return products.filter((p) => {
      const matchesBrand = activeBrand === "all" || p.brandId === activeBrand;
      const matchesSearch =
        p.name.toLowerCase().includes(query) ||
        p.brand.toLowerCase().includes(query);
      return matchesBrand && matchesSearch;
    });
  }, [products, activeBrand, searchQuery]);

  return (
    <>
      <div className="font-sans text-gray-800 bg-gray-50 min-h-screen flex flex-col">
        <Navbar
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          onResetBrand={handleResetBrand}
        />

        <CategoryBar
          brands={brands}
          activeBrand={activeBrand}
          onSelectBrand={setActiveBrand}
        />

        {/* MAIN CONTENT */}
        <main className="flex-grow container mx-auto px-4 py-6 space-y-8">
          {/* CAROUSEL BANNER */}
          {activeBrand === "all" && <BannerCarousel banners={banners} />}

          {/* PRODUCT CATEGORIES / LIST */}
          <ProductList
            products={filteredProducts}
            activeBrand={activeBrand}
            getBrandName={getBrandName}
            onResetBrand={handleResetBrand}
          />
        </main>

        <Footer />
      </div>
      <Chatbox config={config} onGetAiResponse={handleAiResponse} />
    </>
  );
};

export default App;
