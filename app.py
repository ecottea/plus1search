import streamlit as st
import csv
import os
import bisect

# ページの最上部にアンカーを設置
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

# --- 1. データの読み込み (キャッシュ) ---
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
                if len(row) < 3: continue
                sorted_hiragana_words.append(row[0])
                hiragana_words.append(row[1])
                words.append(row[2])
        return sorted_hiragana_words, hiragana_words, words
    except Exception:
        return None, None, None

# --- 2. 準備 ---
st.title("1文字追加検索")

sorted_hiragana_words, hiragana_words, words = load_dictionary()
if sorted_hiragana_words is None:
    st.error("辞書ファイルが見つかりません。")
    st.stop()

# ひらがなリスト
chars = [chr(i) for i in range(ord('ぁ'), ord('ん') + 1)]
chars.extend(['ゔ', 'ー', 'が', 'ぎ', 'ぐ', 'げ', 'ご', 'ざ', 'じ', 'ず', 'ぜ', 'ぞ', 
              'だ', 'ぢ', 'づ', 'で', 'ど', 'ば', 'び', 'ぶ', 'べ', 'ぼ', 'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ'])
all_hiragana = sorted(list(set(chars)))

# セッション状態で検索結果とキーワードを管理（入力欄を消しても結果を残すため）
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

# --- 3. UI部 (フォーム機能を利用) ---
# clear_on_submit=True で送信後に入力欄を空にする
with st.form("search_form", clear_on_submit=True):
    user_input = st.text_input("ひらがなを入力してください（5文字以下）", placeholder="例: あい").strip()
    submitted = st.form_submit_button("検索")

# 検索実行
if submitted and user_input:
    st.session_state.last_query = user_input
    results = []
    
    for ch in all_hiragana:
        current_chars = list(user_input + ch)
        current_chars.sort()
        sorted_str = "".join(current_chars)

        idx = bisect.bisect_left(sorted_hiragana_words, sorted_str)
        while idx < len(sorted_hiragana_words) and sorted_hiragana_words[idx] == sorted_str:
            results.append(f"{hiragana_words[idx]}（{words[idx]}）")
            idx += 1
    
    # 検索結果をセッションに保存
    st.session_state.last_results = sorted(list(set(results)))

# --- 4. 結果表示 ---
if st.session_state.last_query:
    st.subheader(f"「{st.session_state.last_query}」+ 1文字の検索結果")
    
    if hasattr(st.session_state, 'last_results') and st.session_state.last_results:
        for res in st.session_state.last_results:
            st.write(res)
    else:
        st.info("該当する単語は見つかりませんでした。")

# --- 5. フッター & 固定ボタン ---
st.markdown("""
    <style>
    .back-to-top {
        position: fixed;
        bottom: 80px;
        right: 30px;
        background-color: #f0f2f6;
        padding: 10px 20px;
        border-radius: 10px;
        text-decoration: none;
        color: #31333F;
        font-size: 14px;
        font-weight: bold;
        border: 1px solid #d1d5db;
        z-index: 1000;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
    }
    .back-to-top:hover { background-color: #e0e2e6; color: #ff4b4b; }
    </style>
    <a href="#top" class="back-to-top">Topへ移動</a>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Data source: NEologd / Sudachi (Apache License 2.0)")