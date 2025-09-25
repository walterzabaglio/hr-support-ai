import streamlit as st
import openai

# Load OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="HR Support AI Sandbox", page_icon="💼")
st.title("💼 HR Support AI Sandbox")
st.write("Prototype of an HR assistant with confidence scoring and escalation to HR.")

# Fake HR doc snippets
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

    # Build message
    system_msg = "You are a helpful HR support assistant. Base answers on context if given."
    user_msg = f"Context: {context}\n\nQ: {prompt}" if context else prompt

    # Call OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]
    )

    answer = response['choices'][0]['message']['content']

    st.markdown("### 🤖 AI Answer")
    st.write(answer)

    st.markdown(f"**Confidence Score:** {confidence:.0%}")

    # If low confidence, offer escalation
    if confidence < 0.6:
        st.warning("I'm not fully confident in this answer. You may want to escalate to HR.")
        if st.button("📩 Escalate to HR"):
            # In a real app this would log to a database or send an email
            st.success("Your question has been sent to HR for follow-up!")
