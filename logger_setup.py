"""
logger_setup.py
===============
Centralni logging sistem za Talas Downloader.
Loguje u fajl i konzolu istovremeno.
"""

import logging
import os
from datetime import datetime


def setup_logger():
    """Kreira i konfiguriše centralni logger."""
    
    # Napravi logs folder ako ne postoji
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Ime log fajla sa datumom
    log_filename = os.path.join(logs_dir, f"talas_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Konfiguracija loggera
    logger = logging.getLogger("TalasDownloader")
    logger.setLevel(logging.DEBUG)
    
    # Format poruke
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    
    # Handler za fajl
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Handler za konzolu
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Dodaj handlere
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger


# Globalni logger
logger = setup_logger()
