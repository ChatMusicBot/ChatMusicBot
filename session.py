"""
Bu script user session yaratish uchun.
Bir marta ishga tushiring, keyin user_session.session fayli hosil bo'ladi.
"""
from pyrogram import Client
from dotenv import load_dotenv
import os

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

with Client("user_session", api_id=API_ID, api_hash=API_HASH) as app:
    print("✅ Session muvaffaqiyatli yaratildi!")
    print("Endi bot.py ni ishga tushirishingiz mumkin.")
