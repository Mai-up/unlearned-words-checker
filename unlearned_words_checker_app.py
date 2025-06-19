import streamlit as st
import pandas as pd
from janome.tokenizer import Tokenizer

# --- 形態素解析：名詞・動詞・形容詞の基本形を抽出 ---
def extract_keywords(text):
    t = Tokenizer()
    words = []
    for token in t.tokenize(text):
        part = token.part_of_speech.split(',')[0]
        if part in ['名詞', '動詞', '形容詞']:
            base = token.base_form
            words.append(base)
    return list(set(words))  # 重複排除

# --- Streamlit UI ---
st.title("🔍 授業前の未習語チェッカー")
st.caption("授業準備で作成した例文等に、未習語が含まれていないかを自動チェックします。[使い方はこちら](https://note.com/ichimai8/n/nd78bdc437fbf)")


# 📁 ファイルアップロード
uploaded_file = st.file_uploader("【Step1】語彙リスト（Excelファイル）をアップロードしてください。（列名：課, 品詞, 語彙）", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    text = st.text_area("【Step2】授業で使用する例文を入力してください", height=100)

    # 🔢 選択できる課の選択肢を、語彙リストの最大課に合わせる
    max_lesson = int(df["課"].max())
    selected_lesson = st.selectbox(
        "【Step3】この例文は何課で使いますか？",
        options=list(range(1, max_lesson + 1)),
        format_func=lambda x: f"第{x}課"
    )

    if st.button("実行") and text:
        # 1. 既習語彙の抽出（<= 選択課）
        learned_words = df[df["課"] <= selected_lesson]["語彙"].tolist()

        # 2. 入力文からキーワード抽出（漢字ベース）
        keywords = extract_keywords(text)

        # 3. 未習語の抽出
        unlearned_words = [word for word in keywords if word not in learned_words]

        # 4. 未習語が出てくる課を特定
        results = []
        for word in unlearned_words:
            lesson_info = df[df["語彙"] == word]["課"].values
            if len(lesson_info) > 0:
                results.append(f"{word}（第{lesson_info[0]}課）")
            else:
                results.append(word)

        # 5. 結果表示
        if results:
            st.subheader("❗️未習語")

            for item in results:
                st.write(f"・{item}")
        else:
            st.success("未習語は見つかりませんでした。")

