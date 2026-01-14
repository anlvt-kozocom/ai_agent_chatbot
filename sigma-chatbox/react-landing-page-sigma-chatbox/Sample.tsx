import {
  Component,
  OnInit,
  OnDestroy,
  signal,
  computed,
  effect,
} from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";

// --- Interfaces ---
interface Product {
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

interface CartItem extends Product {
  quantity: number;
}

interface BrandCategory {
  id: string;
  name: string;
  logo: string;
}

interface Banner {
  id: number;
  image: string;
  title: string;
  subtitle: string;
}

@Component({
  selector: "app-root",
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div
      class="font-sans text-gray-800 bg-gray-50 min-h-screen flex flex-col relative overflow-x-hidden"
    >
      <!-- HEADER Section -->
      <header class="sticky top-0 z-40 bg-blue-600 shadow-lg">
        <div class="container mx-auto px-4 py-3">
          <div class="flex items-center justify-between gap-4">
            <!-- Logo -->
            <div
              (click)="selectBrand('all')"
              class="flex items-center cursor-pointer group select-none"
            >
              <div
                class="w-10 h-10 bg-white rounded-full flex items-center justify-center mr-2 shadow-sm group-hover:rotate-12 transition-transform"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-6 w-6 text-blue-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <span
                class="text-white font-bold text-xl tracking-tight hidden sm:block"
                >MobileStore</span
              >
            </div>

            <!-- Search Bar -->
            <div class="flex-1 max-w-xl relative">
              <input
                type="text"
                [(ngModel)]="searchQuery"
                placeholder="Tìm kiếm điện thoại, phụ kiện..."
                class="w-full py-2.5 pl-4 pr-10 rounded-lg border-none focus:ring-2 focus:ring-yellow-400 outline-none text-sm transition-shadow shadow-sm"
              />
              <button
                class="absolute right-2 top-1/2 transform -translate-y-1/2 text-blue-600 bg-yellow-400 p-1.5 rounded-md hover:bg-yellow-300 transition-colors"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </button>
            </div>

            <!-- Icons Actions -->
            <div class="flex items-center space-x-4 text-white">
              <div
                class="hidden md:flex flex-col items-center cursor-pointer hover:text-yellow-300 transition-colors"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
                <span class="text-xs mt-1">Tài khoản</span>
              </div>

              <!-- Cart Icon with Click Action -->
              <div
                (click)="toggleCart()"
                class="flex flex-col items-center cursor-pointer hover:text-yellow-300 transition-colors relative"
              >
                <div class="relative">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-6 w-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
                    />
                  </svg>
                  <!-- Dynamic Cart Count -->
                  @if (cartCount() > 0) {
                  <span
                    class="absolute -top-2 -right-2 bg-yellow-400 text-blue-800 text-[10px] font-bold px-1.5 py-0.5 rounded-full animate-bounce-short"
                    >{{ cartCount() }}</span
                  >
                  }
                </div>
                <span class="text-xs mt-1 hidden sm:block">Giỏ hàng</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- CATEGORY BAR -->
      <div
        class="bg-white/95 backdrop-blur-sm border-b border-gray-100 sticky top-[64px] z-30 shadow-sm"
      >
        <div class="container mx-auto px-4 py-3">
          <div
            class="flex items-center justify-start md:justify-center gap-4 md:gap-8 overflow-x-auto no-scrollbar pb-1"
          >
            <div
              (click)="selectBrand('all')"
              class="flex flex-col items-center min-w-[72px] cursor-pointer group transition-all duration-300"
            >
              <div
                class="w-14 h-14 rounded-2xl flex items-center justify-center mb-2 shadow-sm border transition-all duration-300 group-hover:shadow-md group-hover:-translate-y-1"
                [ngClass]="
                  activeBrand() === 'all'
                    ? 'bg-blue-600 border-blue-600 text-white shadow-blue-200 scale-105'
                    : 'bg-gray-50 border-gray-200 text-gray-500 group-hover:border-blue-400 group-hover:text-blue-600'
                "
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              </div>
              <span
                class="text-xs font-bold transition-colors duration-300"
                [ngClass]="
                  activeBrand() === 'all'
                    ? 'text-blue-600'
                    : 'text-gray-500 group-hover:text-blue-600'
                "
                >Tất cả</span
              >
            </div>
            @for (brand of brands(); track brand.id) {
            <div
              (click)="selectBrand(brand.id)"
              class="flex flex-col items-center min-w-[72px] cursor-pointer group transition-all duration-300"
            >
              <div
                class="w-14 h-14 rounded-2xl flex items-center justify-center mb-2 shadow-sm border transition-all duration-300 group-hover:shadow-md group-hover:-translate-y-1"
                [ngClass]="
                  activeBrand() === brand.id
                    ? 'bg-blue-600 border-blue-600 text-white shadow-blue-200 scale-105'
                    : 'bg-white border-gray-200 text-gray-600 group-hover:border-blue-400 group-hover:text-blue-600'
                "
              >
                <span
                  class="text-[10px] font-black uppercase text-center leading-tight tracking-wider"
                  >{{ brand.name }}</span
                >
              </div>
              <span
                class="text-xs font-bold transition-colors duration-300"
                [ngClass]="
                  activeBrand() === brand.id
                    ? 'text-blue-600'
                    : 'text-gray-500 group-hover:text-blue-600'
                "
                >{{ brand.name }}</span
              >
            </div>
            }
          </div>
        </div>
      </div>

      <!-- MAIN CONTENT -->
      <main class="flex-grow container mx-auto px-4 py-6 space-y-8">
        <!-- CAROUSEL BANNER -->
        @if (activeBrand() === 'all') {
        <section
          class="relative w-full h-[180px] md:h-[350px] rounded-2xl overflow-hidden shadow-lg group"
        >
          @for (banner of banners(); track banner.id; let i = $index) {
          <div
            class="absolute inset-0 w-full h-full transition-opacity duration-700 ease-in-out"
            [class.opacity-100]="currentSlide() === i"
            [class.opacity-0]="currentSlide() !== i"
          >
            <img
              [src]="banner.image"
              [alt]="banner.title"
              class="w-full h-full object-cover"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex flex-col justify-end p-6 md:p-10"
            >
              <h2
                class="text-white text-2xl md:text-4xl font-bold mb-2 transform translate-y-4 opacity-0 transition-all duration-700 delay-100"
                [class.animate-slide-up]="currentSlide() === i"
              >
                {{ banner.title }}
              </h2>
              <p
                class="text-gray-200 text-sm md:text-lg transform translate-y-4 opacity-0 transition-all duration-700 delay-200"
                [class.animate-slide-up]="currentSlide() === i"
              >
                {{ banner.subtitle }}
              </p>
            </div>
          </div>
          }
          <button
            (click)="prevSlide()"
            class="absolute left-4 top-1/2 -translate-y-1/2 bg-white/30 hover:bg-white/80 p-2 rounded-full backdrop-blur-sm transition-all opacity-0 group-hover:opacity-100 focus:outline-none"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-gray-800"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </button>
          <button
            (click)="nextSlide()"
            class="absolute right-4 top-1/2 -translate-y-1/2 bg-white/30 hover:bg-white/80 p-2 rounded-full backdrop-blur-sm transition-all opacity-0 group-hover:opacity-100 focus:outline-none"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-gray-800"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              />
            </svg>
          </button>
          <div
            class="absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-2"
          >
            @for (banner of banners(); track banner.id; let i = $index) {
            <button
              (click)="goToSlide(i)"
              class="w-2 h-2 md:w-3 md:h-3 rounded-full transition-all duration-300"
              [ngClass]="
                currentSlide() === i ? 'bg-yellow-400 w-6' : 'bg-white/50'
              "
            ></button>
            }
          </div>
        </section>
        }

        <!-- PRODUCT LIST -->
        <section>
          <div class="flex items-center justify-between mb-6">
            <h3
              class="text-2xl font-bold text-gray-800 border-l-4 border-blue-600 pl-3"
            >
              {{
                activeBrand() === "all"
                  ? "Điện Thoại Nổi Bật"
                  : "Điện thoại " + getBrandName(activeBrand())
              }}
            </h3>
            @if (activeBrand() !== 'all') {
            <button
              (click)="selectBrand('all')"
              class="text-gray-500 hover:text-blue-600 text-sm flex items-center"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 mr-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              Quay lại tất cả
            </button>
            } @else {
            <a
              href="#"
              class="text-blue-600 text-sm font-semibold hover:underline flex items-center"
              >Xem tất cả
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 ml-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                /></svg
            ></a>
            }
          </div>

          <div
            class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4"
          >
            @for (product of filteredProducts(); track product.id) {
            <div
              (click)="openProductModal(product)"
              class="bg-white cursor-pointer rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100 overflow-hidden group flex flex-col relative h-full"
            >
              @if (product.discount > 0) {
              <div
                class="absolute top-2 left-2 z-10 bg-red-500 text-white text-[10px] font-bold px-2 py-1 rounded-full shadow-md"
              >
                -{{ product.discount }}%
              </div>
              } @if (product.isHot) {
              <div
                class="absolute top-2 right-2 z-10 bg-yellow-400 text-blue-900 text-[10px] font-bold px-2 py-1 rounded-full shadow-md flex items-center"
              >
                <span class="mr-1">🔥</span> HOT
              </div>
              }
              <div class="relative w-full pt-[100%] overflow-hidden bg-gray-50">
                <img
                  [src]="product.image"
                  [alt]="product.name"
                  class="absolute inset-0 w-full h-full object-contain p-6 group-hover:scale-110 transition-transform duration-500 mix-blend-multiply"
                />
              </div>
              <div class="p-4 flex flex-col flex-grow">
                <div class="mb-1">
                  <span
                    class="text-[10px] uppercase font-bold text-gray-400 tracking-wider"
                    >{{ product.brand }}</span
                  >
                </div>
                <h4
                  class="font-medium text-gray-800 text-sm md:text-base mb-2 line-clamp-2 min-h-[40px] group-hover:text-blue-600 transition-colors"
                >
                  {{ product.name }}
                </h4>
                <div class="mt-auto">
                  <div class="flex flex-col mb-2">
                    <span class="text-red-600 font-bold text-base md:text-lg"
                      >{{ product.price | number : "1.0-0" }}₫</span
                    >
                    @if (product.discount > 0) {
                    <span class="text-gray-400 text-xs line-through"
                      >{{ product.originalPrice | number : "1.0-0" }}₫</span
                    >
                    }
                  </div>
                  <div class="flex items-center mb-3">
                    <div class="flex text-yellow-400 text-xs">
                      @for (star of [1,2,3,4,5]; track star) {
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-3 w-3"
                        [class.text-gray-300]="star > product.rating"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path
                          d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                        />
                      </svg>
                      }
                    </div>
                    <span class="text-xs text-gray-500 ml-1"
                      >({{ product.reviews }})</span
                    >
                  </div>
                </div>
              </div>
            </div>
            } @if (filteredProducts().length === 0) {
            <div class="col-span-full py-20 text-center">
              <p class="text-gray-500 text-lg">Không tìm thấy sản phẩm nào.</p>
            </div>
            }
          </div>
        </section>
      </main>

      <!-- SIMPLIFIED FOOTER -->
      <footer class="bg-slate-900 text-white pt-10 pb-6 mt-10">
        <div class="container mx-auto px-4">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <h5 class="text-lg font-bold mb-4 flex items-center">
                <div
                  class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center mr-2"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-4 w-4 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
                    />
                  </svg>
                </div>
                MobileStore
              </h5>
              <p class="text-gray-400 text-sm leading-relaxed">
                Hệ thống bán lẻ điện thoại di động chính hãng uy tín hàng đầu.
                Cam kết chất lượng, giá cả cạnh tranh.
              </p>
            </div>
            <div>
              <h5 class="font-bold mb-4 text-gray-200">Về chúng tôi</h5>
              <ul class="space-y-2 text-sm text-gray-400">
                <li>
                  <a href="#" class="hover:text-blue-400 transition-colors"
                    >Giới thiệu</a
                  >
                </li>
                <li>
                  <a href="#" class="hover:text-blue-400 transition-colors"
                    >Tuyển dụng</a
                  >
                </li>
                <li>
                  <a href="#" class="hover:text-blue-400 transition-colors"
                    >Chính sách bảo mật</a
                  >
                </li>
              </ul>
            </div>
            <div>
              <h5 class="font-bold mb-4 text-gray-200">Hỗ trợ khách hàng</h5>
              <ul class="space-y-2 text-sm text-gray-400">
                <li>
                  <a href="#" class="hover:text-blue-400 transition-colors"
                    >Tra cứu đơn hàng</a
                  >
                </li>
                <li>
                  <a href="#" class="hover:text-blue-400 transition-colors"
                    >Chính sách bảo hành</a
                  >
                </li>
                <li>
                  <a href="#" class="hover:text-blue-400 transition-colors"
                    >Hỏi đáp mua hàng</a
                  >
                </li>
              </ul>
            </div>
            <div>
              <h5 class="font-bold mb-4 text-gray-200">Liên hệ</h5>
              <p class="text-gray-400 text-sm mb-2">Hotline: 1800.0000</p>
              <p class="text-gray-400 text-sm mb-4">
                Email: cskh@mobilestore.com
              </p>
              <div class="flex space-x-3">
                <div
                  class="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center hover:bg-blue-600 transition-colors cursor-pointer"
                >
                  <span class="font-bold text-xs">F</span>
                </div>
                <div
                  class="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center hover:bg-red-500 transition-colors cursor-pointer"
                >
                  <span class="font-bold text-xs">Y</span>
                </div>
                <div
                  class="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center hover:bg-pink-500 transition-colors cursor-pointer"
                >
                  <span class="font-bold text-xs">I</span>
                </div>
              </div>
            </div>
          </div>
          <div class="border-t border-gray-800 pt-6 text-center">
            <p class="text-gray-500 text-xs">
              © 2024 MobileStore. All rights reserved.
            </p>
          </div>
        </div>
      </footer>

      <!-- PRODUCT MODAL -->
      @if (selectedProduct(); as product) {
      <div
        class="fixed inset-0 z-[100] flex items-center justify-center p-4"
        aria-labelledby="modal-title"
        role="dialog"
        aria-modal="true"
      >
        <div
          class="fixed inset-0 bg-black/60 transition-opacity backdrop-blur-sm"
          (click)="closeProductModal()"
        ></div>
        <div
          class="relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl overflow-hidden transform transition-all flex flex-col md:flex-row animate-fadeIn"
        >
          <button
            (click)="closeProductModal()"
            class="absolute top-4 right-4 z-10 p-2 bg-white/80 rounded-full hover:bg-gray-100 transition-colors shadow-sm"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-gray-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
          <div
            class="w-full md:w-1/2 bg-gray-50 p-8 flex items-center justify-center relative"
          >
            <div
              class="absolute inset-0 bg-blue-50/50 rounded-full scale-75 blur-3xl opacity-50"
            ></div>
            <img
              [src]="product.image"
              [alt]="product.name"
              class="relative z-10 w-full max-w-[280px] md:max-w-sm object-contain mix-blend-multiply hover:scale-110 transition-transform duration-500"
            />
          </div>
          <div
            class="w-full md:w-1/2 p-6 md:p-8 flex flex-col max-h-[90vh] overflow-y-auto"
          >
            <div class="mb-4">
              <span
                class="inline-block px-3 py-1 bg-blue-100 text-blue-800 text-[10px] md:text-xs font-bold rounded-full uppercase tracking-wide mb-2"
                >{{ product.brand }}</span
              >
              <h2
                class="text-2xl md:text-3xl font-bold text-gray-900 leading-tight mb-2"
              >
                {{ product.name }}
              </h2>
              <div class="flex items-center mb-4">
                <div class="flex text-yellow-400">
                  @for (star of [1,2,3,4,5]; track star) {
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    [class.text-gray-300]="star > product.rating"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                    />
                  </svg>
                  }
                </div>
                <span class="text-gray-500 text-sm ml-2"
                  >({{ product.reviews }} đánh giá)</span
                >
              </div>
              <div class="flex items-end gap-3 mb-6">
                <span class="text-3xl font-bold text-red-600"
                  >{{ product.price | number : "1.0-0" }}₫</span
                >
                @if(product.discount > 0) {
                <span class="text-lg text-gray-400 line-through mb-1"
                  >{{ product.originalPrice | number : "1.0-0" }}₫</span
                >
                <span
                  class="text-sm font-bold text-red-500 mb-2 bg-red-50 px-2 py-0.5 rounded"
                  >-{{ product.discount }}%</span
                >
                }
              </div>
              <p class="text-gray-600 mb-6 leading-relaxed text-sm">
                Sản phẩm chính hãng {{ product.brand }}. Thiết kế sang trọng,
                hiệu năng mạnh mẽ. Bảo hành 12 tháng chính hãng. 1 đổi 1 trong
                30 ngày đầu nếu có lỗi nhà sản xuất.
              </p>
              <div
                class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8 text-sm text-gray-600 bg-gray-50 p-4 rounded-xl border border-gray-100"
              >
                <div class="flex items-center gap-2">
                  <svg
                    class="w-5 h-5 text-blue-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
                    /></svg
                  ><span>Chipset hiệu năng cao</span>
                </div>
                <div class="flex items-center gap-2">
                  <svg
                    class="w-5 h-5 text-green-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
                    /></svg
                  ><span>Pin 5000 mAh</span>
                </div>
                <div class="flex items-center gap-2">
                  <svg
                    class="w-5 h-5 text-purple-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
                    /></svg
                  ><span>Camera AI sắc nét</span>
                </div>
                <div class="flex items-center gap-2">
                  <svg
                    class="w-5 h-5 text-orange-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    /></svg
                  ><span>Bảo hành 12 tháng</span>
                </div>
              </div>
            </div>
            <div class="mt-auto flex gap-3 md:gap-4 flex-col sm:flex-row">
              <!-- Add To Cart Button -->
              <button
                (click)="addToCart(product)"
                class="flex-1 bg-white border-2 border-blue-600 text-blue-600 hover:bg-blue-50 font-bold py-3 px-6 rounded-xl transition-colors flex items-center justify-center gap-2"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
                  />
                </svg>
                Thêm vào giỏ
              </button>
              <button
                class="flex-1 bg-yellow-400 hover:bg-yellow-500 text-blue-900 font-bold py-3 px-6 rounded-xl transition-colors shadow-lg shadow-yellow-100 flex items-center justify-center"
              >
                Mua ngay
              </button>
            </div>
          </div>
        </div>
      </div>
      }

      <!-- CART DRAWER / SIDEBAR -->
      <div
        class="fixed inset-0 z-[100] z-50 overflow-hidden"
        [class.pointer-events-none]="!isCartOpen()"
      >
        <!-- Overlay -->
        <div
          class="absolute inset-0 bg-black/50 transition-opacity duration-300"
          [class.opacity-100]="isCartOpen()"
          [class.opacity-0]="!isCartOpen()"
          (click)="toggleCart()"
        ></div>

        <!-- Drawer -->
        <div
          class="absolute inset-y-0 right-0 max-w-md w-full bg-white shadow-2xl transform transition-transform duration-300 flex flex-col pointer-events-auto"
          [class.translate-x-0]="isCartOpen()"
          [class.translate-x-full]="!isCartOpen()"
        >
          <!-- Cart Header -->
          <div
            class="p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50"
          >
            <h2 class="text-xl font-bold text-gray-800 flex items-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6 mr-2 text-blue-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
                />
              </svg>
              Giỏ hàng ({{ cartCount() }})
            </h2>
            <button
              (click)="toggleCart()"
              class="p-2 text-gray-500 hover:text-red-500 transition-colors rounded-full hover:bg-red-50"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <!-- Cart Items -->
          <div class="flex-1 overflow-y-auto p-4 space-y-4">
            @if (cart().length === 0) {
            <div
              class="flex flex-col items-center justify-center h-full text-center text-gray-500 space-y-4"
            >
              <div
                class="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-12 w-12 text-gray-300"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
                  />
                </svg>
              </div>
              <p>Giỏ hàng của bạn đang trống.</p>
              <button
                (click)="toggleCart()"
                class="text-blue-600 font-bold hover:underline"
              >
                Tiếp tục mua sắm
              </button>
            </div>
            } @for (item of cart(); track item.id) {
            <div
              class="flex gap-3 items-start p-3 bg-white border border-gray-100 rounded-lg shadow-sm"
            >
              <div
                class="w-16 h-16 flex-shrink-0 bg-gray-50 rounded-md overflow-hidden p-2"
              >
                <img
                  [src]="item.image"
                  [alt]="item.name"
                  class="w-full h-full object-contain mix-blend-multiply"
                />
              </div>
              <div class="flex-1 min-w-0">
                <h4 class="text-sm font-medium text-gray-900 line-clamp-2">
                  {{ item.name }}
                </h4>
                <div class="flex items-center justify-between mt-1">
                  <span class="text-red-600 font-bold text-sm"
                    >{{ item.price | number : "1.0-0" }}₫</span
                  >
                  <div
                    class="flex items-center border border-gray-200 rounded-lg"
                  >
                    <button
                      (click)="updateQuantity(item.id, -1)"
                      class="w-7 h-7 flex items-center justify-center text-gray-500 hover:bg-gray-100 transition-colors text-sm"
                    >
                      -
                    </button>
                    <span class="w-8 text-center text-xs font-bold">{{
                      item.quantity
                    }}</span>
                    <button
                      (click)="updateQuantity(item.id, 1)"
                      class="w-7 h-7 flex items-center justify-center text-gray-500 hover:bg-gray-100 transition-colors text-sm"
                    >
                      +
                    </button>
                  </div>
                </div>
              </div>
              <button
                (click)="removeFromCart(item.id)"
                class="text-gray-400 hover:text-red-500 p-1"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            </div>
            }
          </div>

          <!-- Cart Footer -->
          @if (cart().length > 0) {
          <div class="p-4 bg-white border-t border-gray-100 shadow-up">
            <div class="flex justify-between items-center mb-4">
              <span class="text-gray-600">Tổng tiền:</span>
              <span class="text-xl font-bold text-red-600"
                >{{ cartTotal() | number : "1.0-0" }}₫</span
              >
            </div>
            <button
              class="w-full bg-blue-600 text-white font-bold py-3 rounded-xl hover:bg-blue-700 transition-colors shadow-lg shadow-blue-200"
            >
              Thanh Toán
            </button>
          </div>
          }
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      /* Custom Scrollbar hide but keep functionality for categories */
      .no-scrollbar::-webkit-scrollbar {
        display: none;
      }
      .no-scrollbar {
        -ms-overflow-style: none;
        scrollbar-width: none;
      }

      .shadow-up {
        box-shadow: 0 -4px 6px -1px rgba(0, 0, 0, 0.1),
          0 -2px 4px -1px rgba(0, 0, 0, 0.06);
      }

      .animate-bounce-short {
        animation: bounce-short 0.3s ease-in-out;
      }

      @keyframes bounce-short {
        0%,
        100% {
          transform: translateY(0);
        }
        50% {
          transform: translateY(-3px);
        }
      }

      /* Animation Classes */
      .animate-slide-up {
        animation: slideUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }

      .animate-fadeIn {
        animation: fadeIn 0.3s ease-out forwards;
      }

      @keyframes slideUp {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      @keyframes fadeIn {
        from {
          opacity: 0;
          transform: scale(0.95);
        }
        to {
          opacity: 1;
          transform: scale(1);
        }
      }
    `,
  ],
})
export class App implements OnInit, OnDestroy {
  // Signals for state management
  currentSlide = signal(0);
  activeBrand = signal<string>("all");
  searchQuery = signal<string>("");
  selectedProduct = signal<Product | null>(null);

  // Cart State
  cart = signal<CartItem[]>([]);
  isCartOpen = signal(false);

  // Computed Cart Values
  cartCount = computed(() =>
    this.cart().reduce((acc, item) => acc + item.quantity, 0)
  );
  cartTotal = computed(() =>
    this.cart().reduce((acc, item) => acc + item.price * item.quantity, 0)
  );

  // Data mocks
  brands = signal<BrandCategory[]>([
    { id: "apple", name: "Apple", logo: "" },
    { id: "samsung", name: "Samsung", logo: "" },
    { id: "xiaomi", name: "Xiaomi", logo: "" },
    { id: "oppo", name: "OPPO", logo: "" },
    { id: "vivo", name: "Vivo", logo: "" },
    { id: "realme", name: "Realme", logo: "" },
    { id: "asus", name: "Asus", logo: "" },
    { id: "nokia", name: "Nokia", logo: "" },
  ]);

  banners = signal<Banner[]>([
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

  products = signal<Product[]>([
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

  // Computed filter logic
  filteredProducts = computed(() => {
    const brand = this.activeBrand();
    const query = this.searchQuery().toLowerCase();

    return this.products().filter((p) => {
      const matchesBrand = brand === "all" || p.brandId === brand;
      const matchesSearch =
        p.name.toLowerCase().includes(query) ||
        p.brand.toLowerCase().includes(query);
      return matchesBrand && matchesSearch;
    });
  });

  private slideInterval: any;

  ngOnInit() {
    this.startAutoSlide();
    this.loadCart();
  }

  ngOnDestroy() {
    this.stopAutoSlide();
  }

  // --- Cart Methods ---

  loadCart() {
    const saved = localStorage.getItem("cart");
    if (saved) {
      try {
        this.cart.set(JSON.parse(saved));
      } catch (e) {
        console.error("Lỗi khi tải giỏ hàng", e);
      }
    }
  }

  saveCart() {
    localStorage.setItem("cart", JSON.stringify(this.cart()));
  }

  addToCart(product: Product) {
    this.cart.update((items) => {
      const existingItem = items.find((item) => item.id === product.id);
      if (existingItem) {
        // Tăng số lượng nếu đã có
        return items.map((item) =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      // Thêm mới
      return [...items, { ...product, quantity: 1 }];
    });

    this.saveCart();

    // Đóng modal sản phẩm nếu đang mở và mở giỏ hàng để user thấy item đã thêm
    if (this.selectedProduct()) {
      this.closeProductModal();
    }
    this.isCartOpen.set(true);
  }

  removeFromCart(productId: number) {
    this.cart.update((items) => items.filter((item) => item.id !== productId));
    this.saveCart();
  }

  updateQuantity(productId: number, change: number) {
    this.cart.update((items) =>
      items.map((item) => {
        if (item.id === productId) {
          const newQuantity = item.quantity + change;
          // Không cho phép số lượng < 1 (trừ khi xoá, nhưng UX ở đây là giữ tối thiểu 1)
          return { ...item, quantity: Math.max(1, newQuantity) };
        }
        return item;
      })
    );
    this.saveCart();
  }

  toggleCart() {
    this.isCartOpen.update((v) => !v);
  }

  // --- Carousel Methods ---

  startAutoSlide() {
    this.slideInterval = setInterval(() => {
      this.nextSlide();
    }, 5000); // 5 seconds
  }

  stopAutoSlide() {
    if (this.slideInterval) {
      clearInterval(this.slideInterval);
    }
  }

  nextSlide() {
    this.currentSlide.update((curr) => (curr + 1) % this.banners().length);
  }

  prevSlide() {
    this.currentSlide.update((curr) =>
      curr === 0 ? this.banners().length - 1 : curr - 1
    );
  }

  goToSlide(index: number) {
    this.currentSlide.set(index);
    // Reset timer when manually changed
    this.stopAutoSlide();
    this.startAutoSlide();
  }

  selectBrand(brandId: string) {
    this.activeBrand.set(brandId);
  }

  getBrandName(id: string): string {
    return this.brands().find((b) => b.id === id)?.name || "";
  }

  openProductModal(product: Product) {
    this.selectedProduct.set(product);
  }

  closeProductModal() {
    this.selectedProduct.set(null);
  }
}
