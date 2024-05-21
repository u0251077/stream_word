import streamlit as st
from pathlib import Path
from openai import OpenAI
import openpyxl
import random





def translate(sent, text,api_key):
    client = OpenAI(api_key=api_key)        
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are asked to translate an English word into Traditional Chinese."},
            {"role": "user", "content": f"Sentence is {sent} and word is {text}"}
        ],
        temperature=0.7,
        max_tokens=64,
        top_p=1
    )
    return response.choices[0].message.content


def translate_sent(sent,api_key):
    client = OpenAI(api_key=api_key)            
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are asked to translate an English sentence into Traditional Chinese."},
            {"role": "user", "content": sent}
        ],
        temperature=0.7,
        max_tokens=64,
        top_p=1
    )
    return response.choices[0].message.content


def makesentences(word,api_key):
    client = OpenAI(api_key=api_key)        
    temperature = random.uniform(0.5, 1.0)
    variations = ["", ".", "!", "?"]
    modified_word = word + random.choice(variations)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "Create an example sentence using the given English word."},
            {"role": "user", "content": modified_word}
        ],
        temperature=temperature,
        max_tokens=64,
        top_p=1
    )
    return response.choices[0].message.content


def read_excel_words(filename):
    words = []
    try:
        workbook = openpyxl.load_workbook(filename)
        sheet = workbook.active
        for row in sheet.iter_rows(values_only=True):
            words.extend([cell for cell in row if isinstance(cell, str)])
    except FileNotFoundError:
        st.error("找不到指定的 Excel 檔案。")
    return words



def main():
    with st.sidebar:
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    st.title("文檔翻譯和例句生成")
    uploaded_file = st.file_uploader("選擇 Excel 文件", type='xlsx')
    if uploaded_file is not None:
    
        words = read_excel_words(uploaded_file)
        if not words:
            st.warning("Excel 文件中沒有找到任何單詞。")
            return
        with st.form("word_form"):
            random_word = random.choice(words)
            st.write(f"Selected Word: {random_word}")
            generate_sentence = st.form_submit_button("Generate Sentence")
        if generate_sentence:
            sent = makesentences(random_word,openai_api_key)
            st.text_area("Generated Sentence:", value=sent, height=100)
            translated_sent = translate_sent(sent,openai_api_key)
            st.text_area("Translated Sentence:", value=translated_sent, height=100)

if __name__ == "__main__":
    main()
