import React, { useState, useEffect } from "react";
import { Banner } from "../types";

interface BannerCarouselProps {
  banners: Banner[];
}

const BannerCarousel: React.FC<BannerCarouselProps> = ({ banners }) => {
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    const slideInterval = setInterval(() => {
      nextSlide();
    }, 5000);
    return () => clearInterval(slideInterval);
  }, [currentSlide, banners.length]);

  const nextSlide = () => {
    setCurrentSlide((curr) => (curr + 1) % banners.length);
  };

  const prevSlide = () => {
    setCurrentSlide((curr) => (curr === 0 ? banners.length - 1 : curr - 1));
  };

  const goToSlide = (index: number) => {
    setCurrentSlide(index);
  };

  return (
    <section className="relative w-full h-[180px] md:h-[350px] rounded-2xl overflow-hidden shadow-lg group">
      {/* Slides */}
      {banners.map((banner, i) => (
        <div
          key={banner.id}
          className={`absolute inset-0 w-full h-full transition-opacity duration-700 ease-in-out ${
            currentSlide === i ? "opacity-100" : "opacity-0"
          }`}
        >
          <img
            src={banner.image}
            alt={banner.title}
            className="w-full h-full object-cover"
          />
          {/* Text Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex flex-col justify-end p-6 md:p-10">
            <h2
              className={`text-white text-2xl md:text-4xl font-bold mb-2 transform translate-y-4 transition-all duration-700 delay-100 ${
                currentSlide === i ? "opacity-100 translate-y-0" : "opacity-0"
              }`}
            >
              {banner.title}
            </h2>
            <p
              className={`text-gray-200 text-sm md:text-lg transform translate-y-4 transition-all duration-700 delay-200 ${
                currentSlide === i ? "opacity-100 translate-y-0" : "opacity-0"
              }`}
            >
              {banner.subtitle}
            </p>
          </div>
        </div>
      ))}

      {/* Controls */}
      <button
        onClick={prevSlide}
        className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/30 hover:bg-white/80 p-2 rounded-full backdrop-blur-sm transition-all opacity-0 group-hover:opacity-100 focus:outline-none"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6 text-gray-800"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M15 19l-7-7 7-7"
          />
        </svg>
      </button>
      <button
        onClick={nextSlide}
        className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/30 hover:bg-white/80 p-2 rounded-full backdrop-blur-sm transition-all opacity-0 group-hover:opacity-100 focus:outline-none"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6 text-gray-800"
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
      </button>

      {/* Indicators */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-2">
        {banners.map((banner, i) => (
          <button
            key={banner.id}
            onClick={() => goToSlide(i)}
            className={`w-2 h-2 md:w-3 md:h-3 rounded-full transition-all duration-300 ${
              currentSlide === i ? "bg-yellow-400 w-6" : "bg-white/50"
            }`}
          ></button>
        ))}
      </div>
    </section>
  );
};

export default BannerCarousel;
