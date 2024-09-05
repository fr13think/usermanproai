import streamlit as st
from src.assistant_manager import AssistantManager
from src.chat_interface import ChatInterface
from src.database import Database

def main():
    st.set_page_config(page_title="UserManPro", page_icon="🤖", layout="wide")
    st.title("UserManPro - AI Assistant Manager")

    db = Database()
    assistant_manager = AssistantManager(db)
    chat_interface = ChatInterface(assistant_manager)

    col1, col2 = st.columns([1, 3])

    with col1:
        assistant_manager.render_sidebar()

    with col2:
        chat_interface.render()

if __name__ == "__main__":
    main()