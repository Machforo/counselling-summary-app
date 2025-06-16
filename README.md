# 🧑‍🎓 Career Counseling Session Summarizer + Email Agent

This Streamlit app summarizes a career counseling chat transcript and generates a personalized follow-up email using the **Groq `llama-3.1-8b-instant` model** and LangChain. The app optionally allows sending the email via **MailSlurp** or a **mock SMTP** method for testing.

## Reference Video : 

https://drive.google.com/file/d/13_m9bVt3BRjzbWYIWeMI2B9EoNl3_Hm8/view?usp=sharing
---

## ✨ Features

- 🔍 Extracts key **career goals** and **action items** from a student-counselor chat transcript
- ✉️ Automatically generates a **friendly follow-up email** to the student
- 💡 Customizes the email with the **student's name and email**
- 📬 Email sending options:
  - ✅ Mock SMTP (for testing)
  - ✅ MailSlurp API (requires a paid account)
- 🚀 Powered by **LangChain** + **Groq API**

---

## 🛠️ Tech Stack

- Python 🐍
- [Streamlit](https://streamlit.io/)
- [LangChain](https://www.langchain.com/)
- [Groq API](https://console.groq.com/)
- [MailSlurp API](https://www.mailslurp.com/) (optional)
- OpenAI-compatible LLM: `llama-3.1-8b-instant`

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/career-counseling-summarizer.git
cd career-counseling-summarizer
pip install -r requirements.txt
