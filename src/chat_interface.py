import streamlit as st
from .assistant_manager import AssistantManager
from .utils import format_message

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
        
        assistant["chat_history"].append({"role": "user", "content": message})
        assistant["chat_history"].append({"role": "assistant", "content": assistant_response})
        
        # Save the updated chat history to the database
        self.assistant_manager.db.update_chat_history(st.session_state.current_assistant, assistant["chat_history"])
        
        return assistant_response

    def render(self):
        if st.session_state.current_assistant:
            assistant = st.session_state.assistants[st.session_state.current_assistant]
            st.header(f"Chat with {assistant['name']}")
            
            for message in assistant["chat_history"]:
                with st.chat_message(message["role"]):
                    st.write(format_message(message["content"]))
            
            user_input = st.chat_input("Type your message here...")
            if user_input:
                with st.chat_message("user"):
                    st.write(user_input)
                
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        assistant_response = self.chat_with_assistant(user_input)
                    st.write(format_message(assistant_response))

            if st.button("Clear Chat History"):
                assistant["chat_history"] = []
                self.assistant_manager.db.update_chat_history(st.session_state.current_assistant, [])
                st.experimental_rerun()
        else:
            st.info("Create or select an assistant to start chatting.")