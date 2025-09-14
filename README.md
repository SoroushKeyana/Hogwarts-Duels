# Hogwarts Duels

Hogwarts Duels is a dynamic web application built with Python, Django, and JavaScript that allows users to experience the thrill of magical combat. Users can register an account, choose their Hogwarts house, follow other users, and challenge them to live, turn-based duels using a variety of spells. The application features a real-time dueling system, a house points leaderboard, and a social system for finding and challenging friends.

## Distinctiveness and Complexity

This project satisfies the distinctiveness and complexity requirements by moving far beyond the scope of a standard social network or e-commerce site. While it incorporates social elements like user search and a follow system, these are secondary features that serve the application's primary purpose: to facilitate a stateful, interactive game. Unlike a social network where the core user activity is creating and consuming static posts, the central loop of Hogwarts Duels involves users engaging in a persistent, multi-step, competitive interaction with a clear win/loss state.

The complexity of this project is demonstrated in several key areas:

1.  **Stateful, Asynchronous Gameplay:** A duel is not a simple, single request-response action. It is a persistent object in the database with multiple states (`pending`, `accepted`, `finished`). The application must manage the duel's state across multiple interactions from two different users. The backend logic, primarily in `views.py`, handles the complex turn-based flow, ensuring that only the correct user can act at the correct time.

2.  **Simulated Real-Time Interaction:** To create a dynamic and engaging experience without requiring a full page reload for every action, the dueling page uses a JavaScript polling mechanism. Every few seconds, the client fetches the current game state from a dedicated API endpoint (`/duel/<id>/status/`). This keeps the health points, turn information, and spell history updated for both players, simulating a real-time environment and demonstrating a practical application of client-server communication beyond simple form submissions.

3.  **Timed-Response System:** A significant layer of complexity is the defender's timed response. When a player is attacked, they have 10 seconds to choose a defensive spell. This is implemented on the client-side using JavaScript timers (`setInterval`) that provide a visual countdown. If the timer expires, the frontend automatically submits a "timeout" action to the backend, forcing the turn to resolve. This requires careful management of both client-side and server-side state.

4.  **Complex Game Logic and Integrated Systems:** The core of the duel lies in the spell interaction system. A `SPELL_DATA` dictionary in `views.py` acts as a spell matrix, defining each spell's power, type (attack/defense), and its specific counters. When a move is made, the backend calculates damage based on this matrix, checking if a defensive spell successfully counters an attack. Furthermore, the game systems are deeply integrated: a duel's outcome immediately updates the `wins` and `losses` on the participants' `UserProfile` models and, if it was an inter-house duel, updates the global `HousePoints` model, affecting the house leaderboard. This interconnectedness creates a cohesive and complex application ecosystem.

## File Structure and Contents

The project is organized into a main Django project directory (`hogwarts_duels`) and a single, primary application (`core`).

*   `requirements.txt`: A list of all Python packages required to run the application.
*   `core/`: The main application containing the core logic for the website.
    *   `models.py`: Defines the database schema with four key models: `UserProfile` (stores user-specific data like house and stats), `Follow` (manages the relationship between users), `Duel` (the core model for all game-related state), and `HousePoints` (tracks points for the house leaderboard).
    *   `views.py`: The heart of the backend logic. It handles user registration and authentication, serving all HTML pages, and providing the API endpoints for game actions (`attack`, `duel_status`), user searching, and following. It also contains the `SPELL_DATA` dictionary that defines the spell matrix.
    *   `urls.py`: Defines all URL patterns specific to the `core` application, mapping URLs to their corresponding views.
    *   `admin.py`: Registers the database models with the Django admin interface, allowing for easy data management.
    *   `templates/`: This directory contains all user-facing HTML files. Key templates include `base.html` (the main site template), `dashboard.html` (the user's home page), `profile.html`, and `duel.html` (the main interface for the dueling game).
    *   `static/`: Contains all static assets.
        *   `css/style.css`: The custom stylesheet for the project. It provides the Harry Potter-inspired look and all responsive design adjustments.
        *   `js/main.js`: Contains site-wide JavaScript, primarily for handling the dynamic user search and the follow/unfollow functionality. The duel-specific JavaScript is located directly within the `duel.html` template to keep it self-contained.

## How to Run Your Application

To run this application on your local machine, follow these steps:

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/SoroushKeyana/Hogwarts-Duels.git
    ```

2.  **Set up Environment Variables:**
    This project uses environment variables to handle sensitive data like the `SECRET_KEY`. In the root of the project directory (the same level as `manage.py`), create a file named `.env`. Add the following content to it, replacing the placeholder values as needed for your environment:
    ```
    SECRET_KEY=your_super_secret_and_unique_django_key_here
    DEBUG=True
    ALLOWED_HOSTS=127.0.0.1,localhost
    ```

3.  **Set up a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

4.  **Install Dependencies:**
    Install all required packages from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run Database Migrations:**
    Apply the database schema to your local database.
    ```bash
    python manage.py migrate
    ```

6.  **Start the Development Server:**
    ```bash
    python manage.py runserver
    ```

7.  **Access the Application:**
    Open your web browser and navigate to `http://127.0.0.1:8000/`. You can now register a new account and start dueling!

