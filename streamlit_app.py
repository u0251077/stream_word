import streamlit as st
import pandas as pd
import random
from openai import OpenAI

# 在 sidebar 配置 API
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
client = OpenAI(api_key=api_key)

# 文件上傳
uploaded_file = st.file_uploader("Upload an Excel file", type="xlsx")
words = []
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    words = df[df.columns[0]].dropna().tolist()  # 假设单词在第一列
    st.write("Words loaded from Excel:", words)

def make_sentences(word):
    temperature = random.uniform(0.5, 1.0)
    variations = ["", ".", "!", "?"]
    random_variation = random.choice(variations)
    modified_text = word + random_variation
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Make a sentence using the word."},
            {"role": "user", "content": modified_text}
        ],
        temperature=temperature,
        max_tokens=64,
        top_p=1
    )
    completion_text = response.choices[0].message.content
    st.write("Generated Sentence:", completion_text)
    return completion_text

if st.button('Make Sentence from Random Word'):
    if words:
        word = random.choice(words)
        st.write("Selected Word:", word)
        make_sentences(word)
else:
    st.write("Upload an Excel file to start.")

# 确保所有功能仍能正确执行 without the sound playing part
