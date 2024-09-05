import os
import groq
from typing import List, Dict
from tenacity import retry, stop_after_attempt, wait_random_exponential

class GroqClient:
    def __init__(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        self.client = groq.Groq(api_key=groq_api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=60))
    def generate_prompt(self) -> str:
        response = self.client.chat.completions.create(
            model="llama2-70b-4096",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates prompts for AI assistants."},
                {"role": "user", "content": "Generate a creative and useful prompt for a new AI assistant."}
            ],
            max_tokens=100
        )
        return response.choices[0].message.content

    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=60))
    def chat(self, messages: List[Dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model="llama2-70b-4096",
            messages=messages,
            max_tokens=500
        )
        return response.choices[0].message.content