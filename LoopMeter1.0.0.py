# -*- coding: utf-8 -*-

import os

import sys



os.environ["QT_ANGLE_PLATFORM"] = "d3d9"

os.environ["QT_MEDIA_BACKEND"] = "windowsmediafoundation"



if sys.platform == "win32":

    f_nul = open(os.devnull, 'w')

    sys.stderr = f_nul

    os.dup2(f_nul.fileno(), 2)



os.environ["QT_LOGGING_RULES"] = "*=false"

os.environ["QT_MULTIMEDIA_PREFERRED_PLUGINS"] = "windowsmediafoundation"



import time

import platform

import gc

import psutil



from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QStackedWidget, QFileDialog, QGraphicsView, QGraphicsScene

from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem

from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QMovie, QBrush, QPixmap

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QRect, QPoint, QSizeF



if platform.system() == "Windows":

    import ctypes

    WIN_SUPPORT = True

else:

    WIN_SUPPORT = False



def set_window_topmost(hwnd, topmost=True):

    if not WIN_SUPPORT or not hwnd:

        return

    HWND_STATE = -1 if topmost else -2

    SWP_FLAGS = 0x0002 | 0x0001 | 0x0010

    ctypes.windll.user32.SetWindowPos(hwnd, HWND_STATE, 0, 0, 0, 0, SWP_FLAGS)



def find_companion_audio(media_path):

    base, _ = os.path.splitext(media_path)

    for ext in [".mp3", ".wav"]:

        audio_path = base + ext

        if os.path.exists(audio_path):

            return audio_path

    return None



THEMES = [

    {

        "name": "NEON CYBER",

        "bg": (10, 15, 30, 250),

        "border": (34, 197, 94, 80),

        "cpu_bar": (34, 197, 94, 255),

        "ram_bar": (59, 130, 246, 255),

        "text_main": (255, 255, 255, 255),

        "accent": (34, 197, 94)

    },

    {

        "name": "DEEP PURPLE",

        "bg": (20, 10, 35, 250),

        "border": (168, 85, 247, 80),

        "cpu_bar": (217, 70, 239, 255),

        "ram_bar": (129, 140, 248, 255),

        "text_main": (255, 255, 255, 255),

        "accent": (217, 70, 239)

    },

    {

        "name": "SOLAR FLARE",

        "bg": (25, 12, 10, 250),

        "border": (239, 68, 68, 80),

        "cpu_bar": (249, 115, 22, 255),

        "ram_bar": (234, 179, 8, 255),

        "text_main": (255, 255, 255, 255),

        "accent": (249, 115, 22)

    }

]



class TelemetryWorker(QThread):

    stats_updated = pyqtSignal(dict)



    def __init__(self):

        super().__init__()

        self.running = True



    def run(self):

        psutil.cpu_percent()

        while self.running:

            try:

                stats = {

                    "cpu": psutil.cpu_percent(interval=None),

                    "ram": psutil.virtual_memory().percent

                }

                self.stats_updated.emit(stats)

                self.msleep(1200)

            except Exception:

                pass



    def stop(self):

        self.running = False



class DragPinWindowHelper:

    def __init__(self, window, name="Window"):

        self.window = window

        self.name = name

        self.drag_start_pos = QPoint()

        self.is_dragging = False

        self.resize_start_global = QPoint()

        self.resize_start_geometry = QRect()

        self.resize_start_time = 0.0

        self.is_resizing = False

        self.is_pinned = True

        self.feedback_text = ""

        self.feedback_expiry = 0.0

        self.hwnd = None



    def resolve_hwnd_and_pin(self):

        if WIN_SUPPORT and not self.hwnd:

            try:

                self.hwnd = int(self.window.winId())

                set_window_topmost(self.hwnd, self.is_pinned)

            except Exception:

                self.hwnd = None



    def handle_press(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self.drag_start_pos = event.globalPosition().toPoint() - self.window.frameGeometry().topLeft()

            self.is_dragging = True

        elif event.button() == Qt.MouseButton.RightButton:

            self.resize_start_global = event.globalPosition().toPoint()

            self.resize_start_geometry = self.window.geometry()

            self.resize_start_time = time.time()

            self.is_resizing = True



    def handle_move(self, event):

        if event.buttons() & Qt.MouseButton.LeftButton and self.is_dragging:

            self.window.move(event.globalPosition().toPoint() - self.drag_start_pos)

        elif event.buttons() & Qt.MouseButton.RightButton and self.is_resizing:

            delta = event.globalPosition().toPoint() - self.resize_start_global

            min_w = 150 if self.name == "MEDIA" else 200

            min_h = 150 if self.name == "MEDIA" else 100

            new_w = max(min_w, self.resize_start_geometry.width() + delta.x())

            new_h = max(min_h, self.resize_start_geometry.height() + delta.y())

            self.window.resize(new_w, new_h)



    def handle_release(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self.is_dragging = False

        elif event.button() == Qt.MouseButton.RightButton:

            self.is_resizing = False

            duration = time.time() - self.resize_start_time

            delta = event.globalPosition().toPoint() - self.resize_start_global

            dist = abs(delta.x()) + abs(delta.y())

            if duration < 0.25 and dist < 6:

                self.toggle_pin_state()



    def toggle_pin_state(self):

        self.is_pinned = not self.is_pinned

        flags = self.window.windowFlags()

        if self.is_pinned:

            flags |= Qt.WindowType.WindowStaysOnTopHint

        else:

            flags &= ~Qt.WindowType.WindowStaysOnTopHint

        self.window.setWindowFlags(flags)

        self.window.show()

        if WIN_SUPPORT:

            try:

                self.hwnd = int(self.window.winId())

                set_window_topmost(self.hwnd, self.is_pinned)

            except Exception:

                self.hwnd = None

        status = "PINNED" if self.is_pinned else "UNPINNED"

        self.feedback_text = f"{self.name}: {status}"

        self.feedback_expiry = time.time() + 1.2

        self.window.update()



    def draw_feedback_if_active(self, painter, w, h, theme):

        if time.time() < self.feedback_expiry:

            painter.setBrush(QColor(0, 0, 0, 220))

            painter.setPen(QPen(QColor(*theme["border"]), 1))

            painter.drawRoundedRect(10, h - 32, w - 20, 24, 4.0, 4.0)

            font = QFont("Arial", 9, QFont.Weight.Bold)

            painter.setFont(font)

            fill_color = QColor(*theme["accent"]) if self.is_pinned else QColor(156, 163, 175)

            painter.setPen(fill_color)

            painter.drawText(18, h - 16, self.feedback_text)



class TelemetryWindow(QWidget):

    def __init__(self, parent_app, stats):

        super().__init__(None)

        self.main_app = parent_app

        self.stats = stats

        self.setGeometry(520, 100, 300, 120)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SubWindow)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.window_manager = DragPinWindowHelper(self, name="STATS")

        self.theme_btn_bounds = QRect()



    def showEvent(self, event):

        super().showEvent(event)

        self.window_manager.resolve_hwnd_and_pin()



    def mousePressEvent(self, event):

        self.window_manager.handle_press(event)

        if event.button() == Qt.MouseButton.LeftButton:

            click_pos = event.position().toPoint()

            if self.theme_btn_bounds.contains(click_pos):

                self.main_app.current_theme_idx = (self.main_app.current_theme_idx + 1) % len(THEMES)

                self.window_manager.feedback_text = f"THEME: {THEMES[self.main_app.current_theme_idx]['name']}"

                self.window_manager.feedback_expiry = time.time() + 1.2

                self.update()

                self.main_app.update()



    def mouseMoveEvent(self, event):

        self.window_manager.handle_move(event)

        self.update()



    def mouseReleaseEvent(self, event):

        self.window_manager.handle_release(event)

        self.update()



    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = THEMES[self.main_app.current_theme_idx]

        w = self.width()

        h = self.height()

        painter.setBrush(QColor(*theme["bg"]))

        painter.setPen(QPen(QColor(*theme["border"]), 2))

        painter.drawRoundedRect(5, 5, w - 10, h - 10, 10.0, 10.0)

        font_title = QFont("Arial", 11, QFont.Weight.Bold)

        font_btn = QFont("Arial", 9, QFont.Weight.Bold)

        self.theme_btn_bounds = QRect(w - 80, 12, 65, 20)

        painter.setBrush(QColor(255, 255, 255, 15))

        painter.setPen(QPen(QColor(*theme["border"]), 1))

        painter.drawRoundedRect(self.theme_btn_bounds, 4.0, 4.0)

        painter.setPen(QColor(*theme["accent"]))

        painter.setFont(font_btn)

        painter.drawText(self.theme_btn_bounds, int(Qt.AlignmentFlag.AlignCenter), "THEME")



        cpu_val = self.stats["cpu"]

        painter.setPen(QColor(*theme["text_main"]))

        painter.setFont(font_title)

        painter.drawText(18, 30, f"CPU  {cpu_val:.0f}%")

        painter.setBrush(QColor(51, 65, 85, 120))

        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawRect(18, 38, w - 36, 8)

        cpu_w = int((w - 36) * (cpu_val / 100.0))

        painter.setBrush(QColor(*theme["cpu_bar"]))

        painter.drawRect(18, 38, cpu_w, 8)



        ram_val = self.stats["ram"]

        ram_y = int(h * 0.48)

        painter.setPen(QColor(*theme["text_main"]))

        painter.setFont(font_title)

        painter.drawText(18, ram_y + 12, f"RAM  {ram_val:.0f}%")

        bar_y = ram_y + 22

        painter.setBrush(QColor(51, 65, 85, 120))

        painter.drawRect(18, bar_y, w - 36, 8)

        ram_w = int((w - 36) * (ram_val / 100.0))

        painter.setBrush(QColor(*theme["ram_bar"]))

        painter.drawRect(18, bar_y, ram_w, 8)

        self.window_manager.draw_feedback_if_active(painter, w, h, theme)



class MediaWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setGeometry(100, 100, 400, 400)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.running = True

        self.file_path = None

        self.current_theme_idx = 0

        self.stats = {"cpu": 0.0, "ram": 0.0}



        self.container = QStackedWidget(self)

        self.gif_label = QLabel()

        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gif_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.gif_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)



        self.scene = QGraphicsScene(self)

        self.graphics_view = QGraphicsView(self.scene, self)

        self.graphics_view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.graphics_view.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self.graphics_view.setStyleSheet("background: transparent; border: none;")

        self.graphics_view.setFrameShape(QGraphicsView.Shape.NoFrame)

        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.video_item = QGraphicsVideoItem()

        self.scene.addItem(self.video_item)



        self.container.addWidget(self.gif_label)

        self.container.addWidget(self.graphics_view)



        self.video_player = QMediaPlayer()

        self.video_audio_output = QAudioOutput()

        self.video_player.setAudioOutput(self.video_audio_output)

        self.video_player.setVideoOutput(self.video_item)

        self.video_player.setLoops(QMediaPlayer.Loops.Infinite)

        self.companion_audio_player = QMediaPlayer()

        self.companion_audio_output = QAudioOutput()

        self.companion_audio_player.setAudioOutput(self.companion_audio_output)

        self.companion_audio_player.setLoops(QMediaPlayer.Loops.Infinite)



        self.video_audio_output.setVolume(0.7)

        self.companion_audio_output.setVolume(0.7)

        self.gif_movie = None

        self.window_manager = DragPinWindowHelper(self, name="MEDIA")



        self.worker = TelemetryWorker()

        self.worker.stats_updated.connect(self.update_stats)

        self.worker.start()



        self.telemetry_window = TelemetryWindow(self, self.stats)

        self.telemetry_window.show()



    def update_stats(self, data):

        self.stats.update(data)

        self.telemetry_window.update()



    def showEvent(self, event):

        super().showEvent(event)

        self.window_manager.resolve_hwnd_and_pin()



    def resizeEvent(self, event):

        self.container.setGeometry(10, 10, self.width() - 20, self.height() - 20)

        self.graphics_view.setGeometry(self.container.rect())

        self.video_item.setSize(QSizeF(self.graphics_view.size()))

        if self.gif_movie:

            self.gif_movie.setScaledSize(self.container.size())

        self.update()



    def mousePressEvent(self, event):

        self.window_manager.handle_press(event)



    def mouseMoveEvent(self, event):

        self.window_manager.handle_move(event)

        self.update()



    def mouseReleaseEvent(self, event):

        self.window_manager.handle_release(event)

        self.update()



    def mouseDoubleClickEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self.load_file_dialog()



    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_Escape:

            self.safe_close()



    def load_file_dialog(self):

        path, _ = QFileDialog.getOpenFileName(

            self, "Open Media", "", "Media Files (*.mp4 *.gif *.avi *.mov *.mkv *.mp3 *.wav)"

        )

        if path:

            self.file_path = path

            self.stop_all_playback()

            companion = find_companion_audio(path)



            if path.lower().endswith('.gif'):

                self.container.setCurrentIndex(0)

                self.gif_movie = QMovie(path)

                self.gif_movie.setCacheMode(QMovie.CacheMode.CacheAll)

                self.gif_movie.setScaledSize(self.container.size())

                self.gif_label.setMovie(self.gif_movie)

                self.gif_movie.start()

                if companion:

                    self.companion_audio_player.setSource(QUrl.fromLocalFile(companion))

                    self.companion_audio_player.play()

            else:

                self.container.setCurrentIndex(1)

                self.video_player.setSource(QUrl.fromLocalFile(path))

                if companion:

                    self.video_audio_output.setMuted(True)

                    self.companion_audio_player.setSource(QUrl.fromLocalFile(companion))

                    self.companion_audio_player.play()

                else:

                    self.video_audio_output.setMuted(False)

                self.video_player.play()



    def stop_all_playback(self):

        self.video_player.stop()

        self.video_player.setSource(QUrl())

        self.companion_audio_player.stop()

        self.companion_audio_player.setSource(QUrl())

        if self.gif_movie:

            self.gif_movie.stop()

            self.gif_label.setMovie(None)

            self.gif_movie.deleteLater()

            self.gif_movie = None

        gc.collect()



    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = THEMES[self.current_theme_idx]

        w = self.width()

        h = self.height()

        

        if not self.file_path:

            painter.setBrush(QColor(*theme["bg"]))

            painter.setPen(QPen(QColor(*theme["border"]), 2))

            painter.drawRoundedRect(10, 10, w - 20, h - 20, 10.0, 10.0)

            cx, cy = w // 2, h // 2

            font_main = QFont("Arial", 12, QFont.Weight.Bold)

            font_sub = QFont("Arial", 10, QFont.Weight.Bold)

            painter.setBrush(QColor(*theme["accent"]))

            painter.setPen(Qt.PenStyle.NoPen)

            painter.drawRect(cx - 25, cy - 35, 50, 30)

            painter.drawPolygon(QPoint(cx - 25, cy - 35), QPoint(cx, cy - 50), QPoint(cx + 25, cy - 35))

            painter.setPen(QColor(255, 255, 255, 240))

            painter.setFont(font_main)

            painter.drawText(QRect(10, cy + 15, w - 20, 25), int(Qt.AlignmentFlag.AlignCenter), "Double-click to Load Media")

            painter.setPen(QColor(156, 163, 175, 200))

            painter.setFont(font_sub)

            painter.drawText(QRect(10, cy + 40, w - 20, 20), int(Qt.AlignmentFlag.AlignCenter), "Right-click to Pin/Resize Window")

            

        if time.time() < self.window_manager.feedback_expiry:

            self.window_manager.draw_feedback_if_active(painter, w, h, theme)



    def closeEvent(self, event):

        self.running = False

        self.stop_all_playback()

        if self.worker:

            self.worker.stop()

            self.worker.wait()

        if self.telemetry_window:

            self.telemetry_window.close()

        event.accept()



    def safe_close(self):

        self.close()



if __name__ == "__main__":

    app = QApplication(sys.argv)

    media_app = MediaWindow()

    media_app.show()

    sys.exit(app.exec()) 

