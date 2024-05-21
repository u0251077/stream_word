import streamlit as st
from pathlib import Path
from openai import OpenAI
import openpyxl
import random


def ttsM(text,api_key):
    client = OpenAI(api_key=api_key)            
    response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input= str(text)
    )
    response.stream_to_file("speech.mp3")
    st.audio("speech.mp3", format="audio/mpeg", loop=False, autoplay=True )



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
        if 'words' not in st.session_state:
            st.session_state.words = read_excel_words(uploaded_file)  # 加載文件並保存到session_state
            st.session_state.words_used = 0  # 初始化用過的單詞數量

        if not st.session_state.words:
            st.warning("Excel 文件中沒有找到任何單詞。")
            return

        total_words = len(st.session_state.words)
        words_used = st.session_state.words_used
        st.write(f"已出現的單字量: {words_used} / 總單字量: {total_words}")

        if 'selected_word' not in st.session_state or st.button('Choose New Word'):
            st.session_state.selected_word = random.choice(st.session_state.words)
            st.session_state.words_used += 1  # 更新用過的單詞數量
            ttsM(st.session_state.selected_word, openai_api_key)
            

        st.write(f"Selected Word: {st.session_state.selected_word}")
        generate_sentence = st.button("Generate Sentence")

        if generate_sentence:
            sent = makesentences(st.session_state.selected_word, openai_api_key)
            st.session_state.generated_sent = sent 
            st.session_state.show_translation = True  
            st.session_state.translated_sent = translate_sent(sent, openai_api_key)  
            

        if 'generated_sent' in st.session_state:
            st.text_area("Generated Sentence:", value=st.session_state.generated_sent, height=100)
            ttsM(st.session_state.generated_sent, openai_api_key)
            

        if 'show_translation' in st.session_state and st.session_state.show_translation:
            show_translation_button = st.button("Show Translation")
            if show_translation_button:
                st.text_area("Translated Sentence:", value=st.session_state.translated_sent, height=100)
                st.session_state.generated_sent = False 

if __name__ == "__main__":
    main()
