import asyncio
import os
import yt_dlp


DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


def _format_duration(seconds):
    if not seconds:
        return "Noma'lum"
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


async def search_youtube(query: str, max_results: int = 1):
    """YouTube dan qidirish"""
    loop = asyncio.get_event_loop()

    def _search():
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
        }

        search_query = f"ytsearch{max_results}:{query}"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)

            if not info or "entries" not in info:
                return None

            entries = info["entries"]

            if max_results == 1:
                entry = entries[0]
                return {
                    "title": entry.get("title", "Noma'lum"),
                    "url": f"https://www.youtube.com/watch?v={entry['id']}",
                    "duration": _format_duration(entry.get("duration")),
                    "thumbnail": entry.get("thumbnail", ""),
                }

            results = []
            for entry in entries:
                results.append({
                    "title": entry.get("title", "Noma'lum"),
                    "url": f"https://www.youtube.com/watch?v={entry['id']}",
                    "duration": _format_duration(entry.get("duration")),
                    "thumbnail": entry.get("thumbnail", ""),
                })
            return results

    return await loop.run_in_executor(None, _search)


async def download_audio(url: str) -> str | None:
    """Audio faylni yuklab olish"""
    loop = asyncio.get_event_loop()

    def _download():
        output_path = os.path.join(DOWNLOADS_DIR, "%(id)s.%(ext)s")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path,
            "quiet": True,
            "no_warnings": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info["id"]
            file_path = os.path.join(DOWNLOADS_DIR, f"{video_id}.mp3")

            if os.path.exists(file_path):
                return file_path

        return None

    return await loop.run_in_executor(None, _download)
