import sys
import os
import re
import json
import html
import traceback
import ctypes
import send2trash
from PIL import Image

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QSplitter, QFileDialog,
    QStackedWidget, QScrollArea, QToolBar, QMessageBox,
    QFrame, QPushButton, QSizePolicy, QAbstractItemView,
    QToolButton, QMenu, QGridLayout
)
from PyQt6.QtCore import QPoint
from PyQt6.QtGui import (
    QPixmap, QIcon, QAction, QActionGroup, QDragEnterEvent, QDropEvent,
    QImage, QResizeEvent, QColor, QPainter, QShowEvent,
    QShortcut, QKeySequence, QGuiApplication, QFontMetrics
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer, QSettings


# --- 异常捕获 ---
def exception_hook(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    print(err_msg)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Error")
    msg.setText("An unexpected error occurred.")
    msg.setDetailedText(err_msg)
    msg.exec()


sys.excepthook = exception_hook

VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')


# ==========================================
# --- 🎨 现代原生风格配色 (Modern Native) ---
# ==========================================
class NativeTheme:
    FONT_FAMILY = "'Segoe UI', 'Microsoft YaHei', sans-serif"

    LIGHT = {
        "bg_main": "#f5f3ee",
        "bg_panel": "#ece8df",
        "text_main": "#1f2430",
        "text_sub": "#69707d",
        "accent": "#2c5d8a",
        "border": "#d9d2c6",
        "hover": "#ebe6dd",
        "selected": "#dfe9f2",
        "prompt_bg": "#f3f6f8",
        "neg_bg": "#f7f1f2",
        "code_bg": "#f1ede6"
    }

    DARK = {
        "bg_main": "#16181c",
        "bg_panel": "#1e2228",
        "text_main": "#edf0f4",
        "text_sub": "#9aa3af",
        "accent": "#7aa2c7",
        "border": "#323842",
        "hover": "#262c33",
        "selected": "#273241",
        "prompt_bg": "#202933",
        "neg_bg": "#2a2327",
        "code_bg": "#1b2026"
    }


# --- 多语言字典 ---
TRANSLATIONS = {
    'en': {
        'title': "AI Image Metadata Viewer (Basic) v1.2.0",
        'open_file': "Open Image",
        'open_folder': "Open Folder",
        'clear': "Clear All",
        'back': "Grid View",
        'theme': "Theme",
        'lang_btn': "Language",
        'drag_hint': "Drop images / folders here to view",
        'file_info': "Metadata",
        'model': "Model",
        'positive': "Positive",
        'prompt': "Prompt",
        'negative': "Negative",
        'params': "Generation Settings",
        'parameters_card': "Parameters",
        'copy_btn': "Copy",
        'no_data_desc': "This image does not contain usable generation metadata.",
        'comfy_err': "ComfyUI Parse Error",
        'copied': "Copied!",
        'cleared': "List cleared",
        'lora': "LoRA",
        'delete': "Delete",
        'delete_confirm_title': "Delete Image",
        'delete_confirm_one': "Delete this image from disk?\n{0}",
        'delete_error': "Failed to delete some files.",
        'deleted': "Deleted",
        'sort': "Sort",
        'sort_name': "Name (A-Z)",
        'sort_mtime': "Creation Time (Newest)",
        'loading': "Loading thumbnails...",
        'load_done': "Load complete",
        'refresh': "Refresh folder",
    },
    'cn': {
        'title': "AI \u56fe\u7247\u5143\u6570\u636e\u67e5\u770b\u5668 (\u57fa\u7840\u7248) v1.2.0",
        'open_file': "\u6253\u5f00\u56fe\u7247",
        'open_folder': "\u6253\u5f00\u6587\u4ef6\u5939",
        'clear': "\u6e05\u7a7a\u5217\u8868",
        'back': "\u7f51\u683c\u89c6\u56fe",
        'theme': "\u4e3b\u9898",
        'lang_btn': "\u8bed\u8a00",
        'drag_hint': "\u62d6\u5165\u56fe\u7247 / \u6587\u4ef6\u5939\u67e5\u770b",
        'file_info': "\u5143\u6570\u636e",
        'model': "\u6a21\u578b",
        'positive': "\u6b63\u5411\u63d0\u793a\u8bcd",
        'prompt': "\u63d0\u793a\u8bcd",
        'negative': "\u8d1f\u5411\u63d0\u793a\u8bcd",
        'params': "\u751f\u6210\u8bbe\u7f6e",
        'parameters_card': "\u751f\u6210\u53c2\u6570",
        'copy_btn': "\u590d\u5236",
        'no_data_desc': "\u8fd9\u5f20\u56fe\u7247\u4e0d\u5305\u542b\u53ef\u7528\u7684\u751f\u6210\u5143\u6570\u636e\u3002",
        'comfy_err': "ComfyUI \u89e3\u6790\u9519\u8bef",
        'copied': "\u5df2\u590d\u5236\uff01",
        'cleared': "\u5217\u8868\u5df2\u6e05\u7a7a",
        'lora': "LoRA",
        'delete': "\u5220\u9664",
        'delete_confirm_title': "\u5220\u9664\u56fe\u7247",
        'delete_confirm_one': "\u8981\u4ece\u78c1\u76d8\u5220\u9664\u8fd9\u5f20\u56fe\u7247\u5417\uff1f\n{0}",
        'delete_error': "\u5220\u9664\u90e8\u5206\u6587\u4ef6\u5931\u8d25\u3002",
        'deleted': "\u5df2\u5220\u9664",
        'sort': "\u6392\u5e8f",
        'sort_name': "\u6309\u540d\u79f0",
        'sort_mtime': "\u6309\u521b\u5efa\u65f6\u95f4",
        'loading': "\u6b63\u5728\u52a0\u8f7d\u7f29\u7565\u56fe...",
        'load_done': "\u52a0\u8f7d\u5b8c\u6210",
        'refresh': "\u5237\u65b0\u6587\u4ef6\u5939",
    },
    'tc': {
        'title': "AI \u5716\u7247\u5143\u6578\u64da\u67e5\u770b\u5668 (\u57fa\u790e\u7248) v1.2.0",
        'open_file': "\u6253\u958b\u5716\u7247",
        'open_folder': "\u6253\u958b\u8cc7\u6599\u593e",
        'clear': "\u6e05\u7a7a\u5217\u8868",
        'back': "\u7db2\u683c\u8996\u5716",
        'theme': "\u4e3b\u984c",
        'lang_btn': "\u8a9e\u8a00",
        'drag_hint': "\u62d6\u5165\u5716\u7247 / \u8cc7\u6599\u593e\u67e5\u770b",
        'file_info': "\u5143\u6578\u64da",
        'model': "\u6a21\u578b",
        'positive': "\u6b63\u5411\u63d0\u793a\u8a5e",
        'prompt': "\u63d0\u793a\u8a5e",
        'negative': "\u8ca0\u5411\u63d0\u793a\u8a5e",
        'params': "\u751f\u6210\u8a2d\u5b9a",
        'parameters_card': "\u751f\u6210\u53c3\u6578",
        'copy_btn': "\u8907\u88fd",
        'no_data_desc': "\u9019\u5f35\u5716\u7247\u4e0d\u5305\u542b\u53ef\u7528\u7684\u751f\u6210\u4e2d\u7e7c\u8cc7\u6599\u3002",
        'comfy_err': "ComfyUI \u89e3\u6790\u932f\u8aa4",
        'copied': "\u5df2\u8907\u88fd\uff01",
        'cleared': "\u5217\u8868\u5df2\u6e05\u7a7a",
        'lora': "LoRA",
        'delete': "\u522a\u9664",
        'delete_confirm_title': "\u522a\u9664\u5716\u7247",
        'delete_confirm_one': "\u8981\u5f9e\u78c1\u789f\u522a\u9664\u9019\u5f35\u5716\u7247\u55ce\uff1f\n{0}",
        'delete_error': "\u522a\u9664\u90e8\u5206\u6a94\u6848\u5931\u6557\u3002",
        'deleted': "\u5df2\u522a\u9664",
        'sort': "\u6392\u5e8f",
        'sort_name': "\u6309\u540d\u7a31",
        'sort_mtime': "\u6309\u5efa\u7acb\u6642\u9593",
        'loading': "\u6b63\u5728\u52a0\u8f09\u7e2e\u7565\u5716...",
        'load_done': "\u52a0\u8f09\u5b8c\u6210",
        'refresh': "\u91cd\u65b0\u6574\u7406\u8cc7\u6599\u593e",
    },
    'jp': {
        'title': "AI \u753b\u50cf\u30e1\u30bf\u30c7\u30fc\u30bf\u30d3\u30e5\u30fc\u30a2 (Basic) v1.2.0",
        'open_file': "\u753b\u50cf\u3092\u958b\u304f",
        'open_folder': "\u30d5\u30a9\u30eb\u30c0\u3092\u958b\u304f",
        'clear': "\u30ea\u30b9\u30c8\u3092\u30af\u30ea\u30a2",
        'back': "\u30b0\u30ea\u30c3\u30c9\u8868\u793a",
        'theme': "\u30c6\u30fc\u30de",
        'lang_btn': "\u8a00\u8a9e",
        'drag_hint': "\u3053\u3053\u306b\u753b\u50cf / \u30d5\u30a9\u30eb\u30c0\u3092\u30c9\u30ed\u30c3\u30d7",
        'file_info': "\u30e1\u30bf\u30c7\u30fc\u30bf",
        'model': "\u30e2\u30c7\u30eb",
        'positive': "\u30dd\u30b8\u30c6\u30a3\u30d6\u30d7\u30ed\u30f3\u30d7\u30c8",
        'prompt': "\u30d7\u30ed\u30f3\u30d7\u30c8",
        'negative': "\u30cd\u30ac\u30c6\u30a3\u30d6\u30d7\u30ed\u30f3\u30d7\u30c8",
        'params': "\u751f\u6210\u8a2d\u5b9a",
        'parameters_card': "\u751f\u6210\u30d1\u30e9\u30e1\u30fc\u30bf",
        'copy_btn': "\u30b3\u30d4\u30fc",
        'no_data_desc': "\u3053\u306e\u753b\u50cf\u306b\u306f\u4f7f\u7528\u53ef\u80fd\u306a\u751f\u6210\u30e1\u30bf\u30c7\u30fc\u30bf\u304c\u542b\u307e\u308c\u3066\u3044\u307e\u305b\u3093\u3002",
        'comfy_err': "ComfyUI \u89e3\u6790\u30a8\u30e9\u30fc",
        'copied': "\u30b3\u30d4\u30fc\u3057\u307e\u3057\u305f\uff01",
        'cleared': "\u30ea\u30b9\u30c8\u3092\u30af\u30ea\u30a2\u3057\u307e\u3057\u305f",
        'lora': "LoRA",
        'delete': "\u524a\u9664",
        'delete_confirm_title': "\u753b\u50cf\u306e\u524a\u9664",
        'delete_confirm_one': "\u3053\u306e\u753b\u50cf\u3092\u30c7\u30a3\u30b9\u30af\u304b\u3089\u524a\u9664\u3057\u307e\u3059\u304b\uff1f\n{0}",
        'delete_error': "\u4e00\u90e8\u306e\u30d5\u30a1\u30a4\u30eb\u524a\u9664\u306b\u5931\u6557\u3057\u307e\u3057\u305f\u3002",
        'deleted': "\u524a\u9664\u3057\u307e\u3057\u305f",
        'sort': "\u4e26\u3073\u66ff\u3048",
        'sort_name': "\u540d\u524d\u9806",
        'sort_mtime': "\u4f5c\u6210\u65e5\u6642\uff08\u65b0\u3057\u3044\u9806\uff09",
        'loading': "\u30b5\u30e0\u30cd\u30a4\u30eb\u3092\u8aad\u307f\u8fbc\u307f\u4e2d...",
        'load_done': "\u8aad\u307f\u8fbc\u307f\u5b8c\u4e86",
        'refresh': "\u30d5\u30a9\u30eb\u30c0\u3092\u66f4\u65b0",
    },
    'kr': {
        'title': "AI \uc774\ubbf8\uc9c0 \uba54\ud0c0\ub370\uc774\ud130 \ubdf0\uc5b4 (Basic) v1.2.0",
        'open_file': "\uc774\ubbf8\uc9c0 \uc5f4\uae30",
        'open_folder': "\ud3f4\ub354 \uc5f4\uae30",
        'clear': "\ubaa9\ub85d \uc9c0\uc6b0\uae30",
        'back': "\uadf8\ub9ac\ub4dc \ubcf4\uae30",
        'theme': "\ud14c\ub9c8",
        'lang_btn': "\uc5b8\uc5b4",
        'drag_hint': "\uc774\ubbf8\uc9c0 / \ud3f4\ub354\ub97c \uc5ec\uae30\uc5d0 \ub4dc\ub86d\ud558\uc138\uc694",
        'file_info': "\uba54\ud0c0\ub370\uc774\ud130",
        'model': "\ubaa8\ub378",
        'positive': "\uae0d\uc815 \ud504\ub86c\ud504\ud2b8",
        'prompt': "\ud504\ub86c\ud504\ud2b8",
        'negative': "\ubd80\uc815 \ud504\ub86c\ud504\ud2b8",
        'params': "\uc0dd\uc131 \uc124\uc815",
        'parameters_card': "\uc0dd\uc131 \ud30c\ub77c\ubbf8\ud130",
        'copy_btn': "\ubcf5\uc0ac",
        'no_data_desc': "\uc774 \uc774\ubbf8\uc9c0\uc5d0\ub294 \uc0ac\uc6a9\ud560 \uc218 \uc788\ub294 \uc0dd\uc131 \uba54\ud0c0\ub370\uc774\ud130\uac00 \ud3ec\ud568\ub418\uc5b4 \uc788\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.",
        'comfy_err': "ComfyUI \ud30c\uc2f1 \uc624\ub958",
        'copied': "\ubcf5\uc0ac\ub418\uc5c8\uc2b5\ub2c8\ub2e4!",
        'cleared': "\ubaa9\ub85d\uc774 \uc9c0\uc6cc\uc84c\uc2b5\ub2c8\ub2e4",
        'lora': "LoRA",
        'delete': "\uc0ad\uc81c",
        'delete_confirm_title': "\uc774\ubbf8\uc9c0 \uc0ad\uc81c",
        'delete_confirm_one': "\uc774 \uc774\ubbf8\uc9c0\ub97c \ub514\uc2a4\ud06c\uc5d0\uc11c \uc0ad\uc81c\ud560\uae4c\uc694?\n{0}",
        'delete_error': "\uc77c\ubd80 \ud30c\uc77c \uc0ad\uc81c\uc5d0 \uc2e4\ud328\ud588\uc2b5\ub2c8\ub2e4.",
        'deleted': "\uc0ad\uc81c\ub428",
        'sort': "\uc815\ub82c",
        'sort_name': "\uc774\ub984\uc21c",
        'sort_mtime': "\uc0dd\uc131 \uc2dc\uac04(\ucd5c\uc2e0\uc21c)",
        'loading': "\uc378\ub124\uc77c \ub85c\ub529 \uc911...",
        'load_done': "\ub85c\ub529 \uc644\ub8cc",
        'refresh': "\ud3f4\ub354 \uc0c8\ub85c\uace0\uce68",
    },
}

def create_glyph_icon(glyph: str, color: str, size: int = 18) -> QIcon:
    if QGuiApplication.instance() is None:
        return QIcon()

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    font = painter.font()
    font.setFamily("Segoe UI Symbol")
    font.setBold(True)
    font.setPixelSize(max(1, int(size * 1.55)))
    painter.setFont(font)

    metrics = QFontMetrics(font)
    rect = metrics.tightBoundingRect(glyph)
    if rect.isNull():
        rect = metrics.boundingRect(glyph)

    target = size * 0.88
    if rect.width() > 0 and rect.height() > 0:
        scale = min(target / rect.width(), target / rect.height())
        font.setPixelSize(max(1, int(font.pixelSize() * scale)))
        painter.setFont(font)
        metrics = QFontMetrics(font)
        rect = metrics.tightBoundingRect(glyph)
        if rect.isNull():
            rect = metrics.boundingRect(glyph)

    painter.setPen(QColor(color))
    x = (size - rect.width()) / 2 - rect.left()
    y = (size + rect.height()) / 2 - rect.bottom()
    if glyph == "↻":
        y += size * 0.01
    painter.drawText(int(x), int(y), glyph)
    painter.end()
    return QIcon(pixmap)

def create_emoji_icon(emoji_char, size=64, color: str | None = None):
    """Generate an emoji toolbar icon; matches the stable main.py behavior."""
    if QGuiApplication.instance() is None:
        return QIcon()

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    font = painter.font()
    font.setFamily("Segoe UI Emoji")
    font.setPixelSize(int(size * 0.6))
    painter.setFont(font)
    if color:
        painter.setPen(QColor(color))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji_char)
    painter.end()
    return QIcon(pixmap)


def pil2pixmap(pil_image):
    if pil_image.mode == "RGB":
        pil_image = pil_image.convert("RGBA")
    elif pil_image.mode == "L":
        pil_image = pil_image.convert("RGBA")
    if pil_image.mode != "RGBA":
        pil_image = pil_image.convert("RGBA")
    r, g, b, a = pil_image.split()
    im_rgba = Image.merge("RGBA", (r, g, b, a))
    data = im_rgba.tobytes("raw", "RGBA")
    qim = QImage(data, im_rgba.size[0], im_rgba.size[1], QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(qim)


class ThumbnailLoader(QThread):
    thumbnail_loaded = pyqtSignal(str, QPixmap)

    def __init__(self, file_list):
        super().__init__()
        self.file_list = file_list
        self.running = True
        self.request_id = 0


    def run(self):
        for full_path in self.file_list:
            if not self.running:
                break
            try:
                with Image.open(full_path) as img:
                    img.thumbnail((240, 240), Image.Resampling.LANCZOS)
                    self.thumbnail_loaded.emit(full_path, pil2pixmap(img))
            except:
                continue

    def stop(self):
        self.running = False
        self.wait()


class GridListWidget(QListWidget):
    """网格视图用的列表，自定义滚轮步长：每次滚轮滚动两行"""
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta == 0:
            return

        # 一行的高度：gridSize 高度 + 间距
        row_height = self.gridSize().height() + self.spacing()
        # 每个 step（120）滚动 2 行
        steps = delta / 120.0
        pixels = int(-steps * 2 * row_height)   # 向上滚时 delta>0，要减小 scroll value

        bar = self.verticalScrollBar()
        bar.setValue(bar.value() + pixels)
        event.accept()


# --- 自定义滚轮行为的图片滚动区域：在图片区域用滚轮切图 ---
class ImageScrollArea(QScrollArea):
    def __init__(self, owner=None, parent=None):
        super().__init__(parent)
        self.owner = owner  # MainWindow

    def wheelEvent(self, event):
        if self.owner and self.owner.stacked_widget.currentIndex() == 1:
            delta = event.angleDelta().y()
            if delta > 0:
                self.owner.show_prev_image()
            elif delta < 0:
                self.owner.show_next_image()
            event.accept()
        else:
            super().wheelEvent(event)


class PromptTextBox(QFrame):
    def __init__(self, object_name: str, parent=None):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        layout = QVBoxLayout(self)
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(0)

        self.label = QLabel("", self)
        self.label.setObjectName("prompt_text_label")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label.setTextFormat(Qt.TextFormat.RichText)
        self.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.label.setMinimumWidth(0)
        layout.addWidget(self.label)

    def set_text(self, text: str):
        escaped = html.escape(text or "").replace("\n", "<br>")
        self.label.setText(f"<div style='text-align:justify; line-height:1.55;'>{escaped}</div>")
        self.updateGeometry()


class MetadataCard(QFrame):
    def __init__(self, title: str = "", action_text: str | None = None, action_callback=None, parent=None):
        super().__init__(parent)
        self.setObjectName("metadata_card")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        root = QVBoxLayout(self)
        root.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        root.setContentsMargins(6, 8, 6, 8)
        root.setSpacing(10)

        self.header = QWidget(self)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        self.title_label = QLabel(title, self.header)
        self.title_label.setObjectName("card_title")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)

        self.action_button = None
        if action_text is not None:
            self.action_button = QPushButton(action_text, self.header)
            self.action_button.setObjectName("card_action_btn")
            self.action_button.setCursor(Qt.CursorShape.PointingHandCursor)
            if action_callback:
                self.action_button.clicked.connect(action_callback)
            header_layout.addWidget(self.action_button)

        root.addWidget(self.header)

        self.body = QWidget(self)
        self.body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(10)
        root.addWidget(self.body)

    def set_title(self, title: str):
        self.title_label.setText(title)

    def set_action_text(self, text: str):
        if self.action_button:
            self.action_button.setText(text)

    def clear_body(self):
        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            widget = item.widget()
            layout = item.layout()
            if widget:
                widget.deleteLater()
            elif layout:
                while layout.count():
                    child = layout.takeAt(0)
                    child_widget = child.widget()
                    if child_widget:
                        child_widget.deleteLater()


class SummaryCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("summary_card")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        layout = QVBoxLayout(self)
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        layout.setContentsMargins(6, 8, 6, 8)
        layout.setSpacing(10)

        self.filename_label = QLabel("", self)
        self.filename_label.setObjectName("summary_filename")
        self.filename_label.setWordWrap(True)
        layout.addWidget(self.filename_label)

        meta_row = QWidget(self)
        meta_layout = QHBoxLayout(meta_row)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(8)

        self.resolution_label = QLabel("", meta_row)
        self.resolution_label.setObjectName("summary_pill")
        meta_layout.addWidget(self.resolution_label)

        self.index_label = QLabel("", meta_row)
        self.index_label.setObjectName("summary_pill")
        meta_layout.addWidget(self.index_label)
        meta_layout.addStretch(1)
        layout.addWidget(meta_row)

    def set_summary(self, filename: str, resolution: str, index_text: str):
        self.filename_label.setText(filename or "")
        self.resolution_label.setVisible(bool(resolution))
        self.index_label.setVisible(bool(index_text))
        self.resolution_label.setText(resolution or "")
        self.index_label.setText(index_text or "")

    def clear_summary(self):
        self.filename_label.clear()
        self.resolution_label.clear()
        self.index_label.clear()


class InfoRow(QFrame):
    def __init__(self, key: str, value: str, parent=None):
        super().__init__(parent)
        self.setObjectName("info_row")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        key_label = QLabel(key, self)
        key_label.setObjectName("info_row_key")
        layout.addWidget(key_label)

        value_label = QLabel(value, self)
        value_label.setObjectName("info_row_value")
        value_label.setWordWrap(True)
        value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(value_label)


class MetricChip(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("metric_chip")
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)


class TextListCard(MetadataCard):
    def set_lines(self, lines, placeholder: str = ""):
        self.clear_body()
        if not lines:
            if placeholder:
                label = QLabel(placeholder, self.body)
                label.setObjectName("empty_label")
                label.setWordWrap(True)
                self.body_layout.addWidget(label)
            return

        for line in lines:
            text = str(line).strip()
            if not text:
                continue
            key, sep, value = text.partition(":")
            if sep and value.strip():
                self.body_layout.addWidget(InfoRow(key.strip(), value.strip(), self.body))
            else:
                label = QLabel(text, self.body)
                label.setObjectName("content_block")
                label.setWordWrap(True)
                label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                self.body_layout.addWidget(label)


class TagChip(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("tag_chip")
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)


class LoraItem(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setObjectName("lora_item")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        parts = [part.strip() for part in str(text).split("|") if part.strip()]
        title = parts[0] if parts else str(text).strip()

        title_label = QLabel(title, self)
        title_label.setObjectName("lora_name")
        title_label.setWordWrap(True)
        title_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(title_label)

        metrics = []
        for part in parts[1:]:
            key, sep, value = part.partition(":")
            if sep and value.strip():
                metrics.append(f"{key.strip()}: {value.strip()}")
            elif part:
                metrics.append(part)

        if metrics:
            metric_row = QWidget(self)
            metric_layout = QHBoxLayout(metric_row)
            metric_layout.setContentsMargins(0, 0, 0, 0)
            metric_layout.setSpacing(8)
            for metric in metrics:
                metric_layout.addWidget(MetricChip(metric, metric_row))
            metric_layout.addStretch(1)
            layout.addWidget(metric_row)


class LoraCard(MetadataCard):
    def set_loras(self, loras):
        self.clear_body()
        for item in loras or []:
            self.body_layout.addWidget(LoraItem(str(item), self.body))


class PromptCard(MetadataCard):
    def __init__(self, title: str, copy_text: str, copy_callback, object_name: str, parent=None):
        super().__init__(title, action_text="Copy", action_callback=self.copy_content, parent=parent)
        self.editor = PromptTextBox(object_name, self.body)
        self.body_layout.addWidget(self.editor)
        self._copy_callback = copy_callback
        self._content = copy_text

    def copy_content(self):
        if self._copy_callback and self._content:
            self._copy_callback(self._content)

    def set_text(self, text: str):
        self._content = text or ""
        self.editor.set_text(self._content)
        if self.action_button:
            self.action_button.setEnabled(bool(self._content.strip()))


class KeyValueItem(QFrame):
    def __init__(self, key: str, value: str, parent=None):
        super().__init__(parent)
        self.setObjectName("kv_item")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        key_label = QLabel(key, self)
        key_label.setObjectName("kv_key")
        key_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(key_label)

        value_label = QLabel(value, self)
        value_label.setObjectName("kv_value")
        value_label.setWordWrap(True)
        value_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(value_label, 1)


class ParametersCard(MetadataCard):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent=parent)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_widget = QWidget(self.body)
        self.grid_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.grid = QGridLayout(self.grid_widget)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setHorizontalSpacing(10)
        self.grid.setVerticalSpacing(10)
        self.body_layout.addWidget(self.grid_widget)
        self._pairs = []
        self._current_cols = 2

    def _calc_cols(self):
        return 2

    def set_pairs(self, pairs):
        self._pairs = list(pairs or [])
        self._rebuild_grid(force=True)

    def _rebuild_grid(self, force=False):
        cols = self._calc_cols()
        if not force and cols == self._current_cols:
            return
        self._current_cols = cols

        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for col in range(2):
            self.grid.setColumnStretch(col, 0)
        for col in range(cols):
            self.grid.setColumnStretch(col, 1)

        row = 0
        col = 0
        row_heights = {}
        for key, value in self._pairs:
            item = KeyValueItem(str(key), str(value), self.grid_widget)
            hint_h = item.sizeHint().height()
            key_lower = str(key).strip().lower()
            if key_lower in ('details', 'raw', 'raw parameters'):
                if col != 0:
                    row += 1
                    col = 0
                self.grid.addWidget(item, row, 0, 1, cols)
                row_heights[row] = max(row_heights.get(row, 0), hint_h)
                row += 1
                continue

            self.grid.addWidget(item, row, col)
            row_heights[row] = max(row_heights.get(row, 0), hint_h)
            col += 1
            if col >= cols:
                col = 0
                row += 1

        row_count = row + (1 if col != 0 else 0)
        if row_count <= 0:
            min_height = 0
        else:
            content_height = sum(row_heights.get(i, 0) for i in range(row_count))
            min_height = content_height + max(0, row_count - 1) * self.grid.verticalSpacing()

        self.grid_widget.setMinimumHeight(min_height)
        self.body.setMinimumHeight(min_height)
        self.grid.invalidate()
        self.body_layout.invalidate()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._pairs and self._calc_cols() != self._current_cols:
            self._rebuild_grid(force=True)


class MessageCard(MetadataCard):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent=parent)
        self.message_label = QLabel("", self.body)
        self.message_label.setObjectName("empty_label")
        self.message_label.setWordWrap(True)
        self.body_layout.addWidget(self.message_label)

    def set_message(self, text: str):
        self.message_label.setText(text or "")


class MetadataPanel(QWidget):
    def __init__(self, translator, copy_callback, parent=None):
        super().__init__(parent)
        self.setObjectName("metadata_panel_root")
        self._tr = translator

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(12)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.summary_card = SummaryCard(self)
        self.model_card = TextListCard(parent=self)
        self.lora_card = LoraCard(parent=self)
        self.positive_card = PromptCard("", "", copy_callback, "prompt_view_positive", parent=self)
        self.negative_card = PromptCard("", "", copy_callback, "prompt_view_negative", parent=self)
        self.parameters_card = ParametersCard("", parent=self)
        self.empty_card = MessageCard("", parent=self)

        for card in (
            self.summary_card,
            self.positive_card,
            self.negative_card,
            self.model_card,
            self.lora_card,
            self.parameters_card,
            self.empty_card,
        ):
            self.layout.addWidget(card)

        self.retranslate(translator)
        self.clear_metadata()

    def retranslate(self, translator):
        self._tr = translator
        positive_title = self._tr('positive')
        if positive_title == 'positive':
            positive_title = self._tr('prompt')

        parameters_title = self._tr('parameters_card')
        if parameters_title == 'parameters_card':
            parameters_title = self._tr('params')

        self.model_card.set_title(self._tr('model'))
        self.lora_card.set_title(self._tr('lora'))
        self.positive_card.set_title(positive_title)
        self.negative_card.set_title(self._tr('negative'))
        self.parameters_card.set_title(parameters_title)
        self.empty_card.set_title(self._tr('file_info'))
        self.positive_card.set_action_text(self._tr('copy_btn'))
        self.negative_card.set_action_text(self._tr('copy_btn'))

    def clear_metadata(self):
        self.summary_card.clear_summary()
        for card in (self.model_card, self.lora_card, self.positive_card, self.negative_card, self.parameters_card, self.empty_card):
            card.hide()
            if isinstance(card, (TextListCard, LoraCard)):
                card.clear_body()
            elif isinstance(card, PromptCard):
                card.set_text("")
            elif isinstance(card, ParametersCard):
                card.set_pairs([])
            elif isinstance(card, MessageCard):
                card.set_message("")

    def set_metadata(self, data: dict):
        summary = data.get('summary', {})
        self.summary_card.set_summary(
            summary.get('filename', ''),
            summary.get('resolution', ''),
            summary.get('index_text', ''),
        )

        models = data.get('models', [])
        loras = data.get('loras', [])
        positive = data.get('positive', '')
        negative = data.get('negative', '')
        parameters = data.get('parameters', [])
        empty_message = data.get('empty_message', '')

        self.model_card.setVisible(bool(models))
        if models:
            self.model_card.set_lines(models)

        self.lora_card.setVisible(bool(loras))
        if loras:
            self.lora_card.set_loras(loras)

        self.positive_card.setVisible(bool(positive))
        self.positive_card.set_text(positive)

        self.negative_card.setVisible(bool(negative))
        self.negative_card.set_text(negative)

        self.parameters_card.setVisible(bool(parameters))
        if parameters:
            self.parameters_card.set_pairs(parameters)

        has_metadata = any((models, loras, positive, negative, parameters))
        self.empty_card.setVisible(not has_metadata and bool(empty_message))
        if not has_metadata:
            self.empty_card.set_message(empty_message)

    def apply_theme(self, t, dark_mode: bool):
        panel_bg = '#ebe5da' if not dark_mode else '#191d23'
        card_bg = '#f9f6f0' if not dark_mode else '#242a32'
        summary_bg = '#fcfaf5' if not dark_mode else '#2a313a'
        chip_bg = '#f2ece3' if not dark_mode else '#2b313a'
        chip_edge = '#d7cec1' if not dark_mode else '#3a4450'
        prompt_bg = '#f2f5f6' if not dark_mode else '#222b35'
        negative_bg = '#f5eeef' if not dark_mode else '#2c252a'
        button_bg = '#e2eaf0' if not dark_mode else '#2b3745'
        button_hover = '#d2dfe9' if not dark_mode else '#36485b'
        divider = '#d5ccbe' if not dark_mode else '#3a4450'
        strong_divider = '#c9bda9' if not dark_mode else '#495463'
        muted_fill = '#f6f2ea' if not dark_mode else '#20262d'

        self.setStyleSheet(f"""
            QWidget#metadata_panel_root {{
                background-color: {panel_bg};
            }}
            QWidget#metadata_panel_root, QWidget#metadata_panel_root * {{
                font-family: {NativeTheme.FONT_FAMILY};
            }}
            QWidget#metadata_panel_root QWidget {{
                background-color: transparent;
            }}
            QFrame#summary_card, QFrame#metadata_card {{
                background-color: transparent;
                border: none;
                border-radius: 0px;
            }}
            QFrame#summary_card {{
                background-color: transparent;
            }}
            QLabel#summary_filename {{
                color: {t['text_main']};
                font-size: 18px;
                font-weight: 700;
            }}
            QLabel#summary_pill {{
                background-color: {muted_fill};
                color: {t['text_sub']};
                border: 1px solid {chip_edge};
                border-radius: 11px;
                padding: 5px 10px;
                font-size: 12px;
                font-weight: 600;
            }}
            QLabel#card_title {{
                color: {t['text_main']};
                font-size: 15px;
                font-weight: 700;
            }}
            QLabel#content_label {{
                color: {t['text_main']};
                font-size: 13px;
                font-weight: 500;
            }}
            QLabel#content_block {{
                background-color: {muted_fill};
                color: {t['text_main']};
                border: 1px solid {chip_edge};
                border-radius: 12px;
                padding: 10px 12px;
                font-size: 13px;
                font-weight: 500;
            }}
            QFrame#info_row, QFrame#lora_item {{
                background-color: {chip_bg};
                border: 1px solid {chip_edge};
                border-radius: 12px;
            }}
            QLabel#info_row_key {{
                color: {t['text_sub']};
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            QLabel#info_row_value, QLabel#lora_name {{
                color: {t['text_main']};
                font-size: 13px;
                font-weight: 600;
            }}
            QLabel#metric_chip {{
                background-color: {button_bg};
                color: {t['text_sub']};
                border: 1px solid {chip_edge};
                border-radius: 10px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 600;
            }}
            QLabel#empty_label {{
                color: {t['text_sub']};
                font-size: 13px;
                font-weight: 400;
            }}
            QPushButton#card_action_btn {{
                background-color: {button_bg};
                color: {t['accent']};
                border: 1px solid {chip_edge};
                border-radius: 11px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton#card_action_btn:hover {{
                background-color: {button_hover};
            }}
            QPushButton#card_action_btn:disabled {{
                color: {t['text_sub']};
                background-color: {t['hover']};
            }}
            QLabel#tag_chip {{
                background-color: {chip_bg};
                color: {t['text_main']};
                border: 1px solid {chip_edge};
                border-radius: 11px;
                padding: 8px 10px;
                font-size: 13px;
                font-weight: 500;
            }}
            QFrame#prompt_view_positive, QFrame#prompt_view_negative {{
                border: 1px solid {chip_edge};
                border-radius: 13px;
                background-color: {prompt_bg};
            }}
            QFrame#prompt_view_negative {{
                background-color: {negative_bg};
            }}
            QLabel#prompt_text_label {{
                color: {t['text_main']};
                font-size: 13px;
                font-weight: 500;
                background: transparent;
                selection-background-color: {t['accent']};
            }}
            QFrame#kv_item {{
                background-color: {chip_bg};
                border: 1px solid {chip_edge};
                border-radius: 13px;
            }}
            QLabel#kv_key {{
                color: {t['text_sub']};
                font-size: 12px;
                font-weight: 600;
                min-width: 58px;
            }}
            QLabel#kv_value {{
                color: {t['text_main']};
                font-size: 13px;
                font-weight: 600;
            }}
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("AI_Tools", "AI_ImageViewer_Basic")
        self.lang = self.settings.value("language", "en", type=str)
        self.dark_mode = self.settings.value("theme", True, type=bool)
        self.sort_mode = self.settings.value("sort_mode", "name_natural", type=str)

        self.setWindowTitle("AI Image Metadata Viewer (Basic) v1.2.0")
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self._initial_geometry_applied = False
        self.setAcceptDrops(True)

        self.loader_thread = None
        self._loading_request_id = 0
        self._loading_in_progress = False
        self._pending_restore_path = None
        self._pending_restore_selected_paths = []
        self.current_image_path = None
        self.current_loaded_folder = None
        self.current_file_list = []
        self.current_index = -1
        self.current_pos_text = ""
        self.current_neg_text = ""

        self.grid_item_height = 260
        self.grid_item_min_width = 220

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setup_toolbar()
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        self.setup_grid_view()
        self.setup_detail_view()
        self.setup_toast()

        self.apply_style()
        self.update_ui_text()
        self.setup_shortcuts()


    def _target_screen_geometry(self):
        screen = self.screen() or QApplication.primaryScreen()
        if screen is None:
            return None
        return screen.availableGeometry()

    def apply_initial_window_geometry(self, force: bool = False):
        if self._initial_geometry_applied and not force:
            return

        available = self._target_screen_geometry()
        if available is None:
            return

        horizontal_margin = max(24, int(available.width() * 0.035))
        vertical_margin = max(24, int(available.height() * 0.05))

        max_w = max(720, available.width() - horizontal_margin * 2)
        max_h = max(560, available.height() - vertical_margin * 2)
        target_w = min(max(int(available.width() * 0.82), 1180), max_w)
        target_h = min(max(int(available.height() * 0.80), 780), max_h)
        target_w = min(max_w, max(900, target_w))
        target_h = min(max_h, max(680, target_h))

        x = available.x() + (available.width() - target_w) // 2
        y = available.y() + (available.height() - target_h) // 2
        self.setGeometry(x, y, target_w, target_h)
        self._initial_geometry_applied = True

    def center_on_available_screen(self):
        available = self._target_screen_geometry()
        if available is None:
            return

        frame = self.frameGeometry()
        frame.moveCenter(available.center())
        top_left = frame.topLeft()

        min_x = available.left()
        max_x = available.right() - frame.width() + 1
        min_y = available.top()
        max_y = available.bottom() - frame.height() + 1

        if max_x < min_x:
            max_x = min_x
        if max_y < min_y:
            max_y = min_y

        top_left.setX(max(min_x, min(top_left.x(), max_x)))
        top_left.setY(max(min_y, min(top_left.y(), max_y)))
        self.move(top_left)

    def showEvent(self, event: QShowEvent):
        super().showEvent(event)
        if self._initial_geometry_applied:
            QTimer.singleShot(0, self.center_on_available_screen)

    # ---------- Toast ----------
    def setup_toast(self):
        self.toast_label = QLabel(self)
        self.toast_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.toast_label.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(40, 40, 40, 0.9);
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-family: {NativeTheme.FONT_FAMILY};
                font-size: 14px;
                font-weight: 500;
            }}
        """)
        self.toast_label.hide()
        self.toast_timer = QTimer(self)
        self.toast_timer.setSingleShot(True)
        self.toast_timer.timeout.connect(self.toast_label.hide)

    def show_toast(self, message, duration=2000):
        self.toast_label.setText(message)
        self.toast_label.adjustSize()
        x = (self.width() - self.toast_label.width()) // 2
        y = self.height() - 100
        self.toast_label.move(x, y)
        self.toast_label.show()
        self.toast_label.raise_()
        self.toast_timer.stop()
        if duration > 0:
            self.toast_timer.start(duration)

    # ---------- i18n ----------
    def tr(self, key):
        return TRANSLATIONS[self.lang].get(key, key)

    # ---------- Toolbar ----------
    def setup_toolbar(self):
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(20, 20))
        self.toolbar.setMovable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(self.toolbar)

        self.action_file = QAction(self.tr('open_file'), self)
        self.action_file.setIcon(create_emoji_icon("📄"))
        self.action_file.triggered.connect(self.open_files_dialog)

        self.action_folder = QAction(self.tr('open_folder'), self)
        self.action_folder.setIcon(create_emoji_icon("📂"))
        self.action_folder.triggered.connect(self.open_folder_dialog)

        self.back_action = QAction(self.tr('back'), self)
        self.back_action.setIcon(create_emoji_icon("🔙"))
        self.back_action.triggered.connect(self.show_grid)
        self.back_action.setEnabled(False)
        self.toolbar.addAction(self.back_action)

        self.action_delete = QAction(self.tr('delete'), self)
        self.action_delete.setIcon(create_emoji_icon("🗑", color="#ff4d4f"))
        self.action_delete.triggered.connect(self.delete_current_image)
        self.action_delete.setEnabled(False)
        self.toolbar.addAction(self.action_delete)

        empty = QWidget()
        empty.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(empty)

        from PyQt6.QtWidgets import QMenu, QToolButton

        self.lang_action = QAction(self.tr('lang_btn'), self)
        self.lang_action.setIcon(create_emoji_icon("🌐"))
        self.lang_menu = QMenu(self)

        langs = [
            ('English', 'en'),
            ('简体中文', 'cn'),
            ('繁體中文', 'tc'),
            ('日本語', 'jp'),
            ('한국어', 'kr')
        ]

        for label, code in langs:
            action = QAction(label, self)
            action.triggered.connect(lambda checked, c=code: self.set_language(c))
            self.lang_menu.addAction(action)

        self.toolbar.addAction(self.lang_action)
        widget = self.toolbar.widgetForAction(self.lang_action)
        if isinstance(widget, QToolButton):
            widget.setMenu(self.lang_menu)
            widget.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.theme_action = QAction(self.tr('theme'), self)
        self.theme_action.setIcon(create_emoji_icon("🌗"))
        self.theme_action.triggered.connect(self.toggle_theme)
        self.toolbar.addAction(self.theme_action)

        self.action_clear = QAction(self.tr('clear'), self)
        self.action_clear.setIcon(create_emoji_icon("🧹", color="#ff4d4f"))
        self.action_clear.triggered.connect(self.clear_all)
        self.action_clear.setEnabled(False)
        self.toolbar.addAction(self.action_clear)


    # ---------- Grid View ----------
    def setup_grid_view(self):
        self.grid_page = QWidget()
        layout = QVBoxLayout(self.grid_page)
        layout.setContentsMargins(16, 16, 16, 0)
        layout.setSpacing(0)

        self.grid_body_stack = QStackedWidget(self.grid_page)
        layout.addWidget(self.grid_body_stack)

        self.empty_page = QWidget(self.grid_body_stack)
        empty_page_layout = QVBoxLayout(self.empty_page)
        empty_page_layout.setContentsMargins(24, 24, 24, 40)
        empty_page_layout.setSpacing(0)
        empty_page_layout.addStretch(1)

        self.empty_state_container = QWidget(self.empty_page)
        self.empty_state_container.setMaximumWidth(940)
        empty_state_layout = QVBoxLayout(self.empty_state_container)
        empty_state_layout.setContentsMargins(0, 0, 0, 0)
        empty_state_layout.setSpacing(18)

        self.hint_label = QLabel(self.tr('drag_hint'))
        self.hint_label.setObjectName("empty_hint_label")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setWordWrap(True)
        empty_state_layout.addWidget(self.hint_label)

        self.empty_subhint_label = QLabel("Drag is the fastest way to start", self.empty_state_container)
        self.empty_subhint_label.setObjectName("empty_subhint_label")
        self.empty_subhint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_state_layout.addWidget(self.empty_subhint_label)

        self.empty_button_row = QWidget(self.empty_state_container)
        button_row_layout = QHBoxLayout(self.empty_button_row)
        button_row_layout.setContentsMargins(0, 10, 0, 0)
        button_row_layout.setSpacing(22)

        self.empty_open_file_btn = QPushButton(self.empty_button_row)
        self.empty_open_file_btn.setObjectName("empty_action_btn")
        self.empty_open_file_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.empty_open_file_btn.setIcon(self.action_file.icon())
        self.empty_open_file_btn.setIconSize(QSize(18, 18))
        self.empty_open_file_btn.clicked.connect(self.open_files_dialog)
        button_row_layout.addWidget(self.empty_open_file_btn)

        self.empty_open_folder_btn = QPushButton(self.empty_button_row)
        self.empty_open_folder_btn.setObjectName("empty_action_btn")
        self.empty_open_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.empty_open_folder_btn.setIcon(self.action_folder.icon())
        self.empty_open_folder_btn.setIconSize(QSize(18, 18))
        self.empty_open_folder_btn.clicked.connect(self.open_folder_dialog)
        button_row_layout.addWidget(self.empty_open_folder_btn)

        empty_state_layout.addWidget(self.empty_button_row, 0, Qt.AlignmentFlag.AlignHCenter)
        empty_page_layout.addWidget(self.empty_state_container, 0, Qt.AlignmentFlag.AlignHCenter)
        empty_page_layout.addStretch(1)
        self.grid_body_stack.addWidget(self.empty_page)

        self.list_page = QWidget(self.grid_body_stack)
        list_page_layout = QVBoxLayout(self.list_page)
        list_page_layout.setContentsMargins(0, 0, 0, 0)
        list_page_layout.setSpacing(0)

        self.list_widget = GridListWidget()
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setIconSize(QSize(220, 220))
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.setSpacing(3)
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.setGridSize(QSize(self.grid_item_min_width, self.grid_item_height))
        self.list_widget.setWordWrap(False)
        self.list_widget.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.list_widget.itemDoubleClicked.connect(self.on_thumbnail_clicked)
        list_page_layout.addWidget(self.list_widget)
        self.grid_body_stack.addWidget(self.list_page)
        self.grid_body_stack.setCurrentWidget(self.empty_page)
        self.stacked_widget.addWidget(self.grid_page)

        self.fab_container = QFrame(self.grid_page)
        self.fab_container.setObjectName("fab_container")
        self.fab_layout = QVBoxLayout(self.fab_container)
        self.fab_layout.setContentsMargins(3, 3, 3, 3)
        self.fab_layout.setSpacing(3)

        self.sort_fab = QToolButton(self.fab_container)
        self.sort_fab.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.sort_fab.setText("")
        self.sort_fab.setToolTip(self.tr('sort'))
        self.sort_fab.setFixedSize(32, 32)
        self.sort_fab.setIconSize(QSize(29, 29))
        self.sort_fab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sort_fab.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.sort_fab.setObjectName("fab_btn")

        self.refresh_fab = QToolButton(self.fab_container)
        self.refresh_fab.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.refresh_fab.setText("")
        self.refresh_fab.setToolTip(self.tr('refresh'))
        self.refresh_fab.setFixedSize(32, 32)
        self.refresh_fab.setIconSize(QSize(29, 29))
        self.refresh_fab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_fab.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.refresh_fab.setObjectName("fab_btn")
        self.refresh_fab.clicked.connect(self.refresh_folder)

        self.fab_layout.addWidget(self.sort_fab)
        self.fab_separator = QFrame(self.fab_container)
        self.fab_separator.setFixedHeight(1)
        self.fab_separator.setObjectName("fab_separator")
        self.fab_layout.addWidget(self.fab_separator)
        self.fab_layout.addWidget(self.refresh_fab)
        self.fab_container.hide()

        self.sort_menu = QMenu(self)
        self.sort_group = QActionGroup(self)
        self.sort_name_action = QAction(self.tr('sort_name'), self, checkable=True)
        self.sort_mtime_action = QAction(self.tr('sort_mtime'), self, checkable=True)
        self.sort_group.addAction(self.sort_name_action)
        self.sort_group.addAction(self.sort_mtime_action)

        if self.sort_mode == "mtime":
            self.sort_mtime_action.setChecked(True)
        else:
            self.sort_name_action.setChecked(True)

        self.sort_name_action.triggered.connect(lambda: self.set_sort_mode("name_natural"))
        self.sort_mtime_action.triggered.connect(lambda: self.set_sort_mode("mtime"))
        self.sort_menu.addAction(self.sort_name_action)
        self.sort_menu.addAction(self.sort_mtime_action)

        import time
        self._sort_menu_last_hide_time = 0.0
        self.sort_menu.aboutToHide.connect(lambda: setattr(self, '_sort_menu_last_hide_time', time.time()))
        self.sort_fab.clicked.connect(self.show_sort_menu)
        self.fab_container.hide()

        QTimer.singleShot(0, self.update_grid_for_width)
        QTimer.singleShot(0, self.position_sort_fab)



    def set_grid_placeholder_state(self, show_empty: bool):
        if not hasattr(self, 'grid_body_stack'):
            return
        self.grid_body_stack.setCurrentWidget(self.empty_page if show_empty else self.list_page)




    # ---------- Detail View ----------

    def setup_detail_view(self):
        self.detail_page = QWidget()
        layout = QHBoxLayout(self.detail_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)

        self.image_container = QWidget()
        img_layout = QHBoxLayout(self.image_container)
        img_layout.setContentsMargins(0, 0, 0, 0)
        img_layout.setSpacing(0)

        nav_btn_style = """
            QPushButton {
                background-color: rgba(0,0,0,0.05);
                color: #888;
                border: none;
                border-radius: 22px;
                font-family: 'Segoe UI Symbol', 'Segoe UI';
                font-size: 18px;
                width: 44px; height: 44px;
                margin: 10px;
                padding: 0px;
                padding-bottom: 3px;
            }
            QPushButton:hover { background-color: rgba(0,0,0,0.1); color: #333; }
            QPushButton:pressed { background-color: rgba(0,0,0,0.2); }
            QPushButton:disabled { background-color: transparent; color: transparent; }
        """

        self.btn_prev = QPushButton("<")
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.setStyleSheet(nav_btn_style)
        self.btn_prev.clicked.connect(self.show_prev_image)
        img_layout.addWidget(self.btn_prev)

        self.image_scroll = ImageScrollArea(owner=self)
        self.image_scroll.setWidgetResizable(True)
        self.image_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.image_label = QLabel("")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_scroll.setWidget(self.image_label)
        img_layout.addWidget(self.image_scroll)

        self.btn_next = QPushButton(">")
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setStyleSheet(nav_btn_style)
        self.btn_next.clicked.connect(self.show_next_image)
        img_layout.addWidget(self.btn_next)

        self.splitter.addWidget(self.image_container)

        self.info_scroll = QScrollArea()
        self.info_scroll.setObjectName("metadata_scroll")
        self.info_scroll.setWidgetResizable(True)
        self.info_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.info_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.info_scroll.setMinimumWidth(300)
        self.metadata_panel = MetadataPanel(self.tr, self.copy_to_clipboard, self.info_scroll)
        self.info_scroll.setWidget(self.metadata_panel)
        self.splitter.addWidget(self.info_scroll)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setStretchFactor(0, 5)
        self.splitter.setStretchFactor(1, 3)
        layout.addWidget(self.splitter)
        self.stacked_widget.addWidget(self.detail_page)
        QTimer.singleShot(0, self.update_detail_splitter_sizes)

    # ---------- Shortcuts ----------
    def setup_shortcuts(self):
        # 左右键：上一张 / 下一张（默认先禁用）
        self.shortcut_prev = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        self.shortcut_prev.activated.connect(self._shortcut_prev)
        self.shortcut_prev.setEnabled(False)

        self.shortcut_next = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        self.shortcut_next.activated.connect(self._shortcut_next)
        self.shortcut_next.setEnabled(False)


        # 回车：在网格/详情间切换
        self.shortcut_enter = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        self.shortcut_enter.activated.connect(self._shortcut_enter)

        self.shortcut_enter2 = QShortcut(QKeySequence(Qt.Key.Key_Enter), self)
        self.shortcut_enter2.activated.connect(self._shortcut_enter)

        # Delete 键：删除当前图片（网格=选中，详情=当前）
        self.shortcut_delete = QShortcut(QKeySequence(Qt.Key.Key_Delete), self)
        self.shortcut_delete.activated.connect(self.delete_current_image)

    def _shortcut_prev(self):
        if self.stacked_widget.currentIndex() == 1:
            self.show_prev_image()

    def _shortcut_next(self):
        if self.stacked_widget.currentIndex() == 1:
            self.show_next_image()

    def _shortcut_enter(self):
        # 网格 -> 打开当前选中图片
        if self.stacked_widget.currentIndex() == 0:
            if self.list_widget.count() == 0:
                return
            item = self.list_widget.currentItem()
            if item is None:
                item = self.list_widget.item(0)
                self.list_widget.setCurrentItem(item)
            self.show_image_detail(item.data(Qt.ItemDataRole.UserRole))
        # 详情 -> 返回网格
        else:
            self.show_grid()
    def keyPressEvent(self, event):
        if self.stacked_widget.currentIndex() == 1:
            if event.key() == Qt.Key.Key_Left:
                self.show_prev_image()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Right:
                self.show_next_image()
                event.accept()
                return
        super().keyPressEvent(event)

    # ---------- 导航 ----------
    def show_prev_image(self):
        if self.current_index > 0:
            self.show_image_detail(self.current_file_list[self.current_index - 1])

    def show_next_image(self):
        if self.current_index < len(self.current_file_list) - 1:
            self.show_image_detail(self.current_file_list[self.current_index + 1])

    def update_nav_buttons(self):
        self.btn_prev.setEnabled(self.current_index > 0)
        self.btn_next.setEnabled(self.current_index < len(self.current_file_list) - 1)

    def update_action_states(self):
        has_images = bool(self.current_file_list)
        has_current = has_images and self.current_index >= 0 and self.current_index < len(self.current_file_list)
        self.action_clear.setEnabled(has_images)
        self.action_delete.setEnabled(has_current)

    # ---------- 删除当前图片/选中图片 ----------
    # ---------- 删除当前图片 ----------
    def delete_current_image(self):
        """在磁盘中删除按当前选定的图片 / 当前展示的图片。"""
        if not self.current_file_list:
            return

        target_path = None
        if self.stacked_widget.currentIndex() == 0:
            item = self.list_widget.currentItem()
            if not item:
                return
            target_path = item.data(Qt.ItemDataRole.UserRole)
        else:
            if self.current_index < 0 or self.current_index >= len(self.current_file_list):
                return
            target_path = self.current_file_list[self.current_index]

        if not target_path:
            return

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(self.tr('delete_confirm_title'))
        msg.setText(self.tr('delete_confirm_one').format(os.path.basename(target_path)))
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        if msg.exec() != QMessageBox.StandardButton.Yes:
            return

        error = False
        try:
            if os.path.exists(target_path):
                send2trash.send2trash(target_path)
        except Exception:
            error = True

        old_index = self.current_index if self.current_index >= 0 else 0
        if target_path in self.current_file_list:
            self.current_file_list.remove(target_path)

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == target_path:
                self.list_widget.takeItem(i)
                break

        if not self.current_file_list:
            self.current_index = -1
            self.image_label.clear()
            self.metadata_panel.clear_metadata()
            self.set_grid_placeholder_state(True)
            self.show_grid()
        else:
            new_index = min(old_index, len(self.current_file_list) - 1)
            self.current_index = new_index
            if self.stacked_widget.currentIndex() == 0:
                self._select_grid_index(new_index)
            else:
                self.show_image_detail(self.current_file_list[new_index])

        self.update_action_states()
        if error:
            self.show_toast(self.tr('delete_error'))
        else:
            self.show_toast(self.tr('deleted'))


    # ---------- 清空全部 ----------
    def clear_all(self):
        if self.loader_thread and self.loader_thread.isRunning():
            self.loader_thread.stop()
        self.loader_thread = None
        self._loading_in_progress = False

        self.current_file_list = []
        self.current_index = -1
        self.current_image_path = None
        self.current_loaded_folder = None
        self.current_pos_text = ""
        self.current_neg_text = ""

        self.list_widget.clear()
        self.set_grid_placeholder_state(True)
        self.update_fab_visibility()

        self.image_label.clear()
        self.metadata_panel.clear_metadata()
        self.toast_label.hide()

        self.stacked_widget.setCurrentIndex(0)
        self.back_action.setEnabled(False)
        self.shortcut_prev.setEnabled(False)
        self.shortcut_next.setEnabled(False)

        self.update_action_states()
        self.show_toast(self.tr('cleared'))



    # ---------- 多语言 / UI 文本 ----------
    def set_language(self, lang_code):
        self.lang = lang_code
        self.settings.setValue("language", lang_code)
        self.update_ui_text()

    def update_ui_text(self):
        self.setWindowTitle(self.tr('title'))
        self.action_file.setText(self.tr('open_file'))
        self.action_folder.setText(self.tr('open_folder'))
        self.action_clear.setText(self.tr('clear'))
        self.back_action.setText(self.tr('back'))
        self.theme_action.setText(self.tr('theme'))
        self.lang_action.setText(self.tr('lang_btn'))

        if hasattr(self, 'sort_fab'):
            self.sort_fab.setToolTip(self.tr('sort'))
            if hasattr(self, 'refresh_fab'):
                self.refresh_fab.setToolTip(self.tr('refresh'))
            self.sort_name_action.setText(self.tr('sort_name'))
            self.sort_mtime_action.setText(self.tr('sort_mtime'))

        if hasattr(self, 'empty_open_file_btn'):
            self.empty_open_file_btn.setText(self.tr('open_file'))
            self.empty_open_folder_btn.setText(self.tr('open_folder'))
        self.hint_label.setText(self.tr('drag_hint'))
        if hasattr(self, 'empty_subhint_label'):
            subhint_map = {
                'en': '✨ Drag is the fastest way to start ✨',
                'cn': '✨ 拖拽是最快的开始方式 ✨',
                'tc': '✨ 拖曳是最快的開始方式 ✨',
                'jp': '✨ ドラッグ操作が最も素早く始められます ✨',
                'kr': '✨ 드래그가 가장 빠른 시작 방법입니다 ✨',
            }
            self.empty_subhint_label.setText(subhint_map.get(self.lang, subhint_map['en']))

        self.metadata_panel.retranslate(self.tr)
        self.action_delete.setText(self.tr('delete'))
        if self.stacked_widget.currentIndex() == 1 and self.current_image_path:
            self.show_image_detail(self.current_image_path, keep_view=True)




    def copy_to_clipboard(self, text: str):
        if not text:
            return
        QApplication.clipboard().setText(text)
        self.show_toast(self.tr('copied'))

    def update_detail_splitter_sizes(self):
        if not hasattr(self, 'splitter') or not hasattr(self, 'info_scroll'):
            return

        total_w = self.splitter.size().width() or self.width()
        if total_w <= 0:
            return

        if total_w >= 1600:
            right_w = int(total_w * 0.34)
        elif total_w >= 1200:
            right_w = int(total_w * 0.37)
        elif total_w >= 900:
            right_w = int(total_w * 0.42)
        else:
            right_w = int(total_w * 0.48)

        right_w = max(320, min(680, right_w))
        left_w = max(360, total_w - right_w)

        self.info_scroll.setMinimumWidth(max(280, min(360, right_w)))
        self.splitter.setSizes([left_w, right_w])


    # ---------- Resize ----------
    def resizeEvent(self, event: QResizeEvent):
        if self.stacked_widget.currentIndex() == 1 and self.current_image_path:
            QTimer.singleShot(0, self.update_detail_splitter_sizes)
            QTimer.singleShot(50, lambda: self.display_image_fit(self.current_image_path))
        QTimer.singleShot(0, self.update_grid_for_width)
        self.position_sort_fab()
        super().resizeEvent(event)

    # ---------- Drag & Drop ----------
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        try:
            urls = event.mimeData().urls()
            if not urls:
                return

            dropped_dirs = []
            dropped_files = []

            for url in urls:
                p = os.path.normpath(url.toLocalFile())
                if os.path.isdir(p):
                    dropped_dirs.append(p)
                elif os.path.isfile(p) and p.lower().endswith(VALID_EXTENSIONS):
                    dropped_files.append(p)

            if dropped_dirs:
                self.load_from_folder_path(dropped_dirs[0])
                return
            if not dropped_files:
                return
            if len(dropped_files) == 1:
                p = dropped_files[0]
                self.load_from_folder_path(os.path.dirname(p))
                self.show_image_detail(p)
            else:
                self.current_loaded_folder = None
                self.load_images_list(dropped_files)
                if self.current_file_list:
                    self.show_image_detail(self.current_file_list[0])
        except Exception as e:
            print("Drop error:", e)


    # ---------- 打开文件 / 文件夹 ----------
    def open_files_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if not files:
            return
        if len(files) == 1:
            target = files[0]
            self.load_from_folder_path(os.path.dirname(target))
            self.show_image_detail(target)
        else:
            self.current_loaded_folder = None
            self.load_images_list(files)
            self.show_image_detail(files[0])

    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.load_from_folder_path(folder)

    def update_fab_visibility(self):
        if not hasattr(self, "fab_container"):
            return
        if self.stacked_widget.currentIndex() == 0 and len(self.current_file_list) > 0:
            self.fab_container.show()
            self.sort_fab.show()
            if getattr(self, "current_loaded_folder", None):
                self.refresh_fab.show()
                self.fab_separator.show()
            else:
                self.refresh_fab.hide()
                self.fab_separator.hide()
            self.fab_container.adjustSize()
            self.position_sort_fab()
        else:
            self.fab_container.hide()


    def position_sort_fab(self):
        if not hasattr(self, "fab_container"):
            return
        if self.stacked_widget.currentIndex() != 0:
            return

        rect = self.list_widget.geometry()
        sb = self.list_widget.verticalScrollBar()
        sb_w = sb.sizeHint().width() if sb and sb.isVisible() else 0

        self.fab_container.adjustSize()
        margin = 16
        x = rect.x() + rect.width() - sb_w - self.fab_container.width() - margin
        x += 8
        y = rect.y() + margin

        x = max(0, x)
        y = max(0, y)
        self.fab_container.move(x, y)

    def refresh_folder(self):
        if getattr(self, "current_loaded_folder", None) and os.path.isdir(self.current_loaded_folder):
            selected_paths = [it.data(Qt.ItemDataRole.UserRole) for it in self.list_widget.selectedItems()]
            cur_item = self.list_widget.currentItem()
            current_path = cur_item.data(Qt.ItemDataRole.UserRole) if cur_item else None

            self._pending_restore_selected_paths = list(selected_paths)
            self._pending_restore_path = current_path
            self.load_from_folder_path(self.current_loaded_folder)





    def set_sort_mode(self, mode):
        if mode not in ("name_natural", "mtime"):
            return
        if self.sort_mode == mode:
            return
        self.sort_mode = mode
        self.settings.setValue("sort_mode", mode)

        if self.sort_mode == "mtime":
            self.sort_mtime_action.setChecked(True)
        else:
            self.sort_name_action.setChecked(True)

        if not self.current_file_list:
            return

        selected_paths = [it.data(Qt.ItemDataRole.UserRole) for it in self.list_widget.selectedItems()]
        cur_item = self.list_widget.currentItem()
        selected_path = cur_item.data(Qt.ItemDataRole.UserRole) if cur_item else None

        self._pending_restore_selected_paths = list(selected_paths)
        self._pending_restore_path = selected_path
        self.current_file_list = self.apply_sort(self.current_file_list)
        self.current_index = self.current_file_list.index(selected_path) if selected_path in self.current_file_list else -1

        self.list_widget.clear()
        self.set_grid_placeholder_state(False)
        self.update_fab_visibility()

        self.start_thumbnail_loader()
        self.show_toast(self.tr('loading'), duration=0)





    def _select_grid_index(self, idx):
        if 0 <= idx < self.list_widget.count():
            self.current_index = idx
            item = self.list_widget.item(idx)
            self.list_widget.setCurrentItem(item)
            self.list_widget.scrollToItem(item)


    def show_sort_menu(self):
        if not hasattr(self, "sort_menu"):
            return
            
        import time
        # 如果菜单刚刚（在 200 ms 内）因为失去焦点而关闭，说明这次点击是为了关闭菜单，所以不再重新弹出
        if time.time() - getattr(self, '_sort_menu_last_hide_time', 0.0) < 0.2:
            return
        
        
        self.sort_name_action.setChecked(self.sort_mode == "name_natural")
        self.sort_mtime_action.setChecked(self.sort_mode == "mtime")

        br = self.sort_fab.mapToGlobal(self.sort_fab.rect().bottomRight())
        menu_size = self.sort_menu.sizeHint()
        
        x = br.x() - menu_size.width()
        y = br.y() + 6

        x = max(0, x)
        y = max(0, y)

        self.sort_menu.popup(QPoint(x, y))

    def load_from_folder_path(self, folder_path):
        if not os.path.isdir(folder_path):
            return
        files = [
            os.path.normpath(os.path.join(folder_path, f))
            for f in os.listdir(folder_path)
            if f.lower().endswith(VALID_EXTENSIONS)
        ]
        self.current_loaded_folder = os.path.normpath(folder_path)
        self.load_images_list(files)
    def apply_sort(self, files):
        if not files:
            return []
        if self.sort_mode == "mtime":
            def safe_mtime(p):
                try: return os.path.getctime(p)
                except: return 0
            return sorted(files, key=safe_mtime, reverse=True)
        else: # "name_natural"
            def natural_key(p):
                basename = os.path.basename(p).lower()
                return [int(text) if text.isdigit() else text for text in re.split(r'(\d+)', basename)]
            return sorted(files, key=natural_key)

    def start_thumbnail_loader(self):
        if self.loader_thread and self.loader_thread.isRunning():
            self.loader_thread.stop()

        self._loading_in_progress = bool(self.current_file_list)
        self._loading_request_id += 1
        thread = ThumbnailLoader(self.current_file_list)
        thread.request_id = self._loading_request_id
        thread.thumbnail_loaded.connect(self.add_thumbnail_item)
        thread.finished.connect(lambda t=thread: self.on_thumbnails_load_finished(t))
        self.loader_thread = thread
        thread.start()


    # ---------- 加载图片列表 ----------
    def load_images_list(self, file_paths):
        normalized = [os.path.normpath(p) for p in file_paths]
        seen = set()
        unique_paths = []
        for p in normalized:
            if p not in seen:
                seen.add(p)
                unique_paths.append(p)

        previous_current = None
        cur_item = self.list_widget.currentItem() if hasattr(self, 'list_widget') else None
        if cur_item:
            previous_current = cur_item.data(Qt.ItemDataRole.UserRole)
        elif self.current_image_path:
            previous_current = self.current_image_path

        self.current_file_list = self.apply_sort(unique_paths)
        self.list_widget.clear()

        if self._pending_restore_path is None and previous_current in self.current_file_list:
            self._pending_restore_path = previous_current
        if self._pending_restore_selected_paths:
            self._pending_restore_selected_paths = [p for p in self._pending_restore_selected_paths if p in self.current_file_list]

        if self._pending_restore_path in self.current_file_list:
            self.current_index = self.current_file_list.index(self._pending_restore_path)
        else:
            self.current_index = -1

        self.set_grid_placeholder_state(not bool(self.current_file_list))
        self.update_fab_visibility()

        if not self.current_file_list:
            if self.loader_thread and self.loader_thread.isRunning():
                self.loader_thread.stop()
            self.loader_thread = None
            self._loading_in_progress = False
            self.toast_label.hide()
            self.show_grid()
            self.update_action_states()
            QTimer.singleShot(0, self.update_grid_for_width)
            return

        self.start_thumbnail_loader()
        self.show_toast(self.tr('loading'), duration=0)

        self.show_grid()
        self.update_fab_visibility()
        self.update_action_states()
        QTimer.singleShot(0, self.update_grid_for_width)



    def on_thumbnails_load_finished(self, thread=None):
        if thread is None:
            return
        if thread is not self.loader_thread:
            return
        if getattr(thread, 'request_id', None) != self._loading_request_id:
            return

        self._loading_in_progress = False
        restored_item = None
        if self._pending_restore_path and self._pending_restore_path in self.current_file_list:
            idx = self.current_file_list.index(self._pending_restore_path)
            if 0 <= idx < self.list_widget.count():
                self.current_index = idx
                restored_item = self.list_widget.item(idx)
                self.list_widget.setCurrentItem(restored_item)

        if self._pending_restore_selected_paths:
            selected_set = set(self._pending_restore_selected_paths)
            for idx in range(self.list_widget.count()):
                item = self.list_widget.item(idx)
                item.setSelected(item.data(Qt.ItemDataRole.UserRole) in selected_set)
                if restored_item is None and item.isSelected():
                    restored_item = item

        self._pending_restore_path = None
        self._pending_restore_selected_paths = []

        if self.stacked_widget.currentIndex() == 0:
            if restored_item is not None:
                QTimer.singleShot(
                    0,
                    lambda item=restored_item: self.list_widget.scrollToItem(
                        item, QAbstractItemView.ScrollHint.EnsureVisible
                    ),
                )
            self.show_toast(self.tr('load_done'), duration=2000)
        else:
            self.toast_label.hide()





    def add_thumbnail_item(self, path, pixmap):
        if self.sender() != getattr(self, 'loader_thread', None):
            return

        filename = os.path.basename(path)
        if len(filename) > 30:
            filename_display = filename[:18] + "..." + filename[-8:]
        else:
            filename_display = filename

        item = QListWidgetItem(filename_display)
        item.setIcon(QIcon(pixmap))
        item.setData(Qt.ItemDataRole.UserRole, path)
        item.setSizeHint(self.list_widget.gridSize())
        self.list_widget.addItem(item)


    def on_thumbnail_clicked(self, item):
        self.show_image_detail(item.data(Qt.ItemDataRole.UserRole))

    # ---------- 显示详情 ----------
    def show_image_detail(self, path, keep_view=False):
        if not path or not os.path.exists(path):
            return

        if hasattr(self, 'fab_container'):
            self.fab_container.hide()
        path = os.path.normpath(path)
        self.current_image_path = path
        if not keep_view:
            self.image_label.clear()

        self.stacked_widget.setCurrentIndex(1)
        self.toast_label.hide()
        self.back_action.setEnabled(True)
        QApplication.processEvents()
        QTimer.singleShot(0, self.update_detail_splitter_sizes)

        self.shortcut_prev.setEnabled(True)
        self.shortcut_next.setEnabled(True)

        if path in self.current_file_list:
            self.current_index = self.current_file_list.index(path)
        else:
            self.current_index = -1
        self.update_nav_buttons()
        self.update_action_states()

        if not keep_view:
            QTimer.singleShot(50, lambda: self.display_image_fit(path))

        try:
            with Image.open(path) as img:
                metadata = self.parse_metadata(img, path, img.width, img.height)
                self.metadata_panel.set_metadata(metadata)
        except Exception:
            self.metadata_panel.clear_metadata()


    def display_image_fit(self, path):
        try:
            view_w = self.image_scroll.viewport().width()
            view_h = self.image_scroll.viewport().height()
            if view_w <= 50:
                QTimer.singleShot(100, lambda: self.display_image_fit(path))
                return
            
            # --- High DPI Fix Start ---
            dpr = self.image_label.devicePixelRatio()
            # Calculate physical pixels needed
            target_w = int((view_w - 40) * dpr)
            target_h = int((view_h - 40) * dpr)
            
            with Image.open(path) as img:
                pixmap = pil2pixmap(img)
                # Scale to physical pixels
                scaled = pixmap.scaled(
                    target_w,
                    target_h,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                # Tell pixmap it is high-dpi (so it draws smaller in logical coords, matching viewport)
                scaled.setDevicePixelRatio(dpr)
                self.image_label.setPixmap(scaled)
            # --- High DPI Fix End ---
        except:
            pass

    # ---------- 回到网格 ----------
    def show_grid(self):
        self.image_label.clear()
        self.stacked_widget.setCurrentIndex(0)
        QTimer.singleShot(0, self.update_detail_splitter_sizes)
        self.back_action.setEnabled(False)

        if not self.current_file_list:
            self.set_grid_placeholder_state(True)
            self.toast_label.hide()
        elif self._loading_in_progress:
            self.set_grid_placeholder_state(False)
            self.show_toast(self.tr('loading'), duration=0)
        else:
            self.set_grid_placeholder_state(False)
            self.toast_label.hide()

        self.shortcut_prev.setEnabled(False)
        self.shortcut_next.setEnabled(False)

        if 0 <= self.current_index < self.list_widget.count():
            item = self.list_widget.item(self.current_index)
            self.list_widget.setCurrentItem(item)
            QTimer.singleShot(
                50,
                lambda: self.list_widget.scrollToItem(
                    item, QAbstractItemView.ScrollHint.EnsureVisible
                ),
            )

        self.update_action_states()
        QTimer.singleShot(0, self.update_grid_for_width)



    # ---------- 自适应网格尺寸 ----------
    def update_grid_for_width(self):
        self.update_fab_visibility()

        if not hasattr(self, "list_widget"):
            return

        viewport_width = self.list_widget.viewport().width()
        if viewport_width <= 0:
            return

        spacing = self.list_widget.spacing()
        min_unit = self.grid_item_min_width + spacing
        cols = max(1, viewport_width // min_unit)

        total_spacing = (cols + 1) * spacing
        available = max(50, viewport_width - total_spacing)
        item_w = available // cols
        item_w = max(self.grid_item_min_width, item_w)

        new_size = QSize(item_w, self.grid_item_height)
        self.list_widget.setGridSize(new_size)
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setSizeHint(new_size)


    # ---------- 主题 + 元数据解析 ----------
    def get_theme(self):
        return NativeTheme.DARK if self.dark_mode else NativeTheme.LIGHT


    def parse_comfy_data(self, comfy_json):
        """Parse ComfyUI metadata into structured card data."""
        try:
            data = json.loads(comfy_json)
            pos, neg = "", ""
            params = {}
            sampler_node = None
            model_lines = []
            qwen_pos_candidate = ""
            qwen_neg_candidate = ""
            lora_infos = []
            seen_loras = set()
            raw_param_candidates = []

            def add_model_line(line: str):
                if line and line not in model_lines:
                    model_lines.append(line)

            def add_param(key: str, value):
                if value is None:
                    return
                value_str = str(value).strip()
                if not value_str:
                    return
                params[key] = value_str

            def format_weight(value):
                if value is None:
                    return None
                try:
                    return f"{float(value):.1f}"
                except (TypeError, ValueError):
                    value_str = str(value).strip()
                    return value_str or None

            def get_node(ref):
                if isinstance(ref, (list, tuple)) and ref:
                    return data.get(str(ref[0]), {}) or {}
                return {}

            def extract_prompt_text(ref, visited=None):
                if not isinstance(ref, (list, tuple)) or not ref:
                    return ""
                node_id = str(ref[0])
                if visited is None:
                    visited = set()
                if node_id in visited:
                    return ""
                visited.add(node_id)

                node = data.get(node_id, {}) or {}
                inputs = node.get('inputs', {}) or {}

                for text_key in ('text', 'prompt', 'positive_prompt', 'negative_prompt', 'string'):
                    value = inputs.get(text_key)
                    if isinstance(value, str) and value.strip():
                        return value.strip()

                for ref_key in ('text', 'prompt', 'positive', 'negative', 'conditioning', 'cond', 'clip'):
                    nested = inputs.get(ref_key)
                    if isinstance(nested, (list, tuple)) and nested:
                        nested_text = extract_prompt_text(nested, visited)
                        if nested_text:
                            return nested_text

                for value in inputs.values():
                    if isinstance(value, (list, tuple)) and value:
                        nested_text = extract_prompt_text(value, visited)
                        if nested_text:
                            return nested_text

                return ""

            # Keep Parameters aligned with the stable main.py: sampler-related fields only.
            alias_map = {
                'seed': 'seed',
                'noise_seed': 'seed',
                'rand_seed': 'seed',
                'steps': 'steps',
                'num_steps': 'steps',
                'cfg': 'cfg',
                'cfg_scale': 'cfg',
                'guidance': 'cfg',
                'guidance_scale': 'cfg',
                'sampler_name': 'sampler_name',
                'sampler': 'sampler_name',
                'scheduler': 'scheduler',
                'denoise': 'denoise',
                'denoise_strength': 'denoise',
            }

            def collect_from_node(node):
                nonlocal sampler_node, qwen_pos_candidate, qwen_neg_candidate
                if not node:
                    return

                ctype = node.get('class_type', '')
                inputs = node.get('inputs', {}) or {}
                ctype_lower = ctype.lower()

                if 'checkpointloader' in ctype_lower:
                    name = inputs.get('ckpt_name') or inputs.get('model_name') or inputs.get('ckpt_path') or ''
                    if name:
                        add_model_line(f"Checkpoint: {name}")

                if 'unet' in ctype_lower:
                    name = inputs.get('unet_name') or inputs.get('model') or inputs.get('name') or ''
                    if name:
                        add_model_line(f"Diffusion Model: {name}")

                if 'lora' in ctype_lower:
                    name = inputs.get('lora_name') or inputs.get('model') or inputs.get('name') or ''
                    sm = format_weight(inputs.get('strength_model', None))
                    sc = format_weight(inputs.get('strength_clip', None))
                    parts = []
                    if name:
                        parts.append(str(name))
                    if sm is not None:
                        parts.append(f"model: {sm}")
                    if sc is not None:
                        parts.append(f"clip: {sc}")
                    if parts:
                        lora_line = " | ".join(parts)
                        if lora_line not in seen_loras:
                            seen_loras.add(lora_line)
                            lora_infos.append(lora_line)

                if 'qwen' in ctype_lower:
                    p = inputs.get('prompt') or inputs.get('text') or ""
                    n = inputs.get('negative_prompt') or inputs.get('negative') or ""
                    if isinstance(p, str) and p.strip():
                        qwen_pos_candidate = p.strip()
                    if isinstance(n, str) and n.strip():
                        qwen_neg_candidate = n.strip()

                if 'ksampler' in ctype_lower or ('sampler' in ctype_lower and ('advanced' in ctype_lower or 'custom' in ctype_lower)):
                    sampler_node = node

                local_bits = []
                for source_key, target_key in alias_map.items():
                    if source_key in inputs:
                        value = inputs.get(source_key)
                        add_param(target_key, value)
                        if not isinstance(value, (list, tuple, dict)):
                            local_bits.append(f"{target_key}: {value}")

                if local_bits and any(k in ctype_lower for k in ('sampler', 'scheduler', 'guidance', 'noise')):
                    raw_line = f"{ctype}: " + ", ".join(local_bits)
                    if raw_line not in raw_param_candidates:
                        raw_param_candidates.append(raw_line)

            for _, node in data.items():
                collect_from_node(node)

            if sampler_node:
                sampler_inputs = sampler_node.get('inputs', {}) or {}
                pos = extract_prompt_text(sampler_inputs.get('positive')) or pos
                neg = extract_prompt_text(sampler_inputs.get('negative')) or neg

                for ref_key in ('noise', 'sampler', 'sigmas', 'latent_image', 'model', 'vae', 'guider'):
                    collect_from_node(get_node(sampler_inputs.get(ref_key)))

            if not pos or not neg:
                clip_texts = []
                for _, node in data.items():
                    if 'cliptextencode' in node.get('class_type', '').lower():
                        prompt_text = (node.get('inputs', {}) or {}).get('text', '')
                        if isinstance(prompt_text, str) and prompt_text.strip():
                            clip_texts.append(prompt_text.strip())

                if not pos and clip_texts:
                    pos = clip_texts[0]
                if not neg and len(clip_texts) > 1:
                    neg = clip_texts[-1]

            if (not pos) and qwen_pos_candidate:
                pos = qwen_pos_candidate
            if (not neg) and qwen_neg_candidate:
                neg = qwen_neg_candidate

            param_pairs = self.normalize_parameter_pairs(params)

            return {
                'models': model_lines,
                'loras': lora_infos,
                'positive': pos,
                'negative': neg,
                'parameters': param_pairs,
            }
        except Exception:
            return {
                'models': [],
                'loras': [],
                'positive': '',
                'negative': '',
                'parameters': [],
                'empty_message': self.tr('comfy_err'),
            }

    def normalize_parameter_pairs(self, params):
        if isinstance(params, dict):
            raw_items = list(params.items())
        else:
            raw_items = list(params or [])

        formatted = []
        seen = set()
        order = ['seed', 'steps', 'cfg', 'cfg scale', 'sampler_name', 'sampler', 'scheduler', 'denoise']

        def display_key(key):
            key_str = str(key).strip()
            lowered = key_str.lower()
            mapping = {
                'cfg': 'Cfg',
                'cfg scale': 'Cfg',
                'sampler_name': 'Sampler_name',
                'sampler': 'Sampler_name',
                'seed': 'Seed',
                'steps': 'Steps',
                'scheduler': 'Scheduler',
                'denoise': 'Denoise',
                'details': 'Details',
                'raw': 'Details',
                'raw parameters': 'Details',
            }
            return mapping.get(lowered, key_str.replace('_', ' ').title())

        indexed = {str(k).strip().lower(): v for k, v in raw_items if str(v).strip()}
        for key in order:
            if key in indexed and key not in seen:
                formatted.append((display_key(key), str(indexed[key])))
                seen.add(key)

        for key, value in raw_items:
            key_str = str(key).strip()
            lowered = key_str.lower()
            value_str = str(value).strip()
            if not value_str or lowered in seen:
                continue
            formatted.append((display_key(key_str), value_str))
            seen.add(lowered)

        return formatted

    def parse_parameter_pairs(self, text: str):
        if not text:
            return []

        pairs = []
        seen = set()

        def add_pair(key, value):
            key = str(key).strip()
            value = str(value).strip()
            if not key or not value:
                return
            sig = (key.lower(), value)
            if sig in seen:
                return
            seen.add(sig)
            pairs.append((key, value))

        # Preferred split: only break on commas that look like the next key starts.
        pattern = re.compile(r',\s*(?=[A-Za-z][A-Za-z0-9 _\-/]*\s*:)')
        parts = [part.strip() for part in pattern.split(text) if part.strip()]
        for part in parts:
            if ':' not in part:
                continue
            key, value = part.split(':', 1)
            add_pair(key, value)

        if pairs:
            return pairs

        # Fallback: plain comma split for looser parameter strings.
        for chunk in [part.strip() for part in text.split(',') if part.strip()]:
            if ':' not in chunk:
                continue
            key, value = chunk.split(':', 1)
            add_pair(key, value)

        if pairs:
            return pairs

        # Final fallback: keep the raw parameter line instead of dropping it.
        if ':' in text:
            first_key, first_value = text.split(':', 1)
            if first_key.strip() and first_value.strip():
                add_pair(first_key, first_value)
        elif text.strip():
            add_pair('Details', text.strip())

        return pairs

    def parse_metadata(self, img, path, w, h):
        info = img.info
        filename = os.path.basename(path)
        index_text = ""
        if self.current_file_list and 0 <= self.current_index < len(self.current_file_list):
            index_text = f"{self.current_index + 1} / {len(self.current_file_list)}"

        metadata = {
            'summary': {
                'filename': filename,
                'resolution': f"{w} x {h} px",
                'index_text': index_text,
            },
            'models': [],
            'loras': [],
            'positive': '',
            'negative': '',
            'parameters': [],
            'empty_message': self.tr('no_data_desc'),
        }

        if 'prompt' in info:
            metadata.update(self.parse_comfy_data(info['prompt']))
            return metadata

        if 'parameters' in info:
            param_text = info['parameters']
            parts = param_text.split("Negative prompt:")
            pos = parts[0].strip()
            neg = ""
            if len(parts) > 1:
                if "Steps:" in parts[1]:
                    neg = parts[1].split("Steps:")[0].strip()
                else:
                    neg = parts[1].strip()

            full_params = ""
            if "Steps:" in param_text:
                full_params = "Steps:" + param_text.split("Steps:", 1)[1].strip()

            model_name = ""
            if full_params:
                idx_m = full_params.find("Model:")
                if idx_m != -1:
                    after = full_params[idx_m + len("Model:"):].lstrip()
                    end_m = after.find(",")
                    if end_m != -1:
                        model_name = after[:end_m].strip()
                        full_params = (full_params[:idx_m].rstrip(" ,") + ", " + after[end_m + 1:].lstrip()).strip(" ,")
                    else:
                        model_name = after.strip()
                        full_params = full_params[:idx_m].rstrip(" ,")

            lora_list = []
            params_display = full_params
            if full_params:
                lower = full_params.lower()
                idx = lower.find("lora:")
                if idx != -1:
                    cut_start = idx + len("lora:")
                    lora_part = full_params[cut_start:].strip(" ,")
                    lora_items = [s.strip() for s in lora_part.split(",") if s.strip()]
                    if lora_items:
                        lora_list = lora_items
                    params_display = full_params[:idx].rstrip(" ,")

            param_pairs = self.parse_parameter_pairs(params_display)
            if params_display.strip() and not param_pairs:
                param_pairs = [('Details', params_display.strip())]
            if not any(str(key).strip().lower() == 'size' for key, _ in param_pairs):
                param_pairs.append(('Size', f'{w} x {h}'))

            metadata.update({
                'models': [model_name] if model_name else [],
                'loras': lora_list,
                'positive': pos,
                'negative': neg,
                'parameters': self.normalize_parameter_pairs(param_pairs),
            })

        return metadata

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.settings.setValue("theme", self.dark_mode)
        self.apply_style()
        if self.stacked_widget.currentIndex() == 1 and self.current_image_path:
            self.show_image_detail(self.current_image_path, keep_view=True)

    def apply_style(self):
        t = self.get_theme()
        btn_color = "rgba(237,240,244,0.78)" if self.dark_mode else "rgba(31,36,48,0.58)"
        btn_hover = "rgba(122,162,199,0.14)" if self.dark_mode else "rgba(44,93,138,0.08)"
        empty_button_bg = t['bg_panel'] if self.dark_mode else "#ffffff"
        empty_button_border = t['border']

        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {t['bg_main']};
                color: {t['text_main']};
                font-family: {NativeTheme.FONT_FAMILY};
            }}
            QToolBar {{
                background-color: {t['bg_main']};
                border-bottom: 1px solid {t['border']};
                padding: 5px;
                spacing: 10px;
            }}
            QToolButton {{
                background-color: transparent;
                border-radius: 9px;
                padding: 7px 12px;
                color: {t['text_main']};
                font-size: 13px;
            }}
            QToolButton:hover {{
                background-color: {t['hover']};
            }}
            QListWidget {{
                background-color: {t['bg_main']};
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                border-radius: 10px;
                padding: 4px;
                margin: 3px;
                color: {t['text_main']};
            }}
            QListWidget::item:hover {{
                background-color: {t['hover']};
            }}
            QListWidget::item:selected {{
                background-color: {t['selected']};
                color: {t['accent']};
                border: 1px solid {t['accent']};
            }}
            QLabel#empty_hint_label {{
                color: {t['text_main']};
                font-size: 30px;
                font-weight: 300;
                padding: 0 12px;
            }}
            QLabel#empty_subhint_label {{
                color: {t['text_sub']};
                font-size: 14px;
                font-weight: 500;
                padding: 0 12px;
            }}
            QPushButton#empty_action_btn {{
                background-color: {empty_button_bg};
                color: {t['text_main']};
                border: 1px solid {empty_button_border};
                border-radius: 17px;
                padding: 14px 22px;
                min-width: 300px;
                font-size: 16px;
                font-weight: 600;
                text-align: center;
            }}
            QPushButton#empty_action_btn:hover {{
                background-color: {t['hover']};
                color: {t['accent']};
            }}
            QScrollArea#metadata_scroll {{
                background-color: {t['bg_panel']};
                border-left: 1px solid {t['border']};
            }}
            QScrollArea#metadata_scroll > QWidget > QWidget {{
                background-color: transparent;
            }}
            QSplitter::handle {{
                background-color: {t['border']};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {t['bg_main']};
                width: 10px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {t['border']};
                border-radius: 5px;
                min-height: 20px;
                margin: 2px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QPushButton {{
                color: {btn_color};
            }}
            QPushButton:hover {{
                background-color: {btn_hover};
                color: {t['accent']};
            }}
            QMenu {{
                background-color: {t['bg_panel']};
                border: 1px solid {t['border']};
                padding: 5px;
            }}
            QMenu::item {{
                padding: 6px 20px;
                border-radius: 4px;
                color: {t['text_main']};
            }}
            QMenu::item:selected {{
                background-color: {t['accent']};
                color: white;
            }}
        """)
        self.metadata_panel.apply_theme(t, self.dark_mode)
        self.apply_fab_style()




    def apply_fab_style(self):
        if not hasattr(self, 'fab_container'):
            return
        t = self.get_theme()

        icon_color = "#F5F6F8" if self.dark_mode else "#111111"
        fab_bg = "#2b3139" if self.dark_mode else "#f7f3eb"
        fab_hover = "#36404b" if self.dark_mode else "#ece4d7"
        self.sort_fab.setIcon(create_glyph_icon("⇅", icon_color, size=128))
        self.sort_fab.setToolTip(self.tr('sort'))
        self.refresh_fab.setIcon(create_glyph_icon("↻", icon_color, size=128))
        self.refresh_fab.setToolTip(self.tr('refresh'))

        self.fab_container.setStyleSheet(
            f"""
            QFrame#fab_container {{
                background-color: {fab_bg};
                border: 1px solid {t['border']};
                border-radius: 16px;
            }}
            """
        )

        btn_style = f"""
            QToolButton#fab_btn {{
                background-color: transparent;
                border: none;
                border-radius: 12px;
                color: {t['text_main']};
            }}
            QToolButton#fab_btn:hover {{
                background-color: {fab_hover};
            }}
            QToolButton#fab_btn:pressed {{
                background-color: {fab_hover};
            }}
            QToolButton#fab_btn::menu-indicator {{
                image: none;
            }}
        """
        self.sort_fab.setStyleSheet(btn_style)
        self.refresh_fab.setStyleSheet(btn_style)
        if hasattr(self, 'fab_separator'):
            self.fab_separator.setStyleSheet(f"background-color: {t['border']};")




if __name__ == "__main__":
    from PyQt6.QtCore import qInstallMessageHandler, QtMsgType

    def qt_message_handler(mode, context, message):
        # 彻底不显示这行警告
        if "QFont::setPointSize: Point size <= 0 (-1)" in message:
            return
        if mode != QtMsgType.QtDebugMsg:
            print(message)

    qInstallMessageHandler(qt_message_handler)

    if sys.platform.startswith("win"):
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AI_ImageViewer_Basic.main_cards")
        except Exception:
            pass

    app = QApplication(sys.argv)
    font = app.font()
    font.setFamily("Segoe UI")
    app.setFont(font)

    # 如果你有 app.ico，可以顺便让运行时窗口也用同一个图标
    def resource_path(relative_path: str) -> str:
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, relative_path)

    icon_path = resource_path("app.ico")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    else:
        app_icon = QIcon()

    win = MainWindow()
    if not app_icon.isNull():
        win.setWindowIcon(app_icon)
    win.show()
    QTimer.singleShot(0, lambda: win.apply_initial_window_geometry(force=True))
    QTimer.singleShot(0, win.center_on_available_screen)
    sys.exit(app.exec())
