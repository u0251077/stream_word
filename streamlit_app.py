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

        # 初始化 session_state
        if 'show_translation' not in st.session_state:
            st.session_state.show_translation = False
            st.session_state.generated_sent = ""  # 初始化生成的句子保存

        with st.form("word_form"):
            random_word = random.choice(words)
            st.write(f"Selected Word: {random_word}")
            generate_sentence = st.form_submit_button("Generate Sentence")

        if generate_sentence:
            sent = makesentences(random_word, openai_api_key)
            st.session_state.generated_sent = sent  # 保存生成的句子
            st.session_state.show_translation = True  # 允许显示翻译
            st.session_state.translated_sent = translate_sent(sent, openai_api_key)  # 保存翻译结果

        # 只要已经保存了生成的句子，就显示它
        if st.session_state.generated_sent:
            st.text_area("Generated Sentence:", value=st.session_state.generated_sent, height=100)

        if st.session_state.show_translation:  # 仅当标记为True时显示翻译按鈕
            show_translation_button = st.button("Show Translation")
            if show_translation_button:
                st.text_area("Translated Sentence:", value=st.session_state.translated_sent, height=100)
                st.session_state.show_translation = False  # 重新设置标志以等待下一次生成

if __name__ == "__main__":
    main()
