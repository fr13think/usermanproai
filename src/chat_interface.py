import streamlit as st
from typing import List, Dict
from .assistant_manager import AssistantManager
from .utils import format_message
from .groq_client import format_tool_call

class ChatInterface:
    def __init__(self, assistant_manager: AssistantManager):
        self.assistant_manager = assistant_manager

    def chat_with_assistant(self, message: str) -> str:
        assistant = st.session_state.assistants[st.session_state.current_assistant]
        messages = [
            {"role": "system", "content": assistant["prompt"]},
            *assistant["chat_history"],
            {"role": "user", "content": message}
        ]
        assistant_response = self.assistant_manager.groq_client.chat(messages)
        
        if "<tool_call>" in assistant_response:
            formatted_response = format_tool_call(assistant_response)
        else:
            formatted_response = assistant_response
        
        assistant["chat_history"].append({"role": "user", "content": message})
        assistant["chat_history"].append({"role": "assistant", "content": formatted_response})
        
        self.assistant_manager.db.update_chat_history(st.session_state.current_assistant, assistant["chat_history"])
        return formatted_response

    def render(self):
        if 'current_assistant' not in st.session_state or 'assistants' not in st.session_state:
            st.error("Session state not properly initialized. Please select an assistant first.")
            return

        if not st.session_state.current_assistant:
            st.info("Create or select an assistant to start chatting.")
            return

        assistant = st.session_state.assistants[st.session_state.current_assistant]
        st.header(f"Chat with {assistant['name']}")

        # Container for chat messages
        chat_container = st.container()
        with chat_container:
            for message in assistant["chat_history"]:
                with st.chat_message(message["role"]):
                    st.write(format_message(message["content"]))

        # User input
        try:
            user_input = st.chat_input("Type your message here...")
        except Exception as e:
            st.error(f"Error with chat input: {str(e)}")
            user_input = None

        if user_input:
            with st.chat_message("user"):
                st.write(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    assistant_response = self.chat_with_assistant(user_input)
                st.write(format_message(assistant_response))

        # Clear chat history button
        if st.button("Clear Chat History"):
            assistant["chat_history"] = []
            self.assistant_manager.db.update_chat_history(st.session_state.current_assistant, [])
            st.session_state.assistants[st.session_state.current_assistant]["chat_history"] = []
            st.rerun()

def main():
    st.set_page_config(page_title="AI Assistant Chat", layout="wide")
    
    if 'assistants' not in st.session_state:
        st.session_state.assistants = {}
    if 'current_assistant' not in st.session_state:
        st.session_state.current_assistant = None

    assistant_manager = AssistantManager()
    chat_interface = ChatInterface(assistant_manager)

    st.sidebar.title("AI Assistant")

    # Assistant selection or creation logic here
    # ...

    chat_interface.render()

if __name__ == "__main__":
    main()
