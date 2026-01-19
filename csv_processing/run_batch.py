import sys
import asyncio
from telethon_client.client import start_client
from csv_processing.batch import process_csv

async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m csv_processing.run_batch <csv_path> [subfolder]")
        sys.exit(1)

    csv_path = sys.argv[1]
    subfolder = sys.argv[2] if len(sys.argv) > 2 else "topola"

    await start_client()
    await process_csv(csv_path, subfolder)

if __name__ == "__main__":
    asyncio.run(main())
