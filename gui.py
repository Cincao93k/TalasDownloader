"""
gui.py
======
Kompletan GUI za Talas Downloader.
Koristi PySide6 sa custom dark QSS stilizacijom.
Moderan, minimalistički dizajn.
"""

import os
import sys
import webbrowser

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup,
    QProgressBar, QFileDialog, QFrame, QMessageBox, QScrollArea,
    QSizePolicy, QSpacerItem, QGroupBox
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QObject, QTimer, QSize, QPropertyAnimation,
    QEasingCurve
)
from PySide6.QtGui import (
    QPixmap, QFont, QIcon, QColor, QPalette, QFontDatabase,
    QCursor, QDesktopServices
)

from downloader import fetch_video_info, DownloadWorker, format_duration, clear_cache
from updater import check_all_updates_async
from logger_setup import logger


# ============================================================
# DARK TEMA — QSS stilizacija
# ============================================================
DARK_STYLESHEET = """
/* ==== Globalne postavke ==== */
QMainWindow, QWidget {
    background-color: #0d0d0f;
    color: #e8e8f0;
    font-family: "Segoe UI", sans-serif;
    font-size: 14px;
}

QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollBar:vertical {
    background: #1a1a1f;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #3a3a4a;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ==== Input polje za link ==== */
QLineEdit#urlInput {
    background-color: #16161e;
    border: 2px solid #2a2a3a;
    border-radius: 14px;
    padding: 14px 20px;
    font-size: 15px;
    color: #e8e8f0;
    selection-background-color: #4a90d9;
}
QLineEdit#urlInput:focus {
    border: 2px solid #4a90d9;
}
QLineEdit#urlInput:hover {
    border: 2px solid #3a3a5a;
}

/* ==== Folder input ==== */
QLineEdit#folderInput {
    background-color: #16161e;
    border: 2px solid #2a2a3a;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 13px;
    color: #aaaacc;
}
QLineEdit#folderInput:focus {
    border: 2px solid #3a5a8a;
}

/* ==== Glavni dugmići ==== */
QPushButton#findBtn {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #2a6acd, stop:1 #1a4a9d
    );
    color: #ffffff;
    border: none;
    border-radius: 14px;
    padding: 14px 40px;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.5px;
}
QPushButton#findBtn:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #3a7add, stop:1 #2a5aad
    );
}
QPushButton#findBtn:pressed {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #1a5abd, stop:1 #0a3a8d
    );
}
QPushButton#findBtn:disabled {
    background: #2a2a3a;
    color: #666680;
}

QPushButton#downloadBtn {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #1aad6a, stop:1 #0a8d4a
    );
    color: #ffffff;
    border: none;
    border-radius: 14px;
    padding: 14px 40px;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.5px;
}
QPushButton#downloadBtn:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #2abd7a, stop:1 #1a9d5a
    );
}
QPushButton#downloadBtn:pressed {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #0a9d5a, stop:1 #007d3a
    );
}
QPushButton#downloadBtn:disabled {
    background: #1a2a1f;
    color: #445544;
}

/* ==== Browse dugme ==== */
QPushButton#browseBtn {
    background-color: #1e1e2a;
    color: #aaaacc;
    border: 2px solid #2a2a3a;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 13px;
}
QPushButton#browseBtn:hover {
    background-color: #252535;
    border: 2px solid #3a3a5a;
    color: #ccccee;
}

/* ==== Stop dugme ==== */
QPushButton#stopBtn {
    background-color: #2a1515;
    color: #dd6060;
    border: 2px solid #3a2020;
    border-radius: 10px;
    padding: 8px 20px;
    font-size: 13px;
}
QPushButton#stopBtn:hover {
    background-color: #351a1a;
    border: 2px solid #aa3030;
}

/* ==== Radio button-i ==== */
QRadioButton {
    color: #aaaacc;
    font-size: 14px;
    spacing: 8px;
}
QRadioButton:hover {
    color: #ccccee;
}
QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #3a3a5a;
    background-color: #16161e;
}
QRadioButton::indicator:checked {
    background-color: #4a90d9;
    border: 2px solid #4a90d9;
}
QRadioButton::indicator:hover {
    border: 2px solid #5a5a8a;
}

/* ==== Progress bar ==== */
QProgressBar {
    background-color: #16161e;
    border: none;
    border-radius: 6px;
    height: 8px;
    text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #2a6acd, stop:0.5 #4a90d9, stop:1 #1aad6a
    );
    border-radius: 6px;
}

/* ==== Separator linija ==== */
QFrame#separator {
    background-color: #1e1e2a;
    max-height: 1px;
    border: none;
}

/* ==== Group box ==== */
QGroupBox {
    background-color: #11111a;
    border: 1px solid #1e1e2a;
    border-radius: 14px;
    margin-top: 12px;
    padding: 16px;
    font-size: 12px;
    color: #555570;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    color: #555570;
    font-size: 11px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ==== Tooltip ==== */
QToolTip {
    background-color: #1e1e2a;
    color: #ccccee;
    border: 1px solid #3a3a5a;
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 12px;
}

/* ==== Message box ==== */
QMessageBox {
    background-color: #0d0d0f;
}
QMessageBox QPushButton {
    background-color: #2a2a3a;
    color: #ccccee;
    border: 1px solid #3a3a5a;
    border-radius: 8px;
    padding: 8px 20px;
    min-width: 80px;
}
QMessageBox QPushButton:hover {
    background-color: #353548;
}
"""


# ============================================================
# WORKER KLASE ZA THREAD-SAFE GUI AŽURIRANJA
# ============================================================

class FetchWorker(QObject):
    """Worker za fetchovanje video informacija u pozadini."""
    
    finished = Signal(object)   # VideoInfo objekat
    error = Signal(str)         # Poruka greške
    
    def __init__(self, url: str):
        super().__init__()
        self.url = url
    
    def run(self):
        """Fetchuj video info."""
        try:
            from downloader import fetch_video_info
            info = fetch_video_info(self.url)
            self.finished.emit(info)
        except Exception as e:
            self.error.emit(str(e))


class FetchThread(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            from downloader import fetch_video_info
            info = fetch_video_info(self.url)
            self.finished.emit(info)
        except Exception as e:
            import traceback
            traceback.print_exc()   # ← ovo ispisuje grešku u konzolu
            self.error.emit(str(e))


# ============================================================
# THUMBNAIL WIDGET
# ============================================================

class ThumbnailWidget(QLabel):
    """Widget koji prikazuje thumbnail videa."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(180)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #11111a;
                border: 1px solid #1e1e2a;
                border-radius: 14px;
                color: #333355;
                font-size: 13px;
            }
        """)
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Prikaži placeholder tekst."""
        self.clear()
        self.setText("🎬  Thumbnail će biti prikazan ovde")
    
    def set_thumbnail(self, image_path: str):
        """Postavi thumbnail sliku."""
        if not image_path or not os.path.exists(image_path):
            self._show_placeholder()
            return
        
        try:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                self._show_placeholder()
                return
            
            # Skaliranje uz zadržavanje proporcija
            scaled = pixmap.scaled(
                self.width() - 30, self.height() - 20,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.setPixmap(scaled)
            
        except Exception as e:
            logger.warning(f"Nije moguće prikazati thumbnail: {e}")
            self._show_placeholder()
    
    def clear_thumbnail(self):
        """Obriši thumbnail."""
        self._show_placeholder()


# ============================================================
# GLAVNI PROZOR
# ============================================================

class TalasMainWindow(QMainWindow):
    """
    Glavni prozor Talas Downloader aplikacije.
    Moderan dark dizajn sa svim funkcijama.
    """
    
    # Signali za thread-safe GUI ažuriranja
    _progress_signal = Signal(float, str, str)
    _status_signal = Signal(str)
    _finished_signal = Signal(str)
    _error_signal = Signal(str)
    
    def __init__(self):
        super().__init__()
        
        self.video_info = None
        self.download_worker = None
        self.fetch_thread = None
        
        # Podrazumevani folder za skidanje
        self.download_folder = os.path.expanduser("~/Downloads")
        
        self._setup_window()
        self._build_ui()
        self._connect_signals()
        self._check_updates()
    
    def _setup_window(self):
        """Podesi osnovne parametre prozora."""
        self.setWindowTitle("Talas Downloader")
        self.setMinimumSize(600, 780)
        self.resize(680, 860)
        
        # Centriraj prozor na ekranu
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 680) // 2
        y = (screen.height() - 860) // 2
        self.move(x, y)
        
        # Postavi ikonicu ako postoji
        icon_path = self._get_asset("icon.ico")
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
    
    def _get_asset(self, filename: str) -> str:
        """Vrati putanju do asset fajla."""
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(base_dir, "assets", filename)
    
    def _build_ui(self):
        """Izgradnja kompletnog UI-a."""
        
        # Centralni widget sa scroll
        central = QWidget()
        self.setCentralWidget(central)
        
        # Glavni layout
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area za sadržaj
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(0)
        
        # ---- HEADER ----
        self._build_header(content_layout)
        content_layout.addSpacing(30)
        
        # ---- URL INPUT ----
        self._build_url_section(content_layout)
        content_layout.addSpacing(24)
        
        # ---- FORMAT & QUALITY ----
        self._build_format_quality(content_layout)
        content_layout.addSpacing(24)
        
        # ---- FIND VIDEO DUGME ----
        self._build_find_button(content_layout)
        content_layout.addSpacing(28)
        
        # ---- SEPARATOR ----
        self._add_separator(content_layout)
        content_layout.addSpacing(28)
        
        # ---- THUMBNAIL & VIDEO INFO ----
        self._build_video_info(content_layout)
        content_layout.addSpacing(24)
        
        # ---- SAVE FOLDER ----
        self._build_folder_section(content_layout)
        content_layout.addSpacing(24)
        
        # ---- DOWNLOAD DUGME ----
        self._build_download_button(content_layout)
        content_layout.addSpacing(20)
        
        # ---- PROGRESS ----
        self._build_progress(content_layout)
        content_layout.addSpacing(30)
        
        # Stretch na kraju
        content_layout.addStretch(1)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
    
    def _build_header(self, layout: QVBoxLayout):
        """Zaglavlje sa naslovom i podnaslovom."""
        
        title = QLabel("🌊 Talas Downloader")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #e8e8f8;
                font-size: 32px;
                font-weight: 700;
                letter-spacing: -0.5px;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(title)
        
        layout.addSpacing(6)
        
        subtitle = QLabel("Preuzimaj videe i muziku sa interneta")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #44446a;
                font-size: 13px;
                letter-spacing: 0.5px;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(subtitle)
    
    def _build_url_section(self, layout: QVBoxLayout):
        """Input za URL videa."""
        
        label = QLabel("LINK VIDEA")
        label.setStyleSheet("""
            QLabel {
                color: #444466;
                font-size: 10px;
                letter-spacing: 2px;
                font-weight: 600;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(label)
        layout.addSpacing(8)
        
        self.url_input = QLineEdit()
        self.url_input.setObjectName("urlInput")
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        self.url_input.setMinimumHeight(52)
        layout.addWidget(self.url_input)
    
    def _build_format_quality(self, layout: QVBoxLayout):
        """Format i kvalitet sekcija."""
        
        row_layout = QHBoxLayout()
        row_layout.setSpacing(16)
        
        # Format grupa
        format_group = QGroupBox("FORMAT")
        format_group.setMinimumWidth(160)
        format_layout = QVBoxLayout(format_group)
        format_layout.setSpacing(8)
        
        self.format_group = QButtonGroup()
        
        self.radio_mp3 = QRadioButton("🎵  MP3 (Muzika)")
        self.radio_mp4 = QRadioButton("🎬  MP4 (Video)")
        self.radio_mp3.setChecked(True)
        
        self.format_group.addButton(self.radio_mp3)
        self.format_group.addButton(self.radio_mp4)
        
        format_layout.addWidget(self.radio_mp3)
        format_layout.addWidget(self.radio_mp4)
        
        row_layout.addWidget(format_group)
        
        # Kvalitet grupa
        quality_group = QGroupBox("KVALITET (samo za MP4)")
        quality_layout = QVBoxLayout(quality_group)
        quality_layout.setSpacing(8)
        
        self.quality_group = QButtonGroup()
        
        self.radio_720 = QRadioButton("📺  720p (HD)")
        self.radio_1080 = QRadioButton("🖥️  1080p (Full HD)")
        self.radio_4k = QRadioButton("✨  4K / Najbolji")
        self.radio_720.setChecked(True)
        
        self.quality_group.addButton(self.radio_720)
        self.quality_group.addButton(self.radio_1080)
        self.quality_group.addButton(self.radio_4k)
        
        quality_layout.addWidget(self.radio_720)
        quality_layout.addWidget(self.radio_1080)
        quality_layout.addWidget(self.radio_4k)
        
        row_layout.addWidget(quality_group)
        
        layout.addLayout(row_layout)
        
        # Disable quality kada je MP3 izabran
        self.radio_mp3.toggled.connect(self._on_format_changed)
        self._on_format_changed(True)
    
    def _on_format_changed(self, checked):
        """Onemogući quality radio buttons kada je MP3 izabran."""
        is_mp4 = self.radio_mp4.isChecked()
        for btn in [self.radio_720, self.radio_1080, self.radio_4k]:
            btn.setEnabled(is_mp4)
            btn.setStyleSheet("" if is_mp4 else "QRadioButton { color: #333355; }")
    
    def _build_find_button(self, layout: QVBoxLayout):
        """Find Video dugme."""
        
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        
        self.find_btn = QPushButton("🔍  Pronađi Video")
        self.find_btn.setObjectName("findBtn")
        self.find_btn.setMinimumHeight(52)
        self.find_btn.setMinimumWidth(220)
        self.find_btn.setCursor(QCursor(Qt.PointingHandCursor))
        
        btn_layout.addWidget(self.find_btn)
        layout.addLayout(btn_layout)
    
    def _add_separator(self, layout: QVBoxLayout):
        """Horizontalna linija separator."""
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        layout.addWidget(sep)
    
    def _build_video_info(self, layout: QVBoxLayout):
        """Thumbnail i info o videu."""
        
        label = QLabel("PREGLED VIDEA")
        label.setStyleSheet("""
            QLabel {
                color: #444466;
                font-size: 10px;
                letter-spacing: 2px;
                font-weight: 600;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(label)
        layout.addSpacing(10)
        
        # Thumbnail
        self.thumbnail = ThumbnailWidget()
        layout.addWidget(self.thumbnail)
        layout.addSpacing(12)
        
        # Naslov videa
        self.video_title_label = QLabel("")
        self.video_title_label.setAlignment(Qt.AlignCenter)
        self.video_title_label.setWordWrap(True)
        self.video_title_label.setStyleSheet("""
            QLabel {
                color: #ccccee;
                font-size: 15px;
                font-weight: 600;
                background: transparent;
                border: none;
                padding: 0 10px;
            }
        """)
        layout.addWidget(self.video_title_label)
        
        layout.addSpacing(6)
        
        # Trajanje / info
        self.video_meta_label = QLabel("")
        self.video_meta_label.setAlignment(Qt.AlignCenter)
        self.video_meta_label.setStyleSheet("""
            QLabel {
                color: #44446a;
                font-size: 12px;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.video_meta_label)
    
    def _build_folder_section(self, layout: QVBoxLayout):
        """Sekcija za izbor foldera."""
        
        label = QLabel("SAČUVAJ U")
        label.setStyleSheet("""
            QLabel {
                color: #444466;
                font-size: 10px;
                letter-spacing: 2px;
                font-weight: 600;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(label)
        layout.addSpacing(8)
        
        row = QHBoxLayout()
        row.setSpacing(10)
        
        self.folder_input = QLineEdit()
        self.folder_input.setObjectName("folderInput")
        self.folder_input.setText(self.download_folder)
        self.folder_input.setReadOnly(True)
        self.folder_input.setMinimumHeight(44)
        
        self.browse_btn = QPushButton("📁  Pretraži")
        self.browse_btn.setObjectName("browseBtn")
        self.browse_btn.setMinimumHeight(44)
        self.browse_btn.setMinimumWidth(110)
        self.browse_btn.setCursor(QCursor(Qt.PointingHandCursor))
        
        row.addWidget(self.folder_input)
        row.addWidget(self.browse_btn)
        layout.addLayout(row)
    
    def _build_download_button(self, layout: QVBoxLayout):
        """Download dugme i stop dugme."""
        
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignCenter)
        row.setSpacing(12)
        
        self.download_btn = QPushButton("⬇  Preuzmi")
        self.download_btn.setObjectName("downloadBtn")
        self.download_btn.setMinimumHeight(52)
        self.download_btn.setMinimumWidth(200)
        self.download_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.download_btn.setEnabled(False)
        
        self.stop_btn = QPushButton("⬛  Stop")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setMinimumHeight(52)
        self.stop_btn.setMinimumWidth(100)
        self.stop_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.stop_btn.setVisible(False)
        
        row.addWidget(self.download_btn)
        row.addWidget(self.stop_btn)
        layout.addLayout(row)
    
    def _build_progress(self, layout: QVBoxLayout):
        """Progress bar i status tekst."""
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        layout.addSpacing(12)
        
        # Status tekst i brzina
        status_row = QHBoxLayout()
        
        self.status_label = QLabel("Spreman")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #4a6a9a;
                font-size: 13px;
                background: transparent;
                border: none;
            }
        """)
        
        self.speed_label = QLabel("")
        self.speed_label.setAlignment(Qt.AlignRight)
        self.speed_label.setStyleSheet("""
            QLabel {
                color: #2a3a4a;
                font-size: 12px;
                background: transparent;
                border: none;
            }
        """)
        
        status_row.addWidget(self.status_label)
        status_row.addWidget(self.speed_label)
        layout.addLayout(status_row)
    
    def _connect_signals(self):
        """Poveži sve signale sa slotovima."""
        
        # Dugmići
        self.find_btn.clicked.connect(self._on_find_video)
        self.browse_btn.clicked.connect(self._on_browse_folder)
        self.download_btn.clicked.connect(self._on_download)
        self.stop_btn.clicked.connect(self._on_stop_download)
        
        # URL input — Enter key
        self.url_input.returnPressed.connect(self._on_find_video)
        
        # Format change
        self.radio_mp4.toggled.connect(self._on_format_changed)
        
        # Thread-safe signali
        self._progress_signal.connect(self._update_progress)
        self._status_signal.connect(self._update_status)
        self._finished_signal.connect(self._on_download_finished)
        self._error_signal.connect(self._on_download_error)
    
    def _check_updates(self):
        """Proveri ažuriranja u pozadini pri pokretanju."""
        
        def on_app_update(update_info: dict):
            # Pozovi u GUI thread-u
            QTimer.singleShot(0, lambda: self._show_update_dialog(update_info))
        
        def on_ytdlp_update():
            logger.info("yt-dlp ažuriranje dostupno")
        
        check_all_updates_async(
            on_app_update=on_app_update,
            on_ytdlp_update=on_ytdlp_update
        )
    
    def _show_update_dialog(self, update_info: dict):
        """Prikaži dijaloški okvir za ažuriranje."""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Dostupno ažuriranje 🚀")
        msg.setIcon(QMessageBox.Information)
        msg.setText(
            f"<b>Nova verzija {update_info['version']} je dostupna!</b><br><br>"
            f"Kliknite 'Preuzmi ažuriranje' da preuzmete novu verziju."
        )
        
        download_btn = msg.addButton("⬇  Preuzmi ažuriranje", QMessageBox.AcceptRole)
        msg.addButton("Zatvori", QMessageBox.RejectRole)
        
        msg.exec()
        
        if msg.clickedButton() == download_btn and update_info.get('url'):
            QDesktopServices.openUrl(update_info['url'])
    
    # ============================================================
    # AKCIJE — Find Video
    # ============================================================
    
    def _on_find_video(self):
        """Korisnik kliknuo 'Pronađi Video'."""
        
        url = self.url_input.text().strip()
        
        if not url:
            self._show_error("Unesite link videa.")
            return
        
        if not url.startswith(("http://", "https://")):
            self._show_error("Link mora počinjati sa http:// ili https://")
            return
        
        # Reset UI
        self.video_info = None
        self.thumbnail.clear_thumbnail()
        self.video_title_label.setText("")
        self.video_meta_label.setText("")
        self.download_btn.setEnabled(False)
        
        # Prikaži loading status
        self._set_status("Učitavam video...", "#4a90d9")
        self.find_btn.setEnabled(False)
        self.find_btn.setText("⏳  Učitavam...")
        
        # Pokre fetchovanje u thread-u
        self.fetch_thread = FetchThread(url)
        self.fetch_thread.finished.connect(self._on_fetch_finished)
        self.fetch_thread.error.connect(self._on_fetch_error)
        self.fetch_thread.start()
    
    def _on_fetch_finished(self, video_info):
        """Video info uspešno fetchovan."""
        
        self.video_info = video_info
        
        # Prikaži thumbnail
        if video_info.thumbnail_path:
            self.thumbnail.set_thumbnail(video_info.thumbnail_path)
        
        # Prikaži naslov
        title = video_info.title
        if len(title) > 80:
            title = title[:77] + "..."
        self.video_title_label.setText(title)
        
        # Prikaži trajanje i uploader
        duration_str = format_duration(video_info.duration)
        meta_parts = []
        if duration_str != "Nepoznato":
            meta_parts.append(f"⏱ {duration_str}")
        if video_info.uploader:
            meta_parts.append(f"👤 {video_info.uploader}")
        
        self.video_meta_label.setText("   ".join(meta_parts))
        
        # Enable download
        self.download_btn.setEnabled(True)
        self._set_status("Video pronađen! Spreman za preuzimanje.", "#1aad6a")
        
        # Reset find button
        self.find_btn.setEnabled(True)
        self.find_btn.setText("🔍  Pronađi Video")
    
    def _on_fetch_error(self, error_msg: str):
        """Greška pri fetchovanju video info."""
        
        self.find_btn.setEnabled(True)
        self.find_btn.setText("🔍  Pronađi Video")
        self._set_status(f"Greška: {error_msg[:60]}", "#dd4444")
        self._show_error(error_msg)
    
    # ============================================================
    # AKCIJE — Browse Folder
    # ============================================================
    
    def _on_browse_folder(self):
        """Korisnik bira folder za čuvanje."""
        
        folder = QFileDialog.getExistingDirectory(
            self,
            "Izaberite folder",
            self.download_folder,
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.download_folder = folder
            self.folder_input.setText(folder)
    
    # ============================================================
    # AKCIJE — Download
    # ============================================================
    
    def _on_download(self):
        """Korisnik kliknuo 'Preuzmi'."""
        
        if not self.video_info:
            self._show_error("Najpre pronađite video.")
            return
        
        # Proveri folder
        if not os.path.isdir(self.download_folder):
            try:
                os.makedirs(self.download_folder, exist_ok=True)
            except Exception:
                self._show_error(f"Nije moguće kreirati folder:\n{self.download_folder}")
                return
        
        # Odredi format i kvalitet
        if self.radio_mp3.isChecked():
            fmt = "mp3"
            quality = "best"
        else:
            fmt = "mp4"
            if self.radio_720.isChecked():
                quality = "720p"
            elif self.radio_1080.isChecked():
                quality = "1080p"
            else:
                quality = "4k"
        
        # UI u download mod
        self.download_btn.setEnabled(False)
        self.find_btn.setEnabled(False)
        self.stop_btn.setVisible(True)
        self.progress_bar.setValue(0)
        self._set_status("Priprema preuzimanje...", "#4a90d9")
        
        # Kreiraj i pokrni worker
        self.download_worker = DownloadWorker(
            url=self.video_info.url,
            output_dir=self.download_folder,
            format_type=fmt,
            quality=quality
        )
        
        # Postavi callbacks (pozivaju se iz worker thread-a)
        self.download_worker.on_progress = self._progress_callback
        self.download_worker.on_status = self._status_callback
        self.download_worker.on_finished = self._finished_callback
        self.download_worker.on_error = self._error_callback
        
        self.download_worker.start()
    
    def _on_stop_download(self):
        """Korisnik zaustavio download."""
        
        if self.download_worker:
            self.download_worker.stop()
        
        self._reset_download_ui()
        self._set_status("Download prekinut.", "#dd8844")
    
    # ============================================================
    # CALLBACKS — pozivaju se iz worker thread-a
    # Emituju signale za thread-safe GUI ažuriranje
    # ============================================================
    
    def _progress_callback(self, percent: float, speed: str, eta: str):
        self._progress_signal.emit(percent, speed, eta)
    
    def _status_callback(self, message: str):
        self._status_signal.emit(message)
    
    def _finished_callback(self, filepath: str):
        self._finished_signal.emit(filepath)
    
    def _error_callback(self, message: str):
        self._error_signal.emit(message)
    
    # ============================================================
    # SIGNAL HANDLERS — izvršavaju se u GUI thread-u
    # ============================================================
    
    def _update_progress(self, percent: float, speed: str, eta: str):
        """Ažuriraj progress bar i brzinu."""
        self.progress_bar.setValue(int(percent))
        
        if speed and eta:
            self.speed_label.setText(f"{speed}  •  {eta}")
        elif speed:
            self.speed_label.setText(speed)
    
    def _update_status(self, message: str):
        """Ažuriraj status tekst."""
        self._set_status(message, "#4a90d9")
    
    def _on_download_finished(self, filepath: str):
        """Download završen uspešno."""
        
        self._reset_download_ui()
        self.progress_bar.setValue(100)
        self._set_status("✅  Preuzimanje završeno!", "#1aad6a")
        self.speed_label.setText("")
        
        # Prikaži poruku
        msg = QMessageBox(self)
        msg.setWindowTitle("Završeno! 🎉")
        msg.setIcon(QMessageBox.Information)
        
        if os.path.isfile(filepath):
            filename = os.path.basename(filepath)
            msg.setText(f"<b>Preuzimanje završeno!</b><br><br>📁 {filename}")
        else:
            msg.setText(f"<b>Preuzimanje završeno!</b><br><br>📁 {self.download_folder}")
        
        open_btn = msg.addButton("📂  Otvori folder", QMessageBox.AcceptRole)
        msg.addButton("U redu", QMessageBox.RejectRole)
        msg.exec()
        
        if msg.clickedButton() == open_btn:
            folder = os.path.dirname(filepath) if os.path.isfile(filepath) else filepath
            QDesktopServices.openUrl(f"file:///{folder}")
    
    def _on_download_error(self, message: str):
        """Download greška."""
        
        self._reset_download_ui()
        self._set_status("❌  Greška pri preuzimanju", "#dd4444")
        self.speed_label.setText("")
        self._show_error(message)
    
    # ============================================================
    # POMOĆNE METODE
    # ============================================================
    
    def _reset_download_ui(self):
        """Vrati UI u normalan mod posle download-a."""
        self.download_btn.setEnabled(self.video_info is not None)
        self.find_btn.setEnabled(True)
        self.find_btn.setText("🔍  Pronađi Video")
        self.stop_btn.setVisible(False)
    
    def _set_status(self, text: str, color: str = "#4a6a9a"):
        """Postavi status tekst sa bojom."""
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 13px;
                background: transparent;
                border: none;
            }}
        """)
    
    def _show_error(self, message: str):
        """Prikaži error dijaloški okvir."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Greška")
        msg.setIcon(QMessageBox.Warning)
        msg.setText(f"<b>Greška</b><br><br>{message}")
        msg.addButton("U redu", QMessageBox.AcceptRole)
        msg.exec()
    
    def closeEvent(self, event):
        """Čisti cache i zatvara aplikaciju."""
        
        # Zaustavi aktivni download
        if self.download_worker and self.download_worker.is_alive():
            self.download_worker.stop()
        
        # Zaustavi fetch thread
        if self.fetch_thread and self.fetch_thread.isRunning():
            self.fetch_thread.quit()
            self.fetch_thread.wait(2000)
        
        # Obriši cache
        clear_cache()
        
        logger.info("Aplikacija zatvorena.")
        event.accept()
