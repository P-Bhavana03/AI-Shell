import argparse
import sqlite3
import subprocess
import os
import google.generativeai as genai

# import llm_interface  # Placeholder for LLM interaction module
# import db_manager     # Placeholder for DB interaction module

# Placeholder for Gemini API Key - Should be loaded securely, e.g., from env variables
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY", "YOUR_API_KEY_HERE"
)  # Replace with your actual key or loading mechanism

DATABASE_NAME = "ai_shell_history.db"


def initialize_database():
    """Initializes the SQLite database and history table if they don't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS command_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            natural_language_query TEXT NOT NULL,
            generated_command TEXT NOT NULL,
            executed_successfully BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()
    print(f"Database '{DATABASE_NAME}' initialized.")


def add_to_history(query, command, success):
    """Adds a command execution record to the history database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO command_history (natural_language_query, generated_command, executed_successfully)
        VALUES (?, ?, ?)
    """,
        (query, command, success),
    )
    conn.commit()
    conn.close()


def get_command_from_llm(query):
    """Gets the shell command from the Gemini LLM."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        print("Error: GEMINI_API_KEY is not configured.")
        print("Please set the GEMINI_API_KEY environment variable.")
        return None  # Indicate failure due to missing key

    try:
        print(f"Querying Gemini for: '{query}'...")
        genai.configure(api_key=GEMINI_API_KEY)

        # Choose a model that's appropriate for command generation
        # Ensure the model name is correct and available
        model = genai.GenerativeModel("gemini-2.5-pro-preview-03-25")

        # Craft a prompt that instructs the LLM to generate ONLY the command
        # Tailor the prompt for better results
        target_shell = (
            "PowerShell"
            if os.name == "nt"
            else "a POSIX-compliant shell (like bash or zsh)"
        )
        prompt = f"""Translate the following natural language query into a single, executable command for {target_shell} on a {os.name} system. Only output the command itself, with no explanation, formatting, or shell specifier (like 'bash' or 'powershell').

Query: "{query}"

Command:"""

        response = model.generate_content(prompt)

        # Basic safety check: remove potential backticks or formatting
        raw_command = response.text.strip().strip("`")

        # More robust cleaning: Remove potential leading 'powershell' or 'bash' lines
        lines = raw_command.splitlines()
        cleaned_lines = [
            line for line in lines if line.strip().lower() not in ["powershell", "bash"]
        ]
        generated_command = "\n".join(cleaned_lines).strip()

        # Add more robust validation/sanitization if needed
        if not generated_command:
            print("LLM returned an empty response.")
            return None

        print(f"LLM proposed command: {generated_command}")
        return generated_command

    except Exception as e:
        print(f"Error interacting with Gemini API: {e}")
        return None


def execute_command(command):
    """Executes the generated shell command, adapting for PowerShell on Windows."""
    print(f"Attempting to execute: {command}")
    try:
        if os.name == "nt":
            # On Windows, explicitly use powershell.exe
            # Using -Command ensures PowerShell interprets the string directly
            # Consider potential quoting issues if commands get complex
            print("Executing via PowerShell...")
            result = subprocess.run(
                ["powershell.exe", "-Command", command],
                check=True,
                capture_output=True,
                text=True,
                shell=False,  # shell=False is safer here
            )
        else:
            # For other OSes, use the default shell
            print("Executing via default shell...")
            # Using shell=True can be a security risk if the command is constructed from untrusted input.
            # Ensure the LLM output is properly sanitized or validated if necessary.
            result = subprocess.run(
                command, shell=True, check=True, capture_output=True, text=True
            )

        print("--- Execution Result ---")
        print("Output:\n", result.stdout)
        if result.stderr:
            print("---")
            print("Error Output:\n", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print("Error Output:\n", e.stderr)
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="AI-Shell: Translate natural language to shell commands."
    )
    parser.add_argument(
        "query", type=str, nargs="+", help="The natural language query for the command."
    )
    # Add more arguments if needed, e.g., --show-history, --clear-history

    args = parser.parse_args()
    natural_query = " ".join(args.query)

    initialize_database()

    # 1. Get command from LLM
    generated_command = get_command_from_llm(natural_query)

    # Check if command generation was successful
    if generated_command:
        # 2. (Optional) Ask user for confirmation before execution
        # Make confirmation more robust (handle empty input, etc.)
        confirm = ""
        while confirm.lower() not in ["y", "n"]:
            confirm = input(f"Execute command: '{generated_command}'? (y/n): ").strip()
            if not confirm:  # Handle empty input
                confirm = "n"

        if confirm.lower() == "y":
            # 3. Execute command
            success = execute_command(generated_command)
            # 4. Add to history
            add_to_history(natural_query, generated_command, success)
        else:
            print("Command execution cancelled.")
            # Optionally add cancelled commands to history as well
            # add_to_history(natural_query, generated_command, None) # Indicate cancellation
    else:
        # Error message is printed within get_command_from_llm or execute_command
        print("Command generation or execution failed.")
        # Log failed generation attempts if command is None
        if generated_command is None:
            add_to_history(natural_query, "GENERATION_FAILED", False)


if __name__ == "__main__":
    # API key check is now handled within get_command_from_llm
    # if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_API_KEY_HERE":
    #     print("Error: GEMINI_API_KEY is not configured.")
    #     print("Please set the GEMINI_API_KEY environment variable and restart.")
    #     exit(1)
    main()
