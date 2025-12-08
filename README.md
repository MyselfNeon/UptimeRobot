### ⚡ *Premium Uptime Monitor Bot*

*A powerful, asynchronous Telegram bot written in **Python (Pyrogram)** to monitor the uptime of your websites. It checks your URLs in real-time and sends instant notifications if a service goes down or recovers.*

### 🚀 *Features*

* ***Real-Time Monitoring**: Checks websites 24/7.*
* ***Instant Alerts**: Get notified via Telegram immediately when a site goes Offline or comes back Online.*
* ***Smart Retry Logic**: Prevents false alarms by double-checking (3 attempts) before declaring a site down.*
* ***Multi-User Support**: Users can manage their own list of URLs.*
* ***Custom Intervals**: Admin can change the monitoring speed globally via the `/time` command.*
* ***Dashboard**: View live status of all your monitored links with HTTP response codes.*
* ***Web Server**: Built-in `aiohttp` web server to keep the bot alive on cloud platforms (Render, Railway, Heroku).*
* ***Database**: Persistent storage using MongoDB.*

---

### 🛠 Config Vars

*To run this bot, you need to set up the following environment variables. Click on a variable to see details.*

<details>
  <summary><code>API_ID</code> <small>(Required)</small></summary>
  <br>
  <b>Description:</b> Your Telegram API ID.<br>
  <b>How to get:</b> Log in to <a href="https://my.telegram.org">my.telegram.org</a>.
</details>

<details>
  <summary><code>API_HASH</code> <small>(Required)</small></summary>
  <br>
  <b>Description:</b> Your Telegram API Hash.<br>
  <b>How to get:</b> Log in to <a href="https://my.telegram.org">my.telegram.org</a>.
</details>

<details>
  <summary><code>BOT_TOKEN</code> <small>(Required)</small></summary>
  <br>
  <b>Description:</b> The authorization token for your bot.<br>
  <b>How to get:</b> Create a bot via <a href="https://t.me/BotFather">@BotFather</a> on Telegram.
</details>

<details>
  <summary><code>DB_URI</code> <small>(Required)</small></summary>
  <br>
  <b>Description:</b> Your MongoDB Connection String.<br>
  <b>Format:</b> <code>mongodb+srv://user:pass@cluster.mongodb.net/...</code>
</details>

<details>
  <summary><code>DB_NAME</code> <small>(Optional)</small></summary>
  <br>
  <b>Description:</b> The name of the database to use.<br>
  <b>Default:</b> <code>UptimeBot</code>
</details>

<details>
  <summary><code>ADMIN</code> <small>(Optional)</small></summary>
  <br>
  <b>Description:</b> Your Telegram User ID. Used for sending startup logs/errors.<br>
  <b>How to get:</b> Use a bot like @userinfobot.
</details>

<details>
  <summary><code>PORT</code> <small>(Optional)</small></summary>
  <br>
  <b>Description:</b> The port for the internal web server.<br>
  <b>Default:</b> <code>8080</code> (Required for Render/Heroku).
</details>

---

### 🤖 Bot Commands

*Click on a command to see its usage.*

<details>
  <summary><code>/start</code></summary>
  <br>
  <b>Usage:</b> <code>/start</code><br>
  <b>Description:</b> Check if the bot is alive and receive the welcome menu.
</details>

<details>
  <summary><code>/add</code></summary>
  <br>
  <b>Usage:</b> <code>/add https://google.com</code><br>
  <b>Description:</b> Adds a new URL to your monitoring list.
</details>

<details>
  <summary><code>/del</code></summary>
  <br>
  <b>Usage:</b> <code>/del https://google.com</code><br>
  <b>Description:</b> Stops monitoring the specified URL and removes it from the database.
</details>

<details>
  <summary><code>/check</code> or <code>/stats</code></summary>
  <br>
  <b>Usage:</b> <code>/check</code><br>
  <b>Description:</b> Displays a live dashboard with the status (Online/Offline) of all your URLs.
</details>

<details>
  <summary><code>/time</code></summary>
  <br>
  <b>Usage:</b> <code>/time</code><br>
  <b>Description:</b> (Admin Only) View or change the global monitoring interval (in seconds).
</details>

---

## 🐳 Deployment Methods

### Method 1: Docker (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YourUsername/Uptimer-Bot-neon.git](https://github.com/YourUsername/Uptimer-Bot-neon.git)
    cd Uptimer-Bot-neon
    ```

2.  **Build the Docker image:**
    ```bash
    docker build -t uptime-bot .
    ```

3.  **Run the container:**
    ```bash
    docker run -d \
      -e API_ID="12345" \
      -e API_HASH="your_api_hash" \
      -e BOT_TOKEN="your_bot_token" \
      -e DB_URI="your_mongodb_uri" \
      -e ADMIN="your_telegram_id" \
      uptime-bot
    ```

### Method 2: Local Deployment

1.  **Install Python 3.10+** and Clone the repo.
2.  **Install dependencies:**
    ```bash
    pip3 install -r requirements.txt
    ```
3.  **Set Environment Variables** (or create a `.env` file).
4.  **Run the bot:**
    ```bash
    python3 main.py
    ```

### Method 3: Cloud (Heroku/Render)

* **Build Command:** `pip3 install -r requirements.txt`
* **Start Command:** `python3 main.py`
* **Note:** The bot includes a web server on `app.py`. If using Render/Heroku, ensure you provide the `PORT` variable so the platform detects the service is running.

## 📂 Project Structure

```text
Uptimer-Bot-neon/
├── MyselfNeon/
│   ├── __init__.py
│   ├── commands.py    # Telegram Command Handlers
│   ├── db.py          # MongoDB Database Logic
│   ├── monitor.py     # Background Monitoring Task
│   └── ...
├── app.py             # Web Server (Keep-Alive)
├── info.py            # Configuration / Env Vars
├── main.py            # Entry Point
├── Dockerfile         # Docker Config
└── requirements.txt   # Dependencies
