"""
main.py
=======
Ulazna tačka Talas Downloader aplikacije.
Pokreće aplikaciju, kreira glavne foldere i startuje GUI.
"""

import sys
import os

# ---- Kreiraj potrebne foldere pri prvom pokretanju ----
def create_app_dirs():
    """Kreiraj sve potrebne foldere."""
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    
    for folder in ["cache", "downloads", "temp", "logs", "assets"]:
        os.makedirs(os.path.join(base, folder), exist_ok=True)

create_app_dirs()

# ---- Inicijalizuj logger ----
from logger_setup import logger
logger.info("=" * 50)
logger.info("Talas Downloader se pokreće...")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from gui import TalasMainWindow, DARK_STYLESHEET


def main():
    """Główna funkcija aplikacije."""
    
    # High DPI podrška
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Talas Downloader")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("TalasApp")
    
    # Globalni font
    font = QFont("Segoe UI", 10)
    font.setHintingPreference(QFont.PreferFullHinting)
    app.setFont(font)
    
    # Primeni dark temu
    app.setStyleSheet(DARK_STYLESHEET)
    
    # Kreiraj i prikaži glavni prozor
    window = TalasMainWindow()
    window.show()
    
    logger.info("GUI pokrenut.")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
