import streamlit as st
from openai import OpenAI
import openpyxl
import random
from datetime import datetime, timedelta

def ttsM(text, api_key):
    client = OpenAI(api_key=api_key)
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=str(text)
    )
    response.stream_to_file("speech.mp3")
    if not st.session_state.get('played', False):
        st.audio("speech.mp3", format="audio/mpeg", loop=False, autoplay=True)
        st.session_state['played'] = True

def translate(sent, text, api_key):
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

def translate_sent(sent, api_key):
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

def makesentences(word, api_key):
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

def read_excel_words(file):
    words = []
    try:
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active
        for row in sheet.iter_rows(values_only=True):
            words.extend([cell for cell in row if isinstance(cell, str)])
    except FileNotFoundError:
        st.error("找不到指定的 Excel 檔案。")
    return words

def main():
    # 初始化卡片列表
    cards = []
    
    # 起始日期
    start_date = datetime(2024, 5, 24)
    
    # 生成240個卡片
    for i in range(1, 241):
        card = {"name": f"Card {i}", "start_date": start_date, "due_dates": []}
        for j in range(30):
            card["due_dates"].append(start_date + timedelta(days=j))
        cards.append(card)
    
        # 更新起始日期
        start_date += timedelta(days=1)
    
    # 計算每個卡片的截止日期
    for card in cards:
        card["due_dates"] = [
            card["start_date"],
            card["start_date"] + timedelta(days=1),
            card["start_date"] + timedelta(days=3),
            card["start_date"] + timedelta(days=7),
            card["start_date"] + timedelta(days=14),
            card["start_date"] + timedelta(days=28),
        ]
    
    # 選擇當前日期
    today = st.date_input("Select the date", value=datetime.today())
    
    # 顯示當天的任務和進度
    st.title("Tasks Due Today")
    tasks_today = False
    for card in cards:
        if today in [due_date.date() for due_date in card["due_dates"]]:
            days_since_start = (today - card["start_date"].date()).days + 1
            st.write(f"{card['name']}: 進度 - 第{days_since_start}天")
            tasks_today = True
    if not tasks_today:
        st.write("No tasks due today.")
    
    with st.sidebar:
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    st.title("文檔翻譯和例句生成")
    uploaded_file = st.file_uploader("選擇 Excel 文件", type='xlsx')

    if uploaded_file is not None:
        # 每次上傳新文件時，重置單字列表和已用過的單字列表
        st.session_state.words = read_excel_words(uploaded_file)
        st.session_state.used_words = []  # 初始化已用過的單詞列表

    if 'words' not in st.session_state or not st.session_state.words:
        st.warning("Excel 文件中沒有找到任何單詞。")
        return

    # 選擇新單詞時將選過的單詞從列表中移除
    if 'selected_word' not in st.session_state or st.button('Choose New Word'):
        if len(st.session_state.words) > 0:
            st.session_state.selected_word = random.choice(st.session_state.words)
            st.session_state.words.remove(st.session_state.selected_word)
            st.session_state.used_words.append(st.session_state.selected_word)
            st.session_state.played = False  # 重設播放狀態
            st.session_state.generated_sent = None  # Reset
            st.session_state.translated_sent = None  # Reset
            st.session_state.show_translation = False  # Reset
            ttsM(st.session_state.selected_word, openai_api_key)
        else:
            st.warning("所有單詞都已經使用完畢。")

    if 'selected_word' in st.session_state:
        st.write(f"Selected Word: {st.session_state.selected_word}")
        generate_sentence = st.button("Generate Sentence")

        if generate_sentence:
            sent = makesentences(st.session_state.selected_word, openai_api_key)
            st.session_state.generated_sent = sent
            st.session_state.show_translation = True
            st.session_state.translated_sent = translate_sent(sent, openai_api_key)
            st.session_state.played = False  # 重設播放狀態

        if 'generated_sent' in st.session_state:
            st.text_area("Generated Sentence:", value=st.session_state.generated_sent, height=100)
            ttsM(st.session_state.generated_sent, openai_api_key)

        if 'show_translation' in st.session_state and st.session_state.show_translation:
            show_translation_button = st.button("Show Translation")
            if show_translation_button:
                st.text_area("Translated Sentence:", value=st.session_state.translated_sent, height=100)
                st.session_state.generated_sent = None

if __name__ == "__main__":
    main()
