import csv
import asyncio
import random
from telethon_client.parser import query_external_bot_first
from bot.config import DOWNLOAD_PATH

async def process_csv(csv_path: str):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            song_name = row["song"].strip()
            if not song_name:
                continue

            print(f"🎵 Processing: {song_name}")
            filename = await query_external_bot_first(song_name, DOWNLOAD_PATH+"/topola")

            if filename:
                print(f"✅ Done: {filename}")
            else:
                print(f"❌ Failed: {song_name}")

            # Optional: polite delay between requests
            await asyncio.sleep(random.uniform(6, 12))
