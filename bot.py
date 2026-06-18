import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types.input_stream import InputAudioStream
from pytgcalls.types.input_stream.quality import HighQualityAudio
from dotenv import load_dotenv
from queue_manager import MusicQueue
from downloader import search_youtube, download_audio

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Pyrogram client (user session uchun)
user_client = Client("user_session", api_id=API_ID, api_hash=API_HASH)

# Bot client
bot = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# PyTgCalls instance
call_py = PyTgCalls(user_client)

# Har bir chat uchun queue
queues = {}


def get_queue(chat_id):
    if chat_id not in queues:
        queues[chat_id] = MusicQueue()
    return queues[chat_id]


@bot.on_message(filters.command("start"))
async def start_cmd(client, message: Message):
    await message.reply_text(
        "🎵 **Music Bot ga xush kelibsiz!**\n\n"
        "**Komandalar:**\n"
        "▶️ `/play [qo'shiq nomi]` — Musiqa qo'yish\n"
        "⏸ `/pause` — To'xtatib turish\n"
        "▶️ `/resume` — Davom ettirish\n"
        "⏭ `/skip` — Keyingisiga o'tish\n"
        "📋 `/queue` — Navbatni ko'rish\n"
        "⏹ `/stop` — To'xtatish\n"
        "🔍 `/search [nom]` — Qidirish\n"
    )


@bot.on_message(filters.command("play"))
async def play_cmd(client, message: Message):
    chat_id = message.chat.id

    if len(message.command) < 2:
        await message.reply_text("❌ Qo'shiq nomini kiriting: `/play Dildora Niyozova`")
        return

    query = " ".join(message.command[1:])
    status_msg = await message.reply_text(f"🔍 **Qidirilmoqda:** `{query}`...")

    try:
        # YouTube dan qidirish
        result = await search_youtube(query)
        if not result:
            await status_msg.edit_text("❌ Qo'shiq topilmadi!")
            return

        await status_msg.edit_text(f"⬇️ **Yuklanmoqda:** `{result['title']}`...")

        # Audio yuklash
        file_path = await download_audio(result["url"])
        if not file_path:
            await status_msg.edit_text("❌ Yuklab bo'lmadi!")
            return

        queue = get_queue(chat_id)
        track = {
            "title": result["title"],
            "url": result["url"],
            "file": file_path,
            "duration": result["duration"],
            "thumbnail": result.get("thumbnail", ""),
            "requested_by": message.from_user.first_name,
        }

        if queue.is_empty():
            queue.add(track)
            await play_track(chat_id, track, status_msg)
        else:
            queue.add(track)
            await status_msg.edit_text(
                f"📋 **Navbatga qo'shildi:**\n"
                f"🎵 {result['title']}\n"
                f"📍 Navbat: {queue.size()}-chi"
            )

    except Exception as e:
        await status_msg.edit_text(f"❌ Xatolik: {str(e)}")


async def play_track(chat_id, track, message=None):
    try:
        await call_py.join_group_call(
            chat_id,
            InputAudioStream(
                track["file"],
                HighQualityAudio(),
            ),
        )

        text = (
            f"▶️ **Hozir ijro etilmoqda:**\n\n"
            f"🎵 **{track['title']}**\n"
            f"⏱ Davomiyligi: {track['duration']}\n"
            f"👤 So'ragan: {track['requested_by']}"
        )

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⏸ Pause", callback_data="pause"),
                InlineKeyboardButton("⏭ Skip", callback_data="skip"),
                InlineKeyboardButton("⏹ Stop", callback_data="stop"),
            ]
        ])

        if message:
            await message.edit_text(text, reply_markup=buttons)

    except Exception as e:
        if message:
            await message.edit_text(f"❌ Videochatga ulanib bo'lmadi: {str(e)}\n\nVideochatni boshlang va qayta urinib ko'ring.")


@bot.on_message(filters.command("pause"))
async def pause_cmd(client, message: Message):
    try:
        await call_py.pause_stream(message.chat.id)
        await message.reply_text("⏸ **Musiqa to'xtatib turildi**")
    except Exception:
        await message.reply_text("❌ Hozir musiqa ijro etilmayapti")


@bot.on_message(filters.command("resume"))
async def resume_cmd(client, message: Message):
    try:
        await call_py.resume_stream(message.chat.id)
        await message.reply_text("▶️ **Musiqa davom ettirildi**")
    except Exception:
        await message.reply_text("❌ Davom ettirib bo'lmadi")


@bot.on_message(filters.command("skip"))
async def skip_cmd(client, message: Message):
    chat_id = message.chat.id
    queue = get_queue(chat_id)
    queue.next()

    if queue.is_empty():
        await call_py.leave_group_call(chat_id)
        await message.reply_text("⏭ O'tkazildi. Navbat bo'sh.")
    else:
        track = queue.current()
        await play_track(chat_id, track)
        await message.reply_text(f"⏭ **Keyingisi:** {track['title']}")


@bot.on_message(filters.command("stop"))
async def stop_cmd(client, message: Message):
    chat_id = message.chat.id
    queue = get_queue(chat_id)
    queue.clear()
    try:
        await call_py.leave_group_call(chat_id)
        await message.reply_text("⏹ **Musiqa to'xtatildi va navbat tozalandi**")
    except Exception:
        await message.reply_text("⏹ **Navbat tozalandi**")


@bot.on_message(filters.command("queue"))
async def queue_cmd(client, message: Message):
    queue = get_queue(message.chat.id)
    if queue.is_empty():
        await message.reply_text("📋 Navbat bo'sh")
        return

    items = queue.get_all()
    text = "📋 **Navbat:**\n\n"
    for i, track in enumerate(items):
        prefix = "▶️" if i == 0 else f"{i + 1}."
        text += f"{prefix} {track['title']}\n"

    await message.reply_text(text)


@bot.on_message(filters.command("search"))
async def search_cmd(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ Qidirish uchun: `/search Ulug'bek Rahmatullayev`")
        return

    query = " ".join(message.command[1:])
    status_msg = await message.reply_text(f"🔍 **Qidirilmoqda:** `{query}`...")

    try:
        results = await search_youtube(query, max_results=5)
        if not results:
            await status_msg.edit_text("❌ Hech narsa topilmadi")
            return

        # Agar bitta natija qaytsa
        if isinstance(results, dict):
            results = [results]

        buttons = []
        text = "🔍 **Natijalar:**\n\n"
        for i, r in enumerate(results[:5]):
            text += f"{i+1}. {r['title']} ({r['duration']})\n"
            buttons.append([InlineKeyboardButton(
                f"▶️ {i+1}. {r['title'][:30]}",
                callback_data=f"play_{r['url']}"
            )])

        await status_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

    except Exception as e:
        await status_msg.edit_text(f"❌ Xatolik: {str(e)}")


# Callback query handler (inline tugmalar)
@bot.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id

    if data == "pause":
        await call_py.pause_stream(chat_id)
        await callback_query.answer("⏸ To'xtatildi")

    elif data == "resume":
        await call_py.resume_stream(chat_id)
        await callback_query.answer("▶️ Davom ettirildi")

    elif data == "skip":
        queue = get_queue(chat_id)
        queue.next()
        if not queue.is_empty():
            await play_track(chat_id, queue.current())
        else:
            await call_py.leave_group_call(chat_id)
        await callback_query.answer("⏭ O'tkazildi")

    elif data == "stop":
        get_queue(chat_id).clear()
        await call_py.leave_group_call(chat_id)
        await callback_query.answer("⏹ To'xtatildi")

    elif data.startswith("play_"):
        url = data[5:]
        await callback_query.answer("▶️ Qo'shilmoqda...")
        # play_cmd ga o'xshash logika


# Stream tugaganda keyingisiga o'tish
@call_py.on_stream_end()
async def on_stream_end(_, update: Update):
    chat_id = update.chat_id
    queue = get_queue(chat_id)
    queue.next()

    if not queue.is_empty():
        track = queue.current()
        await play_track(chat_id, track)


async def main():
    await user_client.start()
    await bot.start()
    await call_py.start()
    print("✅ Bot ishga tushdi!")
    await asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    asyncio.run(main())
