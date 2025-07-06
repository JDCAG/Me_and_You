import streamlit as st
from openai import OpenAI

# Load API key from secrets
oai_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=oai_key)

# App Setup
st.set_page_config(page_title="Me & You – AI Life Dashboard", layout="wide")
st.title("🤖 Me & You – AI Life Dashboard")
st.markdown("Welcome to your AI-powered personal dashboard!")

# ---------------------- Nudges & Reminders Display ----------------------
st.markdown("---")
st.subheader("🎯 Nudges & Gentle Reminders")

def display_nudges():
    import datetime
    today = datetime.date.today()
    nudges = []

    # 1. Approaching Deadlines
    tasks_due_soon = [
        t for t in st.session_state.tasks
        if t['status'] == 'pending' and t['due_date'] and (t['due_date'] == today or t['due_date'] == today + datetime.timedelta(days=1))
    ]
    for task in tasks_due_soon:
        due_status = "today" if task['due_date'] == today else "tomorrow"
        nudges.append(f"🔔 Heads up! **'{task['description']}'** is due {due_status}.")

    # 2. Overdue Task Emphasis (already handled in task list, but can add a summary nudge)
    overdue_tasks_count = len([
        t for t in st.session_state.tasks if t['status'] == 'pending' and t['due_date'] and t['due_date'] < today
    ])
    if overdue_tasks_count > 0:
        nudges.append(f"⏳ You have {overdue_tasks_count} overdue task(s). Let's tackle them!")

    # 3. Contextual Nudge Simulation (Kitchen & Company)
    kitchen_task_pending = None
    company_event_soon = None
    for task in st.session_state.tasks:
        if "kitchen" in task['description'].lower() and task['status'] == 'pending':
            kitchen_task_pending = task
        if "company" in task['description'].lower() and task['due_date'] and \
           today <= task['due_date'] <= today + datetime.timedelta(days=3):
            company_event_soon = task

    if kitchen_task_pending and company_event_soon:
        nudge_message = f"✨ Just a thought: With company coming for '{company_event_soon['description']}' (due {company_event_soon['due_date'].strftime('%Y-%m-%d')}), " \
                        f"maybe now's a good time to look at **'{kitchen_task_pending['description']}'**? " \
                        f"Even a small part, like the sink?"
        nudges.append(nudge_message)

    # 4. Nudge based on mood (Example - if user logged low focus)
    if st.session_state.get('mood_log'):
        last_mood_log = st.session_state.mood_log[-1]
        if "Not at all" in last_mood_log.get('focus', '') or "Poorly" in last_mood_log.get('sleep', ''):
            # Suggest an easy task if available
            easy_tasks = [t for t in st.session_state.tasks if t['status'] == 'pending' and t['priority'] == 'Low']
            if easy_tasks:
                nudges.append(f"Feeling a bit off? No worries. How about starting with something small, like **'{easy_tasks[0]['description']}'**?")
            else:
                nudges.append("Feeling a bit off? Remember to be kind to yourself. Maybe a short break or a simple, quick win?")

    # 5. Nudge for tasks blocking others (Placeholder - requires dependency tracking)
    # nudges.append("Reminder: Task 'X' is blocking Task 'Y'. Consider prioritizing 'X'.")


    if not nudges:
        st.info("No specific nudges right now. You're on top of things or it's a fresh start!")
    else:
        for i, nudge in enumerate(nudges):
            # Using st.info, st.warning, or custom markdown for different nudge types
            if "overdue" in nudge.lower() or "blocking" in nudge.lower():
                st.warning(nudge)
            elif "heads up" in nudge.lower() or "reminder" in nudge.lower() or "small" in nudge.lower():
                st.success(nudge, icon="💡") # Using success for a lighter touch, like a gentle idea
            else:
                st.info(nudge)
            if i < len(nudges) -1:
                 st.markdown("---")


if 'tasks' in st.session_state and st.session_state.tasks is not None : # Ensure tasks exist
    display_nudges()
else:
    st.info("Add some tasks to get personalized nudges!")


# ---------------------- Smart To-Do List ----------------------
st.header("✅ Smart To-Do List")

# Initialize session state for tasks if not already present
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# --- Task Input Form ---
st.subheader("➕ Add New Task")
task_description = st.text_input("Task Description:")
task_due_date = st.date_input("Due Date (Optional):", value=None)
task_priority_options = ["None", "Low", "Medium", "High"]
task_priority = st.selectbox("Priority (Optional):", options=task_priority_options)

if st.button("💾 Save Task"):
    if not task_description:
        st.warning("Task description cannot be empty.")
    else:
        # Auto-classification (simple keyword-based for now)
        task_type = "personal" # Default
        description_lower = task_description.lower()
        if any(keyword in description_lower for keyword in ["work", "meeting", "project", "email", "report"]):
            task_type = "work"
        elif any(keyword in description_lower for keyword in ["bill", "appointment", "irs", "bank", "admin"]):
            task_type = "admin"
        elif any(keyword in description_lower for keyword in ["meditation", "journal", "connect", "feelings"]):
            task_type = "emotional"

        new_task = {
            "id": len(st.session_state.tasks) + 1,
            "description": task_description,
            "due_date": task_due_date,
            "priority": task_priority,
            "type": task_type,
            "status": "pending"
        }
        st.session_state.tasks.append(new_task)
        st.success(f"Task '{task_description}' added!")
        # Clear inputs for next task - Streamlit reruns, so widgets will reset if their keys aren't managed
        # For a true "clear", we'd need to use widget keys and reset them, or re-structure.
        # For now, this relies on the user typing new values.

# --- Display Tasks ---
st.subheader("📋 Your Tasks")
if not st.session_state.tasks:
    st.info("No tasks yet. Add some above!")
else:
    import datetime

    today = datetime.date.today()
    overdue_tasks = []
    pending_tasks = []
    completed_tasks = []

    for task in st.session_state.tasks:
        if task['status'] == 'completed':
            completed_tasks.append(task)
        elif task['due_date'] and task['due_date'] < today and task['status'] == 'pending':
            overdue_tasks.append(task)
        else:
            pending_tasks.append(task)

    if overdue_tasks:
        st.warning(f"🚨 You have {len(overdue_tasks)} overdue task(s)!")
        for i, task in enumerate(overdue_tasks):
            st.markdown(f"""
            **{task['description']}** (Overdue since: {task['due_date'].strftime('%Y-%m-%d')})
            - Priority: {task['priority']}
            - Type: {task['type']}
            """)
            col1, col2, col3, col4 = st.columns(4)
            if col1.button(f"Mark Completed##overdue_{task['id']}", key=f"complete_overdue_{task['id']}"):
                task['status'] = 'completed'
                st.rerun()
            if col2.button(f"Move to Today##overdue_{task['id']}", key=f"today_overdue_{task['id']}"):
                task['due_date'] = today
                st.rerun()
            if col3.button(f"Move to Tomorrow##overdue_{task['id']}", key=f"tomorrow_overdue_{task['id']}"):
                task['due_date'] = today + datetime.timedelta(days=1)
                st.rerun()
            # Add more options like "Delete" or "Edit" later
            st.markdown("---")


    st.markdown("---")
    st.write("### Current & Upcoming Tasks")
    if not pending_tasks and not overdue_tasks: # If only completed tasks exist or no tasks
        if not any(t for t in st.session_state.tasks if t['status'] == 'pending'):
             st.info("No pending tasks. Great job or add some new ones!")

    for task in pending_tasks: # Display non-overdue pending tasks
        if task['status'] == 'pending': # Double check, though list is pre-filtered
            st.markdown(f"""
            **{task['description']}**
            - Due: {task['due_date'].strftime('%Y-%m-%d') if task['due_date'] else 'Not set'}
            - Priority: {task['priority']}
            - Type: {task['type']}
            - Status: {task['status']}
            """)
            col1, col2, col3 = st.columns(3)
            if col1.button(f"Mark Completed##{task['id']}", key=f"complete_{task['id']}"):
                task['status'] = 'completed'
                st.rerun()
            if col2.button(f"Edit##{task['id']}", key=f"edit_{task['id']}"):
                st.warning("Edit functionality not yet implemented.") # Placeholder
            if col3.button(f"Delete##{task['id']}", key=f"delete_{task['id']}"):
                st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                st.rerun()
            st.markdown("---")

    if completed_tasks:
        st.markdown("---")
        st.write("### ✅ Completed Tasks")
        for task in completed_tasks:
            st.markdown(f"""
            ~~**{task['description']}**~~ (Completed)
            - Due: {task['due_date'].strftime('%Y-%m-%d') if task['due_date'] else 'Not set'}
            - Priority: {task['priority']}
            - Type: {task['type']}
            """)
            if st.button(f"Mark Pending##completed_{task['id']}", key=f"uncomplete_{task['id']}"):
                task['status'] = 'pending'
                st.rerun()
            st.markdown("---")


# --- Original GPT-4 To-Do Analysis (can be adapted or removed) ---
st.markdown("---")
st.header("💡 Task Analysis (Legacy)")
# todo_tasks_text = "\n".join([t['description'] for t in st.session_state.tasks]) # Use new task list
# st.text_area("Current tasks for analysis:", value=todo_tasks_text, height=100, disabled=True)

# if st.button("Get Focus Strategy (on current tasks)"):
#     if not st.session_state.tasks:
#         st.warning("No tasks to analyze.")
#     else:
#         with st.spinner("Analyzing your tasks and optimizing your focus..."):
#             todo_prompt = f"""You are a productivity strategist. Given the following to-do list, group the tasks into:
# 1. Top Priorities
# 2. Quick Wins
# 3. Delegatable
# 4. Time Blocks
# Then suggest an efficient game plan.

# Tasks:
# {"\n".join([t['description'] for t in st.session_state.tasks])}"""

#             response = client.chat.completions.create(
#                 model="gpt-4",
#                 messages=[{"role": "user", "content": todo_prompt}]
#             )
#             st.subheader("🧠 Focus Strategy")
#             st.write(response.choices[0].message.content)


# ---------------------- Document Upload & Task Extraction ----------------------
st.markdown("---")
st.header("📄 Document Upload & Task Extraction")

# Initialize session state for document analysis results if not already present
if 'doc_analysis_results' not in st.session_state:
    st.session_state.doc_analysis_results = None
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None


import PyPDF2
import pandas as pd
import io

def extract_text_from_pdf(file_bytes):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Error extracting PDF: {e}"

def extract_data_from_csv(file_bytes):
    try:
        # Read CSV into pandas DataFrame
        # Use BytesIO to treat bytes as a file
        string_data = io.StringIO(file_bytes.decode('utf-8'))
        df = pd.read_csv(string_data)
        return df.to_string() # Convert DataFrame to string for GPT analysis
    except Exception as e:
        return f"Error extracting CSV: {e}"

def extract_data_from_excel(file_bytes):
    try:
        # Read Excel into pandas DataFrame
        # Use BytesIO to treat bytes as a file
        df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl') # Specify engine
        return df.to_string() # Convert DataFrame to string for GPT analysis
    except Exception as e:
        return f"Error extracting Excel: {e}"

uploaded_file = st.file_uploader("Upload a document (PDF, CSV, Excel)", type=["pdf", "csv", "xlsx"])

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    file_name = uploaded_file.name
    st.session_state.uploaded_file_name = file_name
    st.write(f"Uploaded: {file_name}")

    extracted_text = ""
    if file_name.lower().endswith(".pdf"):
        with st.spinner(f"Extracting text from {file_name}..."):
            extracted_text = extract_text_from_pdf(file_bytes)
    elif file_name.lower().endswith(".csv"):
        with st.spinner(f"Extracting data from {file_name}..."):
            extracted_text = extract_data_from_csv(file_bytes)
    elif file_name.lower().endswith(".xlsx"):
        with st.spinner(f"Extracting data from {file_name}..."):
            extracted_text = extract_data_from_excel(file_bytes)

    if extracted_text.startswith("Error extracting"):
        st.error(extracted_text)
        st.session_state.doc_analysis_results = None # Clear previous results
    elif extracted_text:
        st.text_area("Extracted Content (Preview)", extracted_text[:2000], height=200) # Show preview

        if st.button("✨ Analyze Document & Suggest Tasks", key=f"analyze_{file_name}"):
            st.session_state.doc_analysis_results = None # Clear previous results before new analysis
            with st.spinner(f"Asking AI to analyze '{file_name}' and suggest tasks..."):
                prompt = f"""You are an AI assistant that helps extract actionable tasks from documents.
Given the following text extracted from a document named '{file_name}', please:
1. Briefly summarize the document's purpose or main content.
2. Identify any potential deadlines, important dates, or events.
3. Identify key entities, amounts, or reference numbers.
4. Suggest 1-3 specific, actionable tasks that should be added to a to-do list based on this document. For each task, suggest a concise description. If possible, infer a due date from the text.

Extracted text:
---
{extracted_text[:10000]}
---
Please format your response clearly. For suggested tasks, use a format like:
- Task: [Description of task] (Due: [YYYY-MM-DD or 'Not specified'])
"""
                try:
                    response = client.chat.completions.create(
                        model="gpt-4", # Or gpt-3.5-turbo for faster/cheaper results
                        messages=[{"role": "user", "content": prompt}]
                    )
                    st.session_state.doc_analysis_results = response.choices[0].message.content
                except Exception as e:
                    st.error(f"Error calling OpenAI API: {e}")
                    st.session_state.doc_analysis_results = None
    else:
        st.info("Could not extract text or data from the document.")
        st.session_state.doc_analysis_results = None


if st.session_state.get('doc_analysis_results'):
    st.subheader(f"💡 Analysis & Suggested Tasks for {st.session_state.uploaded_file_name}")
    st.markdown(st.session_state.doc_analysis_results)

    # Basic parsing of suggested tasks (example - this needs to be robust)
    # This is a simplified example. Real parsing would need regex or more structured GPT output.
    lines = st.session_state.doc_analysis_results.splitlines()
    suggested_doc_tasks = []
    import re
    for line in lines:
        match = re.search(r"Task: (.*) \(Due: (.*)\)", line, re.IGNORECASE)
        if match:
            desc, due_str = match.groups()
            due_date = None
            try:
                if due_str.lower() != 'not specified' and due_str:
                    due_date = datetime.datetime.strptime(due_str.strip(), "%Y-%m-%d").date()
            except ValueError: # Handle cases where date parsing might fail
                pass # Keep due_date as None
            suggested_doc_tasks.append({"description": desc.strip(), "due_date": due_date})

    if suggested_doc_tasks:
        st.write("---")
        st.subheader("Quick Add Suggested Tasks:")
        for i, suggested_task in enumerate(suggested_doc_tasks):
            task_desc_with_due = f"{suggested_task['description']}"
            if suggested_task['due_date']:
                task_desc_with_due += f" (Due: {suggested_task['due_date'].strftime('%Y-%m-%d')})"

            if st.button(f"➕ Add Task: {task_desc_with_due}", key=f"add_suggested_task_{i}_{st.session_state.uploaded_file_name}"):
                # Auto-classification (simple keyword-based for now)
                task_type = "admin" # Default for document tasks
                description_lower = suggested_task['description'].lower()
                if any(keyword in description_lower for keyword in ["work", "meeting", "project"]):
                    task_type = "work"

                new_task_entry = {
                    "id": len(st.session_state.tasks) + 1,
                    "description": suggested_task['description'],
                    "due_date": suggested_task['due_date'],
                    "priority": "Medium", # Default priority for suggested tasks
                    "type": task_type,
                    "status": "pending"
                }
                st.session_state.tasks.append(new_task_entry)
                st.success(f"Task '{suggested_task['description']}' added to your to-do list!")
                # To prevent re-adding on rerun if button remains, could clear doc_analysis_results or use more complex state
    st.markdown("---")


# ---------------------- Mood & Sleep Check-in ----------------------
st.markdown("---")
st.header("☀️ Mood & Sleep Check-in")

if 'mood_log' not in st.session_state:
    st.session_state.mood_log = []
if 'current_mood_selection' not in st.session_state:
    st.session_state.current_mood_selection = None

st.subheader("How are you feeling today?")
mood_options = {
    "🙂 Happy": "🙂",
    "😊 Content": "😊",
    "😐 Neutral": "😐",
    "😟 Worried": "😟",
    "😠 Annoyed": "😠",
    "😢 Sad": "😢",
    "😴 Tired": "😴",
    "😵‍💫 Overwhelmed": "😵‍💫",
    "🤩 Excited": "🤩",
    "🤔 Thoughtful": "🤔"
}
# Display moods in columns
cols = st.columns(5)
mood_keys = list(mood_options.keys())
for i, mood_text in enumerate(mood_keys):
    col_idx = i % 5
    if cols[col_idx].button(f"{mood_options[mood_text]} {mood_text}", key=f"mood_{mood_text}"):
        st.session_state.current_mood_selection = mood_text
        # st.write(f"You selected: {st.session_state.current_mood_selection}") # Optional: immediate feedback

if st.session_state.current_mood_selection:
    st.markdown(f"**Selected Mood:** {st.session_state.current_mood_selection.split(' ')[1]}")


sleep_options = ["😴 Poorly", "😐 Okay", "👍 Great!"]
selected_sleep = st.radio(
    "How did you sleep last night?",
    options=sleep_options,
    index=1, # Default to 'Okay'
    horizontal=True,
    key="sleep_quality"
)

focus_options = ["📉 Not at all", "📊 Somewhat", "📈 Very Focused"]
selected_focus = st.radio(
    "How focused are you feeling right now?",
    options=focus_options,
    index=1, # Default to 'Somewhat'
    horizontal=True,
    key="focus_level"
)

if st.button("💾 Log Mood & Energy"):
    if st.session_state.current_mood_selection:
        import datetime
        log_entry = {
            "timestamp": datetime.datetime.now(),
            "mood": st.session_state.current_mood_selection,
            "sleep": selected_sleep,
            "focus": selected_focus
        }
        st.session_state.mood_log.append(log_entry)
        st.success(f"Logged: {log_entry['mood']}, Sleep: {log_entry['sleep']}, Focus: {log_entry['focus']}")
        st.session_state.current_mood_selection = None # Reset mood selection for next time
        st.rerun() # Rerun to clear selection and update log display
    else:
        st.warning("Please select a mood first.")

# Display Mood Log
st.subheader("Recent Check-ins")
if not st.session_state.mood_log:
    st.info("No mood check-ins logged yet.")
else:
    # Display last 5 entries
    for entry in reversed(st.session_state.mood_log[-5:]):
        st.markdown(f"""
        - **{entry['timestamp'].strftime('%Y-%m-%d %H:%M')}**:
          Mood: {entry['mood']}, Sleep: {entry['sleep']}, Focus: {entry['focus']}
        """)
    if len(st.session_state.mood_log) > 5:
        if st.expander("View all check-ins"):
            for entry in reversed(st.session_state.mood_log):
                st.markdown(f"""
                - **{entry['timestamp'].strftime('%Y-%m-%d %H:%M')}**:
                  Mood: {entry['mood']}, Sleep: {entry['sleep']}, Focus: {entry['focus']}
                """)
st.markdown("---")


# ---------------------- Journal Reflection ----------------------
# todo_tasks_text = "\n".join([t['description'] for t in st.session_state.tasks]) # Use new task list
# st.text_area("Current tasks for analysis:", value=todo_tasks_text, height=100, disabled=True)

# if st.button("Get Focus Strategy (on current tasks)"):
#     if not st.session_state.tasks:
#         st.warning("No tasks to analyze.")
#     else:
#         with st.spinner("Analyzing your tasks and optimizing your focus..."):
#             todo_prompt = f"""You are a productivity strategist. Given the following to-do list, group the tasks into:
# 1. Top Priorities
# 2. Quick Wins
# 3. Delegatable
# 4. Time Blocks
# Then suggest an efficient game plan.

# Tasks:
# {"\n".join([t['description'] for t in st.session_state.tasks])}"""

#             response = client.chat.completions.create(
#                 model="gpt-4",
#                 messages=[{"role": "user", "content": todo_prompt}]
#             )
#             st.subheader("🧠 Focus Strategy")
#             st.write(response.choices[0].message.content)


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

# ---------------------- Brain Dump / Think With Me ----------------------
st.markdown("---")
st.header("🤔 Brain Dump / Think With Me")

if 'brain_dump_analysis' not in st.session_state:
    st.session_state.brain_dump_analysis = None
if 'brain_dump_text_input' not in st.session_state: # To store the user's input
    st.session_state.brain_dump_text_input = ""

# Use a key for text_area to potentially manage its state better if needed
user_brain_dump = st.text_area("Jot down your thoughts, ideas, worries, or anything on your mind...", height=200, key="brain_dump_input", value=st.session_state.brain_dump_text_input)

if st.button("💡 Think With Me"):
    if user_brain_dump:
        st.session_state.brain_dump_text_input = user_brain_dump # Save current input
        st.session_state.brain_dump_analysis = None # Clear previous analysis
        with st.spinner("Processing your thoughts..."):
            prompt = f"""You are a helpful AI assistant. The user has provided the following "brain dump" text.
Please:
1.  Acknowledge their thoughts empathetically.
2.  Scan the text for any statements that sound like actionable tasks. For each potential task, rephrase it clearly and ask if they'd like to add it to their to-do list. Present these as a list. Use the format:
    - Potential Task: [Description of task]
3.  Identify 2-3 key themes or ideas in the text that they might want to revisit later. List them as "Themes/Ideas to Revisit:".
4.  Conclude with a supportive or encouraging remark.

User's Brain Dump:
---
{user_brain_dump}
---

Example of how to suggest tasks (if any are found):
If the user writes "I need to remember to buy milk and also that report is due Friday", you could suggest:
- Potential Task: Buy milk
- Potential Task: Complete report (Due: Friday)

If no tasks are obvious, just say something like "I didn't spot any clear tasks in this dump, but let me know if I missed something!"
"""
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.session_state.brain_dump_analysis = response.choices[0].message.content
            except Exception as e:
                st.error(f"Error calling OpenAI API: {e}")
                st.session_state.brain_dump_analysis = "Sorry, I couldn't process that right now."
        st.rerun() # Rerun to display analysis and clear the button press state
    else:
        st.info("Pour your thoughts into the text box above, and I'll help you sort them out!")

if st.session_state.brain_dump_analysis:
    st.subheader("AI Companion's Thoughts:")
    st.markdown(st.session_state.brain_dump_analysis)

    # Parse potential tasks from the analysis
    lines = st.session_state.brain_dump_analysis.splitlines()
    suggested_braindump_tasks = []
    import re
    import datetime # Ensure datetime is available

    for line in lines:
        # Regex to capture task description and optional due date
        match = re.search(r"- Potential Task: (.*?)(?:\s*\(Due: (.*?)\))?$", line.strip())
        if match:
            desc = match.group(1).strip()
            due_str = match.group(2)
            due_date = None
            if due_str:
                due_str = due_str.strip()
                # Attempt to parse various date formats if GPT provides them
                # For simplicity, sticking to YYYY-MM-DD or specific keywords
                try:
                    if due_str.lower() == 'today':
                        due_date = datetime.date.today()
                    elif due_str.lower() == 'tomorrow':
                        due_date = datetime.date.today() + datetime.timedelta(days=1)
                    # Add more flexible date parsing here if needed e.g. using dateutil.parser
                    # For now, assume YYYY-MM-DD if not 'today' or 'tomorrow'
                    elif re.match(r"\d{4}-\d{2}-\d{2}", due_str):
                         due_date = datetime.datetime.strptime(due_str, "%Y-%m-%d").date()
                    # else, could try to parse with dateutil, or leave as None
                except ValueError:
                    pass # due_date remains None if parsing fails
            suggested_braindump_tasks.append({"description": desc, "due_date": due_date, "raw_line": line})

    if suggested_braindump_tasks:
        st.write("---")
        st.subheader("✏️ Add to Your To-Do List?")
        for i, s_task in enumerate(suggested_braindump_tasks):
            task_display_text = s_task['description']
            if s_task['due_date']:
                task_display_text += f" (Due: {s_task['due_date'].strftime('%Y-%m-%d')})"

            if st.button(f"➕ Add: {task_display_text}", key=f"add_braindump_task_{i}"):
                task_type = "personal" # Default
                description_lower = s_task['description'].lower()
                if any(keyword in description_lower for keyword in ["work", "meeting", "project", "email", "report"]):
                    task_type = "work"
                elif any(keyword in description_lower for keyword in ["bill", "appointment", "irs", "bank", "admin"]):
                    task_type = "admin"

                new_task_entry = {
                    "id": len(st.session_state.tasks) + 1,
                    "description": s_task['description'],
                    "due_date": s_task['due_date'],
                    "priority": "Medium", # Default priority
                    "type": task_type,
                    "status": "pending"
                }
                st.session_state.tasks.append(new_task_entry)
                st.success(f"Task '{s_task['description']}' added!")
                # Remove the added task from suggestions to prevent re-adding
                st.session_state.brain_dump_analysis = st.session_state.brain_dump_analysis.replace(s_task['raw_line'], f"- ~~{s_task['raw_line'].lstrip('- ')}~~ (Added)")
                st.rerun()
    st.markdown("---")

# ---------------------- Voice Assistant (Text Simulation) ----------------------
st.markdown("---")
st.header("🗣️ Voice Assistant (Text Simulation)")

if 'voice_assistant_response' not in st.session_state:
    st.session_state.voice_assistant_response = None
if 'voice_command_history' not in st.session_state: # To store conversation
    st.session_state.voice_command_history = []

# Display conversation history (optional, could be nice for context)
# for entry in st.session_state.voice_command_history:
#     if entry['role'] == 'user':
#         st.text_area("You:", value=entry['content'], disabled=True, height=50, key=f"hist_user_{entry['content'][:10]}")
#     else: # assistant
#         st.markdown(f"**Me & You AI:** {entry['content']}")

user_voice_command = st.text_input("Type your command (e.g., 'Add task buy groceries for tomorrow', 'What are my tasks today?')", key="voice_command_input")

if st.button("💬 Send Command", key="send_voice_command"):
    if user_voice_command:
        st.session_state.voice_command_history.append({"role": "user", "content": user_voice_command})
        st.session_state.voice_assistant_response = None # Clear previous response

        # Prepare a simplified list of current tasks for context to GPT
        # This helps with commands like "Did I finish X?" or "Complete Y"
        current_tasks_summary = []
        for task in st.session_state.tasks:
            due_date_str = f" (Due: {task['due_date'].strftime('%Y-%m-%d')})" if task['due_date'] else ""
            status_str = f" (Status: {task['status']})"
            current_tasks_summary.append(f"- {task['description']}{due_date_str}{status_str}")
        tasks_context_str = "\n".join(current_tasks_summary)
        if not tasks_context_str:
            tasks_context_str = "No tasks currently in the list."

        with st.spinner("Thinking..."):
            prompt = f"""You are "Me & You", a friendly and helpful voice assistant.
The user has typed the following command: "{user_voice_command}"

Current tasks in the user's list:
{tasks_context_str}

Your goal is to:
1. Understand the user's command.
2. Provide a natural, conversational response.
3. If the command implies an action on the task list (add, complete, list, check status), explicitly state the action you will perform in a structured way on a NEWLINE at the VERY END of your response. Use ONE of the following formats:
   ACTION: ADD_TASK | DESCRIPTION: [task description] | DUE_DATE_STR: [e.g., tomorrow, next Friday, YYYY-MM-DD, or N/A]
   ACTION: COMPLETE_TASK | DESCRIPTION: [task description from the list to mark complete]
   ACTION: LIST_TASKS | FILTER: [today, overdue, all, or based on user query e.g., 'pending work tasks']
   ACTION: CHECK_STATUS | DESCRIPTION: [task description from the list to check]
   ACTION: GENERAL_QUERY (If no task list action is needed)

Examples:
User: Add 'Submit report' for this Friday
Assistant Response: Okay, I'll add "Submit report" for this Friday to your task list. You got this!
ACTION: ADD_TASK | DESCRIPTION: Submit report | DUE_DATE_STR: this Friday

User: What do I have today?
Assistant Response: Let's see what's on your plate for today...
ACTION: LIST_TASKS | FILTER: today

User: Mark 'call John' as done.
Assistant Response: Great job finishing 'call John'! I've marked it as completed.
ACTION: COMPLETE_TASK | DESCRIPTION: call John

User: How is the weather?
Assistant Response: I can't check the weather, but I can help you with your tasks!
ACTION: GENERAL_QUERY

User: Did I finish the IRS task?
Assistant Response: Let me check on the 'IRS task' for you... (then AI would see its status from context)
ACTION: CHECK_STATUS | DESCRIPTION: IRS task

Respond naturally, then add the ACTION line if applicable.
"""
            try:
                # For more conversational context, could include previous turns from st.session_state.voice_command_history
                messages = [{"role": "system", "content": "You are 'Me & You', a friendly and helpful voice assistant."}]
                # Add recent history if any
                # for entry in st.session_state.voice_command_history[-3:]: # last few turns
                #    messages.append(entry)
                messages.append({"role": "user", "content": prompt}) # Using the detailed prompt as the user message here for simplicity

                response = client.chat.completions.create(
                    model="gpt-4", # Or "gpt-4o" if available and preferred
                    messages=messages
                )
                full_gpt_response = response.choices[0].message.content
                st.session_state.voice_assistant_response = full_gpt_response
                st.session_state.voice_command_history.append({"role": "assistant", "content": full_gpt_response})

            except Exception as e:
                st.error(f"Error calling OpenAI API: {e}")
                st.session_state.voice_assistant_response = "Sorry, I couldn't process that command right now."
                st.session_state.voice_command_history.append({"role": "assistant", "content": st.session_state.voice_assistant_response})
        st.rerun() # Rerun to display response and clear input
    else:
        st.info("Please type a command for the assistant.")

if st.session_state.voice_assistant_response:
    st.subheader("📣 Me & You AI Says:")

    # Separate the natural language part from the action line
    response_lines = st.session_state.voice_assistant_response.splitlines()
    natural_response_parts = []
    action_line = None
    for line in response_lines:
        if line.startswith("ACTION:"):
            action_line = line
        else:
            natural_response_parts.append(line)

    natural_response_display = "\n".join(natural_response_parts).strip()
    if natural_response_display:
        st.markdown(natural_response_display)
    else: # If AI only returned action_line or empty response before action
        st.markdown("Got it.")


    if action_line:
        st.write(f"*(Action identified: `{action_line}`)*") # For debugging/clarity
        try:
            import re
            import datetime

            action_parts = [part.strip() for part in action_line.split("|")]
            action_type = action_parts[0].replace("ACTION:", "").strip()

            action_params = {}
            for part in action_parts[1:]:
                key_value = part.split(":", 1)
                if len(key_value) == 2:
                    action_params[key_value[0].strip()] = key_value[1].strip()

            if action_type == "ADD_TASK":
                desc = action_params.get("DESCRIPTION")
                due_str = action_params.get("DUE_DATE_STR", "N/A")
                due_date = None
                if desc:
                    if due_str and due_str.lower() != 'n/a':
                        # Simplified date parsing (can be expanded)
                        if 'today' in due_str.lower():
                            due_date = datetime.date.today()
                        elif 'tomorrow' in due_str.lower():
                            due_date = datetime.date.today() + datetime.timedelta(days=1)
                        elif 'next week' in due_str.lower(): # very basic
                            due_date = datetime.date.today() + datetime.timedelta(days=7)
                        else: # Try to parse specific dates like YYYY-MM-DD or day names
                            try:
                                # Attempt to parse YYYY-MM-DD
                                due_date = datetime.datetime.strptime(due_str, "%Y-%m-%d").date()
                            except ValueError:
                                # Attempt to parse day names (e.g., "Friday")
                                # This is complex; for now, we'll just say "N/A" if not simple
                                # A more robust solution would use dateutil.parser or more sophisticated NLP
                                current_weekday = datetime.date.today().weekday() # Monday is 0 and Sunday is 6
                                days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                                if due_str.lower() in days:
                                    target_weekday = days.index(due_str.lower())
                                    days_ahead = target_weekday - current_weekday
                                    if days_ahead <= 0: # If it's today or already passed this week
                                        days_ahead += 7
                                    due_date = datetime.date.today() + datetime.timedelta(days=days_ahead)
                                else:
                                     st.warning(f"Could not parse due date: '{due_str}'. Task added without due date.")


                    task_type = "personal" # Default
                    if any(keyword in desc.lower() for keyword in ["work", "meeting", "project"]): task_type = "work"

                    new_task_entry = {
                        "id": len(st.session_state.tasks) + 1, "description": desc,
                        "due_date": due_date, "priority": "Medium", "type": task_type, "status": "pending"
                    }
                    st.session_state.tasks.append(new_task_entry)
                    st.success(f"✅ Task '{desc}' added to your list by voice command!")
                    # No rerun here, success message is enough, main response already shown
                else:
                    st.error("Assistant tried to add a task but description was missing.")

            elif action_type == "COMPLETE_TASK":
                desc_to_complete = action_params.get("DESCRIPTION")
                task_found_and_completed = False
                if desc_to_complete:
                    for task in st.session_state.tasks:
                        if task['description'].lower() == desc_to_complete.lower() and task['status'] == 'pending':
                            task['status'] = 'completed'
                            st.success(f"✅ Task '{task['description']}' marked as complete by voice command!")
                            task_found_and_completed = True
                            break
                    if not task_found_and_completed:
                        st.warning(f"Could not find pending task '{desc_to_complete}' to mark complete.")
                else:
                    st.error("Assistant tried to complete a task but description was missing.")

            elif action_type == "LIST_TASKS":
                filter_str = action_params.get("FILTER", "all").lower()
                st.subheader(f"📋 Tasks based on your command (Filter: {filter_str}):")
                tasks_to_show = []
                today = datetime.date.today()

                if filter_str == "today":
                    tasks_to_show = [t for t in st.session_state.tasks if t['due_date'] == today and t['status'] == 'pending']
                elif filter_str == "overdue":
                    tasks_to_show = [t for t in st.session_state.tasks if t['due_date'] and t['due_date'] < today and t['status'] == 'pending']
                elif filter_str == "all":
                    tasks_to_show = [t for t in st.session_state.tasks if t['status'] == 'pending']
                # Add more sophisticated filtering based on keywords in filter_str (e.g. 'work tasks')
                else: # Basic keyword search in description or type
                     tasks_to_show = [t for t in st.session_state.tasks if (filter_str in t['description'].lower() or filter_str in t['type'].lower()) and t['status'] == 'pending']


                if tasks_to_show:
                    for task in tasks_to_show:
                        st.markdown(f"- **{task['description']}** (Due: {task['due_date'].strftime('%Y-%m-%d') if task['due_date'] else 'N/A'}, Prio: {task['priority']}, Type: {task['type']})")
                else:
                    st.info(f"No tasks found matching '{filter_str}'.")

            elif action_type == "CHECK_STATUS":
                desc_to_check = action_params.get("DESCRIPTION")
                task_found_for_status = False
                if desc_to_check:
                    for task in st.session_state.tasks:
                        if task['description'].lower() == desc_to_check.lower():
                            st.info(f"Status of task '{task['description']}': **{task['status']}**.")
                            task_found_for_status = True
                            break
                    if not task_found_for_status:
                        st.warning(f"Could not find task '{desc_to_check}' to check its status.")
                else:
                    st.error("Assistant tried to check status but task description was missing.")

            elif action_type == "GENERAL_QUERY":
                pass # Natural language response is enough

            else:
                st.warning(f"Unknown action type from assistant: {action_type}")

        except Exception as e:
            st.error(f"Error processing assistant's action: {e}")
            # import traceback
            # st.text(traceback.format_exc()) # For debugging the parsing error itself

    st.markdown("---")
