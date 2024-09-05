```
project_structure/
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
└── src/
    ├── __init__.py
    ├── assistant_manager.py
    ├── chat_interface.py
    ├── groq_client.py
    ├── database.py
    └── utils.py

```


# UserManPro - AI Assistant Manager

UserManPro is a Streamlit-based application for creating and managing AI assistants using the Groq API with the LLaMA model.

## Features

- Create custom AI assistants with user-defined or auto-generated prompts
- Chat with multiple assistants
- Persist assistants and chat histories using SQLite database
- Delete assistants
- Clear chat history

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/usermanpro.git
   cd usermanpro
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Groq API key in the `.env` file:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

## Usage

Run the Streamlit app:
```
streamlit run app.py
```

Access the app through your web browser at the provided local URL.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.