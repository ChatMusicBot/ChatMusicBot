# 🎵 Telegram Music Bot

Telegram videochat uchun musiqa boti.

## O'rnatish

### 1. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

FFmpeg ham kerak:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# https://ffmpeg.org/download.html dan yuklab, PATH ga qo'shing
```

### 2. .env faylini yaratish
```bash
cp .env.example .env
```

`.env` faylini oching va ma'lumotlarni kiriting:
```
API_ID=31008887
API_HASH=504c65ab388909af2de058bf07f6c6bf
BOT_TOKEN=yangi_token_bu_yerga
```

### 3. User Session yaratish
```bash
python session.py
```
Telefon raqamingizni kiriting va kodni tasdiqlang.

### 4. Botni ishga tushirish
```bash
python bot.py
```

## Ishlatish

1. Botni guruhga qo'shing
2. Guruhda **Videochat**ni boshlang
3. `/play Ulug'bek Rahmatullayev` — musiqa qo'ying!

## Komandalar

| Komanda | Izoh |
|---------|------|
| `/play [nom]` | Musiqa qo'yish |
| `/pause` | To'xtatib turish |
| `/resume` | Davom ettirish |
| `/skip` | Keyingisiga o'tish |
| `/queue` | Navbatni ko'rish |
| `/stop` | To'xtatish |
| `/search [nom]` | YouTube qidirish |
