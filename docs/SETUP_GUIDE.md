# 🚀 Contextify Setup Guide

Contextify is a powerful CLI tool that generates context-aware prompts for AI coding assistants by scanning your codebase and using Gemini AI to refine your requests.

---

## 🛠️ Prerequisites

*   **Python 3.9+** installed on your system.
*   **Gemini API Key:** Get one for free at [Google AI Studio](https://aistudio.google.com/app/apikey).

---

## 💻 Installation (Windows)

1.  **Clone or Download** the repository to a permanent location (e.g., `C:\Tools\Contextify`).
2.  **Open PowerShell** as Administrator and navigate to the folder:
    ```powershell
    cd "C:\Path\To\Contextify"
    ```
3.  **Run the Setup Script:**
    ```powershell
    .\scripts\setup.ps1
    ```
    *This will create a virtual environment, install dependencies, and add Contextify to your system PATH.*

4.  **Restart your Terminal** to apply the PATH changes.

---

## 🐧 Installation (Linux/macOS)

1.  **Navigate to the folder:**
    ```bash
    cd /path/to/contextify
    ```
2.  **Make script executable and run:**
    ```bash
    chmod +x scripts/install.sh
    ./scripts/install.sh
    ```
3.  **Restart your Terminal** or run `source ~/.bashrc` (or `~/.zshrc`).

---

## 🔑 Configuration

To use the AI-powered prompt refinement, you must set your Gemini API key as an environment variable.

### **Windows (Permanent)**
1.  Search for "Environment Variables" in Start.
2.  Add a new **User Variable**:
    *   **Name:** `GEMINI_API_KEY`
    *   **Value:** `your-api-key-here`

### **Linux/macOS (Permanent)**
Add this to your `~/.bashrc` or `~/.zshrc`:
```bash
export GEMINI_API_KEY='your-api-key-here'
```

---

## 🚀 How to Use

You can now run `contextify` from **any workspace** on your computer!

| Command | Description |
| :--- | :--- |
| `contextify "add dynamic routing"` | Basic context-aware prompt generation |
| `contextify "fix login bug" --changed` | Only include files changed in Git |
| `contextify "refactor ui" --focus frontend` | Focus on specific parts (frontend/backend/db/etc.) |
| `contextify "setup auth" --output prompt.md` | Save refined prompt to a file |

### **Example Workflow**
1.  Open your project in a terminal.
2.  Run: `contextify "implement a dark mode toggle using tailwind"`
3.  **Paste** the results (automatically copied to clipboard) directly into ChatGPT, Claude, or GitHub Copilot.

---

## 🧪 Verification
Run this command to verify the installation:
```bash
contextify --help
```

If you see the help menu, you're all set! Happy coding! 🚀
