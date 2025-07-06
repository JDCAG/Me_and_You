import streamlit as st
from openai import OpenAI

# Load API key from secrets
oai_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=oai_key)

# App Setup
st.set_page_config(page_title="Me & You – AI Life Dashboard", layout="wide")
st.title("🤖 Me & You – AI Life Dashboard")
st.markdown("Welcome to your AI-powered personal dashboard!")

# ---------------------- Smart To-Do List ----------------------
st.header("✅ Smart To-Do List")
todo_tasks = st.text_area("List your tasks for today (one per line)")
if st.button("Get Focus Strategy"):
    with st.spinner("Analyzing your tasks and optimizing your focus..."):
        todo_prompt = f"""You are a productivity strategist. Given the following to-do list, group the tasks into: 
1. Top Priorities 
2. Quick Wins 
3. Delegatable 
4. Time Blocks
Then suggest an efficient game plan.

Tasks:
{todo_tasks}"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": todo_prompt}]
        )
        st.subheader("🧠 Focus Strategy")
        st.write(response.choices[0].message.content)

# ---------------------- Journal Reflection ----------------------
st.header("📓 Daily Reflection")
journal_input = st.text_area("Write your thoughts or challenges from today")
if st.button("Analyze Reflection"):
    with st.spinner("Analyzing your journal entry..."):
        journal_prompt = f"""You are a personal AI life coach. Analyze the following journal entry and provide:
- Emotional tone summary
- Key themes
- One small improvement idea
- One affirmation to carry forward

Entry:
{journal_input}"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": journal_prompt}]
        )
        st.subheader("🌟 Reflection Analysis")
        st.write(response.choices[0].message.content)

# ---------------------- Brainstorm Assistant ----------------------
st.header("🧠 Brainstorm with Me")
brainstorm_prompt = st.text_area("What's on your mind? (idea, problem, strategy)")
if st.button("Brainstorm It"):
    with st.spinner("Let me think with you..."):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": brainstorm_prompt}]
        )
        st.subheader("🌍 AI's Brainstorm")
        st.write(response.choices[0].message.content)
