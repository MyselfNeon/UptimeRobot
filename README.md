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

  * ***Go to <a href="#mandatory-vars">Variables Tab</a> for more info on Setting up Environmental Variables.***
  </details>

<details>
  <summary><b><i>Deploy Using Docker</i></b></summary>
<br>

* ***Clone the Repository :***
```sh
git clone https://github.com/myselfneon/FileStream-Bot
cd FileStreamBot
```

* ***Build own Docker Image :***
```sh
docker build -t file-stream .
```

* ***Create ENV and Start Container :***
```sh
docker run -d --restart unless-stopped --name fsb \
-v /PATH/TO/.env:/app/.env \
-p 8000:8000 \
file-stream
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
  git clone https://github.com/myselfneon/FileStream-Bot
  cd FileStreamBot
  python3 -m venv ./venv
  . ./venv/bin/activate
  pip install -r requirements.txt
  python3 -m FileStream
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
* [`OWNER_ID`]: ***Your Telegram User ID. Get From [@MissRose_Bot](https://t.me/MissRose_Bot)***
* [`BOT_TOKEN`]: ***Telegram API Bot Token, Get it from [@BotFather](https://t.me/BotFather).***
* [`FLOG_CHANNEL`]: ***ID of the Channel where Bot will Store all Files from Users `int`***
* [`ULOG_CHANNEL`]: ***ID of the Channel where Bot will send Logs of New Users`int`***
* [`BOT_WORKERS`]: ***Number of updates Bot should process from Telegram at once, by Default to 10 Updates. `int`***
* [`DATABASE_URL`]: ***[MongoDB URI](https://cloud.mongodb.com) for Saving User Data and Files List created by User. `str`***
* [`FQDN`]: ***A Fully Qualified Domain Name if present without https. Defaults `BIND_ADDRESS`.***

</details>

#### *Bot Commands ➠* 

<details><summary><b><i>Bot Commands</i></b></summary>
  
```
start - Check if Bot is Alive
help - Get Help Message
about - Check About the Bot
files - Get All Files List of User
del - Delete Files from DB with File ID [ADMIN]
ban - Ban any Channel or User from using Bot [ADMIN]
unban - Unban any Channel or User from using Bot [ADMIN]
status - To Get Bot Status and Total Users [ADMIN]
broadcast - To Broadcast any Message to all Users of Bot [ADMIN]
```
<b><i>⪼ Copy all Commands and paste it in <a href='https://t.me/botfather'>BotFather</a> to apply Commands.

</details>

#### *Channel Support ➠*

***The Bot also Supports Telegram Channels, Just add it as an Admin. Whenever a new File is posted in the Channel, the Bot will Automatically edit the Message and add a “Get Download Link” Button.***

#### Contact Developer 👨‍💻

[![Contact Developer](https://img.shields.io/badge/Contact-Developer-blue?logo=telegram)](https://t.me/MyselfNeon)    
[![Telegram Channel](https://img.shields.io/badge/Telegram-Main%20Channel-blue?logo=telegram)](https://t.me/neonfiles)  
Join My <a href='https://t.me/neonfiles'>Update Channel</a> For More Update Regarding Repo.

</details>

#### *Thanks To ➠* ❤️
 - <b>Thanks To [Neon An](https://t.me/MyselfNeon) To Modify And Add Amazing Features
 - Thanks To Everyone who have Contributed In This Repo ❤️</b>

---
<h4 align="center">➠ © <a href="https://myselfneon.github.io/neon/" target="_blank" rel="noopener noreferrer">MyselfNeon 🍟</a></h4>

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
