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

        # Custom CSS to create a fixed footer
        st.markdown("""
        <style>
        .stApp {
            margin-bottom: 80px;
        }
        .fixed-bottom {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: white;
            padding: 20px;
            z-index: 999;
            border-top: 1px solid #e6e6e6;
        }
        .chat-container {
            height: calc(100vh - 200px);
            overflow-y: auto;
            padding-right: 15px;
        }
        </style>
        """, unsafe_allow_html=True)

        # Main chat container
        chat_container = st.container()
        
        # Fixed bottom container for user input
        bottom_container = st.container()

        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for message in assistant["chat_history"]:
                with st.chat_message(message["role"]):
                    st.write(format_message(message["content"]))
            st.markdown('</div>', unsafe_allow_html=True)

        with bottom_container:
            st.markdown('<div class="fixed-bottom">', unsafe_allow_html=True)
            try:
                user_input = st.chat_input("Type your message here...")
            except Exception as e:
                st.error(f"Error with chat input: {str(e)}")
                user_input = None
            
            if user_input:
                with chat_container:
                    with st.chat_message("user"):
                        st.write(user_input)
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            assistant_response = self.chat_with_assistant(user_input)
                        st.write(format_message(assistant_response))
                st.rerun()  # Force a rerun to update the chat container
            
            # Clear chat history button
            if st.button("Clear Chat History"):
                assistant["chat_history"] = []
                self.assistant_manager.db.update_chat_history(st.session_state.current_assistant, [])
                st.session_state.assistants[st.session_state.current_assistant]["chat_history"] = []
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

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
                st.rerun()
            else:
                st.error("Please provide both name and prompt for the new assistant.")

    # Select existing assistant
    assistant_names = list(st.session_state.assistants.keys())
    if assistant_names:
        selected_assistant = st.sidebar.selectbox("Select Assistant", assistant_names)
        if selected_assistant != st.session_state.current_assistant:
            st.session_state.current_assistant = selected_assistant
            st.rerun()
    else:
        st.sidebar.warning("No assistants available. Create one to start chatting!")

def main():
    st.set_page_config(page_title="AI Assistant Chat", layout="wide")
    
    if 'assistants' not in st.session_state:
        st.session_state.assistants = {}
    if 'current_assistant' not in st.session_state:
        st.session_state.current_assistant = None

    assistant_manager = AssistantManager()
    chat_interface = ChatInterface(assistant_manager)

    create_or_select_assistant(assistant_manager)
    chat_interface.render()

if __name__ == "__main__":
    main()
