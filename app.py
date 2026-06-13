"""Lead Qualification Bot with Groq (Llama 3.3 70B). Author: Avatar Putra Sigit"""
import os
import sys
import pandas as pd
import streamlit as st
from langchain_groq import ChatGroq

def get_llm() -> ChatGroq:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        st.error("GROQ_API_KEY not found.")
        sys.exit(1)
    return ChatGroq(model="llama-3.3-70b-versatile", api_key=key, temperature=0.2)

def load_leads() -> pd.DataFrame:
    csv = os.path.join(os.path.dirname(__file__), "data", "leads.csv")
    if not os.path.exists(csv):
        os.system(f"{sys.executable} data/generator.py")
    return pd.read_csv(csv)

def qualify_lead(row: pd.Series, llm: ChatGroq) -> dict:
    """AI scoring + draft email."""
    prompt = f"""You are a B2B sales expert for property maintenance services (rope access, glass cleaning, maintenance).
Score this lead HOT/WARM/COLD and write a short follow-up email draft in Indonesian.

Lead: {row['name']} from {row['company']} ({row['industry']})
Estimated contract: Rp {row['contract_value_estimate']:,}
Source: {row['source']}
Days since contact: {row['days_since_contact']}
Engagement score: {row['engagement_score']}/10

Return format:
SCORE: [HOT/WARM/COLD]
REASON: [1 sentence]
EMAIL_DRAFT: [3 sentences in Indonesian]"""

    response = llm.invoke(prompt)
    text = response.content
    score = "WARM"
    if "HOT" in text:
        score = "HOT"
    elif "COLD" in text:
        score = "COLD"
    return {"score": score, "raw": text}

def main() -> None:
    st.set_page_config(page_title="Lead Qualification Bot", layout="wide")
    st.title("🎯 Lead Qualification Bot — Groq Powered")
    st.markdown("AI scoring untuk lead B2B PT RKARI + draft email follow-up")

    df = load_leads()
    llm = get_llm()

    st.subheader("📋 All Leads")
    st.dataframe(df, use_container_width=True)

    lead_id = st.selectbox("Pilih Lead untuk Qualify:", df["id"].tolist())
    row = df[df["id"] == lead_id].iloc[0]

    if st.button("🤖 Qualify with AI", type="primary"):
        with st.spinner("AI analyzing..."):
            result = qualify_lead(row, llm)
            col1, col2 = st.columns(2)
            col1.metric("AI Score", result["score"])
            col2.metric("Contract Value", f"Rp {row['contract_value_estimate']:,.0f}")
            st.subheader("📧 AI Draft Email")
            st.markdown(result["raw"])

if __name__ == "__main__":
    main()
