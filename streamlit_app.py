import streamlit as st
from pathlib import Path
from openai import OpenAI
import openpyxl
import random
def get_adjusted_words(words_dict):
    """根据熟悉度调整单词出现的频率。"""
    repeated_words = []
    for word, familiarity in words_dict.items():
        if familiarity == 'not_familiar':
            repeated_words.extend([word]*3)  # 不熟悉的单词出现频率增加
        elif familiarity == 'familiar':
            continue  # 熟悉的单词将被排除在外
        else:
            repeated_words.append(word)  # 正常频率
    return repeated_words

def update_familiarity(word, familiarity):
    """更新单词的熟悉度。"""
    if 'words_familiarity' not in st.session_state:
        st.session_state.words_familiarity = {}
    st.session_state.words_familiarity[word] = familiarity

def ttsM(text,api_key):
    client = OpenAI(api_key=api_key)            
    response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input= str(text)
    )
    response.stream_to_file("speech.mp3")
    if not st.session_state.get('played', False):
        st.audio("speech.mp3", format="audio/mpeg", loop=False, autoplay=True)
        st.session_state['played'] = True


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
            # 加载文件并保存到session_state
            st.session_state.words = read_excel_words(uploaded_file)
            st.session_state.words_used = 0

        if not st.session_state.words:
            st.warning("Excel 文件中沒有找到任何单词。")
            return

        # 调整单词出现频率
        adjusted_words = get_adjusted_words(st.session_state.words)
        total_words = len(adjusted_words)
        words_used = st.session_state.words_used
        st.write(f"已出現的單字量: {words_used} / 總單字量: {total_words}")

        if 'selected_word' not in st.session_state or st.button('Choose New Word'):
            st.session_state.selected_word = random.choice(adjusted_words)
            ttsM(st.session_state.selected_word, openai_api_key)

        st.write(f"Selected Word: {st.session_state.selected_word}")

        # 为单词熟悉度提供选项
        familiarity_choice = st.radio("你對這個單字的熟悉程度怎麼樣？", ('熟悉', '不熟悉', '一般'))
        if st.button('Update Familiarity'):
            update_familiarity(st.session_state.selected_word, familiarity_choice)

        generate_sentence = st.button("Generate Sentence")
        if generate_sentence:
            sent = makesentences(st.session_state.selected_word, openai_api_key)
            st.session_state.generated_sent = sent
            st.session_state.translated_sent = translate_sent(sent, openai_api_key)
            st.session_state.played = False

        if 'generated_sent' in st.session_state:
            st.text_area("Generated Sentence:", value=st.session_state.generated_sent, height=100)
            ttsM(st.session_state.generated_sent, openai_api_key)

        if 'translated_sent' in st.session_state and st.button("Show Translation"):
            st.text_area("Translated Sentence:", value=st.session_state.translated_sent, height=100)

if __name__ == "__main__":
    main()
