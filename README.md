# AI-Shell: AI-Powered Command Line

AI-Shell is a command-line interface that translates natural language queries into executable shell commands using the power of Google's Gemini LLM. It also keeps a persistent history of your commands in an SQLite database.

## Features

- **Natural Language Interface:** Write commands in plain English instead of remembering specific syntax.
- **Gemini LLM Integration:** Leverages Google's Gemini model for accurate command generation.
- **Persistent History:** Stores your queries and generated commands in an SQLite database (`ai_shell_history.db`) for easy recall and review.
- **Cross-Platform Awareness:** Attempts to generate commands suitable for the detected operating system (PowerShell for Windows, POSIX shells for Linux/macOS).
- **Confirmation Step:** Prompts for confirmation before executing potentially impactful commands.

## Setup

1.  **Clone the repository (if applicable):**

    ```bash
    git clone <repository-url>
    cd AI-Shell
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv .venv
    # Activate the environment
    # Windows (PowerShell/CMD):
    .\.venv\Scripts\activate
    # Linux/macOS (bash/zsh):
    source .venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Gemini API Key:**
    - Obtain an API key from Google AI Studio.
    - Set the API key as an environment variable named `GEMINI_API_KEY`. You can do this temporarily in your terminal session:
      - **Windows (PowerShell):**
        ```powershell
        $env:GEMINI_API_KEY="YOUR_API_KEY_HERE"
        ```
      - **Windows (CMD):**
        ```cmd
        set GEMINI_API_KEY=YOUR_API_KEY_HERE
        ```
      - **Linux/macOS (bash/zsh):**
        ```bash
        export GEMINI_API_KEY="YOUR_API_KEY_HERE"
        ```
    - Alternatively, create a `.env` file in the project root and add the line `GEMINI_API_KEY=YOUR_API_KEY_HERE`. The script currently loads it directly via `os.getenv`, so setting the environment variable is the primary method. (Note: `.env` file loading is not implemented in the current script version but is good practice).

## Usage

Run the `ai_shell.py` script from your terminal, followed by your natural language query:

```bash
python ai_shell.py <your natural language query>
```

The script will:

1.  Initialize the database (if it doesn't exist).
2.  Query the Gemini LLM with your request.
3.  Show you the proposed command.
4.  Ask for confirmation (y/n).
5.  If confirmed ('y'), execute the command.
6.  Record the query, command, and execution status in the history database.

## Examples

```bash
# List files
python ai_shell.py list all files in the current directory

# Show git status
python ai_shell.py show git status

# Create a directory
python ai_shell.py make a new folder called temp_files

# Check Python version
python ai_shell.py what is my python version

# Ping a server
python ai_shell.py ping 8.8.8.8
```
