import pandas as pd
import json
import re
import os

# 1. DỮ LIỆU ĐẦU VÀO
data_json = json.load(open('data/phone.json'))

# 2. HÀM HỖ TRỢ (UTILS)

def clean_money(price_str):
    """Chuyển đổi tiền tệ (như bài trước)"""
    if not isinstance(price_str, str): return 0
    rates = {'EUR': 27000, 'USD': 25000, '₹': 300, 'INR': 300}
    clean_str = price_str.replace(',', '').replace('.', '')
    numbers = re.findall(r'\d+', clean_str)
    if not numbers: return 0
    val = float(numbers[0])
    for symbol, rate in rates.items():
        if symbol in price_str or symbol in price_str.upper():
            return int(val * rate)
    return int(val)

def flatten_json(y):
    """Hàm đệ quy để làm phẳng JSON không giới hạn cấp độ"""
    out = {}
    
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            # Nếu gặp list, nối lại thành chuỗi
            out[name[:-1]] = ", ".join([str(i) for i in x])
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

# 3. QUY TRÌNH XỬ LÝ CHÍNH (CORE PROCESS)

all_rows = []

for brand in data_json:
    brand_name = brand['brand_name']
    
    for device in brand['devices']:
        # A. Lấy thông tin cơ bản
        base_info = {
            'Brand': brand_name,
            'Model': device['model_name'],
            'Image_URL': device['imageUrl']
        }
        
        # B. Làm phẳng (Flatten) toàn bộ Specifications
        # Hàm này sẽ tự động lôi hết Network, Body, Display... ra thành cột
        specs_flat = flatten_json(device['specifications'])
        
        # C. Merge 2 dict lại
        full_row = {**base_info, **specs_flat}
        
        # D. Xử lý hậu kỳ (Post-processing) cho các cột đặc biệt
        
        # 1. Clean giá tiền (nếu cột Misc_Price tồn tại sau khi flatten)
        if 'Misc_Price' in full_row:
            full_row['Price_VND'] = clean_money(full_row['Misc_Price'])
            full_row['Price_Display'] = "{:,.0f} đ".format(full_row['Price_VND'])
        
        # 2. Clean ký tự xuống dòng (\r\n) trong Camera hoặc các cột khác
        for key, val in full_row.items():
            if isinstance(val, str):
                full_row[key] = val.replace('\r\n', '; ').replace('\n', '; ')
        
        all_rows.append(full_row)

# 4. TẠO DATAFRAME VÀ CSV
df = pd.DataFrame(all_rows)

# Lưu ý: Các cột sẽ có tên dạng 'Category_SubCategory' (VD: Display_Resolution)
print(f"✅ Đã trích xuất tổng cộng {len(df.columns)} trường thông tin.")

# Xuất CSV
# df.to_csv("full_specs_data.csv", index=False, encoding='utf-8-sig')

# 5. TẠO TEXT CHO RAG (DYNAMIC TEXT GENERATION)
# Phần này sẽ tạo văn bản tự động dựa trên TẤT CẢ các cột có dữ liệu

def generate_full_rag_text(row):
    # Bắt đầu với thông tin chính
    text_parts = [f"Name: {row.get('Brand', '')} {row.get('Model', '')}."]
    
    if 'Price_Display' in row:
        text_parts.append(f"Price Display: {row['Price_Display']}.")
    
    text_parts.append("Specifications:")
    
    # Duyệt qua tất cả các cột còn lại để đưa vào văn bản
    skip_cols = ['Brand', 'Model', 'Image_URL', 'Price_VND', 'Price_Display']
    
    for col, val in row.items():
        if col in skip_cols or pd.isna(val) or val == "" or val == "Unspecified":
            continue
            
        # Làm đẹp tên trường: "Display_Resolution" -> "Display Resolution"
        readable_col = col.replace('_', ' ')
        text_parts.append(f"- {readable_col}: {val}.")
        
    return " ".join(text_parts)

rag_texts = df.apply(generate_full_rag_text, axis=1).tolist()

print("\n--- KẾT QUẢ RAG TEXT (CHI TIẾT 100%) ---")
print(rag_texts[0])
output_dir = "data"
os.makedirs(output_dir, exist_ok=True)

# Gán nội dung RAG vào DataFrame để dễ xử lý theo nhóm
# (Đảm bảo độ dài df và rag_texts khớp nhau từ bước trước)
df['RAG_Content'] = rag_texts 

# Ký tự phân cách giữa các sản phẩm trong cùng 1 file hãng
separator = "\n\n### END OF PRODUCT ###\n\n"

print(f"📂 Đang ghi dữ liệu vào thư mục: {output_dir}/ ...\n")

# 2. XỬ LÝ NHÓM THEO HÃNG (GROUP BY)
# Lấy danh sách các hãng duy nhất có trong dữ liệu
unique_brands = df['Brand'].unique()

print(unique_brands)
for brand in unique_brands:
    if brand not in ['Nokia', 'Apple', 'Samsung', 'Sony', 'Xiaomi', 'Huawei', 'Realme']:
      continue
    try:
        # Lọc lấy tất cả dòng dữ liệu của hãng hiện tại
        brand_df = df[df['Brand'] == brand]
        
        # Lấy list các đoạn văn (rag text) của hãng này
        content_list = brand_df['RAG_Content'].tolist()
        
        # Nối chúng lại thành 1 chuỗi lớn, ngăn cách bởi separator
        full_file_content = separator.join(content_list)
        
        # Thêm separator vào cuối cùng của file (để splitter không bị lỗi EOF)
        full_file_content += separator
        
        # 3. TẠO TÊN FILE AN TOÀN
        # Xử lý tên hãng để làm tên file (ví dụ: "Sony Ericsson" -> "Sony_Ericsson.txt")
        safe_filename = str(brand).strip().replace(" ", "_").replace("/", "-").lower() + ".txt"
        file_path = os.path.join(output_dir, safe_filename)
        
        # 4. GHI FILE
        with open(file_path, "w", encoding="utf-8") as f:
            # Ghi thêm header để context rõ ràng hơn (Optional)
            f.write(f"Dữ liệu danh sách điện thoại của hãng {brand}.\n")
            f.write("-" * 50 + "\n\n")
            f.write(full_file_content)
            
        print(f"✅ Đã tạo: {safe_filename:<20} | Số lượng: {len(content_list)} sản phẩm")
        
    except Exception as e:
        print(f"❌ Lỗi khi ghi file hãng {brand}: {e}")

print("\n🎉 Hoàn tất! Bạn có thể vào thư mục 'phones_by_brand' để kiểm tra.")