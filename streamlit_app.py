import streamlit as st
import pandas as pd
import os
from openai import OpenAI
import random
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 函數: 讀取所有 Excel 檔案中的單詞
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

# 函數: 使用 OpenAI API 生成句子
def generate_sentence(word, client, model):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates English sentences for language learners."},
            {"role": "user", "content": f"使用單詞 '{word}' 造一個符合多益考試難度的英語句子。"}
        ]
    )
    return response.choices[0].message.content.strip()

# 函數: 檢查翻譯
def check_translation(original, translation, client, model):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that checks English to Chinese translations."},
            {"role": "user", "content": f"請判斷以下翻譯是否正確。原句: '{original}' 翻譯: '{translation}' 請回答 '正確' 或 '不正確'，並簡要說明原因。"}
        ]
    )
    return response.choices[0].message.content.strip()
# Updated function to create the habit tracker heatmap
def create_habit_heatmap(completed_dates):
    # Create a date range for the entire year
    end_date = datetime.now()
    start_date = end_date.replace(month=1, day=1)  # Start from January 1st of the current year
    date_range = pd.date_range(start=start_date, end=end_date)

    # Create a DataFrame with all dates and their completion status
    df = pd.DataFrame({'date': date_range})
    df['completed'] = df['date'].dt.strftime('%Y/%m/%d').isin(completed_dates)
    df['weekday'] = df['date'].dt.weekday
    df['week'] = df['date'].dt.strftime('%Y-W%W')

    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=df['completed'].astype(int),
        x=df['week'],
        y=df['weekday'],
        colorscale=[[0, 'rgb(240,240,240)'], [1, 'rgb(0,128,0)']],
        showscale=False
    ))

    fig.update_layout(
        title='年度學習追蹤',
        xaxis_title='週',
        yaxis_title='星期',
        yaxis=dict(
            tickmode='array',
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            ticktext=['週一', '週二', '週三', '週四', '週五', '週六', '週日']
        ),
        height=300,
        margin=dict(l=40, r=40, t=40, b=20)
    )

    return fig

# Streamlit app
def main():
    st.set_page_config(page_title="英語學習助手", page_icon="📚", layout="wide")

    st.title("📚 英語學習助手")
    st.caption("🚀 由 OpenAI 和 Streamlit 提供支持的英語學習工具")

    # Predefined array of completed dates
    habit_dates = ["2024/07/28", 
                   "2024/08/29",
                   "2024/08/30",
                  ]  # Add more dates as needed

    # Sidebar setup
    with st.sidebar:
        st.header("設置")
        openai_api_key = st.text_input("OpenAI API Key", key="openai_api_key", type="password")
        selected_model = st.selectbox("選擇模型", ["gpt-4o-mini"])
        "[取得 OpenAI API key](https://platform.openai.com/account/api-keys)"
        "[查看源代碼](https://github.com/your-repo-link)"

    if not openai_api_key:
        st.info("請在側邊欄輸入你的 OpenAI API 金鑰以開始。")
        return

    client = OpenAI(api_key=openai_api_key)

    # Display Habit Tracker Heatmap
    st.subheader("學習習慣追蹤")
    fig = create_habit_heatmap(habit_dates)
    st.plotly_chart(fig, use_container_width=True)
    try:
        # Read words
        words = read_excel_files('data')

        if not words:
            st.error("無法從 Excel 文件中讀取單詞。請檢查 data 資料夾中的文件。")
            return

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.current_word = random.choice(words)
            st.session_state.current_sentence = generate_sentence(st.session_state.current_word, client, selected_model)
            st.session_state.messages.append({"role": "assistant", "content": f"讓我們開始學習吧！今天的單詞是 '{st.session_state.current_word}'。\n\n例句: {st.session_state.current_sentence}\n\n請試著翻譯這個句子。"})

        # Display chat history
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        # User input
        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            # Check translation
            with st.spinner("正在檢查翻譯..."):
                result = check_translation(st.session_state.current_sentence, prompt, client, selected_model)

            st.session_state.messages.append({"role": "assistant", "content": result})
            st.chat_message("assistant").write(result)

        # Next word button
        if st.button("下一個單詞"):
            st.session_state.current_word = random.choice(words)
            with st.spinner("正在生成新句子..."):
                st.session_state.current_sentence = generate_sentence(st.session_state.current_word, client, selected_model)
            new_message = f"很好！讓我們繼續學習下一個單詞。新的單詞是 '{st.session_state.current_word}'。\n\n例句: {st.session_state.current_sentence}\n\n請試著翻譯這個新的句子。"
            st.session_state.messages.append({"role": "assistant", "content": new_message})
            st.rerun()



    except Exception as e:
        st.error(f"發生錯誤: {str(e)}")
        st.error("請檢查 API 金鑰是否正確，以及 Excel 文件格式和 data 資料夾中的文件。")

if __name__ == "__main__":
    main()
