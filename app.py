import streamlit as st
import csv
import os
import bisect

# --- 1. データの読み込み (キャッシュして高速化) ---
@st.cache_resource
def load_dictionary():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'integrated_dict.csv')
    
    sorted_hiragana_words = []
    hiragana_words = []
    words = []

    if not os.path.exists(file_path):
        return None, None, None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 3:
                    continue
                sorted_hiragana_words.append(row[0])
                hiragana_words.append(row[1])
                words.append(row[2])
        return sorted_hiragana_words, hiragana_words, words
    except Exception:
        return None, None, None

# --- 2. 準備 ---
st.title("1文字追加検索")

# データの読み込み実行
sorted_hiragana_words, hiragana_words, words = load_dictionary()

if sorted_hiragana_words is None:
    st.error("辞書ファイル 'integrated_dict.csv' が見つからないか、読み込めませんでした。")
    st.stop()

# ひらがなリストの作成
chars = [chr(i) for i in range(ord('ぁ'), ord('ん') + 1)]
chars.extend(['ゔ', 'ー', 'が', 'ぎ', 'ぐ', 'げ', 'ご', 'ざ', 'じ', 'ず', 'ぜ', 'ぞ', 
              'だ', 'ぢ', 'づ', 'で', 'ど', 'ば', 'び', 'ぶ', 'べ', 'ぼ', 'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ'])
all_hiragana = sorted(list(set(chars)))

# --- 3. UI部 ---
user_input = st.text_input("ひらがなを入力してください（4文字以下）", placeholder="例: あい").strip()

if user_input:
    st.subheader(f"「{user_input}」+ 1文字の検索結果")
    
    results = []
    
    # 検索ロジック
    for ch in all_hiragana:
        current_chars = list(user_input + ch)
        current_chars.sort()
        sorted_str = "".join(current_chars)

        idx = bisect.bisect_left(sorted_hiragana_words, sorted_str)
        while idx < len(sorted_hiragana_words) and sorted_hiragana_words[idx] == sorted_str:
            results.append(f"{hiragana_words[idx]}（{words[idx]}）")
            idx += 1
    
    # 結果の表示
    if results:
        # 重複を排除して表示（同じ構成で読みが複数ある場合など）
        for res in sorted(list(set(results))):
            st.write(f"- {res}")
    else:
        st.info("該当する単語は見つかりませんでした。")
else:
    st.write("左のテキストボックスにひらがなを入力してください。")

# --- 4. フッター (Apache License等の表示) ---
st.markdown("---")
st.caption("Data source: NEologd / Sudachi (Apache License 2.0)")