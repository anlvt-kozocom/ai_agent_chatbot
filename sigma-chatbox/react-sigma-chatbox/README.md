# React Sigma Chatbox ✨

A high-performance, modern React Chatbox UI library inspired by the Bitu AI assistant (FPT Shop). It features a sleek design, support for product carousels, quick replies, and built-in compatibility with the Gemini AI streaming API.

---

## 🚀 Development Setup

If you have cloned this repository and want to run the demo or continue development:

1.  **Install dependencies:**
    ```bash
    npm install
    ```

2.  **Run the development server:**
    ```bash
    npm run dev
    ```
    The demo application will be available at `http://localhost:5173`.

3.  **Build the library:**
    ```bash
    npm run build
    ```
    This generates the `dist` folder containing the compiled library (`index.mjs`, `index.js`) and the bundled CSS (`react-sigma-chatbox.css`).

---

## 📦 Integrating into Another Local Project

### 1. Link or Copy the Library
You can use the library in your other local projects before it's published to NPM:

**Option A: NPM Link**
1. In the `react-sigma-chatbox` directory: `npm link`
2. In your target project directory: `npm link react-sigma-chatbox`

**Option B: Manual Copy**
Copy the `dist` folder directly into your project and import from it.

### 2. Tailwind CSS Configuration
To ensure the chatbox styles are correctly applied in your target project, update your `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
    "./node_modules/react-sigma-chatbox/**/*.{js,ts,jsx,tsx}", 
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### 3. Import Styles
Import the library's stylesheet in your entry file (e.g., `main.tsx` or `App.tsx`):
```typescript
import 'react-sigma-chatbox/dist/react-sigma-chatbox.css';
```

---

## 🛠 Basic & Streaming Usage

The `Chatbox` component is highly flexible and handles logic through a `threadId` (unique session ID) and a `language` parameter (en, vi, ja). Both change or get passed whenever the user interacts with the UI.

### Option 1: Standard Text Response (Plain Text or Markdown)
You can choose to render responses as plain text (default) or basic Markdown (Bold, Lists, etc.).

```tsx
import { Language } from 'react-sigma-chatbox';

const config = {
  // ... other config
  renderMarkdown: true // Set to true to enable Markdown rendering
};

// Handler now receives (userInput, threadId, language)
const handleSimpleAi = async (userInput: string, threadId: string, language: Language) => {
  console.log(`Session ID: ${threadId}, Selected Language: ${language}`);
  
  if (language === 'vi') {
    return "Xin chào! Tôi là **trợ lý AI**. Tôi có thể giúp gì cho bạn?";
  }
  return "Hello! I am your **AI assistant**. How can I help you today?";
};

<Chatbox onGetAiResponse={handleSimpleAi} config={config} />
```

### Option 2: Streaming Response (Async Generator)
Use this for real-time "typing" effects.

```tsx
async function* handleStreamingAi(userInput: string, threadId: string, language: Language) {
  const chunks = language === 'ja' 
    ? ["こんにちは！", "私は **Sigma AI** です。", "何かお手伝いしましょうか？"]
    : ["Hello! ", "I am **Sigma AI**. ", "How can I help?"];
    
  for (const chunk of chunks) {
    await new Promise(r => setTimeout(r, 150));
    yield chunk;
  }
}

<Chatbox onGetAiResponse={handleStreamingAi} config={config} />
```

### Option 3: Product Carousel Response
You can return an object containing products to show a carousel.
```tsx
const handleProductSearch = async (userInput: string, threadId: string, language: Language) => {
  return {
    text: language === 'vi' ? "Xem các mẫu **iPhone** mới nhất:" : "Check out our latest **iPhone** models:",
    products: [
      {
        id: 'ip15',
        name: 'iPhone 15 Pro Max',
        price: '29.990.000₫',
        image: 'https://fptshop.com.vn/img/products/iphone-15-pro-max.png',
        description: 'The ultimate iPhone.'
      }
    ]
  };
};
```

---

## ⚙️ Component Configuration

### Chatbox Props
| Prop | Type | Description |
| :--- | :--- | :--- |
| `config` | `ChatboxConfig` | Object containing UI branding and initial messages. |
| `onGetAiResponse` | `AiResponseHandler` | Logic handler receiving `(userInput, threadId, language)`. |

### ChatboxConfig Fields
| Field | Type | Description |
| :--- | :--- | :--- |
| `primaryColor` | `string` | Hex color used for accents and user bubbles. |
| `botName` | `string` | The display name shown in the header. |
| `welcomeMessage` | `string` | Initial message sent by the bot. |
| `placeholder` | `string` | Input field placeholder. |
| `avatarUrl` | `string` | URL for the bot icon. |
| `quickReplies` | `string[]` | One-tap answer buttons. |
| `renderMarkdown` | `boolean` | Enable Markdown support for AI messages. |

---

## 📄 License
MIT