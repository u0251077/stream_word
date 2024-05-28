import streamlit as st
from openai import OpenAI
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

def main():
  # 初始化卡片列表
  cards = {
      "Card 1": ["apple", "banana", "cat", "dog", "elephant"],
      "Card 2": ["flower", "tree", "house", "car", "table"],
      # ... 添加更多卡片
  }

  # 起始日期
  start_date = datetime(2024, 5, 24)

  # 生成卡片日程表
  card_schedule = {}
  for card_name, words in cards.items():
      card_schedule[card_name] = []
      for i in range(1, 241):
          card_schedule[card_name].append({
              "start_date": start_date + timedelta(days=i),
              "due_dates": [
                  start_date + timedelta(days=i),
                  start_date + timedelta(days=i + 1),
                  start_date + timedelta(days=i + 3),
                  start_date + timedelta(days=i + 7),
                  start_date + timedelta(days=i + 14),
                  start_date + timedelta(days=i + 28),
              ]
          })
      start_date += timedelta(days=1)

  # 選擇當前日期
  today = st.date_input("Select the date", value=datetime.today())

  # 顯示當天的任務和進度
  st.title("Tasks Due Today")
  tasks_today = False
  for card_name, card_details in card_schedule.items():
      if today in [due_date.date() for due_date in card_details[0]["due_dates"]]:
          days_since_start = (today - card_details[0]["start_date"].date()).days + 1
          st.write(f"{card_name}: 進度 - 第{days_since_start}天")
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
      st.session_state.used_words = [] 

  if 'words' not in st.session_state or not st.session_state.words:
      st.warning("Excel 文件中沒有找到任何單詞。")
      return

  # 選擇新單詞時將選過的單詞從列表中移除
  if 'selected_word' not in st.session_state or st.button('Choose New Word'):
      if len(st.session_state.words) > 0:
          st.session_state.selected_word = random.choice(st.session_state.words)
          st.session_state.words.remove(st.session_state.selected_word)
          st.session_state.used_words.append(st.session_state.selected_word)
          st.session_state.played = False # 重設播放狀態
          st.session_state.generated_sent = None # Reset
          st.session_state.translated_sent = None # Reset
          st.session_state.show_translation = False # Reset
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
          st.session_state.played = False # 重設播放狀態

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
