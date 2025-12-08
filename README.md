# ⚡ Premium Uptime Monitor Bot

A powerful, asynchronous Telegram bot written in **Python (Pyrogram)** to monitor the uptime of your websites. It checks your URLs in real-time and sends instant notifications if a service goes down or recovers.

## 🚀 Features

* **Real-Time Monitoring**: Checks websites 24/7.
* **Instant Alerts**: Get notified via Telegram immediately when a site goes Offline or comes back Online.
* **Smart Retry Logic**: Prevents false alarms by double-checking (3 attempts) before declaring a site down.
* **Multi-User Support**: Users can manage their own list of URLs.
* **Custom Intervals**: Admin can change the monitoring speed globally via the `/time` command.
* **Dashboard**: View live status of all your monitored links with HTTP response codes.
* **Web Server**: Built-in `aiohttp` web server to keep the bot alive on cloud platforms (Render, Railway, Heroku).
* **Database**: Persistent storage using MongoDB.

---

## 🛠 Config Vars

To run this bot, you need to set up the following environment variables.

| Variable | Description | Required |
| :--- | :--- | :--- |
| `API_ID` | Your Telegram API ID (get from my.telegram.org) | **Yes** |
| `API_HASH` | Your Telegram API Hash (get from my.telegram.org) | **Yes** |
| `BOT_TOKEN` | Your Bot Token (get from @BotFather) | **Yes** |
| `DB_URI` | Your MongoDB Connection String | **Yes** |
| `DB_NAME` | Database Name (Default: `UptimeBot`) | No |
| `ADMIN` | Your Telegram User ID (For startup logs) | No |
| `PORT` | Port for the web server (Default: `8080`) | No |

---

## 🤖 Bot Commands

| Command | Description |
| :--- | :--- |
| `/start` | Check if the bot is alive and get the menu. |
| `/add <url>` | Add a new URL to monitor (e.g., `/add https://google.com`). |
| `/del <url>` | Stop monitoring a specific URL. |
| `/check` | View the dashboard with live status of all your URLs. |
| `/stats` | Same as `/check`. |
| `/time` | (Admin) View or change the global monitoring interval in seconds. |

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

---

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
