# Admin Interface - Quick Start Guide

Web-based admin interface để quản lý prompts, data files, và đồng bộ vector store.

## 🚀 Khởi động Admin Interface

### Option 1: Sử dụng Terminal mới

Mở terminal mới và chạy:

```bash
cd /Users/anlvt/Documents/AI/LangGraph/ai_product_agent
uvicorn app.admin_api:app --host 127.0.0.1 --port 8007 --reload
```

### Option 2: Background process

```bash
nohup uvicorn app.admin_api:app --host 127.0.0.1 --port 8007 --reload > admin.log 2>&1 &
```

## 📱 Truy cập Interface

Mở browser và vào: **http://localhost:8007**

## ✨ Tính năng

### 1. Quản lý Prompts
- Xem danh sách tất cả prompt files trong `app/prompts/`
- Click vào file để xem và chỉnh sửa  
- Editor hỗ trợ syntax highlighting cho Python
- Nút **Save** để lưu thay đổi

### 2. Quản lý Data Files
- Xem files trong `data/clean/`, `data/raw/`, `data/warranty/`
- Chỉnh sửa JSON, TXT files
- Tự động backup file gốc khi save

### 3. Đồng bộ Vector Store
- **Sync Product Vector Store**: Rebuild vector store cho product data từ `data/clean/`
- **Sync Warranty Vector Store**: Rebuild vector store cho warranty data từ `data/warranty/`
- Hiển thị progress và status

## 🎨 Interface Features

- ✅ Modern dark theme
- ✅ Monaco editor with syntax highlighting
- ✅ Real-time save/reset functionality
- ✅ Toast notifications
- ✅ File browser with icons
- ✅ Vector store sync với progress indicators

## 📡 API Endpoints

Admin API chạy trên port 8007:

- `GET /api/files/prompts` - List prompt files  
- `GET /api/files/data` - List data files
- `GET /api/file/content?path=` - Get file content
- `PUT /api/file/content` - Update file content
- `POST /api/sync/vector-store` - Sync product vector store
- `POST /api/sync/warranty-vector-store` - Sync warranty vector store
- `GET /api/sync/status` - Get vector store status

## ⚠️ Lưu ý

- Admin interface có quyền chỉnh sửa toàn bộ source code và data
- File backup được tạo với extension `.backup` khi save
- Vector store sync có thể mất vài phút tùy theo kích thước data
- F5 để refresh nếu có lỗi kết nối API

## 🔧 Troubleshooting

### Nếu không kết nối được API:
1. Kiểm tra admin server đang chạy: `lsof -i :8007`
2. Kiểm tra CORS settings trong `app/admin_api.py`
3. Xem logs trong terminal chạy uvicorn

### Nếu vector sync thất bại:
1. Kiểm tra data files có đúng format không
2. Xem error trong terminal logs
3. Verify `.env` có đủ API keys (GOOGLE_API_KEY hoặc OPENAI_API_KEY)
