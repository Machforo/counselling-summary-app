import os
import json
import re
import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq.chat_models import ChatGroq
from mailslurp_client import Configuration, ApiClient, SendEmailOptions, InboxControllerApi

# Load .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MAILSLURP_API_KEY = os.getenv("MAILSLURP_API_KEY")

# Initialize Groq Chat model
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0.3,
    max_tokens=1024
)

# LangChain prompt for extracting summary
summary_prompt = PromptTemplate.from_template("""
You are a helpful assistant. From the chat transcript below, extract:
1. The student's career goals.
2. The main action items discussed.

Provide the output in valid JSON with keys:
- "career_goals" (a list of strings)
- "action_items" (a list of strings)

Chat Transcript:
{chat_transcript}
""")

# Email generation prompt
email_prompt = PromptTemplate.from_template("""
Using the following session summary, write a warm and friendly follow-up email to the student.
Make sure the tone is encouraging and clear. Include a greeting, recap, and next steps.

Career Goals: {career_goals}
Action Items: {action_items}

End with a kind closing, signed by "Your Career Counselor".
""")

# Streamlit UI
st.title("🧑‍🎓 Counseling Session Summarizer + Email Agent")
st.markdown("Paste the chat transcript between a student and a counselor below:")

chat_input = st.text_area("Chat Transcript", height=250)
student_email = st.text_input("Student Email (to send follow-up)", value="student@example.com")

if st.button("✍️ Generate Summary & Email"):
    if not chat_input.strip():
        st.warning("Please enter a chat transcript.")
    else:
        with st.spinner("Analyzing transcript..."):

            # Limit input to last 2000 characters to speed things up
            trimmed_input = chat_input[-2000:]

            summary_chain = LLMChain(llm=llm, prompt=summary_prompt)
            summary_output = summary_chain.run(chat_transcript=trimmed_input)

            # Try to parse the output as JSON
            try:
                summary = json.loads(summary_output)
            except json.JSONDecodeError:
                st.warning("⚠️ Failed to parse summary output. Attempting to fix...")

                # Try extracting JSON block using regex
                match = re.search(r"\{[\s\S]*\}", summary_output)
                if match:
                    try:
                        summary = json.loads(match.group())
                    except Exception as e:
                        st.error(f"Still unable to parse extracted JSON: {e}")
                        st.code(summary_output)
                        st.stop()
                else:
                    st.error("❌ Could not extract JSON block from output.")
                    st.code(summary_output)
                    st.stop()

            # Display JSON summary
            st.success("✅ Summary Extracted")
            st.json(summary)

            # Generate email using summary
            email_chain = LLMChain(llm=llm, prompt=email_prompt)
            email_text = email_chain.run(
                career_goals=summary["career_goals"],
                action_items=summary["action_items"]
            )

            st.subheader("📨 Generated Follow-up Email")
            st.text_area("Follow-up Email", email_text, height=200)

            # Store for later
            st.session_state.generated_email = email_text
            st.session_state.student_email = student_email

# MailSlurp sending
if "generated_email" in st.session_state:
    if st.button("📬 Send Email via MailSlurp"):
        try:
            configuration = Configuration()
            configuration.api_key['x-api-key'] = MAILSLURP_API_KEY
            with ApiClient(configuration) as api_client:
                inbox_api = InboxControllerApi(api_client)
                inbox = inbox_api.create_inbox()
                send_options = SendEmailOptions(
                    to=[st.session_state.student_email],
                    subject="Your Career Counseling Follow-up",
                    body=st.session_state.generated_email,
                    is_html=False
                )
                inbox_api.send_email(inbox.id, send_options)
                st.success(f"📤 Email sent to {st.session_state.student_email} via MailSlurp!")
        except Exception as e:
            st.error(f"Error sending email: {e}")

    if st.button("📩 Mock Send with smtplib"):
        import smtplib
        from email.message import EmailMessage

        msg = EmailMessage()
        student_name = st.session_state.get("student_name", "Student")
        msg.set_content(st.session_state.generated_email.replace("[Student's Name]", student_name))
        msg["Subject"] = "Your Career Counseling Follow-up"
        msg["From"] = "noreply@mockdomain.com"
        msg["To"] = st.session_state.student_email

        try:
            st.info(f"📧 [Mock] Sending to {msg['To']}")
            st.code(msg.as_string())
            st.success("Mock email 'sent' successfully!")
        except Exception as e:
            st.error(f"SMTP Error: {e}")
