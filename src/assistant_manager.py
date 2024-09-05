import streamlit as st
from .groq_client import GroqClient
from .database import Database
from .utils import validate_input

class AssistantManager:
    def __init__(self, db: Database):
        self.groq_client = GroqClient()
        self.db = db
        if "assistants" not in st.session_state:
            st.session_state.assistants = self.db.get_all_assistants()
        if "current_assistant" not in st.session_state:
            st.session_state.current_assistant = None

    def create_assistant(self, name: str, prompt: str):
        if validate_input(name) and validate_input(prompt):
            assistant_id = self.db.add_assistant(name, prompt)
            st.session_state.assistants[assistant_id] = {"name": name, "prompt": prompt, "chat_history": []}
            st.session_state.current_assistant = assistant_id
            return True
        return False

    def delete_assistant(self, assistant_id: str):
        if assistant_id in st.session_state.assistants:
            del st.session_state.assistants[assistant_id]
            self.db.delete_assistant(assistant_id)
            if st.session_state.current_assistant == assistant_id:
                st.session_state.current_assistant = None

    def auto_generate_prompt(self) -> str:
        return self.groq_client.generate_prompt()

    def render_sidebar(self):
        st.sidebar.header("Create New Assistant")
        new_assistant_name = st.sidebar.text_input("Assistant Name")
        prompt_option = st.sidebar.radio("Prompt Option", ["Custom", "Auto-generate"])
        
        if prompt_option == "Custom":
            new_assistant_prompt = st.sidebar.text_area("Custom Prompt")
        else:
            if st.sidebar.button("Generate Prompt"):
                new_assistant_prompt = self.auto_generate_prompt()
                st.sidebar.write(f"Generated Prompt: {new_assistant_prompt}")
        
        if st.sidebar.button("Create Assistant"):
            if self.create_assistant(new_assistant_name, new_assistant_prompt):
                st.sidebar.success(f"Assistant '{new_assistant_name}' created!")
            else:
                st.sidebar.error("Invalid input. Please check your assistant name and prompt.")
        
        st.sidebar.header("Select Assistant")
        selected_assistant = st.sidebar.selectbox("Choose an assistant", 
                                                  options=list(st.session_state.assistants.keys()),
                                                  format_func=lambda x: st.session_state.assistants[x]['name'])
        if selected_assistant:
            st.session_state.current_assistant = selected_assistant

        if st.session_state.current_assistant:
            if st.sidebar.button("Delete Current Assistant"):
                self.delete_assistant(st.session_state.current_assistant)
                st.sidebar.success("Assistant deleted successfully.")