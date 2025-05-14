from fastapi import FastAPI
from pyrogram import Client, filters
from pyrogram.types import Message
import os
import requests
from threading import Thread
import asyncio
from pyrogram.idle import idle

# Load environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
STREAMUP_API_KEY = os.getenv("STREAMUP_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Initialize Pyrogram bot client
bot = Client(
    "streamup_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Handle incoming video or document
@bot.on_message(filters.private & (filters.video | filters.document))
async def handle_video(client: Client, message: Message):
    msg = await message.reply_text("Downloading video...")
    path = None

    try:
        media = message.video or message.document
        path = await client.download_media(message)

        await msg.edit("Uploading to StreamUP...")

        file_name = media.file_name if media.file_name else "video.mp4"

        with open(path, "rb") as f:
            files = {"videoFile": (file_name, f, "video/mp4")}
            headers = {
                "Origin": "https://streamup.cc",
                "Referer": "https://streamup.cc/",
                "User-Agent": "Mozilla/5.0"
            }
            response = requests.post(
                "https://e1.beymtv.com/upload.php?id=1254",
                files=files,
                headers=headers
            )

        # Fetch latest uploaded video from StreamUP API
        r = requests.get(f"https://api.streamup.cc/v1/data?api_key={STREAMUP_API_KEY}&page=1")
        if r.ok:
            videos = r.json().get("videos", [])
            if videos:
                latest = videos[0]
                filecode = latest.get("Filecode")
                if filecode:
                    await msg.edit(f"**Upload successful!**\nhttps://streamup.ws/{filecode}")
                    return

        await msg.edit("Upload successful, but no link found.")

    except Exception as e:
        await msg.edit(f"Error: {str(e)}")

    finally:
        if path and os.path.exists(path):
            os.remove(path)

# Handle /start command
@bot.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    await message.reply_text("Send a video or document and I’ll upload it to StreamUP.")

# Start Pyrogram bot in a separate thread when FastAPI app starts
@app.on_event("startup")
async def on_startup():
    await bot.start()
    print("Bot started.")
    asyncio.create_task(idle())  # keeps the bot running

@app.on_event("shutdown")
async def on_shutdown():
    await bot.stop()
    print("Bot stopped.")
    
# FastAPI route for health check
@app.get("/")
def root():
    return {"status": "Bot is running"}
