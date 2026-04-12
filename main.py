import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# 設定の読み込み
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ページの設定
st.set_page_config(page_title="法学的・旅行計画エージェント", page_icon="⚖️")

# --- プロンプト設定 ---
PROMPTS = {
    "A": "あなたは旅の浪漫担当。ユーザーの願いを全肯定して、最高の魅力を提案してください。",
    "B": "あなたは現実・効率担当。予算と移動の無駄を徹底的に指摘し、論破してください。",
    "C": "あなたは審判・利益衡量担当。法学的な視点でAとBの意見を天秤にかけ、最終判決を下してください。"
}

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
st.title("⚖️ 旅行計画マルチエージェント")
st.write("法学の『利益衡量』を用いて、理想と現実のバランスを取ったプランを提案します。")

# 目的地入力
destination = st.text_input("どこに旅行に行きたいですか？", placeholder="例：台湾、北海道")

if st.button("議論を開始する") and destination:
    # Agent A
    with st.status("Agent Aがプランを考案中...", expanded=True):
        plan_a = ask_agent(PROMPTS["A"], f"{destination}の最高の旅行プランを作って！")
        st.chat_message("assistant", avatar="🌸").write(plan_a)
    
    
    # Agent B
    with st.status("Agent Bが反論を準備中...", expanded=True):
        plan_b = ask_agent(PROMPTS["B"], f"Agent Aのこのプランを徹底的に論破して：{plan_a}")
        st.chat_message("assistant", avatar="⚡").write(plan_b)
    
    # Agent C
    with st.status("Agent Cが利益衡量中...", expanded=True):
        final_judgment = ask_agent(PROMPTS["C"], f"Aの提案：{plan_a}\nBの反論：{plan_b}\nこれらを利益衡量して、最終案を出してください。")
        st.subheader("⚖️ 最終判決（プラン）")
        st.success(final_judgment)

    st.balloons() # 終わったら風船を飛ばす演出！