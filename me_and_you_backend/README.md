# Me & You - AI Life Dashboard (Backend)

This directory contains the Python Flask backend for the "Me & You" AI Life Dashboard. It provides API endpoints for AI-powered features like task classification.

## Setup and Running Locally

### 1. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

Navigate to the `me_and_you_backend` directory and run:

```bash
python -m venv venv
```

Activate the virtual environment:

*   On macOS and Linux:
    ```bash
    source venv/bin/activate
    ```
*   On Windows:
    ```bash
    .\venv\Scripts\activate
    ```

You should see `(venv)` at the beginning of your terminal prompt.

### 2. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

This application requires an OpenAI API key to function.

1.  Create a file named `.env` in the `me_and_you_backend` directory (this file is ignored by Git).
2.  Add your OpenAI API key to the `.env` file like this:

    ```env
    OPENAI_API_KEY="your_openai_api_key_here"
    ```

    Replace `"your_openai_api_key_here"` with your actual key.

### 4. Run the Flask Development Server

Once the setup is complete, you can run the Flask development server:

```bash
python app.py
```

The server should start, typically on `http://127.0.0.1:5001/` or `http://0.0.0.0:5001/`. Check the terminal output for the exact address. You should see messages indicating if the OpenAI client was initialized successfully.

### 5. Testing the API (Example)

You can test the `/api/tasks` endpoint using a tool like `curl` or Postman.

**Example using `curl`:**

Open a new terminal window (ensure the Flask app is still running in the other one).

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{"description": "Schedule a meeting with the project team for next Tuesday"}' \
http://127.0.0.1:5001/api/tasks
```

**Expected Response (example):**

```json
{
  "classified_type": "work",
  "description": "Schedule a meeting with the project team for next Tuesday"
}
```
(The `classified_type` might vary based on the OpenAI model's current interpretation.)

---

This backend is intended to be used with a separate frontend application and a Supabase backend for database and authentication.
