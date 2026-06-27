"""database.py — SQLite persistence for the Lead Qualification Bot.
Author: Avatar Putra Sigit | GitHub: qurrrrsebastian-prog
"""
import os
import sqlite3
from datetime import datetime
from typing import List, Optional

import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")

DEFAULT_TEMPLATES = [
    ("HOT — Close", "Halo {name}, terima kasih atas ketertarikan {company}. "
     "Kami siap menjadwalkan survei lokasi minggu ini. Kapan waktu terbaik Anda?"),
    ("WARM — Nurture", "Halo {name}, kami dari tim layanan maintenance ingin "
     "berbagi studi kasus relevan untuk {company}. Boleh kami kirimkan?"),
    ("COLD — Re-engage", "Halo {name}, sudah beberapa waktu sejak kontak terakhir. "
     "Apakah kebutuhan maintenance {company} masih relevan untuk dibahas?"),
]


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with row access by name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables and seed default email templates."""
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, company TEXT,
            industry TEXT, contract_value_estimate REAL, source TEXT,
            days_since_contact INTEGER, engagement_score INTEGER,
            ai_score TEXT, ai_reason TEXT, email_draft TEXT,
            qualified_at TEXT, status TEXT DEFAULT 'new');
        CREATE TABLE IF NOT EXISTS qualification_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id INTEGER,
            timestamp TEXT, previous_score TEXT, new_score TEXT, reason TEXT);
        CREATE TABLE IF NOT EXISTS email_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, body TEXT);
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, user TEXT,
            action TEXT, details TEXT);
        """
    )
    for name, body in DEFAULT_TEMPLATES:
        conn.execute(
            "INSERT OR IGNORE INTO email_templates (name, body) VALUES (?, ?)",
            (name, body),
        )
    conn.commit()
    conn.close()


def add_log(action: str, details: str = "", user: str = "anonymous") -> None:
    """Append an entry to the audit log."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO audit_log (timestamp, user, action, details) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(timespec="seconds"), user, action, details),
    )
    conn.commit()
    conn.close()


# --------------------------------------------------------------------------- #
# Leads
# --------------------------------------------------------------------------- #
def lead_count() -> int:
    """Return the number of leads stored."""
    conn = get_connection()
    n = conn.execute("SELECT COUNT(*) AS c FROM leads").fetchone()["c"]
    conn.close()
    return int(n)


def import_leads(df: pd.DataFrame) -> int:
    """Import leads from a DataFrame if the table is empty. Returns rows added."""
    if df.empty or lead_count() > 0:
        return 0
    conn = get_connection()
    rows = []
    for _, r in df.iterrows():
        rows.append((
            str(r.get("name", "")), str(r.get("company", "")),
            str(r.get("industry", "")), float(r.get("contract_value_estimate", 0) or 0),
            str(r.get("source", "")), int(r.get("days_since_contact", 0) or 0),
            int(r.get("engagement_score", 0) or 0), "new",
        ))
    conn.executemany(
        """INSERT INTO leads (name, company, industry, contract_value_estimate,
           source, days_since_contact, engagement_score, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )
    conn.commit()
    conn.close()
    return len(rows)


def get_leads(
    status: Optional[str] = None,
    industry: Optional[str] = None,
    min_value: Optional[float] = None,
    search: Optional[str] = None,
) -> pd.DataFrame:
    """Return leads as a DataFrame, optionally filtered."""
    conn = get_connection()
    q = "SELECT * FROM leads WHERE 1=1"
    params: list = []
    if status and status != "All":
        q += " AND status = ?"
        params.append(status)
    if industry and industry != "All":
        q += " AND industry = ?"
        params.append(industry)
    if min_value:
        q += " AND contract_value_estimate >= ?"
        params.append(min_value)
    if search:
        q += " AND (name LIKE ? OR company LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    q += " ORDER BY contract_value_estimate DESC"
    df = pd.read_sql_query(q, conn, params=params)
    conn.close()
    return df


def get_lead(lead_id: int) -> Optional[dict]:
    """Return a single lead as a dict, or None."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_qualification(lead_id: int, ai_score: str, ai_reason: str,
                         email_draft: str) -> None:
    """Persist an AI qualification result and record the change history."""
    conn = get_connection()
    prev = conn.execute("SELECT ai_score FROM leads WHERE id = ?", (lead_id,)).fetchone()
    previous_score = prev["ai_score"] if prev else None
    ts = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        """UPDATE leads SET ai_score=?, ai_reason=?, email_draft=?,
           qualified_at=?, status=? WHERE id=?""",
        (ai_score, ai_reason, email_draft, ts, ai_score, lead_id),
    )
    conn.execute(
        """INSERT INTO qualification_history
           (lead_id, timestamp, previous_score, new_score, reason)
           VALUES (?, ?, ?, ?, ?)""",
        (lead_id, ts, previous_score, ai_score, ai_reason),
    )
    conn.commit()
    conn.close()


def status_counts() -> dict:
    """Return a dict of status -> count across all kanban columns."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT status, COUNT(*) AS c FROM leads GROUP BY status"
    ).fetchall()
    conn.close()
    return {r["status"]: r["c"] for r in rows}


# --------------------------------------------------------------------------- #
# Email templates
# --------------------------------------------------------------------------- #
def get_templates() -> List[dict]:
    """Return all email templates."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM email_templates ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_template(name: str, body: str) -> None:
    """Insert or update an email template by name."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO email_templates (name, body) VALUES (?, ?)
           ON CONFLICT(name) DO UPDATE SET body=excluded.body""",
        (name, body),
    )
    conn.commit()
    conn.close()


def delete_template(template_id: int) -> None:
    """Delete an email template by id."""
    conn = get_connection()
    conn.execute("DELETE FROM email_templates WHERE id = ?", (template_id,))
    conn.commit()
    conn.close()
