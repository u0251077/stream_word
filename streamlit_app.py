import streamlit as st
import pandas as pd
import os
import openai
import random

# 函數:讀取所有 Excel 檔案中的單詞
def read_excel_files(folder_path):
    words = []
    for file in os.listdir(folder_path):
        if file.endswith('.xlsx'):
            try:
                df = pd.read_excel(os.path.join(folder_path, file), header=None)
                if not df.empty:
                    words.extend(df[0].dropna().tolist())
                else:
                    st.warning(f"警告: {file} 是空的")
            except Exception as e:
                st.error(f"讀取 {file} 時出錯: {str(e)}")
    
    return list(set(words))  # 移除重複單詞

# 函數:使用 OpenAI API 生成句子
def generate_sentence(word, api_key):
    openai.api_key = api_key
    prompt = f"使用單詞 '{word}' 造一個符合多益考試難度的英語句子。"
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates English sentences for language learners."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content'].strip()

# 函數:檢查翻譯
def check_translation(original, translation, api_key):
    openai.api_key = api_key
    prompt = f"請判斷以下翻譯是否正確。原句: '{original}' 翻譯: '{translation}' 請回答 '正確' 或 '不正確'，並簡要說明原因。"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that checks English to Chinese translations."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content'].strip()

# Streamlit 應用
def main():
    st.set_page_config(page_title="英語學習助手", page_icon="📚", layout="wide")
    
    st.title("📚 英語學習助手")

    # 側邊欄設置
    with st.sidebar:
        st.header("設置")
        api_key = st.text_input("OpenAI API Key", key="openai_api_key", type="password")
        "[取得 OpenAI API key](https://platform.openai.com/account/api-keys)"
        "[查看源代碼](https://github.com/your-repo-link)"

    if not api_key:
        st.info("請在側邊欄輸入你的 OpenAI API 金鑰以開始。")
        return

    try:
        # 讀取單詞
        words = read_excel_files('data')
        
        if not words:
            st.error("無法從 Excel 文件中讀取單詞。請檢查 data 資料夾中的文件。")
            return

        col1, col2 = st.columns([2, 1])

        with col1:
            if 'current_word' not in st.session_state or st.session_state.current_word not in words:
                st.session_state.current_word = random.choice(words)
                st.session_state.current_sentence = generate_sentence(st.session_state.current_word, api_key)

            st.subheader("當前單詞")
            st.write(f"**{st.session_state.current_word}**")
            
            st.subheader("例句")
            st.write(f"*{st.session_state.current_sentence}*")

            # 使用者輸入翻譯
            user_translation = st.text_area("請輸入你的翻譯:", height=100)

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("提交翻譯", use_container_width=True):
                    if user_translation:
                        with st.spinner("正在檢查翻譯..."):
                            result = check_translation(st.session_state.current_sentence, user_translation, api_key)
                        st.write(result)
                    else:
                        st.warning("請輸入翻譯後再提交。")
            
            with col2:
                if st.button("下一個單詞", use_container_width=True):
                    st.session_state.current_word = random.choice(words)
                    with st.spinner("正在生成新句子..."):
                        st.session_state.current_sentence = generate_sentence(st.session_state.current_word, api_key)
                    st.rerun()

        with col2:
            st.subheader("學習進度")
            # 這裡可以添加學習進度的統計信息
            st.write("已學習單詞數：X")
            st.write("正確率：Y%")
            st.progress(0.6)  # 示例進度條

    except Exception as e:
        st.error(f"發生錯誤: {str(e)}")
        st.error("請檢查 API 金鑰是否正確，以及 Excel 文件格式和 data 資料夾中的文件。")

if __name__ == "__main__":
    main()
