import asyncio
from telethon_client.client import start_client
from csv_processing.batch import process_csv

async def main():
    await start_client()
    await process_csv("songs.csv")

if __name__ == "__main__":
    asyncio.run(main())
