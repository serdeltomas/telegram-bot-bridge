# Telegram-bot-bridge
Telegram Bot Bridge (Production Ready)

This repository implements a Telegram Bot → User Account → External Bot bridge that:

Accepts commands from users via your Telegram bot

Queries another Telegram bot using a real user account (Telethon)

Displays selectable options to the user

Downloads the selected file to a specified server directory

🧱 Architecture
User (public users & friends)
 ↓
Your Bot (aiogram, Bot API)
 ↓
User Account Client (Telethon)
 ↓
@fmusbot
 ↓
User Account Client
 ↓
Your Bot
 ↓
Debian Server Storage (Audio files)

User ↓ Your Bot (Bot API / aiogram) ↓ User Client (Telethon) ↓ External Bot ↓ User Client ↓ Your Bot ↓ Local Storage



---


## 📁 Project Structure

telegram-bot-bridge/ │ ├── bot/ │ ├── main.py # Bot entrypoint │ ├── handlers.py # Commands & callbacks │ ├── config.py # Env config │ ├── telethon_client/ │ ├── client.py # Telethon user client │ ├── parser.py # Parses external bot responses │ ├── storage/ │ └── downloads/ # Downloaded files │ ├── requirements.txt ├── .env.example ├── Dockerfile └── README.md



---


## ⚙️ Requirements
- Python 3.10+
- Telegram API ID & HASH
- Telegram Bot Token


---


## 🔐 `.env.example`
```env
BOT_TOKEN=YOUR_BOT_TOKEN
API_ID=123456
API_HASH=YOUR_API_HASH
EXTERNAL_BOT=@fmusbot
DOWNLOAD_PATH=storage/downloads/audio
```env
BOT_TOKEN=YOUR_BOT_TOKEN
API_ID=123456
API_HASH=YOUR_API_HASH
EXTERNAL_BOT=@OtherBotUsername
DOWNLOAD_PATH=storage/downloads
