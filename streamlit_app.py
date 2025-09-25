import streamlit as st
from openai import OpenAI
import pandas as pd
import os

# ✅ Initialize OpenAI client (new SDK style)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="HR Support AI Sandbox", page_icon="💼")
st.title("💼 HR Support AI Sandbox")
st.write("Prototype of an HR assistant with confidence scoring and escalation to HR.")

# File where escalations will be logged
ESCALATION_FILE = "hr_escalations.csv"

# Fake HR doc snippets (simulating a small knowledge base)
docs = {
    "vacation": "Full-time employees accrue 15 vacation days per year. Requests must be submitted at least 2 weeks in advance via the HR portal.",
    "sick": "Employees are entitled to 10 sick days per year. If you are unwell for more than 3 consecutive days, a doctor's note is required.",
    "benefits": "Our benefits package includes medical, dental, and vision coverage, as well as a 401(k) with company match.",
    "remote": "Employees may request to work remotely up to 3 days per week with manager approval."
}

# User input
prompt = st.text_input("Ask HR AI something...")

if st.button("Send") and prompt:
    # Simple keyword-based confidence
    context = ""
    confidence = 0
    for key, snippet in docs.items():
        if key in prompt.lower():
            context = snippet
            confidence = 0.9
            break
    if not context:
        confidence = 0.4

    # Build user/system messages
    system_msg = "You are a helpful HR support assistant. Base answers on context if given."
    user_msg = f"Context: {context}\n\nQ: {prompt}" if context else prompt

    # ✅ Call OpenAI API (1.0 syntax)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # preferred model
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ]
        )
    except Exception as e:
        st.warning(f"⚠️ Primary model unavailable ({e}). Falling back to GPT-3.5.")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ]
        )

    # ✅ Extract content with new SDK
    answer = response.choices[0].message.content

    st.markdown("### 🤖 AI Answer")
    st.write(answer)

    st.markdown(f"**Confidence Score:** {confidence:.0%}")

    # Escalation path if low confidence
    if confidence < 0.6:
        st.warning("I'm not fully confident in this answer. You may want to escalate to HR.")
        if st.button("📩 Escalate to HR"):
            # Save escalation to CSV
            new_entry = pd.DataFrame([{
                "question": prompt,
                "answer": answer
            }])
            if os.path.exists(ESCALATION_FILE):
                new_entry.to_csv(ESCALATION_FILE, mode="a", header=False, index=False)
            else:
                new_entry.to_csv(ESCALATION_FILE, index=False)

            st.success("✅ Your question has been logged for HR review!")

# HR inbox viewer
if st.checkbox("📂 Show HR Inbox (Escalated Questions)"):
    if os.path.exists(ESCALATION_FILE):
        inbox = pd.read_csv(ESCALATION_FILE)
        st.dataframe(inbox)
    else:
        st.info("No escalated questions yet.")
