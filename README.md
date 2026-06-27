# Project #14 — AI Lead Qualification Bot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=chainlink&logoColor=white" />
  <img src="https://img.shields.io/badge/Gemini%20API-4285F4?style=flat&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" />
</p>

> AI scoring lead B2B otomatis: HOT / WARM / COLD. Input data lead, dapatkan score + draft email follow-up profesional.

---

## Demo Langsung

[![Deploy to Streamlit Cloud](https://img.shields.io/badge/Deploy-Streamlit%20Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://share.streamlit.io/deploy?repository=qurrrrsebastian-prog/lead-qualification-bot)

**Tech Stack:** `LangChain` · `Google Gemini API` · `Pandas` · `Streamlit`

---

## Fitur

| Fitur | Status |
|-------|--------|
| Lead scoring (HOT/WARM/COLD) | ✅ |
| Auto-generate follow-up email | ✅ |
| CSV upload batch processing | ✅ |
| Download hasil CSV | ✅ |
| Kriteria scoring customizable | ✅ |
| Tema gelap AVA purple | ✅ |

---

## Cara Menjalankan

```bash
git clone https://github.com/qurrrrsebastian-prog/lead-qualification-bot.git
cd lead-qualification-bot
pip install -r requirements.txt
$env:GEMINI_API_KEY="your_api_key_here"
streamlit run app.py
```

## Deploy ke Streamlit Cloud (GRATIS)

1. [share.streamlit.io](https://share.streamlit.io) → Login GitHub
2. **New app** → Pilih repo ini
3. Tambahkan secret: `GEMINI_API_KEY`
4. **Deploy**

---

## Struktur Project

```
lead-qualification-bot/
├── app.py              # Main Streamlit app
├── requirements.txt    # Dependencies
├── data/               # Sample lead data
├── .streamlit/
│   └── config.toml    # AVA purple branding
├── .gitignore
└── LICENSE            # MIT License
```

---

**Dibuat oleh:** [Avatar Putra Sigit](https://github.com/qurrrrsebastian-prog) · Founder @AVA.Group
