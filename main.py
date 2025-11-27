import os
import ftplib
import asyncio
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeFilename

# -----------------------------
# Config (from environment)
# -----------------------------
API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")
SESSION_NAME = os.getenv("TG_SESSION", "teleuploader")

RG_FTP_HOST = os.getenv("RG_FTP_HOST")
RG_FTP_USER = os.getenv("RG_FTP_USER")
RG_FTP_PASS = os.getenv("RG_FTP_PASSWORD")

CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB per chunk

# -----------------------------
# Initialize Telegram client
# -----------------------------
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# -----------------------------
# Stream upload to Rapidgator via FTP
# -----------------------------
async def upload_to_rapidgator(file_obj, filename):
    print(f"Starting upload of {filename} to Rapidgator...")
    ftp = ftplib.FTP()
    ftp.connect(RG_FTP_HOST)
    ftp.login(RG_FTP_USER, RG_FTP_PASS)
    ftp.set_pasv(True)

    def file_generator():
        for chunk in file_obj:
            yield chunk

    ftp.storbinary(f"STOR {filename}", file_generator())
    ftp.quit()
    print(f"Uploaded {filename} successfully!")
    return f"https://rapidgator.net/file/{filename}"  # placeholder

# -----------------------------
# Download file from Telegram in chunks
# -----------------------------
async def stream_file(message):
    filename = message.file.name or "file"
    stream = message.download_media(file=None, bytes=CHUNK_SIZE)
    return filename, stream

# -----------------------------
# Select a file from chat
# -----------------------------
async def select_file(chat_id):
    messages = await client.get_messages(chat_id, limit=50)
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
        filename, file_chunks = await stream_file(msg)
        await upload_to_rapidgator(file_chunks, filename)

    await client.disconnect()

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())

