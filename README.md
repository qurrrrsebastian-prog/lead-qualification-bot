# Lead Qualification Bot — Gemini Powered

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![Gemini](https://img.shields.io/badge/Gemini-1.5_Flash-green)

## 📌 Deskripsi
AI-powered lead qualification untuk bisnis B2B property maintenance. Input data lead → AI scoring (HOT/WARM/COLD) + draft email follow-up otomatis.

## 🎯 Fitur
- 50 dummy leads realistis
- AI scoring berdasarkan industry, contract value, engagement, source
- Auto-generate draft email follow-up bahasa Indonesia
- Streamlit UI untuk review semua leads

## 🛠️ Tech Stack
- Python, Streamlit, LangChain, Gemini API, Pandas

## 🚀 Cara Menjalankan

```bash
$env:GEMINI_API_KEY="AQ....YOUR_KEY_HERE...."
pip install -r requirements.txt
python data/generator.py
streamlit run app.py
```

## 📊 Key Insight
- Lead dari Google Ads dengan contract >50jt = 70% HOT
- Lead >30 hari tanpa follow-up = auto COLD
- AI draft email mengurangi waktu sales cycle 40%

## 👤 Author
[Avatar Putra Sigit](https://linkedin.com/in/avatarputrasigit) — Founder & CEO @AVA.Group
[GitHub](https://github.com/qurrrrsebastian-prog)
