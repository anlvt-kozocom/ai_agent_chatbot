import React, { useState, useMemo } from "react";
import Navbar from "./components/Navbar";
import CategoryBar from "./components/CategoryBar";
import BannerCarousel from "./components/BannerCarousel";
import ProductList from "./components/ProductList";
import Footer from "./components/Footer";
import ProductModal from "./components/ProductModal";
import { Chatbox } from "react-sigma-chatbox";
import "react-sigma-chatbox/dist/react-sigma-chatbox.css";
import { geminiService } from "./services/geminiService";
import { BrandCategory, Banner, Product, CartItem } from "./types";
import { productList } from "@/constants/productList";
import CartDrawer from "./components/CartDrawer";

const App: React.FC = () => {
  // State
  const [activeBrand, setActiveBrand] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [isCartOpen, setIsCartOpen] = useState<boolean>(false);
  const itemsPerPage = 20;

  // Data mocks from Sample.tsx
  const [brands] = useState<BrandCategory[]>([
    { id: "apple", name: "Apple", logo: "" },
    { id: "samsung", name: "Samsung", logo: "" },
    { id: "sony", name: "sony", logo: "" },
    { id: "realme", name: "Realme", logo: "" },
  ]);

  const [banners] = useState<Banner[]>([
    {
      id: 1,
      image:
        "https://happyphone.vn/wp-content/uploads/2024/01/iPhone-15-Pro-Max2222-1024x576.webp",
      title: "iPhone 15 Pro Max",
      subtitle: "Thiết kế Titan. Hiệu năng vượt trội.",
    },
    {
      id: 2,
      image:
        "https://snapcraze.co.za/wp-content/uploads/2024/01/s24-series-banner-1.jpeg",
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

  const [products] = useState<Product[]>(productList);

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
      vi: "**Sigma Assistant** hỗ trợ bạn mọi lúc mọi nơi",
      en: "**Sigma Assistant** supports you anytime, anywhere",
      ja: "**Sigma Assistant** はいつでもどこでもあなたをサポートします",
    },
    avatarUrl: "./public/images/sigma.png",
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

  // Pagination Logic
  React.useEffect(() => {
    setCurrentPage(1);
  }, [activeBrand, searchQuery]);

  // Cart Persistence
  React.useEffect(() => {
    const savedCart = localStorage.getItem("cart");
    if (savedCart) {
      try {
        setCartItems(JSON.parse(savedCart));
      } catch (e) {
        console.error("Failed to load cart", e);
      }
    }
  }, []);

  React.useEffect(() => {
    localStorage.setItem("cart", JSON.stringify(cartItems));
  }, [cartItems]);

  const cartCount = useMemo(() => {
    return cartItems.reduce((acc, item) => acc + item.quantity, 0);
  }, [cartItems]);

  const cartTotal = useMemo(() => {
    return cartItems.reduce((acc, item) => acc + item.price * item.quantity, 0);
  }, [cartItems]);

  const addToCart = (product: Product) => {
    setCartItems((prev) => {
      const existing = prev.find((item) => item.id === product.id);
      if (existing) {
        return prev.map((item) =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prev, { ...product, quantity: 1 }];
    });
    setIsCartOpen(true);
    setSelectedProduct(null); // Close modal when adding to cart
  };

  const removeFromCart = (productId: number) => {
    setCartItems((prev) => prev.filter((item) => item.id !== productId));
  };

  const updateQuantity = (productId: number, change: number) => {
    setCartItems((prev) =>
      prev.map((item) => {
        if (item.id === productId) {
          const newQuantity = Math.max(1, item.quantity + change);
          return { ...item, quantity: newQuantity };
        }
        return item;
      })
    );
  };

  const toggleCart = () => {
    setIsCartOpen(!isCartOpen);
  };

  const totalPages = Math.ceil(filteredProducts.length / itemsPerPage);
  const paginatedProducts = filteredProducts.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // Optional: scroll to product list
    const productListSection = document.getElementById("product-list");
    if (productListSection) {
      productListSection.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleProductClick = (product: Product) => {
    setSelectedProduct(product);
  };

  const closeProductModal = () => {
    setSelectedProduct(null);
  };

  return (
    <>
      <div className="font-sans text-gray-800 bg-gray-50 min-h-screen flex flex-col">
        <Navbar
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          onResetBrand={handleResetBrand}
          cartCount={cartCount}
          onToggleCart={toggleCart}
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
          <div id="product-list">
            <ProductList
              products={paginatedProducts}
              activeBrand={activeBrand}
              getBrandName={getBrandName}
              onResetBrand={handleResetBrand}
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
              onProductClick={handleProductClick}
            />
          </div>
        </main>

        <Footer />
        <ProductModal
          product={selectedProduct}
          onClose={closeProductModal}
          onAddToCart={addToCart}
        />
        <CartDrawer
          isOpen={isCartOpen}
          onClose={toggleCart}
          items={cartItems}
          onRemove={removeFromCart}
          onUpdateQuantity={updateQuantity}
          total={cartTotal}
        />
      </div>
      <Chatbox config={config} onGetAiResponse={handleAiResponse} />
    </>
  );
};

export default App;
