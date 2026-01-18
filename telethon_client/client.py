from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from bot.config import API_ID, API_HASH, EXTERNAL_BOT

# Create Telethon client
client = TelegramClient("user_session", API_ID, API_HASH)

async def start_client():
    await client.start()  # Logs in if needed
    print("✅ Telethon user client started")

# Debug helper
def debug_message_buttons(msg):
    print("===== DEBUG BOT MENU =====")
    print("Message ID:", msg.id)
    print("Text:", msg.text)
    if msg.reply_markup:
        print("Reply markup present!")
        for i, row in enumerate(msg.reply_markup.rows):
            print(f"Row {i}:")
            for j, button in enumerate(row.buttons):
                print(f"  Button {j}: text='{button.text}', type={type(button)}")
                if hasattr(button, "url"):
                    print(f"    URL: {button.url}")
                if hasattr(button, "data"):
                    print(f"    callback data: {button.data}")
    else:
        print("No reply markup.")
    print("===========================")

# Handler for debugging menus from the external bot
@client.on(events.NewMessage(chats=EXTERNAL_BOT))
async def menu_handler(event):
    msg = event.message
    debug_message_buttons(msg)

    # Automatically click the first track button (row 0, button 0)
    if msg.reply_markup and msg.reply_markup.rows:
        first_row = msg.reply_markup.rows[0]
        if first_row.buttons and hasattr(first_row.buttons[0], "data"):
            callback_data = first_row.buttons[0].data
            print(f"⚡ Automatically sending callback: {callback_data}")

            try:
                await client(GetBotCallbackAnswerRequest(
                    peer=msg.chat_id,
                    msg_id=msg.id,
                    data=callback_data
                ))
                print("✅ Callback sent successfully!")
            except Exception as e:
                print("❌ Failed to send callback:", e)

# Start the client
if __name__ == "__main__":
    import asyncio
    asyncio.run(start_client())
    print("🚀 Client running. Listening for bot messages...")
    client.run_until_disconnected()
