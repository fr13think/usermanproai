import os
import streamlit as st
import groq
from typing import List, Dict
from tenacity import retry, stop_after_attempt, wait_random_exponential
import json

class GroqClient:
    def __init__(self):
        groq_api_key = st.secrets["GROQ_API_KEY"]
        # print(dir(groq))
        # client = Groq(
        #     # This is the default and can be omitted
        #     api_key=st.secrets["GROQ_API_KEY"],
        # )
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        self.client = groq.Groq(api_key=groq_api_key)
        
    
    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=60))
    def generate_prompt(self) -> str:
        response = self.client.chat.completions.create(
            model="llama3-groq-70b-8192-tool-use-preview",
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
            model="llama3-groq-70b-8192-tool-use-preview",
            messages=messages,
            max_tokens=500
        )
        return response.choices[0].message.content

def format_tool_call(tool_call: str) -> str:
    try:
        tool_call_dict = json.loads(tool_call.replace("<tool_call> ", "").replace(" </tool_call>", ""))

        tool_id = tool_call_dict.get("id")
        tool_name = tool_call_dict.get("name")
        arguments = tool_call_dict.get("arguments", {})

        formatted_arguments = format_arguments(arguments)

        formatted_tool_call = f"""
        **Tool Call:**
        - **ID:** {tool_id}
        - **Name:** {tool_name}
        - **Arguments:**
        {formatted_arguments}
        """
        return formatted_tool_call
    except json.JSONDecodeError:
        return tool_call  # Return the original tool call if it cannot be parsed

def format_arguments(arguments: Dict) -> str:
    formatted_args = []
    for key, value in arguments.items():
        if isinstance(value, dict):
            formatted_value = format_dict(value)
        elif isinstance(value, list):
            formatted_value = format_list(value)
        else:
            formatted_value = value
        formatted_args.append(f"  - **{key.replace('_', ' ').title()}:** {formatted_value}")
    return "\n".join(formatted_args)

def format_dict(d: Dict) -> str:
    formatted_items = []
    for key, value in d.items():
        if isinstance(value, dict):
            formatted_value = format_dict(value)
        elif isinstance(value, list):
            formatted_value = format_list(value)
        else:
            formatted_value = value
        formatted_items.append(f"    - **{key.replace('_', ' ').title()}:** {formatted_value}")
    return "\n".join(formatted_items)

def format_list(lst: List) -> str:
    formatted_items = []
    for item in lst:
        if isinstance(item, dict):
            formatted_item = format_dict(item)
        elif isinstance(item, list):
            formatted_item = format_list(item)
        else:
            formatted_item = item
        formatted_items.append(f"    - {formatted_item}")
    return "\n".join(formatted_items)

tool_call = '<tool_call> {"id": 0, "name": "generate_plan", "arguments": {"schedule": {"meetings": ["Zoom meeting to discuss the app"], "deadlines": ["Project deadline on December 12, 2024"]}, "tasks": []}} </tool_call>'
formatted_prompt = format_tool_call(tool_call)
# print(formatted_prompt)
