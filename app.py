import streamlit as st
import pandas as pd
import re
import os
from io import StringIO, BytesIO

# Tùy chỉnh CSS
st.markdown("""
    <style>
    .st-emotion-cache-1w723zb,
    .main .block-container,
    .stApp > div > div > div {
        max-width: 1200px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin: 0 auto !important;
    }
    /* Tiêu đề chính */
    .main .block-container h1 {
        color: #2E4053;
        font-size: 2.5rem;
        font-weight: 700;
        padding: 1rem 0;
        border-bottom: 2px solid #2E4053;
        margin-bottom: 2rem;
    }
    
    /* Tiêu đề phụ */
    .main .block-container h2 {
        color: #34495E;
        font-size: 1.8rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Text area */
    .stTextArea textarea {
        border-radius: 8px;
        border: 1px solid #BDC3C7;
        height:200px;
    }
    
    /* Nút */
    .stButton button {
        background-color: #3498DB;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #2980B9;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Checkbox */
    .stCheckbox {
        margin: 1rem 0;
    }
    
    /* Tab */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: black;
    border-radius: 8px 8px 0 0;
    gap: 1rem;
    padding: 0 1rem;
    border: 1px solid #3498DB;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3498DB;
        color: white;
    }
    
    /* File uploader */
    .stFileUploader {
        border: 2px dashed #BDC3C7;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Success message */
    .stSuccess {
        background-color: #D5F5E3;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Warning message */
    .stWarning {
        background-color: #FCF3CF;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Debug info */
    .debug-info {
        background-color: #F8F9F9;
        border-left: 4px solid #3498DB;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    ..st-emotion-cache-1w723zb{
        max-width:1200px !important;
    }
    </style>
""", unsafe_allow_html=True)

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
            st.markdown(f"""
                <div class="debug-info">
                    <strong>Dòng bị khớp:</strong> {row['Keyword Phrase']} - {row['Vietnamese Translation']}<br>
                    {f'<strong>Từ khóa khớp:</strong> {keyword_match.group()}' if keyword_match else ''}
                    {f'<strong>Bản dịch khớp:</strong> {translation_match.group()}' if translation_match else ''}
                </div>
            """, unsafe_allow_html=True)
        
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
