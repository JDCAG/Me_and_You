import pytest
from unittest.mock import MagicMock, patch
from me_and_you_backend.ai_utils import get_ai_task_classification

# To run these tests, ensure you have pytest and pytest-mock installed:
# pip install pytest pytest-mock

class MockChoice:
    def __init__(self, content):
        self.message = MagicMock()
        self.message.content = content

class MockCompletion:
    def __init__(self, content):
        self.choices = [MockChoice(content)]

@pytest.fixture
def mock_openai_client():
    """Fixture to create a mock OpenAI client."""
    client = MagicMock()
    return client

def test_get_ai_task_classification_success_work(mock_openai_client):
    """Test successful classification for a 'work' task."""
    mock_openai_client.chat.completions.create.return_value = MockCompletion("work")

    description = "Submit the quarterly report"
    classification = get_ai_task_classification(mock_openai_client, description)

    assert classification == "work"
    mock_openai_client.chat.completions.create.assert_called_once()
    # We can also assert details of the call if needed, e.g., model, messages content
    args, kwargs = mock_openai_client.chat.completions.create.call_args
    assert kwargs['model'] == "gpt-3.5-turbo"
    assert f'Task: "{description}"' in kwargs['messages'][1]['content']

def test_get_ai_task_classification_success_personal(mock_openai_client):
    """Test successful classification for a 'personal' task."""
    mock_openai_client.chat.completions.create.return_value = MockCompletion("personal")

    description = "Call mom on her birthday"
    classification = get_ai_task_classification(mock_openai_client, description)

    assert classification == "personal"

def test_get_ai_task_classification_unexpected_response_fallback(mock_openai_client):
    """Test fallback to 'general' if OpenAI returns an unexpected category."""
    mock_openai_client.chat.completions.create.return_value = MockCompletion("unexpected_category")

    description = "This is a strange task"
    classification = get_ai_task_classification(mock_openai_client, description)

    assert classification == "general"

def test_get_ai_task_classification_openai_api_error_fallback(mock_openai_client):
    """Test fallback to 'general' if OpenAI API call raises an exception."""
    mock_openai_client.chat.completions.create.side_effect = Exception("OpenAI API Error")

    description = "A task that will cause an error"
    classification = get_ai_task_classification(mock_openai_client, description)

    assert classification == "general"

def test_get_ai_task_classification_no_client_fallback():
    """Test fallback to 'general' if no OpenAI client is provided."""
    description = "A task without a client"
    classification = get_ai_task_classification(None, description) # Pass None as client

    assert classification == "general"

def test_get_ai_task_classification_with_quotes_in_response(mock_openai_client):
    """Test that quotes are stripped from the classification response."""
    mock_openai_client.chat.completions.create.return_value = MockCompletion('"home"')
    description = "Clean the garage"
    classification = get_ai_task_classification(mock_openai_client, description)
    assert classification == "home"

    mock_openai_client.chat.completions.create.return_value = MockCompletion("'finance'")
    description = "Pay credit card bill"
    classification = get_ai_task_classification(mock_openai_client, description)
    assert classification == "finance"

# Example of how to check the prompt being sent (optional)
def test_get_ai_task_classification_prompt_structure(mock_openai_client):
    mock_openai_client.chat.completions.create.return_value = MockCompletion("work")
    description = "Develop new feature"
    get_ai_task_classification(mock_openai_client, description)

    args, kwargs = mock_openai_client.chat.completions.create.call_args
    system_message = kwargs['messages'][0]
    user_message = kwargs['messages'][1]

    assert system_message['role'] == "system"
    assert "You are a task classification assistant" in system_message['content']
    assert user_message['role'] == "user"
    assert f'Task: "{description}"' in user_message['content']
    assert "Category:" in user_message['content']
    assert "personal, work, admin, emotional, shopping, health, learning, finance, home, other" in user_message['content']

# To make this file runnable by pytest when it's inside me_and_you_backend/tests/
# and ai_utils.py is in me_and_you_backend/,
# you might need an __init__.py in me_and_you_backend/ and me_and_you_backend/tests/
# and ensure pytest is run from the directory *above* me_and_you_backend,
# or configure PYTHONPATH.
# For simplicity of execution here, we assume direct import works if pytest is run from root.
# If `me_and_you_backend` is not in PYTHONPATH, imports might fail.
# A common way is to run `python -m pytest` from the root directory.

# Create __init__.py files if they don't exist to make packages recognizable
# (This tool can't create empty files, but they would be:
# me_and_you_backend/__init__.py
# me_and_you_backend/tests/__init__.py
# )
