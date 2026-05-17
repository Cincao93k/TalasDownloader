# 🌊 Talas Downloader

Moderna desktop aplikacija za preuzimanje videa i muzike sa interneta.

## Funkcije

- ✅ Download MP3 (muzika)
- ✅ Download MP4 (720p, 1080p, 4K)
- ✅ Thumbnail preview
- ✅ Naslov i trajanje videa
- ✅ Progress bar sa brzinom
- ✅ Izbor foldera
- ✅ Auto update provera
- ✅ Bundlovan FFmpeg
- ✅ Dark moderan UI

## Instalacija za razvoj

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Build .exe

```
build.bat
```

## Napravi installer

1. Instaliraj [Inno Setup](https://jrsoftware.org/isdl.php)
2. Otvori `setup.iss`
3. Kompajliraj (Ctrl+F9)

## Zahtevi

- Windows 10 / 11
- Python 3.11+ (za razvoj)
- FFmpeg (bundlovan u ffmpeg/ folderu)
