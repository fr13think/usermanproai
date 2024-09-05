import streamlit as st
import plotly.express as px

# Set page configuration at the very beginning
st.set_page_config(page_title="UserManPro", page_icon="🤖", layout="wide")

from src.assistant_manager import AssistantManager
from src.chat_interface import ChatInterface
from src.database import Database

def main():
    st.title("UserManPro - AI Assistant Manager")

    db = Database()
    assistant_manager = AssistantManager(db)
    chat_interface = ChatInterface(assistant_manager)

    col1, col2 = st.columns([1,9])

    with col1:
        assistant_manager.render_sidebar()

    with col2:
        chat_interface.render()
        assistant_manager.render_dashboard()

if __name__ == "__main__":
    main()
