import asyncio

_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from lists_teletips.quotes_teletips import *
from lists_teletips.emojis_teletips import *
from PIL import Image, ImageDraw, ImageFont
import datetime
import pytz
import random
import os

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
    try:
        while True:
            if Date_Time_Userbot_teletips.is_connected:
                Quotes_teletips = random.choice(quotes_teletips)
                Emojis_teletips = random.choice(emojis_teletips)
                TimeZone_teletips = datetime.datetime.now(pytz.timezone(f"{TIME_ZONE}"))
                Time_teletips = TimeZone_teletips.strftime("%I:%M %p")
                Date_teletips = TimeZone_teletips.strftime("%b %d")
                Image_teletips = Image.open("image.jpg")
                Image_font_teletips = ImageFont.truetype("ds-digit.ttf", 360)
                Image_text_teletips = f"{Time_teletips}"
                Image_edit_teletips = ImageDraw.Draw(Image_teletips)
                Image_edit_teletips.text((690, 550), Image_text_teletips, (0, 255, 255), font=Image_font_teletips)
                Image_teletips.save("Image_final_teletips.jpg")
                await Date_Time_Userbot_teletips.update_profile(
                    bio=f"{Emojis_teletips} {Quotes_teletips}",
                    last_name=f"| ⏰ {Time_teletips} | 📅 {Date_teletips}",
                )
                await Date_Time_Userbot_teletips.set_profile_photo(photo="Image_final_teletips.jpg")
                me = await Date_Time_Userbot_teletips.get_me()
                photos = Date_Time_Userbot_teletips.get_chat_photos("me")
                try:
                    await Date_Time_Userbot_teletips.delete_profile_photos(photos[1].file_id)
                except Exception:
                    pass
                print("Profile Updated!")
            await asyncio.sleep(60)
    except FloodWait as e:
        await asyncio.sleep(e.x)


print("DATE TIME USERBOT IS ALIVE!")
asyncio.ensure_future(main_teletips())
Date_Time_Userbot_teletips.run()
