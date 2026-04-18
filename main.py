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

# --- プロンプト設定 ---
PROMPTS = {
    "A": """あなたは【旅の理想・ワクワク担当】です。
ユーザーの願いをすべて肯定し、夢のような最高のプランを提案してください。
「せっかく行くなら全部楽しむ！」という視点で、魅力的なスポットや体験を詰め込んでください。""",

    "B": """あなたは【現実の制約・ブレーキ担当】です。
Agent Aが提案したプランに対し、「予算」「移動時間」「体力的な無理」という厳しい現実の視点から徹底的にダメ出しをしてください。
旅行を失敗させないために、あえて現実的なリスクを指摘する役割です。""",

    "C": """あなたは【納得の合意形成・まとめ担当】です。
法学の『利益衡量（りえきこうりょう）』の考え方を用い、Agent Aの「理想」とAgent Bの「現実」を天秤にかけてください。
相反する意見のバランスをとり、誰もが納得できる「現実的な最高案」を最終的なスケジュール形式で提示してください。"""
}

# 3. AIへの問い合わせ関数
def ask_agent(role_prompt, user_input):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": role_prompt},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content

# --- UI部分 ---
st.title("🧳 旅行計画マルチエージェント")
st.write("理想と現実のバランスを取ったプランを提案します。")

# 目的地入力
destination = st.text_input("どこに旅行に行きたいですか？", placeholder="例：台湾、北海道")

# サイドバー：ユーザー入力with st.sidebar:

st.header("旅行の条件")

budget = st.select_slider("予算イメージ", options=["節約", "標準", "贅沢"])

preferences = st.text_area("こだわり（自由入力）", placeholder="例：映えスポット、歩きすぎない、海が見えるカフェ")

if st.button("議論を開始する") and destination:
    # Agent A
    with st.status("🌸 理想担当がプランを考案中...", expanded=True):
        plan_a = ask_agent(PROMPTS["A"], f"{destination}の最高の旅行プランを作って！")
        st.chat_message("assistant", avatar="🌸").write(plan_a)
    
    # Agent B
    with st.status("⚡ 現実担当が反論を準備中...", expanded=True):
        plan_b = ask_agent(PROMPTS["B"], f"Agent Aのこのプランを予算や移動時間、体力的な観点から徹底的にダメ出しをして：{plan_a}")
        st.chat_message("assistant", avatar="⚡").write(plan_b)
    
    # Agent C
    with st.status("⚖️ 最終案を調整中...", expanded=True):
        final_judgment = ask_agent(PROMPTS["C"], f"Aの提案：{plan_a}\nBの反論：{plan_b}\nこれらの意見をまとめて納得感のある最終案を出してください。")
        st.divider() # 区切り線を入れて結論を強調
        st.subheader("⚖️ 最終判断（プラン）")
        st.success(final_judgment)

    st.balloons() # 演出！