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

Conversation checkpoints are stored in memory and are lost when the server restarts. Browser session history resets when the Streamlit session is lost. This project does not use a persistent database.

## Troubleshooting

- **`GROQ_API_KEY is missing`**: Ensure `.env` is in the project folder, contains your key, and is not named `.env.txt`. Restart the app after changing it.
- **Authentication or model errors**: Check your Groq key and account's access to the model configured in `langgraph_backend.py`.
- **`ModuleNotFoundError`**: Activate the virtual environment and run `python -m pip install -r requirements.txt` again.
- **Checkpointer requires `thread_id`**: Ensure the frontend passes `config=CONFIG` to `chatbot.invoke(...)`. The included frontend already supplies this configuration.
- **Port already in use**: Run `python -m streamlit run streamlit_frontend.py --server.port 8502`.
- **An old traceback appears after a fix**: Save your files, stop the running app with Ctrl+C, and restart it from the correct project folder.
