"""
downloader.py
=============
Sva logika vezana za download videa, konverziju i FFmpeg.
Koristi yt-dlp za download i FFmpeg za konverziju.
"""

import os
import sys
import json
import shutil
import tempfile
import threading
import subprocess
from pathlib import Path

import yt_dlp
import requests
from logger_setup import logger


def get_ffmpeg_path():
    """
    Pronađi ffmpeg.exe.
    Prvo gleda u bundlovani ffmpeg/ folder (za .exe build),
    zatim u PATH sistemu.
    """
    # Putanja do ffmpeg bundlovanog sa aplikacijom
    if getattr(sys, 'frozen', False):
        # Pokrenuto kao PyInstaller .exe
        base_dir = os.path.dirname(sys.executable)
    else:
        # Pokrenuto kao Python skript
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    bundled_ffmpeg = os.path.join(base_dir, "ffmpeg", "ffmpeg.exe")
    if os.path.isfile(bundled_ffmpeg):
        logger.info(f"FFmpeg pronađen: {bundled_ffmpeg}")
        return bundled_ffmpeg
    
    # Pokušaj da nađeš ffmpeg u PATH
    ffmpeg_in_path = shutil.which("ffmpeg")
    if ffmpeg_in_path:
        logger.info(f"FFmpeg u PATH: {ffmpeg_in_path}")
        return ffmpeg_in_path
    
    logger.error("FFmpeg nije pronađen!")
    return None


def get_ffprobe_path():
    """Pronađi ffprobe.exe."""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    bundled_ffprobe = os.path.join(base_dir, "ffmpeg", "ffprobe.exe")
    if os.path.isfile(bundled_ffprobe):
        return bundled_ffprobe
    
    return shutil.which("ffprobe")


def get_cache_dir():
    """Vrati putanju do cache foldera."""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    cache_dir = os.path.join(base_dir, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def clear_cache():
    """Obriši sve privremene fajlove iz cache foldera."""
    cache_dir = get_cache_dir()
    try:
        for filename in os.listdir(cache_dir):
            filepath = os.path.join(cache_dir, filename)
            try:
                if os.path.isfile(filepath):
                    os.remove(filepath)
            except Exception as e:
                logger.warning(f"Nije moguće obrisati: {filepath} — {e}")
        logger.info("Cache očišćen.")
    except Exception as e:
        logger.error(f"Greška pri čišćenju cache-a: {e}")


class VideoInfo:
    """Klasa koja drži informacije o videu."""
    
    def __init__(self):
        self.title = ""
        self.duration = 0
        self.thumbnail_url = ""
        self.thumbnail_path = ""
        self.url = ""
        self.uploader = ""
        self.view_count = 0
        self.formats = []


def fetch_video_info(url: str) -> VideoInfo:
    """
    Fetchuje metadata o videu bez download-a.
    
    Args:
        url: URL videa
        
    Returns:
        VideoInfo objekat sa metapodacima
        
    Raises:
        ValueError: Ako link nije validan ili video nije dostupan
        ConnectionError: Ako nema interneta
    """
    logger.info(f"Fetchujem info za: {url}")
    
    # yt-dlp opcije — samo metadata, bez download-a
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'skip_download': True,
        'socket_timeout': 15,
        'noplaylist': True,
    }
    
    ffmpeg = get_ffmpeg_path()
    if ffmpeg:
        ydl_opts['ffmpeg_location'] = os.path.dirname(ffmpeg)
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info is None:
                raise ValueError("Nije moguće dobiti informacije o videu.")
            
            video = VideoInfo()
            video.url = url
            video.title = info.get('title', 'Nepoznat naslov')
            video.duration = info.get('duration', 0)
            video.thumbnail_url = info.get('thumbnail', '')
            video.uploader = info.get('uploader', '')
            video.view_count = info.get('view_count', 0)
            
            logger.info(f"Video pronađen: {video.title} ({video.duration}s)")
            
            # Skini thumbnail u cache
            if video.thumbnail_url:
                video.thumbnail_path = _download_thumbnail(video.thumbnail_url)
            
            return video
            
    except yt_dlp.utils.DownloadError as e:
        error_str = str(e).lower()
        logger.error(f"yt-dlp greška: {e}")
        
        if "private" in error_str:
            raise ValueError("Ovaj video je privatan.")
        elif "unavailable" in error_str or "removed" in error_str:
            raise ValueError("Video nije dostupan ili je uklonjen.")
        elif "not a valid url" in error_str or "unsupported url" in error_str:
            raise ValueError("Nevažeći link. Proverite URL.")
        else:
            raise ValueError(f"Greška pri učitavanju videa: {str(e)[:200]}")
            
    except Exception as e:
        error_str = str(e).lower()
        if "network" in error_str or "connection" in error_str or "timeout" in error_str:
            raise ConnectionError("Nema internet veze ili server nije dostupan.")
        raise ValueError(f"Neočekivana greška: {str(e)[:200]}")


def _download_thumbnail(thumbnail_url: str) -> str:
    """
    Skini thumbnail u cache folder.
    
    Returns:
        Putanja do skinute slike, ili prazan string ako nije uspelo.
    """
    try:
        cache_dir = get_cache_dir()
        thumb_path = os.path.join(cache_dir, "thumbnail_temp.jpg")
        
        response = requests.get(thumbnail_url, timeout=10, stream=True)
        response.raise_for_status()
        
        with open(thumb_path, 'wb') as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
        
        logger.info(f"Thumbnail preuzet: {thumb_path}")
        return thumb_path
        
    except Exception as e:
        logger.warning(f"Nije moguće preuzeti thumbnail: {e}")
        return ""


def format_duration(seconds: int) -> str:
    """Konvertuj sekunde u HH:MM:SS ili MM:SS format."""
    if not seconds:
        return "Nepoznato"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


class DownloadWorker(threading.Thread):
    """
    Worker thread koji obavlja download u pozadini.
    GUI ostaje responzivan dok se skida video.
    
    Callbacks:
        on_progress(percent: float, speed: str, eta: str)
        on_status(message: str)
        on_finished(filepath: str)
        on_error(message: str)
    """
    
    def __init__(self, url: str, output_dir: str, format_type: str, quality: str):
        super().__init__(daemon=True)
        
        self.url = url
        self.output_dir = output_dir
        self.format_type = format_type   # "mp3" ili "mp4"
        self.quality = quality           # "720p", "1080p", "4k", "best"
        
        # Callbacks — GUI ih postavlja
        self.on_progress = None
        self.on_status = None
        self.on_finished = None
        self.on_error = None
        
        # Flag za zaustavljanje
        self._stop_event = threading.Event()
        self._downloaded_file = ""
    
    def stop(self):
        """Zaustavi download."""
        self._stop_event.set()
    
    def _progress_hook(self, d):
        """
        yt-dlp progress hook — poziva se pri svakom napretku.
        Prosleđuje podatke GUI-u kroz callback.
        """
        if self._stop_event.is_set():
            raise Exception("Download prekinut od strane korisnika.")
        
        status = d.get('status', '')
        
        if status == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
            speed = d.get('speed', 0)
            eta = d.get('eta', 0)
            
            # Izračunaj procenat
            if total > 0:
                percent = (downloaded / total) * 100
            else:
                percent = 0
            
            # Formatiraj brzinu
            if speed:
                if speed > 1_000_000:
                    speed_str = f"{speed/1_000_000:.1f} MB/s"
                else:
                    speed_str = f"{speed/1_000:.0f} KB/s"
            else:
                speed_str = "..."
            
            # Formatiraj ETA
            if eta:
                eta_str = f"{eta}s"
            else:
                eta_str = ""
            
            if self.on_progress:
                self.on_progress(percent, speed_str, eta_str)
                
        elif status == 'finished':
            self._downloaded_file = d.get('filename', '')
            if self.on_status:
                self.on_status("Konvertujem...")
    
    def _get_ydl_opts(self):
        """Konstruiši yt-dlp opcije na osnovu formata i kvaliteta."""
        
        ffmpeg_path = get_ffmpeg_path()
        
        # Osnovna konfiguracija
        opts = {
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
            'retries': 3,
        }
        
        # Dodaj ffmpeg ako postoji
        if ffmpeg_path:
            opts['ffmpeg_location'] = os.path.dirname(ffmpeg_path)
        
        if self.format_type == "mp3":
            # MP3 konfiguracija
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
            
        elif self.format_type == "mp4":
            # MP4 konfiguracija na osnovu kvaliteta
            if self.quality == "720p":
                opts['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]'
            elif self.quality == "1080p":
                opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]'
            elif self.quality in ("4k", "best"):
                opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best'
            else:
                opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'
            
            # Spoji video i audio u MP4
            opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]
            opts['merge_output_format'] = 'mp4'
        
        return opts
    
    def run(self):
        """Glavni thread — ovde se odvija download."""
        try:
            logger.info(f"Počinjem download: {self.url} [{self.format_type}/{self.quality}]")
            
            if self.on_status:
                self.on_status("Preuzimam...")
            
            # Proveri ffmpeg za mp3/mp4 konverziju
            ffmpeg = get_ffmpeg_path()
            if not ffmpeg:
                if self.on_error:
                    self.on_error(
                        "FFmpeg nije pronađen!\n\n"
                        "FFmpeg je potreban za konverziju videa.\n"
                        "Aplikacija očekuje ffmpeg.exe u folderu 'ffmpeg/'."
                    )
                return
            
            opts = self._get_ydl_opts()
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                
                if self._stop_event.is_set():
                    return
                
                # Pronađi skinuti fajl
                if info:
                    filename = ydl.prepare_filename(info)
                    # Za MP3, yt-dlp menja ekstenziju
                    if self.format_type == "mp3":
                        filename = os.path.splitext(filename)[0] + ".mp3"
                    
                    if os.path.exists(filename):
                        logger.info(f"Download završen: {filename}")
                        if self.on_finished:
                            self.on_finished(filename)
                    else:
                        # Pokušaj da pronađeš fajl u folderu
                        if self.on_finished:
                            self.on_finished(self.output_dir)
                
        except yt_dlp.utils.DownloadError as e:
            error_str = str(e).lower()
            logger.error(f"Download greška: {e}")
            
            if self._stop_event.is_set():
                return
            
            if "private" in error_str:
                msg = "Video je privatan."
            elif "unavailable" in error_str:
                msg = "Video nije dostupan."
            else:
                msg = f"Greška pri download-u:\n{str(e)[:300]}"
            
            if self.on_error:
                self.on_error(msg)
                
        except Exception as e:
            if self._stop_event.is_set():
                return
            
            logger.error(f"Neočekivana greška pri download-u: {e}")
            
            if self.on_error:
                self.on_error(f"Greška:\n{str(e)[:300]}")
