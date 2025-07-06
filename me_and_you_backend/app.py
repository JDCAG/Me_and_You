from flask import Flask
import os
from dotenv import load_dotenv
from flask_cors import CORS # Import CORS

# Load environment variables from .env file (if it exists)
load_dotenv()

app = Flask(__name__)
CORS(app) # Enable CORS for all routes and origins by default for development

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

from flask import request, jsonify
import openai

# Placeholder for OpenAI client initialization
# Will be initialized properly when an AI feature is added.
if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY environment variable not found. AI features will be disabled.")
    # Depending on the application's needs, you might want to exit or raise an error here
    # For now, we'll let it run but AI calls will fail.
    client = None
else:
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        print("OpenAI client initialized successfully.")
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        client = None


@app.route('/')
def hello_world():
    if not OPENAI_API_KEY or not client:
        return 'Hello, Me & You Backend! (Warning: OPENAI_API_KEY not configured or client init failed)'
    return 'Hello, Me & You Backend! (OpenAI client initialized and key configured)'

# Import the refactored AI utility function
from me_and_you_backend.ai_utils import get_ai_task_classification

@app.route('/api/tasks', methods=['POST'])
def create_task():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    description = data.get('description')
    due_date_str = data.get('due_date_str') # Optional
    priority = data.get('priority')         # Optional

    if not description:
        return jsonify({"error": "Missing task description"}), 400

    # Get AI classification for the task
    # Ensure the client is passed to the imported function
    classified_type = get_ai_task_classification(client, description)

    # For now, this endpoint focuses on classification and returns the enriched task data.
    # The actual saving to Supabase would typically be handled by the frontend
    # or in a subsequent step if this backend were to interact with Supabase directly.

    task_response = {
        "description": description,
        "classified_type": classified_type,
    }
    if due_date_str:
        task_response["due_date_str"] = due_date_str
        # We could add date parsing logic here later if desired
        # from app import parse_due_date_from_string (if refactored)
        # parsed_due_date = parse_due_date_from_string(due_date_str)
        # if parsed_due_date:
        #    task_response["parsed_due_date"] = parsed_due_date.isoformat()

    if priority:
        task_response["priority"] = priority

    # Here, you might also assign a unique ID if the backend were responsible for it.
    # task_response["id"] = str(uuid.uuid4())

    return jsonify(task_response), 201


if __name__ == '__main__':
    # For local development, debug=True is fine.
    # For production, use a proper WSGI server like Gunicorn or Waitress.
    app.run(debug=True, host='0.0.0.0', port=5001) # Using port 5001 to avoid potential conflicts
