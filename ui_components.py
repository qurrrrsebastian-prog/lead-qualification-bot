"""ui_components.py — Reusable UI components.
Author: Avatar Putra Sigit | GitHub: qurrrrsebastian-prog
"""
import streamlit as st

PRIMARY = "#D97706"
SECONDARY = "#FBBF24"

# Lead-score colour map (shared across the app).
SCORE_COLORS = {
    "HOT": "#DC2626",
    "WARM": "#D97706",
    "COLD": "#2563EB",
    "NEW": "#64748B",
}


def render_header(title: str, subtitle: str, color: str = PRIMARY) -> None:
    """Render a gradient page header."""
    st.markdown(
        f"""
    <div style="background: linear-gradient(135deg, {color}22, {color}08);
        border-left: 4px solid {color}; border-radius: 8px; padding: 20px 24px; margin-bottom: 20px;">
        <h1 style="color: {color}; margin: 0; font-size: 28px;">{title}</h1>
        <p style="color: #94A3B8; margin: 8px 0 0 0; font-size: 14px;">{subtitle}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    """Render the standard footer."""
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #64748B; font-size: 12px; padding: 10px;">
        <p>Built with ❤️ by <a href="https://github.com/qurrrrsebastian-prog" target="_blank">Avatar Putra Sigit</a>
        | Founder @AVA.Group | © 2026</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_status_badge(label: str, color: str) -> None:
    """Render a small pill-style status badge."""
    st.markdown(
        f"""
    <span style="background: {color}22; color: {color}; border: 1px solid {color}44;
        border-radius: 12px; padding: 4px 12px; font-size: 12px; font-weight: 600;">{label}</span>
    """,
        unsafe_allow_html=True,
    )


def render_card(title: str, content: str, color: str = PRIMARY) -> None:
    """Render a titled content card."""
    st.markdown(
        f"""
    <div style="background: {color}11; border: 1px solid {color}33; border-radius: 10px;
        padding: 16px; margin: 8px 0;">
        <h4 style="color: {color}; margin: 0 0 8px 0;">{title}</h4>
        <p style="color: #CBD5E1; margin: 0; font-size: 13px;">{content}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_lead_card(name: str, company: str, value: float, reason: str,
                     score: str) -> None:
    """Render a compact Kanban-style lead card."""
    color = SCORE_COLORS.get(score, PRIMARY)
    st.markdown(
        f"""
    <div style="background: {color}11; border: 1px solid {color}44; border-left: 4px solid {color};
        border-radius: 8px; padding: 10px 12px; margin: 6px 0;">
        <div style="color: #F1F5F9; font-weight: 600; font-size: 14px;">{name}</div>
        <div style="color: #94A3B8; font-size: 12px;">{company}</div>
        <div style="color: {color}; font-size: 13px; font-weight: 600; margin-top: 4px;">
            Rp {value:,.0f}</div>
        <div style="color: #CBD5E1; font-size: 11px; margin-top: 4px;">{reason}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
