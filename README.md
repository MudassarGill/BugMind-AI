# BugMind AI 🧠

**BugMind AI** is an intelligent, full-stack web application designed to act as your personal AI coding assistant. It provides a rich code editing experience with real-time execution, automated error analysis, and AI-driven bug fixing, all wrapped in a beautiful, futuristic UI.

## 🚀 Features

*   **Intelligent Code Editor:** Powered by Monaco Editor (the same engine behind VS Code), featuring syntax highlighting, code formatting, and **auto-completion**.
*   **Live Code Execution:** Safely run your Python code directly in the browser and see the output instantly.
*   **AI Error Analysis:** When your code throws an error, BugMind AI catches it and provides a human-readable explanation of what went wrong.
*   **One-Click Auto-Fix:** Get AI-suggested code fixes that you can apply with a single click.
*   **Learning Dashboard:** Tracks your coding journey, showing statistics on your code runs, common errors you encounter, and your learning streak.
*   **Community Hub:** Connect with other developers, see leaderboard rankings, and participate in discussions and weekly challenges.
*   **Customizable Workspace:**
    *   **App Themes:** Choose from multiple stunning themes (Dark Navy, Midnight, Abyss, Dracula).
    *   **Editor Themes:** Customize the code editor's syntax highlighting.
    *   **Fullscreen Mode:** Focus entirely on your code.
*   **Secure Authentication:** Full user registration and login system with JWT-based security.

## 🛠️ Technology Stack

*   **Frontend:** HTML5, CSS3 (Vanilla), JavaScript (Vanilla)
*   **Editor:** Monaco Editor
*   **Backend:** Python, FastAPI
*   **Database:** SQLite (with `aiosqlite` for async operations)
*   **Authentication:** JWT (JSON Web Tokens), `passlib` (bcrypt)

## 🏁 Getting Started

### Prerequisites
*   Python 3.8+
*   `pip`

### Installation & Running

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start the Backend Server:**
    ```bash
    cd backend
    python main.py
    ```

3.  **Open the Application:**
    Navigate to `http://localhost:8000` in your web browser.

### User Flow
1.  **Sign Up:** Create a new account.
2.  **Log In:** Access your personalized workspace.
3.  **Write Code:** Type Python code in the editor (e.g., `print("Hello World!")`).
4.  **Run Code:** Click the **Run** button to execute.
5.  **Fix Bugs:** Try writing code with an error (e.g., `10 / 0`). See how BugMind AI explains the `ZeroDivisionError` and suggests a fix!

## 📂 Project Structure

```
BugMind-AI/
├── backend/                  # FastAPI Backend
│   ├── main.py               # API routing and server entry
│   ├── database.py           # SQLite DB setup and CRUD operations
│   ├── auth.py               # JWT authentication and password hashing
│   ├── code_runner.py        # Safe Python code execution logic
│   ├── ai_engine.py          # AI error analysis and generic fixes
│   └── models.py             # Pydantic schemas for API requests
├── frontend/                 # Vanilla HTML/CSS/JS Frontend
│   ├── index.html            # Main editor workspace
│   ├── login.html            # User login page
│   ├── signup.html           # User registration page
│   ├── dashboard.html        # User statistics and learning hub
│   ├── community.html        # Community leaderboard and discussions
│   ├── settings.html         # User preferences and themes
│   ├── styles.css            # Global stylesheet with modern UI/UX
│   ├── app.js               # Frontend logic and API integration
│   └── assets/               # Images and icons (e.g., logo.svg)
└── requirements.txt          # Python dependencies
```

---
*Built to help developers write better code, faster.*
