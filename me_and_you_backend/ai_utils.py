import openai

def get_ai_task_classification(client: openai.OpenAI, task_description: str) -> str:
    """
    Uses OpenAI to classify the task description using the provided client.
    Returns a string like "personal", "work", "admin", "emotional", etc.
    """
    if not client:
        print("OpenAI client not provided to get_ai_task_classification. Cannot classify task.")
        return "general" # Default fallback type

    try:
        prompt_content = f"""Classify the following task description into one of these categories: personal, work, admin, emotional, shopping, health, learning, finance, home, other.
Task: "{task_description}"
Category:"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a task classification assistant. Respond with only one category name from the provided list."},
                {"role": "user", "content": prompt_content}
            ],
            temperature=0,
            max_tokens=10
        )
        classification = response.choices[0].message.content.strip().lower()

        # It's good practice to clean up potential quote marks if any
        classification = classification.replace('"', '').replace("'", "")

        valid_categories = ["personal", "work", "admin", "emotional", "shopping", "health", "learning", "finance", "home", "other", "general"]
        if classification not in valid_categories:
            print(f"Warning: Unexpected classification '{classification}' from OpenAI for task '{task_description}'. Falling back to 'general'.")
            return "general"
        return classification
    except Exception as e:
        print(f"Error calling OpenAI for task classification in ai_utils: {e}")
        return "general" # Fallback category
