# LangGraph chatbot with Python and Streamlit

A simple chat application using Streamlit for the interface, LangGraph for conversation state, and Groq for AI responses. The backend uses the `openai/gpt-oss-20b` model through Groq.

## Requirements

- Python 3.12 (the version used for local verification)
- Git, if cloning the repository
- A Groq API key
- An internet connection to install dependencies and receive AI responses

## 1. Get the project

```bash
git clone https://github.com/faiz-ttnew/langgraph_chatbot_python_streamlit.git
cd langgraph_chatbot_python_streamlit
```

Alternatively, download and extract the project ZIP, then open a terminal in the folder containing `streamlit_frontend.py` and `requirements.txt`.

## 2. Create a virtual environment

Create a fresh environment on each machine; do not copy the existing `venv` folder.

### Linux / macOS

```bash
python3.12 -m venv venv
source venv/bin/activate
```

### Windows PowerShell

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt instead:

```bat
venv\Scripts\activate.bat
```

## 3. Install dependencies

With the virtual environment active:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Configure the API key

Create a Groq API key in the [Groq console](https://console.groq.com/keys).

Copy the example configuration into `.env` in the project folder.

Linux / macOS:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and replace the placeholder with your own key:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
```

Keep `.env` private. It is excluded by `.gitignore`; share `.env.example` without credentials instead. Each machine needs its own local configuration.

## 5. Run the app

From the project folder, with the virtual environment active:

```bash
python -m streamlit run streamlit_frontend.py
```

Open the local URL printed in the terminal, usually `http://localhost:8501`. Type a message in the chat input and press Enter. Stop the app with **Ctrl+C** in the terminal.

For later runs, open a terminal in the project folder, activate the virtual environment, and run the same command.

## Project files

| File | Purpose |
| --- | --- |
| `streamlit_frontend.py` | Chat interface and browser session history |
| `langgraph_backend.py` | LangGraph workflow, Groq client, and in-memory checkpoints |
| `requirements.txt` | Python dependencies |
| `.env.example` | API key configuration template |
| `.gitignore` | Excludes credentials, virtual environments, and Python caches |

The basic app stores conversation checkpoints in memory, which are lost when the server restarts. Browser session history resets when the Streamlit session is lost. The database app (`streamlit_frontend_database.py`) uses `langgraph_database_backend.py` to persist checkpoints in a local SQLite database.

## Local database files and Git

Run the database app from the project folder with:

```bash
python -m streamlit run streamlit_frontend_database.py
```

The database backend creates `chatbot.db` locally. SQLite may also create `chatbot.db-shm` and `chatbot.db-wal` companion files. These contain local conversation data and must stay out of Git. The following filenames are excluded by `.gitignore`:

```gitignore
chatbot.db
chatbot.db-shm
chatbot.db-wal
.chatbot.db
.chatbot.db-shm
.chatbot.db-wal
```

These rules have no trailing `/` because they match files. Keep the files on your machine; do not commit or push them. Each machine creates its own database when the database app runs.

If these files were committed previously, `.gitignore` alone does not stop tracking them. Remove only their Git index entries (keeping local files) with:

```bash
git rm --cached --ignore-unmatch -- chatbot.db chatbot.db-shm chatbot.db-wal .chatbot.db .chatbot.db-shm .chatbot.db-wal
```

This stops tracking in future commits; it does not remove database contents from earlier commits.

## Troubleshooting

- **`GROQ_API_KEY is missing`**: Ensure `.env` is in the project folder, contains your key, and is not named `.env.txt`. Restart the app after changing it.
- **Authentication or model errors**: Check your Groq key and account's access to the model configured in `langgraph_backend.py`.
- **`ModuleNotFoundError`**: Activate the virtual environment and run `python -m pip install -r requirements.txt` again.
- **Checkpointer requires `thread_id`**: Ensure the frontend passes `config=CONFIG` to `chatbot.invoke(...)`. The included frontend already supplies this configuration.
- **Port already in use**: Run `python -m streamlit run streamlit_frontend.py --server.port 8502`.
- **An old traceback appears after a fix**: Save your files, stop the running app with Ctrl+C, and restart it from the correct project folder.

## 3. Resume feature docs

The following features describe the planned conversation management workflow.

### Sidebar and session setup

- Add a sidebar with a title, a **Start Chat** button, and a heading named **My Conversations**.
- Generate a dynamic `thread_id` and store it in Streamlit session state.
- Display the current `thread_id` in the sidebar.

### New chat

- Add a **New Chat** button.
- Clicking **New Chat** opens a fresh conversation in the chat area:
  - Generate a new `thread_id`.
  - Save it in session state.
  - Reset the displayed message history.

### Conversation list

- Create a list to store all `thread_id` values.
- Display all saved thread IDs in the sidebar under **My Conversations**.
- Render each thread ID as a clickable button.

### Resume a conversation

- Clicking a thread ID selects that conversation.
- Save the selected `thread_id` in session state.
- Load that thread's conversation history from the LangGraph checkpointer and display its messages.
- Continue the conversation using the selected thread ID.

With the current in-memory checkpointer, conversations are available only while the server remains running.
