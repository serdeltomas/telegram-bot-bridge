import os
from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
EXTERNAL_BOT = os.getenv("EXTERNAL_BOT")
DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH")
