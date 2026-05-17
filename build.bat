@echo off
REM build.bat
REM =========
REM Automatski build skript za Talas Downloader
REM Pokreni: build.bat

echo.
echo ====================================
echo   Talas Downloader - Build Skript
echo ====================================
echo.

REM Aktiviraj virtual env
call venv\Scripts\activate

echo [1/4] Proveravam zavisnosti...
pip install -r requirements.txt -q
echo       OK.

echo [2/4] Brisem stari build...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
echo       OK.

echo [3/4] Pokrecem PyInstaller...
pyinstaller talas.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo GRESKA: PyInstaller nije uspeo!
    pause
    exit /b 1
)
echo       Build uspesno kreiran.

echo [4/4] Proveravam build...
if exist "dist\TalasDownloader\TalasDownloader.exe" (
    echo       dist\TalasDownloader\TalasDownloader.exe - OK
) else (
    echo       GRESKA: TalasDownloader.exe nije pronađen!
    pause
    exit /b 1
)

echo.
echo ====================================
echo   Build zavrseno!
echo   Lokacija: dist\TalasDownloader\
echo ====================================
echo.
echo Sledeci korak: otvori setup.iss u Inno Setup
echo i kompajliraj installer.
echo.
pause
