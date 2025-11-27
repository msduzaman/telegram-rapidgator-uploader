import os
import ftplib
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeFilename
import aiohttp

# -----------------------------
# CONFIG (from environment)
# -----------------------------
API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")
SESSION_NAME = os.getenv("TG_SESSION", "teleuploader")

RG_FTP_HOST = os.getenv("RG_FTP_HOST")
RG_FTP_USER = os.getenv("RG_FTP_USER")
RG_FTP_PASS = os.getenv("RG_FTP_PASSWORD")

# -----------------------------
# Initialize Telegram client
# -----------------------------
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# -----------------------------
# Function to upload a file to Rapidgator streaming
# -----------------------------
async def upload_to_rapidgator(file_path, filename):
    print(f"Uploading {filename} to Rapidgator...")
    ftp = ftplib.FTP()
    ftp.connect(RG_FTP_HOST)
    ftp.login(RG_FTP_USER, RG_FTP_PASS)
    ftp.set_pasv(True)

    # Stream upload in chunks using aiohttp
    with open(file_path, "rb") as f:
        ftp.storbinary(f"STOR {filename}", f)

    ftp.quit()
    print(f"Uploaded {filename} successfully!")
    return f"https://rapidgator.net/file/{filename}"  # placeholder

# -----------------------------
# Helper to select file from Telegram
# -----------------------------
async def select_file(chat_id):
    messages = await client.get_messages(chat_id, limit=50)
    print("Last 50 messages in chat:")
    files = []
    for i, msg in enumerate(messages):
        if msg.file:
            fname = msg.file.name or f"file_{i}"
            print(f"{i}: {fname}")
            files.append(msg)
    if not files:
        print("No files found in this chat.")
        return None

    choice = int(input("Enter the number of the file to upload: "))
    return files[choice]

# -----------------------------
# Main logic
# -----------------------------
async def main():
    await client.start()
    print("Logged in successfully!")

    chat = input("Enter chat username or ID: ")
    msg = await select_file(chat)
    if msg:
        filename = msg.file.name or "file"
        temp_path = f"/tmp/{filename}"  # temporary path in cloud
        await msg.download_media(temp_path)
        await upload_to_rapidgator(temp_path, filename)
        os.remove(temp_path)

    await client.disconnect()

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())
