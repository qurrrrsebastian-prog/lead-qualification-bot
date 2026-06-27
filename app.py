"""Lead Qualification Bot — Groq (Llama 3.3 70B) | v2.0 production upgrade.

Amber Sales theme. Adds a Kanban pipeline (NEW/HOT/WARM/COLD), SQLite
persistence, batch AI qualification, an analytics dashboard, filtering/search,
an email-template manager and CSV export. Falls back to a transparent heuristic
scorer when no GROQ_API_KEY is configured so the app remains usable offline.

Author: Avatar Putra Sigit | GitHub: qurrrrsebastian-prog
"""
import os
import re
import sys
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

import database as db
from security import sanitize_input
from ui_components import (PRIMARY, SCORE_COLORS, render_footer, render_header,
                           render_lead_card)

st.set_page_config(page_title="Lead Qualification Bot", layout="wide", page_icon="🎯")

DATA_CSV = os.path.join(os.path.dirname(__file__), "data", "leads.csv")


# --------------------------------------------------------------------------- #
# LLM (lazy — never exits the process)
# --------------------------------------------------------------------------- #
@st.cache_resource(show_spinner=False)
def get_llm():
    """Return a cached ChatGroq client, or None if no API key is set."""
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return None
    try:
        from langchain_groq import ChatGroq
        return ChatGroq(model="llama-3.3-70b-versatile", api_key=key, temperature=0.2)
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------- #
# Data bootstrap
# --------------------------------------------------------------------------- #
@st.cache_resource
def bootstrap() -> bool:
    """Initialise DB and import leads.csv (generating it if needed) once."""
    db.init_db()
    if db.lead_count() == 0:
        if not os.path.exists(DATA_CSV):
            os.system(f'"{sys.executable}" data/generator.py')
        if os.path.exists(DATA_CSV):
            df = pd.read_csv(DATA_CSV)
            n = db.import_leads(df)
            db.add_log("import_leads", f"Imported {n} leads", "system")
    return True


bootstrap()


# --------------------------------------------------------------------------- #
# Qualification
# --------------------------------------------------------------------------- #
def _heuristic_score(lead: dict) -> tuple:
    """Transparent rule-based fallback when the LLM is unavailable."""
    eng = lead.get("engagement_score", 0) or 0
    val = lead.get("contract_value_estimate", 0) or 0
    days = lead.get("days_since_contact", 99) or 99
    points = eng + (3 if val > 50_000_000 else 1) + (2 if days < 14 else 0)
    if points >= 10:
        score = "HOT"
    elif points >= 6:
        score = "WARM"
    else:
        score = "COLD"
    reason = (f"Heuristik: engagement {eng}/10, nilai Rp {val:,.0f}, "
              f"{days} hari sejak kontak.")
    draft = (f"Halo {lead.get('name','')}, terima kasih atas minat "
             f"{lead.get('company','')}. Kami ingin menindaklanjuti kebutuhan "
             f"layanan maintenance Anda. Boleh kami jadwalkan diskusi singkat?")
    return score, reason, draft


def _parse_ai(text: str) -> tuple:
    """Parse SCORE / REASON / EMAIL_DRAFT out of the model response."""
    score = "WARM"
    upper = text.upper()
    if "HOT" in upper:
        score = "HOT"
    elif "COLD" in upper:
        score = "COLD"
    reason_m = re.search(r"REASON:\s*(.+)", text, re.IGNORECASE)
    reason = reason_m.group(1).strip() if reason_m else text.strip()[:200]
    draft_m = re.search(r"EMAIL_DRAFT:\s*(.+)", text, re.IGNORECASE | re.DOTALL)
    draft = draft_m.group(1).strip() if draft_m else ""
    return score, reason, draft


def qualify(lead: dict, llm) -> tuple:
    """Return (score, reason, draft) for a lead using the LLM or fallback."""
    if llm is None:
        return _heuristic_score(lead)
    prompt = f"""You are a B2B sales expert for property maintenance services (rope access, glass cleaning, maintenance).
Score this lead HOT/WARM/COLD and write a short follow-up email draft in Indonesian.

Lead: {lead['name']} from {lead['company']} ({lead['industry']})
Estimated contract: Rp {lead['contract_value_estimate']:,.0f}
Source: {lead['source']}
Days since contact: {lead['days_since_contact']}
Engagement score: {lead['engagement_score']}/10

Return format:
SCORE: [HOT/WARM/COLD]
REASON: [1 sentence]
EMAIL_DRAFT: [3 sentences in Indonesian]"""
    try:
        text = llm.invoke(prompt).content
        return _parse_ai(text)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"AI call failed ({exc}); using heuristic fallback.")
        return _heuristic_score(lead)


# --------------------------------------------------------------------------- #
# UI
# --------------------------------------------------------------------------- #
llm = get_llm()
render_header(
    "🎯 Lead Qualification Bot",
    "AI-scored B2B sales pipeline for PT RKARI · v2.0 Amber Sales",
)
if llm is None:
    st.info("ℹ️ GROQ_API_KEY not set — running in **heuristic demo mode**. "
            "Set the key to enable Llama 3.3 70B scoring.")

counts = db.status_counts()
hc1, hc2, hc3, hc4, hc5 = st.columns(5)
hc1.metric("Total Leads", db.lead_count())
hc2.metric("🆕 New", counts.get("new", 0))
hc3.metric("🔥 Hot", counts.get("HOT", 0))
hc4.metric("🌤️ Warm", counts.get("WARM", 0))
hc5.metric("❄️ Cold", counts.get("COLD", 0))

tab_kanban, tab_qualify, tab_analytics, tab_templates, tab_data = st.tabs(
    ["📋 Kanban", "🤖 Qualify", "📊 Analytics", "✉️ Templates", "💾 Data & Export"]
)

# --------------------------------------------------------------------------- #
# TAB — Kanban board
# --------------------------------------------------------------------------- #
with tab_kanban:
    st.caption("Pipeline view — leads grouped by qualification status.")
    columns = [("new", "🆕 NEW"), ("HOT", "🔥 HOT"),
               ("WARM", "🌤️ WARM"), ("COLD", "❄️ COLD")]
    cols = st.columns(4)
    for (status, label), col in zip(columns, cols):
        with col:
            board = db.get_leads(status=status)
            st.markdown(f"#### {label}  ·  {len(board)}")
            for _, lead in board.head(25).iterrows():
                render_lead_card(
                    lead["name"], lead["company"],
                    lead["contract_value_estimate"],
                    (lead["ai_reason"] or "Not yet qualified"),
                    lead["status"] if lead["status"] != "new" else "NEW",
                )

# --------------------------------------------------------------------------- #
# TAB — Qualify (single + batch)
# --------------------------------------------------------------------------- #
with tab_qualify:
    st.subheader("🤖 Qualify Leads")
    bcol1, bcol2 = st.columns([1, 3])
    with bcol1:
        if st.button("⚡ Batch qualify all NEW", type="primary",
                     use_container_width=True):
            new_leads = db.get_leads(status="new")
            if new_leads.empty:
                st.info("No new leads to qualify.")
            else:
                progress = st.progress(0.0)
                for i, (_, lead) in enumerate(new_leads.iterrows()):
                    score, reason, draft = qualify(dict(lead), llm)
                    db.update_qualification(int(lead["id"]), score, reason, draft)
                    progress.progress((i + 1) / len(new_leads))
                db.add_log("batch_qualify", f"{len(new_leads)} leads", "operator")
                st.success(f"Qualified {len(new_leads)} leads.")
                st.rerun()
    with bcol2:
        st.caption("Batch runs the AI (or heuristic) over every lead still in NEW.")

    st.divider()
    all_leads = db.get_leads()
    if all_leads.empty:
        st.warning("No leads available.")
    else:
        lead_id = st.selectbox(
            "Pick a lead to qualify individually:",
            all_leads["id"].tolist(),
            format_func=lambda i: (
                f"#{i} — {all_leads.loc[all_leads['id'] == i, 'name'].iloc[0]} "
                f"({all_leads.loc[all_leads['id'] == i, 'company'].iloc[0]})"
            ),
        )
        lead = db.get_lead(int(lead_id))
        if lead and st.button("🤖 Qualify this lead"):
            with st.spinner("Analyzing..."):
                score, reason, draft = qualify(lead, llm)
                db.update_qualification(int(lead_id), score, reason, draft)
            st.rerun()
        if lead and lead.get("ai_score"):
            c1, c2 = st.columns(2)
            c1.metric("AI Score", lead["ai_score"])
            c2.metric("Contract Value", f"Rp {lead['contract_value_estimate']:,.0f}")
            st.markdown(f"**Reason:** {lead['ai_reason']}")
            st.markdown("**📧 Draft email:**")
            st.text_area("Draft", lead["email_draft"] or "", height=150,
                         label_visibility="collapsed")

# --------------------------------------------------------------------------- #
# TAB — Analytics
# --------------------------------------------------------------------------- #
with tab_analytics:
    st.subheader("📊 Pipeline Analytics")
    leads = db.get_leads()
    if leads.empty:
        st.warning("No data.")
    else:
        a1, a2 = st.columns(2)
        with a1:
            dist = leads["status"].replace({"new": "NEW"}).value_counts().reset_index()
            dist.columns = ["status", "count"]
            fig = px.bar(dist, x="status", y="count", color="status",
                         color_discrete_map=SCORE_COLORS, title="Score distribution")
            st.plotly_chart(fig, use_container_width=True)
        with a2:
            pipe = (leads.assign(status=leads["status"].replace({"new": "NEW"}))
                    .groupby("status")["contract_value_estimate"].sum().reset_index())
            fig2 = px.pie(pipe, names="status", values="contract_value_estimate",
                          color="status", color_discrete_map=SCORE_COLORS,
                          title="Pipeline value by score")
            st.plotly_chart(fig2, use_container_width=True)
        qualified = leads[leads["status"] != "new"]
        hot_value = leads.loc[leads["status"] == "HOT",
                              "contract_value_estimate"].sum()
        v1, v2, v3 = st.columns(3)
        v1.metric("Total pipeline", f"Rp {leads['contract_value_estimate'].sum():,.0f}")
        v2.metric("🔥 Hot pipeline", f"Rp {hot_value:,.0f}")
        v3.metric("Qualified", f"{len(qualified)}/{len(leads)}")
        st.divider()
        st.markdown("##### Industry breakdown")
        ind = px.bar(
            leads.groupby("industry")["contract_value_estimate"].sum().reset_index(),
            x="industry", y="contract_value_estimate", title="Value by industry")
        st.plotly_chart(ind, use_container_width=True)

# --------------------------------------------------------------------------- #
# TAB — Email templates
# --------------------------------------------------------------------------- #
with tab_templates:
    st.subheader("✉️ Email Template Manager")
    templates = db.get_templates()
    for t in templates:
        with st.expander(f"📄 {t['name']}"):
            body = st.text_area("Body", t["body"], key=f"tpl_{t['id']}", height=120)
            tc1, tc2 = st.columns([1, 1])
            if tc1.button("💾 Save", key=f"save_{t['id']}"):
                db.save_template(t["name"], sanitize_input(body, 2000))
                st.success("Saved.")
                st.rerun()
            if tc2.button("🗑️ Delete", key=f"del_{t['id']}"):
                db.delete_template(t["id"])
                st.rerun()
    st.divider()
    st.markdown("##### ➕ New template")
    with st.form("new_tpl", clear_on_submit=True):
        nm = st.text_input("Template name")
        bd = st.text_area("Template body (use {name}, {company})")
        if st.form_submit_button("Create") and nm:
            db.save_template(sanitize_input(nm, 80), sanitize_input(bd, 2000))
            st.rerun()

# --------------------------------------------------------------------------- #
# TAB — Data & export
# --------------------------------------------------------------------------- #
with tab_data:
    st.subheader("💾 Data & Export")
    f1, f2, f3, f4 = st.columns(4)
    leads_all = db.get_leads()
    industries = ["All"] + sorted(leads_all["industry"].dropna().unique().tolist())
    f_status = f1.selectbox("Status", ["All", "new", "HOT", "WARM", "COLD"])
    f_industry = f2.selectbox("Industry", industries)
    f_minval = f3.number_input("Min value (Rp)", value=0, step=5_000_000)
    f_search = f4.text_input("Search name/company")
    filtered = db.get_leads(
        status=f_status, industry=f_industry,
        min_value=f_minval or None, search=sanitize_input(f_search, 80) or None,
    )
    st.caption(f"{len(filtered)} leads match.")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    qualified = filtered[filtered["status"] != "new"]
    e1, e2 = st.columns(2)
    e1.download_button(
        "⬇️ Export filtered (CSV)", filtered.to_csv(index=False).encode("utf-8"),
        file_name="leads_filtered.csv", mime="text/csv", use_container_width=True)
    e2.download_button(
        "⬇️ Export qualified only (CSV)", qualified.to_csv(index=False).encode("utf-8"),
        file_name="leads_qualified.csv", mime="text/csv",
        disabled=qualified.empty, use_container_width=True)

render_footer()
