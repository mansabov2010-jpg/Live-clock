import asyncio
import datetime
import os
import random
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytz
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client
from pyrogram.errors import FloodWait

from lists_teletips.emojis_teletips import *
from lists_teletips.quotes_teletips import *

# Render Web Service uchun kichik HTTP health server
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass


def start_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()


start_http_server()

_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)

# Siz bergan ma'lumotlar
BOT_TOKEN = "9172543528:AAES7H12sK9vRkpYo8SKuDydUZ-eyswAevg"
ADMIN_IDS = [7986354170, 7637155944]
CHANNEL_USERNAME = "@AniKinolar_kanal"
OWNER_USERNAME = "@Yegerist_mvp"

# Pyrogram userbot sozlamalari
API_ID = int(os.environ.get("API_ID", "34334454"))
API_HASH = os.environ.get("API_HASH", "a79d7ff6c07f5654ca52d8bbb69a68c5")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
TIME_ZONE = os.environ.get("TIME_ZONE", "Asia/Tashkent")

Date_Time_Userbot_teletips = Client(
    name="date_time_userbot_teletips",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)


async def main_teletips():
    tz = pytz.timezone(TIME_ZONE)
    font = ImageFont.truetype("ds-digit.ttf", 360)

    while True:
        try:
            if Date_Time_Userbot_teletips.is_connected:
                quote = random.choice(quotes_teletips)
                emoji = random.choice(emojis_teletips)
                now = datetime.datetime.now(tz)
                time_str = now.strftime("%I:%M %p")
                date_str = now.strftime("%b %d")

                img = Image.open("image.jpg").convert("RGB")
                draw = ImageDraw.Draw(img)
                draw.text((690, 550), time_str, (0, 255, 255), font=font)
                img.save("Image_final_teletips.jpg", quality=95)

                await Date_Time_Userbot_teletips.update_profile(
                    bio=f"{emoji} {quote}",
                    last_name=f"| ⏰ {time_str} | 📅 {date_str}",
                )
                await Date_Time_Userbot_teletips.set_profile_photo(
                    photo="Image_final_teletips.jpg"
                )

                # Eski profil rasmlarini (2-rasmdan boshlab) tozalash
                photos = []
                async for p in Date_Time_Userbot_teletips.get_chat_photos("me", limit=5):
                    photos.append(p)
                if len(photos) > 1:
                    await Date_Time_Userbot_teletips.delete_profile_photos(
                        [p.file_id for p in photos[1:]]
                    )

                print(f"Profile Updated! ({time_str})")

            await asyncio.sleep(60)

        except FloodWait as e:
            print(f"FloodWait: {e.value}s kutilmoqda...")
            await asyncio.sleep(e.value + 2)
        except Exception as err:
            print(f"Xato yuz berdi: {err}")
            await asyncio.sleep(15)


print("DATE TIME USERBOT IS ALIVE!")
asyncio.ensure_future(main_teletips())
Date_Time_Userbot_teletips.run()
