from vertexai.preview.language_models import ChatModel, ChatSession


def get_chat_session() -> ChatSession:
    """Initializes and returns a new Gemini 1.5 Pro chat session."""
    model = ChatModel.from_pretrained("gemini-3.1-flash-lite-preview")
    chat = model.start_chat()
    return chat


def run_task(task_prompt: str) -> str:
    """Runs a single task by sending a prompt to a new Gemini chat session.

    Args:
        task_prompt: The user prompt to send to the model.

    Returns:
        The text response from the model.

    """
    chat_session = get_chat_session()
    response = chat_session.send_message(task_prompt)
    return response.text
