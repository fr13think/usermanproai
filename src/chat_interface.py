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

        # Chat history display
        chat_container = st.container()
        with chat_container:
            for message in assistant["chat_history"]:
                with st.chat_message(message["role"]):
                    st.write(format_message(message["content"]))

        # User input area
        if 'user_input' not in st.session_state:
            st.session_state.user_input = ""

        def clear_input():
            st.session_state.user_input = ""

        def send_message():
            if st.session_state.user_input:
                with st.spinner("Thinking..."):
                    assistant_response = self.chat_with_assistant(st.session_state.user_input)
                st.session_state.need_rerun = True
                clear_input()

        user_input = st.text_input("Type your message here...", key="user_input", on_change=send_message, args=())
        col1, col2, col3 = st.columns([1, 1, 5])
        with col1:
            st.button("Send", on_click=send_message)
        with col2:
            st.button("Clear", on_click=clear_input)

        # Clear chat history button
        if st.button("Clear Chat History"):
            assistant["chat_history"] = []
            self.assistant_manager.db.update_chat_history(st.session_state.current_assistant, [])
            st.session_state.assistants[st.session_state.current_assistant]["chat_history"] = []
            st.session_state.need_rerun = True

        # Check if we need to rerun the app
        if st.session_state.get('need_rerun', False):
            st.session_state.need_rerun = False
            st.rerun()

def create_or_select_assistant(assistant_manager: AssistantManager):
    st.sidebar.title("Assistant Management")

    # Create new assistant
    with st.sidebar.expander("Create New Assistant"):
        new_assistant_name = st.text_input("Assistant Name")
        new_assistant_prompt = st.text_area("Assistant Prompt")
        if st.button("Create Assistant"):
            if new_assistant_name and new_assistant_prompt:
                assistant_manager.create_assistant(new_assistant_name, new_assistant_prompt)
                st.success(f"Assistant '{new_assistant_name}' created successfully!")
                st.session_state.need_rerun = True
            else:
                st.error("Please provide both name and prompt for the new assistant.")

    # Select existing assistant
    assistant_names = list(st.session_state.assistants.keys())
    if assistant_names:
        selected_assistant = st.sidebar.selectbox("Select Assistant", assistant_names)
        if selected_assistant != st.session_state.current_assistant:
            st.session_state.current_assistant = selected_assistant
            st.session_state.need_rerun = True
    else:
        st.sidebar.warning("No assistants available. Create one to start chatting!")

def main():
    st.set_page_config(page_title="AI Assistant Chat", layout="wide")
    
    if 'assistants' not in st.session_state:
        st.session_state.assistants = {}
    if 'current_assistant' not in st.session_state:
        st.session_state.current_assistant = None
    if 'need_rerun' not in st.session_state:
        st.session_state.need_rerun = False

    assistant_manager = AssistantManager()
    chat_interface = ChatInterface(assistant_manager)

    create_or_select_assistant(assistant_manager)
    chat_interface.render()

if __name__ == "__main__":
    main()
