
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./components/**/*.{js,ts,jsx,tsx}",
    "./index.tsx",
    "./App.tsx",
    // Đối với người dùng thư viện, họ sẽ thêm:
    // "./node_modules/react-sigma-chatbox/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        'sigma-primary': '#ef4444',
        'sigma-bg': '#f8fafc',
      },
      keyframes: {
        'chat-pop': {
          '0%': { transform: 'scale(0.9) translateY(20px)', opacity: '0' },
          '100%': { transform: 'scale(1) translateY(0)', opacity: '1' },
        },
        'msg-fade-in': {
          'from': { opacity: '0', transform: 'translateY(10px)' },
          'to': { opacity: '1', transform: 'translateY(0)' },
        }
      },
      animation: {
        'chat-pop': 'chat-pop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
        'msg': 'msg-fade-in 0.3s ease-out forwards',
      }
    },
  },
  plugins: [],
}
