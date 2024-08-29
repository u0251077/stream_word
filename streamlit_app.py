import streamlit as st
import pandas as pd
import os
from openai import OpenAI
import random
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ... [Previous functions remain unchanged] ...

# New function to create the habit tracker heatmap
def create_habit_heatmap(completed_dates):
    # Create a date range for the past year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    date_range = pd.date_range(start=start_date, end=end_date)

    # Create a DataFrame with all dates and their completion status
    df = pd.DataFrame({'date': date_range})
    df['completed'] = df['date'].dt.strftime('%Y-%m-%d').isin(completed_dates)
    df['weekday'] = df['date'].dt.weekday
    df['week'] = df['date'].dt.to_period('W').apply(lambda r: r.start_time)

    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=df['completed'].astype(int),
        x=df['week'],
        y=df['weekday'],
        colorscale=[[0, 'rgb(255,255,255)'], [1, 'rgb(0,128,0)']],
        showscale=False
    ))

    fig.update_layout(
        title='Habit Tracker Heatmap',
        xaxis_title='Week',
        yaxis_title='Weekday',
        yaxis=dict(
            tickmode='array',
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        ),
        height=400
    )

    return fig

# Streamlit app
def main():
    st.set_page_config(page_title="英語學習助手", page_icon="📚", layout="wide")

    st.title("📚 英語學習助手")
    st.caption("🚀 由 OpenAI 和 Streamlit 提供支持的英語學習工具")

    # Sidebar setup
    with st.sidebar:
        st.header("設置")
        openai_api_key = st.text_input("OpenAI API Key", key="openai_api_key", type="password")
        selected_model = st.selectbox("選擇模型", ["gpt-4-0314", "gpt-3.5-turbo"])
        "[取得 OpenAI API key](https://platform.openai.com/account/api-keys)"
        "[查看源代碼](https://github.com/your-repo-link)"

        # Habit Tracker input
        st.subheader("Habit Tracker")
        habit_date = st.date_input("選擇完成日期")
        if st.button("添加完成日期"):
            if "completed_dates" not in st.session_state:
                st.session_state.completed_dates = []
            st.session_state.completed_dates.append(habit_date.strftime('%Y-%m-%d'))
            st.success(f"已添加完成日期: {habit_date}")

    if not openai_api_key:
        st.info("請在側邊欄輸入你的 OpenAI API 金鑰以開始。")
        return

    client = OpenAI(api_key=openai_api_key)

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

        # Display Habit Tracker Heatmap
        if "completed_dates" in st.session_state:
            st.subheader("學習習慣追蹤")
            fig = create_habit_heatmap(st.session_state.completed_dates)
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"發生錯誤: {str(e)}")
        st.error("請檢查 API 金鑰是否正確，以及 Excel 文件格式和 data 資料夾中的文件。")

if __name__ == "__main__":
    main()
