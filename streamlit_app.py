import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import random

# 配置 Google AI API
genai.configure(api_key='你的_API_金鑰')
model = genai.GenerativeModel('gemini-1.5-flash')

# 函數:讀取所有 Excel 檔案中的單詞
def read_excel_files(folder_path):
    words = []
    for file in os.listdir(folder_path):
        if file.endswith('.xlsx'):
            df = pd.read_excel(os.path.join(folder_path, file))
            words.extend(df['單詞列的名稱'].tolist())  # 請替換為實際的列名
    return list(set(words))  # 移除重複單詞

# 函數:使用 AI 生成句子
def generate_sentence(word):
    prompt = f"使用單詞 '{word}' 造一個符合多益考試難度的英語句子。"
    response = model.generate_content(prompt)
    return response.text

# 函數:檢查翻譯
def check_translation(original, translation):
    prompt = f"請判斷以下翻譯是否正確。原句: '{original}' 翻譯: '{translation}' 請回答 '正確' 或 '不正確'，並簡要說明原因。"
    response = model.generate_content(prompt)
    return response.text

# Streamlit 應用
def main():
    st.title("英語學習助手")

    # 讀取單詞
    words = read_excel_files('data')

    if 'current_word' not in st.session_state:
        st.session_state.current_word = random.choice(words)
        st.session_state.current_sentence = generate_sentence(st.session_state.current_word)

    st.write(f"句子: {st.session_state.current_sentence}")

    # 使用者輸入翻譯
    user_translation = st.text_input("請輸入你的翻譯:")

    if st.button("提交翻譯"):
        if user_translation:
            result = check_translation(st.session_state.current_sentence, user_translation)
            st.write(result)
        else:
            st.write("請輸入翻譯後再提交。")

    if st.button("下一個句子"):
        st.session_state.current_word = random.choice(words)
        st.session_state.current_sentence = generate_sentence(st.session_state.current_word)
        st.experimental_rerun()

if __name__ == "__main__":
    main()
