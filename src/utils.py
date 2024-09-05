import re

def validate_input(text: str) -> bool:
    return bool(text) and len(text.strip()) > 0

def format_message(message: str) -> str:
    # Convert markdown code blocks to streamlit code blocks
    message = re.sub(r'```(\w+)?\n(.*?)\n```', r'```\1\n\2\n```', message, flags=re.DOTALL)
    return message