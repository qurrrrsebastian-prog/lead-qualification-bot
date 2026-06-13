# Lead Qualification Bot — Groq Powered

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-orange)

## 📌 Deskripsi
AI-powered lead qualification untuk bisnis B2B property maintenance. Input data lead → AI (Groq Llama 3.3 70B) scoring (HOT/WARM/COLD) + draft email follow-up otomatis.

## 🎯 Fitur
- 50 dummy leads realistis
- AI scoring berdasarkan industry, contract value, engagement, source
- Auto-generate draft email follow-up bahasa Indonesia
- Streamlit UI untuk review semua leads

## 🛠️ Tech Stack
- Python, Streamlit, LangChain, Groq (Llama 3.3 70B), Pandas

## 🚀 Cara Menjalankan

```bash
# Ambil API key gratis di https://console.groq.com/keys
$env:GROQ_API_KEY="gsk_....YOUR_KEY_HERE...."
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
