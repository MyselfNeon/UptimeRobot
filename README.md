### *Premium Uptime Monitor Bot*

***A powerful, High-performance asynchronous Telegram Bot written in Python (Pyrogram) to monitor the uptime of your websites. It monitors latency, SSL health, and uptime percentage in real-time.***

### 🚀 *Features*

* ***🚀 Concurrent Monitoring: Uses `asyncio` to check hundreds of URLs simultaneously without lag.***
* ***⚡ Latency Tracking: Tracks response time (ping) in milliseconds for every check.***
* ***🔒 SSL Health Checks: Monitors SSL certificate validity and alerts if expired.***
* ***📈 Uptime Analytics: Calculates and displays the Uptime Percentage (e.g., 99.98%) for each site.***
* ***🔔 Smart Alerts: Instant notifications for Downtime, Recovery, and Slow Response times.***
* ***📊 Live Dashboard: A beautiful text-based dashboard with auto-refresh capabilities.***
* ***🛠 Multi-User & Admin Controls: Users manage their own lists; Admins control global intervals.***
* ***☁️ Cloud Ready: Built-in `aiohttp` web server to keep the bot alive on Render/Railway/Heroku.***

---

#### *How To Deploy ➠*

<details><summary><b><i>Deploy on Multiple Servers</i></summary></b></summary>
<br>
<details>
    <summary><b><i>Deploy on Heroku (Paid)</i></b></summary>
    <br>

  * ***Fork This Repo***
  * ***Click on Deploy Easily***
  * ***Press the below Button to Fast Deploy on Heroku***

  [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

  * ***Go to <a href="config-variables">Variables Tab</a> for more info on Setting up Environmental Variables.***
  </details>

<details>
  <summary><b><i>Deploy Using Docker</i></b></summary>
<br>

* ***Clone the Repository :***
```sh
git clone [https://github.com/myselfneon/Uptimer-Bot](https://github.com/myselfneon/Uptimer-Bot)
cd Uptimer-Bot
```

* ***Build own Docker Image :***
```sh
docker build -t uptime-bot .
```

* ***Create ENV and Start Container :***
```sh
docker run -d --restart unless-stopped --name uptime-bot \
-e API_ID=123456 \
-e API_HASH=your_api_hash \
-e BOT_TOKEN=your_bot_token \
-e ADMIN=123456789 \
-e DB_URI=your_mongodb_uri \
-p 8080:8080 \
uptime-bot

```

* ***If you Need to Change the Variables in .env File after your Bot was Already Started, all you need to do is Restart the container for the Bot Settings to get Updated:***
```sh
docker restart fsb
```

</details>

<details>
    <summary><b><i>Deploy Locally</i></b></summary>
    <br>

  ```sh
  git clone [https://github.com/myselfneon/Uptimer-Bot-neon](https://github.com/myselfneon/Uptimer-Bot-neon)
cd Uptimer-Bot-neon
python3 -m venv ./venv
source ./venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python3 main.py
  ```

  * ***To stop the Bot Press <kbd>CTRL</kbd> + <kbd>C</kbd>.***

  * ***If you want to run this Bot 24/7 on a VPS, follow these Steps :***
  ```sh
  sudo apt install tmux -y
  tmux
  python3 -m FileStream
  ```
  * ***Now you can Close the VPS terminal — the Bot will Keep Running in the Background.***

  </details>

</details>

#### *Config Variables ➠*

<details><summary><b><i>ENV Variables</i></summary></b></summary>

#### *Mandatory Variables ➠*

* [`API_ID`]: ***From [My Telegram](https://my.telegram.org).***
* [`API_HASH`]: ***From [My Telegram](https://my.telegram.org).***
* [`ADMIN`]: ***Your Telegram User ID. Get From [@MissRose_Bot](https://t.me/MissRose_Bot)***
* [`BOT_TOKEN`]: ***Telegram API Bot Token, Get it from [@BotFather](https://t.me/BotFather).***
* [`DB_NAME`]: ***DataBase Name Optional. Default to UptimeBot.***
* [`DB_URI`]: ***[MongoDB URI](https://cloud.mongodb.com) for Saving Urls and History by User.***
* [`PORT`]: ***Web Server Port. Optional Defaults to `8080`.***

</details>

#### *Bot Commands ➠* 

<details><summary><b><i>Bot Commands</i></b></summary>
  
```
start - Welcome & Help Menu
add - Start monitoring a URL (Usage: /add [https://google.com](https://google.com))
del - Stop monitoring a URL (Usage: /del [https://google.com](https://google.com))
check - View Live Dashboard with Latency & Uptime %
time - [Admin Only] Change Global Monitoring Interval
```
<b><i>⪼ Copy all Commands and paste it in <a href='https://t.me/botfather'>BotFather</a> to apply Commands.

</details>

#### Contact Developer 👨‍💻

[![Contact Developer](https://img.shields.io/badge/Contact-Developer-blue?logo=telegram)](https://t.me/MyselfNeon)    
[![Telegram Channel](https://img.shields.io/badge/Telegram-Main%20Channel-blue?logo=telegram)](https://t.me/neonfiles)  
Join My <a href='https://t.me/neonfiles'>Update Channel</a> For More Update Regarding Repo.

</details>

#### *Thanks To ➠* ❤️
 - <b>Thanks To [Neon An](https://t.me/MyselfNeon) To Modify And Add Amazing Features
 - Thanks To Everyone who have Contributed In This Repo ❤️</b>

---

#### 📂 Project Structure

```text
Uptimer-Bot-neon/
├── MyselfNeon/
│   ├── __init__.py
│   ├── commands.py    # Handlers for /add, /del, /check
│   ├── db.py          # Database: Stores URLs, Uptime Counts, Latency
│   ├── monitor.py     # Core Engine: Asyncio, SSL Check, Latency Tracking
│   └── ...
├── app.py             # Web Server (Keep-Alive)
├── info.py            # Configuration / Env Vars
├── main.py            # Startup Logic
├── Dockerfile         # Docker Config
└── requirements.txt   # Dependencies
```
---

<h4 align="center">➠ © <a href="https://myselfneon.github.io/neon/" target="_blank" rel="noopener noreferrer">MyselfNeon 🍟</a></h4>
