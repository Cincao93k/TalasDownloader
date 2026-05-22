"""
updater.py
==========
Auto update sistem za Talas Downloader.
Proverava GitHub releases za novu verziju aplikacije.
Proverava ažuriranje yt-dlp biblioteke.
"""

import json
import os
import sys
import subprocess
import threading
import requests
from packaging.version import Version
from logger_setup import logger


# GitHub repo za aplikaciju (promeni na svoj repo)
GITHUB_REPO = "Cincao93k/TalasDownloader"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

# Fallback — lokalni version.json (ako nema GitHub)
LOCAL_VERSION_URL = "https://raw.githubusercontent.com/Cincao93k/TalasDownloader/main/version.json"


def get_current_version() -> str:
    """Čita trenutnu verziju iz version.json."""
    try:
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        version_file = os.path.join(base_dir, "version.json")
        
        with open(version_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("version", "1.0.0")
    except Exception as e:
        logger.warning(f"Nije moguće čitati version.json: {e}")
        return "1.0.0"


def check_app_update() -> dict:
    """
    Proverava da li postoji nova verzija aplikacije na GitHub.
    
    Returns:
        dict sa ključevima: 'available', 'version', 'url', 'changelog'
    """
    result = {
        'available': False,
        'version': '',
        'url': '',
        'changelog': ''
    }
    
    try:
        current = get_current_version()
        logger.info(f"Proveravam ažuriranja... Trenutna verzija: {current}")
        
        # Pokušaj GitHub API
        response = requests.get(GITHUB_API_URL, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        latest_version = data.get('tag_name', '').lstrip('v')
        download_url = data.get('html_url', '')
        changelog = data.get('body', '')
        
        if latest_version and Version(latest_version) > Version(current):
            logger.info(f"Nova verzija dostupna: {latest_version}")
            result['available'] = True
            result['version'] = latest_version
            result['url'] = download_url
            result['changelog'] = changelog
        else:
            logger.info("Aplikacija je ažurna.")
            
    except requests.RequestException as e:
        logger.warning(f"Nije moguće proveriti ažuriranja (GitHub): {e}")
        
        # Fallback: pokušaj lokalni version.json sa servera
        try:
            response = requests.get(LOCAL_VERSION_URL, timeout=8)
            data = response.json()
            latest_version = data.get("version", "")
            current = get_current_version()
            
            if latest_version and Version(latest_version) > Version(current):
                result['available'] = True
                result['version'] = latest_version
                result['url'] = "https://github.com/" + GITHUB_REPO
                result['changelog'] = data.get("changelog", "")
        except Exception:
            pass
            
    except Exception as e:
        logger.error(f"Greška pri proveri ažuriranja: {e}")
    
    return result


def check_ytdlp_update() -> bool:
    """
    Proverava da li postoji nova verzija yt-dlp.
    
    Returns:
        True ako je ažuriranje dostupno, False inače
    """
    try:
        import yt_dlp
        current_ytdlp = yt_dlp.version.__version__
        
        response = requests.get(
            "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest",
            timeout=8
        )
        response.raise_for_status()
        
        data = response.json()
        latest = data.get('tag_name', '').replace('/', '').strip()
        
        logger.info(f"yt-dlp: trenutna={current_ytdlp}, najnovija={latest}")
        
        return latest != current_ytdlp
        
    except Exception as e:
        logger.warning(f"Nije moguće proveriti yt-dlp verziju: {e}")
        return False


def update_ytdlp(callback=None):
    """
    Ažurira yt-dlp na najnoviju verziju.
    
    Args:
        callback: Funkcija koja prima string poruke o napretku
    """
    def _do_update():
        try:
            if callback:
                callback("Ažuriram yt-dlp...")
            
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("yt-dlp uspešno ažuriran.")
                if callback:
                    callback("yt-dlp ažuriran!")
            else:
                logger.error(f"Greška pri ažuriranju yt-dlp: {result.stderr}")
                if callback:
                    callback(f"Greška: {result.stderr[:100]}")
                    
        except Exception as e:
            logger.error(f"Nije moguće ažurirati yt-dlp: {e}")
            if callback:
                callback(f"Greška: {str(e)[:100]}")
    
    thread = threading.Thread(target=_do_update, daemon=True)
    thread.start()


def check_all_updates_async(on_app_update=None, on_ytdlp_update=None):
    """
    Proverava sva ažuriranja asinhrono u pozadini.
    Ne blokira GUI.
    
    Args:
        on_app_update: Callback(dict) kada postoji nova verzija aplikacije
        on_ytdlp_update: Callback() kada postoji nova verzija yt-dlp
    """
    def _check():
        try:
            # Proveri aplikaciju
            app_update = check_app_update()
            if app_update['available'] and on_app_update:
                on_app_update(app_update)
            
            # Proveri yt-dlp
            ytdlp_update = check_ytdlp_update()
            if ytdlp_update and on_ytdlp_update:
                on_ytdlp_update()
                
        except Exception as e:
            logger.error(f"Greška pri proveri ažuriranja: {e}")
    
    thread = threading.Thread(target=_check, daemon=True)
    thread.start()
