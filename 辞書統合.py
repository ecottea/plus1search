import os
import csv
import re
import unicodedata

# --- 設定 ---
PATHS = {
    'neologd': r'D:\tools\mecab-ipadic-neologd',
    'sudachi': r'D:\tools\sudachi-dictionary-sources'
}
# スクリプトと同じディレクトリに書き出し
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'integrated_dict.csv')

def kana_to_hira(text):
    """カタカナをひらがなに変換"""
    return "".join([chr(ord(c) - 96) if "ァ" <= c <= "ヶ" else c for c in text])

def contains_kanji(text):
    """単語に漢字が含まれているか判定（重複排除の優先度用）"""
    return any('CJK UNIFIED IDEOGRAPH' in unicodedata.name(c, '') for c in text)

def is_valid_yomi(yomi):
    """10文字以下かつ、ひらがな・カタカナ・長音のみ（記号不可）"""
    if not yomi or len(yomi) > 6:
        return False
    # ひらがな、カタカナ、長音のみを許可（正規表現）
    return re.fullmatch(r'[ぁ-んァ-ヶー]+', yomi) is not None

# 一時格納用：{読み(ひらがな): 単語}
temp_data = {}

def update_entry(yomi_hira, word):
    """条件に沿って辞書を更新（重複時は漢字入りを優先）"""
    if yomi_hira not in temp_data:
        temp_data[yomi_hira] = word
    else:
        # すでに登録済みの場合、既存が非漢字かつ新規が漢字なら差し替え
        if not contains_kanji(temp_data[yomi_hira]) and contains_kanji(word):
            temp_data[yomi_hira] = word

print("辞書の読み込みを開始します...")

# 1. MeCab-IPADIC-NEologd (UTF-8)
if os.path.exists(PATHS['neologd']):
    for file in os.listdir(PATHS['neologd']):
        if file.endswith('.csv'):
            with open(os.path.join(PATHS['neologd'], file), 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 12: continue
                    word, pos, yomi_kata = row[0], row[4], row[11]
                    if '名詞' in pos and is_valid_yomi(yomi_kata):
                        update_entry(kana_to_hira(yomi_kata), word)

# 2. Sudachi (UTF-8)
if os.path.exists(PATHS['sudachi']):
    for file in os.listdir(PATHS['sudachi']):
        if file.endswith('.csv'):
            with open(os.path.join(PATHS['sudachi'], file), 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 12: continue
                    word, pos, yomi_kata = row[0], row[5], row[11]
                    if '名詞' in pos and is_valid_yomi(yomi_kata):
                        update_entry(kana_to_hira(yomi_kata), word)

# --- データの加工と最終ソート ---

print("データの並べ替えを実行中...")
final_list = []
for yomi_hira, word in temp_data.items():
    # 1列目：読みの文字を1文字ずつバラしてソートし、文字列に戻したもの
    char_sorted_yomi = "".join(sorted(yomi_hira))
    # 形式：ソートした読み, 読み, 単語
    final_list.append([char_sorted_yomi, yomi_hira, word])

# 1列目（char_sorted_yomi）を基準に昇順で全体をソート
# これにより二分探索が可能になる
final_list.sort(key=lambda x: x[0])

# CSV出力
try:
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in final_list:
            writer.writerow(row)
    print(f"成功: {len(final_list)} 件のデータを出力しました。")
    print(f"ファイルパス: {os.path.abspath(OUTPUT_FILE)}")
except Exception as e:
    print(f"エラーが発生しました: {e}")

# デバッグ用確認（最初の数行を表示）
if final_list:
    print("\n[出力イメージ (最初の3件)]")
    for i in range(min(3, len(final_list))):
        print(f"Row {i}: {final_list[i]}")