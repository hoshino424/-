import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. 設定の読み込み
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 2. ページの設定
st.set_page_config(page_title="旅行計画エージェント", page_icon="🧳")

# --- プロンプト設定（動的に前提条件を埋め込めるように変更） ---
# 役割の定義
ROLES = {
    "A": """あなたは【旅の理想・ワクワク担当】です。
ユーザーの願いをすべて肯定し、夢のような最高のプランを提案してください。
指定された「出発地点」と「出発時刻」を起点に、魅力的なスポットを詰め込んだ行程を作成してください。""",

    "B": """あなたは【現実の制約・ブレーキ担当】です。
Agent Aが提案したプランに対し、「出発地点からの移動距離」「出発時刻からのタイムスケジュール」「予算」「体力」の観点から厳しくダメ出しをしてください。
特に、移動時間に無理がないかを現実的に指摘してください。""",

    "C": """あなたは【納得の合意形成・まとめ担当】です。
Agent Aの『理想的な体験』とAgent Bの『物理的な制約』において両者のバランスが最も取れた『最適解』**を導き出してください。出発地と時刻という絶対的な制約条件を満たしつつ、ユーザー満足度を最大化するスケジュールを提示してください。」。"""
}

# 3. AIへの問い合わせ関数
def ask_agent(role_prompt, context, user_input):
    # システムプロンプトに共通の前提条件（出発地・時間など）を結合
    system_content = f"{role_prompt}\n\n【現在の前提条件】\n{context}"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content

# --- UI部分 ---
st.title("🧳 旅行計画マルチエージェント")
st.write("出発地点と時刻を考慮した、より実用的なプランを提案します。")

# 目的地入力
destination = st.text_input("どこにどの期間旅行に行きたいですか？", placeholder="例：北海道に二泊三日")

# サイドバー：ユーザー入力
with st.sidebar:
    st.header("旅行の条件")
    
    # 追加：出発地点と出発時刻
    departure_loc = st.text_input("📍 出発地点※最寄りの駅など",placeholder ="西宮北口駅")
    departure_time = st.text_input("⏰ 出発時刻", placeholder="13時")
    
    st.divider()
    
    budget = st.select_slider("予算イメージ", options=["節約", "標準", "贅沢"])
    preferences = st.text_area("こだわり（自由入力）", placeholder="例：映えスポット、歩きすぎない、海が見えるカフェ")

# すべてのエージェントに共有するコンテキスト情報
context_info = f"""
- 目的地: {destination}
- 出発地点: {departure_loc}
- 出発時刻: {departure_time}
- 予算: {budget}
- こだわり: {preferences}
"""

if st.button("議論を開始する") and destination:
    # Agent A
    with st.status("🌸 理想担当がプランを考案中...", expanded=True):
        plan_a = ask_agent(ROLES["A"], context_info, f"{destination}の最高の旅行プランを作って！")
        st.chat_message("assistant", avatar="🌸").write(plan_a)
    
    # Agent B
    with st.status("⚡ 現実担当が反論を準備中...", expanded=True):
        plan_b = ask_agent(ROLES["B"], context_info, f"Agent Aのこのプランを、{departure_loc}を{departure_time}に出発するという制約を含めて徹底的にチェックして：{plan_a}")
        st.chat_message("assistant", avatar="⚡").write(plan_b)
    
    # Agent C
    with st.status("⚖️ 最終案を調整中...", expanded=True):
        final_judgment = ask_agent(ROLES["C"], context_info, f"Aの提案：{plan_a}\nBの反論：{plan_b}\nこれらを踏まえ、{departure_loc}発の納得感のある最終スケジュールを出してください。")
        st.divider()
        st.subheader("⚖️ 最終判断（プラン）")
        st.success(final_judgment)

    st.balloons()

    # 2026-04-18 通信テスト実施：3G環境でもUXに問題ないことを確認済み