import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
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
                    print(f"Warning: {file} is empty")
            except Exception as e:
                print(f"Error reading {file}: {str(e)}")
    
    return list(set(words))  # 移除重複單詞

# 函數:使用 AI 生成句子
def generate_sentence(word, model):
    prompt = f"使用單詞 '{word}' 造一個符合多益考試難度的英語句子。"
    response = model.generate_content(prompt)
    return response.text

# 函數:檢查翻譯
def check_translation(original, translation, model):
    prompt = f"請判斷以下翻譯是否正確。原句: '{original}' 翻譯: '{translation}' 請回答 '正確' 或 '不正確'，並簡要說明原因。"
    response = model.generate_content(prompt)
    return response.text

# Streamlit 應用
def main():
    st.title("英語學習助手")

    # 側邊欄設置
    with st.sidebar:
        api_key = st.text_input("Google AI API Key", key="chatbot_api_key", type="password")
        "[Get a Google AI API key](https://makersuite.google.com/app/apikey)"
        "[View the source code](https://github.com/your-repo-link)"

    if not api_key:
        st.info("請在側邊欄輸入你的 Google AI API 金鑰以開始。")
        return

    try:
        # 配置 Google AI API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # 讀取單詞
        words = read_excel_files('data')
        
        if not words:
            st.error("無法從 Excel 文件中讀取單詞。請檢查 data 資料夾中的文件。")
            return

        if 'current_word' not in st.session_state or st.session_state.current_word not in words:
            st.session_state.current_word = random.choice(words)
            st.session_state.current_sentence = generate_sentence(st.session_state.current_word, model)

        st.write(f"目前單詞: {st.session_state.current_word}")
        st.write(f"句子: {st.session_state.current_sentence}")

        # 使用者輸入翻譯
        user_translation = st.text_input("請輸入你的翻譯:")

        if st.button("提交翻譯"):
            if user_translation:
                result = check_translation(st.session_state.current_sentence, user_translation, model)
                st.write(result)
            else:
                st.write("請輸入翻譯後再提交。")

        if st.button("下一個單詞"):
            st.session_state.current_word = random.choice(words)
            st.session_state.current_sentence = generate_sentence(st.session_state.current_word, model)
            st.experimental_rerun()

    except Exception as e:
        st.error(f"發生錯誤: {str(e)}")
        st.error("請檢查 API 金鑰是否正確，以及 Excel 文件格式和 data 資料夾中的文件。")

if __name__ == "__main__":
    main()
