import asyncio
import random
from pathlib import Path
from telethon_client.parser import query_external_bot_first
from bot.config import DOWNLOAD_PATH

async def process_csv(
    csv_path: str,
    subdir: str = "csv_upload",
):
    download_path = Path(DOWNLOAD_PATH) / subdir
    download_path.mkdir(parents=True, exist_ok=True)

    with open(csv_path, encoding="utf-8") as f:
        for line in f:
            song_name = line.strip()

            if not song_name:
                continue

            print(f"🎵 Processing: {song_name}")
            filename = await query_external_bot_first(
                song_name,
                str(download_path)
            )

            if filename:
                print(f"✅ Done: {filename}")
            else:
                print(f"❌ Failed: {song_name}")

            await asyncio.sleep(random.uniform(6, 12))
