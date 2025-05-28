import streamlit as st
import pandas as pd
import re
import os
from io import StringIO, BytesIO

# Đọc danh sách từ khóa loại trừ từ file
def load_exclude_keywords():
    if os.path.exists("exclude_keywords.txt"):
        with open("exclude_keywords.txt", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def save_exclude_keywords(keywords):
    with open("exclude_keywords.txt", "w", encoding="utf-8") as f:
        for kw in keywords:
            f.write(kw.strip() + "\n")

# Hàm lọc dữ liệu
def filter_keywords(df, exclude_keywords, debug_mode=False):
    if not exclude_keywords:
        return df
    
    # Thêm ranh giới từ để đảm bảo chỉ khớp với từ hoàn chỉnh
    pattern = re.compile(r'\b(' + '|'.join(map(re.escape, exclude_keywords)) + r')\b', re.IGNORECASE)
    
    def is_excluded(row):
        keyword = str(row['Keyword Phrase'])
        translation = str(row['Vietnamese Translation'])
        
        # Thông tin debug cho các kết quả khớp
        keyword_match = pattern.search(keyword)
        translation_match = pattern.search(translation)
        
        if debug_mode and (keyword_match or translation_match):
            st.write(f"Dòng bị khớp: {row['Keyword Phrase']} - {row['Vietnamese Translation']}")
            if keyword_match:
                st.write(f"Từ khóa khớp: {keyword_match.group()}")
            if translation_match:
                st.write(f"Bản dịch khớp: {translation_match.group()}")
        
        return bool(keyword_match) or bool(translation_match)
    
    return df[~df.apply(is_excluded, axis=1)]

st.title("Lọc từ khóa thực phẩm")

# --- Bước 1: Upload file hoặc paste dữ liệu ---
tab1, tab2 = st.tabs(["Upload file Excel", "Paste dữ liệu"])

df = None

with tab1:
    uploaded_file = st.file_uploader("Chọn file Excel (4 cột: Keyword Phrase, Vietnamese Translation, Keyword Sales, Search Volume)", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)

with tab2:
    pasted_data = st.text_area("Paste dữ liệu từ Excel (4 cột, có header, cách nhau bằng tab hoặc dấu phẩy)")
    if pasted_data:
        try:
            if "\t" in pasted_data:
                df = pd.read_csv(StringIO(pasted_data), sep="\t")
            else:
                df = pd.read_csv(StringIO(pasted_data))
        except Exception as e:
            st.error(f"Lỗi khi đọc dữ liệu: {e}")
            df = None

# --- Bước 2: Quản lý danh sách từ khóa loại trừ ---
st.subheader("Danh sách từ khóa loại trừ")
exclude_keywords = st.text_area("Mỗi dòng 1 từ khóa loại trừ", "\n".join(load_exclude_keywords()))
if st.button("Lưu danh sách từ khóa loại trừ"):
    save_exclude_keywords(exclude_keywords.splitlines())
    st.success("Đã lưu danh sách từ khóa loại trừ!")

# Thêm tùy chọn debug mode
debug_mode = st.checkbox("Bật chế độ debug (hiển thị thông tin chi tiết về các từ khóa bị lọc)")

exclude_keywords_list = [kw.strip() for kw in exclude_keywords.splitlines() if kw.strip()]

# --- Bước 3: Lọc và hiển thị kết quả ---
if df is not None and len(exclude_keywords_list) > 0:
    st.subheader("Kết quả sau khi lọc")
    filtered_df = filter_keywords(df, exclude_keywords_list, debug_mode)
    st.write(filtered_df)
    # Tải về file Excel
    output = BytesIO()
    filtered_df.to_excel(output, index=False, engine='openpyxl')
    st.download_button(
        label="Tải về file Excel đã lọc",
        data=output.getvalue(),
        file_name="filtered_keywords.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
elif df is not None:
    st.warning("Vui lòng nhập danh sách từ khóa loại trừ.")
