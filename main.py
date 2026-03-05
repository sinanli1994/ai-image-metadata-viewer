import sys
import os
import re
import json
import traceback
import send2trash
from PIL import Image

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QSplitter, QTextBrowser, QFileDialog,
    QStackedWidget, QScrollArea, QToolBar, QMessageBox,
    QFrame, QPushButton, QSizePolicy, QAbstractItemView,
    QToolButton, QMenu
)
import PyQt6.QtCore
from PyQt6.QtCore import QPoint
from PyQt6.QtGui import (
    QPixmap, QIcon, QAction, QActionGroup, QDragEnterEvent, QDropEvent,
    QImage, QResizeEvent, QColor, QPainter,
    QShortcut, QKeySequence
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QUrl, QTimer, QSettings


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
        "bg_main": "#ffffff",
        "bg_panel": "#fcfcfc",
        "text_main": "#333333",
        "text_sub": "#666666",
        "accent": "#0067c0",
        "border": "#e5e5e5",
        "hover": "#f0f0f0",
        "selected": "#e8f1fa",
        "prompt_bg": "#f0f6ff",
        "neg_bg": "#fff5f5",
        "code_bg": "#f7f7f7"
    }

    DARK = {
        "bg_main": "#202020",
        "bg_panel": "#2b2b2b",
        "text_main": "#e0e0e0",
        "text_sub": "#aaaaaa",
        "accent": "#4cc2ff",
        "border": "#3d3d3d",
        "hover": "#333333",
        "selected": "#3a3a3a",
        "prompt_bg": "#2a3a4a",
        "neg_bg": "#4a2a2a",
        "code_bg": "#333333"
    }


# --- 多语言字典 ---
TRANSLATIONS = {
    'en': {
        'title': "AI Image Metadata Viewer (Basic) v1.1.0",
        'open_file': "Open Image",
        'open_folder': "Open Folder",
        'clear': "Clear All",
        'back': "Grid View",
        'theme': "Theme",
        'lang_btn': "Language",
        'drag_hint': "Drop images / folders here to view",
        'preview': "Preview",
        'file_info': "Metadata",
        'filename': "File:",
        'size': "Size:",
        'model': "Model",
        'prompt': "Prompt",
        'negative': "Negative",
        'params': "Settings",
        'copy_btn': "Copy",
        'no_data': "No Metadata Detected",
        'no_data_desc': "This image does not contain generation data.",
        'comfy_err': "ComfyUI Parse Error",
        'copied': "Copied!",
        'width': "W",
        'height': "H",
        'cleared': "List cleared",
        'lora': "LoRA",
        'delete': "Delete",
        'delete_confirm_title': "Delete Image",
        'delete_confirm_one': "Delete this image from disk?\n{0}",
        'delete_error': "Failed to delete some files.",
        'deleted': "Deleted",
        'sort': "Sort",
        'sort_name': "Name (A → Z)",
        'sort_mtime': "Modified Time (Newest)",
    },
    'cn': {
        'title': "AI 图片元数据查看器 (基础版) v1.1.0",
        'open_file': "打开图片",
        'open_folder': "打开文件夹",
        'clear': "清空列表",
        'back': "网格视图",
        'theme': "切换主题",
        'lang_btn': "语言",
        'drag_hint': "拖入图片 / 文件夹查看元数据",
        'preview': "预览",
        'file_info': "元数据详情",
        'filename': "文件:",
        'size': "尺寸:",
        'model': "基础模型",
        'prompt': "正向提示词",
        'negative': "负面提示词",
        'params': "生成参数",
        'copy_btn': "复制",
        'no_data': "未检测到元数据",
        'no_data_desc': "该图片可能不是原图或已被清理信息。",
        'comfy_err': "ComfyUI 解析错误",
        'copied': "已复制！",
        'width': "宽",
        'height': "高",
        'cleared': "列表已清空",
        'lora': "LoRA",
        'delete': "删除图片",
        'delete_confirm_title': "删除图片",
        'delete_confirm_one': "从磁盘中删除这张图片？\n{0}",
        'delete_error': "部分文件删除失败。",
        'deleted': "已删除",
        'sort': "排序",
        'sort_name': "按名称",
        'sort_mtime': "按修改时间",
    },
    'tc': {
        'title': "AI 圖片元數據查看器 (基礎版) v1.1.0",
        'open_file': "打開圖片",
        'open_folder': "打開文件夾",
        'clear': "清空列表",
        'back': "網格視圖",
        'theme': "切換主題",
        'lang_btn': "語言",
        'drag_hint': "拖入圖片 / 文件夾查看元數據",
        'preview': "預覽",
        'file_info': "元數據詳情",
        'filename': "文件:",
        'size': "尺寸:",
        'model': "基礎模型",
        'prompt': "正向提示詞",
        'negative': "負面提示詞",
        'params': "生成參數",
        'copy_btn': "複製",
        'no_data': "未檢測到元數據",
        'no_data_desc': "該圖片可能不是原圖或已被清理信息。",
        'comfy_err': "ComfyUI 解析錯誤",
        'copied': "已複製！",
        'width': "寬",
        'height': "高",
        'cleared': "列表已清空",
        'lora': "LoRA",
        'delete': "刪除圖片",
        'delete_confirm_title': "刪除圖片",
        'delete_confirm_one': "從磁盤中刪除這張圖片？\n{0}",
        'delete_error': "部分文件刪除失敗。",
        'deleted': "已刪除",
        'sort': "排序",
        'sort_name': "按名稱",
        'sort_mtime': "按修改時間",
    },
    'jp': {
        'title': "AI 画像メタデータビューア (Basic) v1.1.0",
        'open_file': "画像を開く",
        'open_folder': "フォルダを開く",
        'clear': "リストをクリア",
        'back': "グリッド表示",
        'theme': "テーマ切替",
        'lang_btn': "言語",
        'drag_hint': "ここに画像/フォルダをドロップ",
        'preview': "プレビュー",
        'file_info': "メタデータ",
        'filename': "ファイル:",
        'size': "サイズ:",
        'model': "モデル",
        'prompt': "プロンプト",
        'negative': "ネガティブ",
        'params': "生成パラメータ",
        'copy_btn': "コピー",
        'no_data': "メタデータなし",
        'no_data_desc': "この画像には生成データが含まれていません。",
        'comfy_err': "ComfyUI 解析エラー",
        'copied': "コピーしました！",
        'width': "幅",
        'height': "高",
        'cleared': "リストをクリアしました",
        'lora': "LoRA",
        'delete': "削除",
        'delete_confirm_title': "画像の削除",
        'delete_confirm_one': "この画像をディスクから削除しますか？\n{0}",
        'delete_error': "一部のファイルの削除に失敗しました。",
        'deleted': "削除しました",
        'sort': "並び替え",
        'sort_name': "名前順",
        'sort_mtime': "更新日時（新しい順）",
    },
    'kr': {
        'title': "AI 이미지 메타데이터 뷰어 (Basic) v1.1.0",
        'open_file': "이미지 열기",
        'open_folder': "폴더 열기",
        'clear': "목록 지우기",
        'back': "그리드 보기",
        'theme': "테마 변경",
        'lang_btn': "언어",
        'drag_hint': "이미지 / 폴더를 여기에 드롭하세요",
        'preview': "미리보기",
        'file_info': "메타데이터",
        'filename': "파일:",
        'size': "크기:",
        'model': "모델",
        'prompt': "프롬프트",
        'negative': "네거티브",
        'params': "생성 파라미터",
        'copy_btn': "복사",
        'no_data': "메타데이터 없음",
        'no_data_desc': "이 이미지에는 생성 데이터가 포함되어 있지 않습니다.",
        'comfy_err': "ComfyUI 파싱 오류",
        'copied': "복사되었습니다!",
        'width': "너비",
        'height': "높이",
        'cleared': "목록 지워짐",
        'lora': "LoRA",
        'delete': "삭제",
        'delete_confirm_title': "이미지 삭제",
        'delete_confirm_one': "이 이미지를 디스크에서 삭제하시겠습니까?\n{0}",
        'delete_error': "일부 파일을 삭제하지 못했습니다.",
        'deleted': "삭제됨",
        'sort': "정렬",
        'sort_name': "이름순",
        'sort_mtime': "수정 시간(최신순)",
    }
}

def create_glyph_icon(glyph: str, color: str, size: int = 18) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    
    font = painter.font()
    font.setFamily("Segoe UI Symbol")
    font.setPixelSize(int(size * 0.95))
    painter.setFont(font)
    
    painter.setPen(QColor(color))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, glyph)
    painter.end()
    return QIcon(pixmap)

def create_emoji_icon(emoji_char, size=64, color: str | None = None):
    """生成 emoji 图标，可选指定颜色（用于清空/删除按钮红色图标）"""
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("AI_Tools", "AI_ImageViewer_Basic")
        self.lang = self.settings.value("language", "en", type=str)
        self.dark_mode = self.settings.value("theme", False, type=bool)
        self.sort_mode = self.settings.value("sort_mode", "name_natural", type=str)

        self.setWindowTitle("AI Image Viewer Basic v1.1.0")
        self.resize(1300, 850)
        self.setAcceptDrops(True)

        self.loader_thread = None
        self.current_image_path = None
        self.current_file_list = []
        self.current_index = -1
        self.current_pos_text = ""
        self.current_neg_text = ""
        self.last_html = ""

        # 网格相关参数：高度固定，最小宽度，用来做自适应铺满
        self.grid_item_height = 260
        self.grid_item_min_width = 220  # 最小宽度



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
        self.setup_shortcuts()  # 全局快捷键

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

    def show_toast(self, message):
        self.toast_label.setText(message)
        self.toast_label.adjustSize()
        x = (self.width() - self.toast_label.width()) // 2
        y = self.height() - 100
        self.toast_label.move(x, y)
        self.toast_label.show()
        self.toast_label.raise_()
        QTimer.singleShot(2000, self.toast_label.hide)

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

        # 左侧：打开图片 / 文件夹
        self.action_file = QAction(self.tr('open_file'), self)
        self.action_file.setIcon(create_emoji_icon("📄"))
        self.action_file.triggered.connect(self.open_files_dialog)
        self.toolbar.addAction(self.action_file)

        self.action_folder = QAction(self.tr('open_folder'), self)
        self.action_folder.setIcon(create_emoji_icon("📂"))
        self.action_folder.triggered.connect(self.open_folder_dialog)
        self.toolbar.addAction(self.action_folder)

        self.toolbar.addSeparator()

        # 网格视图（返回）
        self.back_action = QAction(self.tr('back'), self)
        self.back_action.setIcon(create_emoji_icon("🔙"))
        self.back_action.triggered.connect(self.show_grid)
        self.back_action.setEnabled(False)
        self.toolbar.addAction(self.back_action)



        # 删除图片按钮
        self.action_delete = QAction(self.tr('delete'), self)
        self.action_delete.setIcon(create_emoji_icon("🗑", color="#ff4d4f"))
        self.action_delete.triggered.connect(self.delete_current_image)
        self.toolbar.addAction(self.action_delete)

        # 中间空白撑开
        empty = QWidget()
        empty.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(empty)

        # 右侧：语言 (QMenu) / 主题 / 清空列表
        from PyQt6.QtWidgets import QMenu, QToolButton

        self.lang_action = QAction(self.tr('lang_btn'), self)
        self.lang_action.setIcon(create_emoji_icon("🌐"))
        
        # 创建菜单
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
        
        # 将 action 对应的 widget 设置为弹出菜单模式
        widget = self.toolbar.widgetForAction(self.lang_action)
        if isinstance(widget, QToolButton):
            widget.setMenu(self.lang_menu)
            widget.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.theme_action = QAction(self.tr('theme'), self)
        self.theme_action.setIcon(create_emoji_icon("🌗"))
        self.theme_action.triggered.connect(self.toggle_theme)
        self.toolbar.addAction(self.theme_action)

        # 清空列表：最右侧，用红色图标
        self.action_clear = QAction(self.tr('clear'), self)
        self.action_clear.setIcon(create_emoji_icon("🧹", color="#ff4d4f"))
        self.action_clear.triggered.connect(self.clear_all)
        self.toolbar.addAction(self.action_clear)

    # ---------- Grid View ----------
    def setup_grid_view(self):
        self.grid_page = QWidget()
        layout = QVBoxLayout(self.grid_page)
        layout.setContentsMargins(10, 10, 10, 0)

        self.hint_label = QLabel(self.tr('drag_hint'))
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.hint_label)

        self.list_widget = GridListWidget()
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setIconSize(QSize(220, 220))
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)

        # 更紧凑
        self.list_widget.setSpacing(3)
        self.list_widget.setUniformItemSizes(True)
        # 单选
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # 初始 gridSize，高度固定，宽度先用最小值
        self.list_widget.setGridSize(QSize(self.grid_item_min_width, self.grid_item_height))

        # 不换行 + 文本省略，避免长文件名撑高 item
        self.list_widget.setWordWrap(False)
        self.list_widget.setTextElideMode(Qt.TextElideMode.ElideMiddle)

        self.list_widget.itemDoubleClicked.connect(self.on_thumbnail_clicked)
        layout.addWidget(self.list_widget)
        
        # 初始状态：列表隐藏，显示提示文字（居中）
        self.list_widget.hide()
        
        self.stacked_widget.addWidget(self.grid_page)

        # 悬浮排序按钮
        self.sort_fab = QToolButton(self.grid_page)
        self.sort_fab.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.sort_fab.setToolTip(self.tr('sort'))
        self.sort_fab.setFixedSize(36, 36)
        self.sort_fab.setIconSize(QSize(18, 18))
        self.sort_fab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sort_fab.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.sort_fab.setObjectName("sort_fab")

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

        # 跟踪菜单的关闭时间，用于防止点击按钮时立即重新打开
        import time
        self._sort_menu_last_hide_time = 0.0
        self.sort_menu.aboutToHide.connect(lambda: setattr(self, '_sort_menu_last_hide_time', time.time()))

        # 绑定点击事件，改为自定义弹出位置
        self.sort_fab.clicked.connect(self.show_sort_menu)
        # 小切换动画：按下时图标缩小，松开后假恢复
        self.sort_fab.pressed.connect(lambda: self.sort_fab.setIconSize(QSize(13, 13)))
        self.sort_fab.released.connect(lambda: QTimer.singleShot(0, lambda: self.sort_fab.setIconSize(QSize(18, 18))))
        self.sort_fab.hide()

        # 初次显示时，延迟调整一次
        QTimer.singleShot(0, self.update_grid_for_width)
        QTimer.singleShot(0, self.position_sort_fab)

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

        self.btn_prev = QPushButton("◀")
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.setStyleSheet(nav_btn_style)
        self.btn_prev.clicked.connect(self.show_prev_image)
        img_layout.addWidget(self.btn_prev)

        # 使用自定义滚轮的 ImageScrollArea
        self.image_scroll = ImageScrollArea(owner=self)
        self.image_scroll.setWidgetResizable(True)
        self.image_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.image_label = QLabel("")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_scroll.setWidget(self.image_label)
        img_layout.addWidget(self.image_scroll)

        self.btn_next = QPushButton("▶")
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setStyleSheet(nav_btn_style)
        self.btn_next.clicked.connect(self.show_next_image)
        img_layout.addWidget(self.btn_next)

        self.splitter.addWidget(self.image_container)

        self.info_text = QTextBrowser()
        self.info_text.setOpenExternalLinks(False)
        self.info_text.anchorClicked.connect(self.on_link_clicked)
        self.info_text.setFrameShape(QFrame.Shape.NoFrame)
        self.splitter.addWidget(self.info_text)

        self.splitter.setStretchFactor(0, 70)
        self.splitter.setStretchFactor(1, 30)
        layout.addWidget(self.splitter)
        self.stacked_widget.addWidget(self.detail_page)

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



    # 备用 KeyEvent（有时候焦点在 QTextBrowser 用这个兜底）
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

    # ---------- 删除当前图片/选中图片 ----------
    # ---------- 删除当前图片 ----------
    def delete_current_image(self):
        """在磁盘中删除按当前选定的图片/当前展示的图片：
        """
        if not self.current_file_list:
            return

        target_path = None
        if self.stacked_widget.currentIndex() == 0:
            # 网格页：删除当前项
            item = self.list_widget.currentItem()
            if not item:
                return
            target_path = item.data(Qt.ItemDataRole.UserRole)
        else:
            # 详情页：删除当前张
            if self.current_index < 0 or self.current_index >= len(self.current_file_list):
                return
            target_path = self.current_file_list[self.current_index]

        if not target_path:
            return

        # 确认弹窗
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(self.tr('delete_confirm_title'))

        name = os.path.basename(target_path)
        msg.setText(self.tr('delete_confirm_one').format(name))

        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        ret = msg.exec()
        if ret != QMessageBox.StandardButton.Yes:
            return

        # 移入回收站
        error = False
        try:
            if os.path.exists(target_path):
                send2trash.send2trash(target_path)
        except Exception:
            error = True

        # 从内存列表中删掉
        old_index = self.current_index if self.current_index >= 0 else 0
        if target_path in self.current_file_list:
            self.current_file_list.remove(target_path)

        # 从 QListWidget 中删除对应 item
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == target_path:
                self.list_widget.takeItem(i)
                break

        # 更新界面
        if not self.current_file_list:
            # 全删光了，回到空网格
            self.current_index = -1
            self.image_label.clear()
            self.info_text.clear()
            self.hint_label.show()
            self.show_grid()
        else:
            # 还有图片，算一个新的 index
            new_index = min(old_index, len(self.current_file_list) - 1)
            self.current_index = new_index

            if self.stacked_widget.currentIndex() == 0:
                # 网格页：更新选中项
                next_path = self.current_file_list[new_index]
                for i in range(self.list_widget.count()):
                    item = self.list_widget.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == next_path:
                        self.list_widget.setCurrentItem(item)
                        self.list_widget.scrollToItem(item)
                        break
            else:
                # 详情页：跳到新的一张
                self.show_image_detail(self.current_file_list[new_index])

        # 提示
        if error:
            self.show_toast(self.tr('delete_error'))
        else:
            self.show_toast(self.tr('deleted'))

    # ---------- 清空全部 ----------
    def clear_all(self):
        # 停止 loader 线程
        if self.loader_thread and self.loader_thread.isRunning():
            self.loader_thread.stop()
        self.loader_thread = None



        # 清空状态
        self.current_file_list = []
        self.current_index = -1
        self.current_image_path = None
        self.last_html = ""
        self.current_pos_text = ""
        self.current_neg_text = ""

        # 清空 UI
        self.list_widget.clear()
        
        # 清空后：隐藏列表，显示提示（居中）
        self.list_widget.hide()
        self.hint_label.show()
        
        if hasattr(self, "sort_fab"):
            self.sort_fab.hide()
        
        self.image_label.clear()
        self.info_text.clear()

        # 回到网格页，禁用左右键快捷键
        self.stacked_widget.setCurrentIndex(0)
        self.back_action.setEnabled(False)
        self.shortcut_prev.setEnabled(False)
        self.shortcut_next.setEnabled(False)

        # 提示
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
            self.sort_name_action.setText(self.tr('sort_name'))
            self.sort_mtime_action.setText(self.tr('sort_mtime'))

        self.action_delete.setText(self.tr('delete'))
        self.hint_label.setText(self.tr('drag_hint'))
        self.hint_label.setStyleSheet(
            f"color: #aaa; font-family: {NativeTheme.FONT_FAMILY}; font-size: 24px; font-weight: 300;")
        if self.stacked_widget.currentIndex() == 1 and self.current_image_path:
            self.show_image_detail(self.current_image_path, keep_view=True)

    def on_link_clicked(self, url: QUrl):
        if url.toString() == 'copy_pos':
            QApplication.clipboard().setText(self.current_pos_text)
            self.show_toast(self.tr('copied'))
            self.info_text.setHtml(self.last_html)
        elif url.toString() == 'copy_neg':
            QApplication.clipboard().setText(self.current_neg_text)
            self.show_toast(self.tr('copied'))
            self.info_text.setHtml(self.last_html)

    # ---------- Resize ----------
    def resizeEvent(self, event: QResizeEvent):
        # 详情页调整图片
        if self.stacked_widget.currentIndex() == 1 and self.current_image_path:
            QTimer.singleShot(50, lambda: self.display_image_fit(self.current_image_path))
        # 列表页根据宽度自适应铺满
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
            if not urls: return
            
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
            elif not dropped_files:
                return
            elif len(dropped_files) == 1:
                p = dropped_files[0]
                self.load_from_folder_path(os.path.dirname(p))
                self.show_image_detail(p)
            else:
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
            self.load_images_list(files)
            self.show_image_detail(files[0])

    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.load_from_folder_path(folder)

    def position_sort_fab(self):
        if not hasattr(self, "sort_fab"): return
        if self.stacked_widget.currentIndex() != 0: return

        rect = self.list_widget.geometry()
        sb = self.list_widget.verticalScrollBar()
        sb_w = sb.sizeHint().width() if sb and sb.isVisible() else 0

        margin = 16
        x = rect.x() + rect.width() - sb_w - self.sort_fab.width() - margin
        x -= 4 # Small extra offset
        y = rect.y() + margin
        
        x = max(0, x)
        y = max(0, y)

        self.sort_fab.move(x, y)

    def set_sort_mode(self, mode):
        if mode not in ("name_natural", "mtime"): return
        if self.sort_mode == mode: return
        self.sort_mode = mode
        self.settings.setValue("sort_mode", mode)

        if self.sort_mode == "mtime":
            self.sort_mtime_action.setChecked(True)
        else:
            self.sort_name_action.setChecked(True)

        if not self.current_file_list:
            return

        self.current_file_list = self.apply_sort(self.current_file_list)

        selected_path = None
        cur_item = self.list_widget.currentItem()
        if cur_item:
            selected_path = cur_item.data(Qt.ItemDataRole.UserRole)

        self.list_widget.clear()
        self.hint_label.hide()
        self.list_widget.show()

        if self.loader_thread and self.loader_thread.isRunning():
            self.loader_thread.stop()

        self.loader_thread = ThumbnailLoader(self.current_file_list)
        self.loader_thread.thumbnail_loaded.connect(self.add_thumbnail_item)
        self.loader_thread.start()

        if selected_path and selected_path in self.current_file_list:
            idx = self.current_file_list.index(selected_path)
            QTimer.singleShot(200, lambda: self._select_grid_index(idx))

    def _select_grid_index(self, idx):
        if 0 <= idx < self.list_widget.count():
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
        self.load_images_list(files)
    def apply_sort(self, files):
        if not files:
            return []
        if self.sort_mode == "mtime":
            def safe_mtime(p):
                try: return os.path.getmtime(p)
                except: return 0
            return sorted(files, key=safe_mtime, reverse=True)
        else: # "name_natural"
            def natural_key(p):
                basename = os.path.basename(p).lower()
                return [int(text) if text.isdigit() else text for text in re.split(r'(\d+)', basename)]
            return sorted(files, key=natural_key)

    # ---------- 加载图片列表 ----------
    def load_images_list(self, file_paths):
        normalized = [os.path.normpath(p) for p in file_paths]
        seen = set()
        unique_paths = []
        for p in normalized:
            if p not in seen:
                seen.add(p)
                unique_paths.append(p)
                
        self.current_file_list = self.apply_sort(unique_paths)

        self.list_widget.clear()
        
        # 有数据时：显示列表，隐藏提示
        self.hint_label.hide()
        self.list_widget.show()

        if hasattr(self, "sort_fab"):
            if len(self.current_file_list) > 0 and self.stacked_widget.currentIndex() == 0:
                self.sort_fab.show()
            else:
                self.sort_fab.hide()

        if self.loader_thread and self.loader_thread.isRunning():
            self.loader_thread.stop()

        self.loader_thread = ThumbnailLoader(self.current_file_list)
        self.loader_thread.thumbnail_loaded.connect(self.add_thumbnail_item)
        self.loader_thread.start()
        self.show_grid()
        self.sort_fab.setVisible(len(self.current_file_list) > 0)

        # 加载新列表后，根据当前宽度再适配一次
        QTimer.singleShot(0, self.update_grid_for_width)

    def add_thumbnail_item(self, path, pixmap):
        filename = os.path.basename(path)

        # 极端长文件名截断
        if len(filename) > 30:
            filename_display = filename[:18] + "…" + filename[-8:]
        else:
            filename_display = filename

        item = QListWidgetItem(filename_display)
        item.setIcon(QIcon(pixmap))
        item.setData(Qt.ItemDataRole.UserRole, path)

        # 使用当前 gridSize 作为 sizeHint，保证高度统一
        item.setSizeHint(self.list_widget.gridSize())

        self.list_widget.addItem(item)

    def on_thumbnail_clicked(self, item):
        self.show_image_detail(item.data(Qt.ItemDataRole.UserRole))

    # ---------- 显示详情 ----------
    def show_image_detail(self, path, keep_view=False):
        if not path or not os.path.exists(path):
            return
            
        if hasattr(self, 'sort_fab'):
            self.sort_fab.hide()
        path = os.path.normpath(path)
        self.current_image_path = path
        if not keep_view:
            self.image_label.clear()

        self.stacked_widget.setCurrentIndex(1)
        self.back_action.setEnabled(True)
        QApplication.processEvents()

        # 详情页启用左右键快捷键
        self.shortcut_prev.setEnabled(True)
        self.shortcut_next.setEnabled(True)

        if path in self.current_file_list:
            self.current_index = self.current_file_list.index(path)
        else:
            self.current_index = -1
        self.update_nav_buttons()

        if not keep_view:
            QTimer.singleShot(50, lambda: self.display_image_fit(path))

        try:
            with Image.open(path) as img:
                self.parse_metadata(img, path, img.width, img.height)
        except:
            pass

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
        self.current_image_path = None
        self.image_label.clear()
        self.stacked_widget.setCurrentIndex(0)
        self.back_action.setEnabled(False)

        # 回到网格时禁用左右方向键快捷键
        self.shortcut_prev.setEnabled(False)
        self.shortcut_next.setEnabled(False)

        if 0 <= self.current_index < self.list_widget.count():
            item = self.list_widget.item(self.current_index)
            self.list_widget.setCurrentItem(item)
            self.list_widget.scrollToItem(item)
            
        QTimer.singleShot(0, self.update_grid_for_width)

    # ---------- 自适应网格尺寸 ----------
    def update_grid_for_width(self):
        if hasattr(self, "sort_fab"):
            if self.stacked_widget.currentIndex() == 0 and len(self.current_file_list) > 0:
                self.sort_fab.show()
                self.position_sort_fab()
            else:
                self.sort_fab.hide()

        if not hasattr(self, "list_widget"):
            return

        viewport_width = self.list_widget.viewport().width()
        if viewport_width <= 0:
            return

        spacing = self.list_widget.spacing()

        # 以“最小宽度”估算一行能放多少列
        min_unit = self.grid_item_min_width + spacing
        cols = max(1, viewport_width // min_unit)

        total_spacing = (cols + 1) * spacing
        available = max(50, viewport_width - total_spacing)
        item_w = available // cols

        # 给个下限，避免特别窄
        item_w = max(self.grid_item_min_width, item_w)

        new_size = QSize(item_w, self.grid_item_height)
        self.list_widget.setGridSize(new_size)

        # 同步更新所有 item 的 sizeHint
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setSizeHint(new_size)

    # ---------- 主题 + 元数据解析 ----------
    def get_theme(self):
        return NativeTheme.DARK if self.dark_mode else NativeTheme.LIGHT

    def parse_comfy_data(self, comfy_json):
        """
        解析 ComfyUI 的 JSON 数据：
        - 模型：只展示 Checkpoint / Diffusion Model 名称
        - KSampler 的参数
        - 正/负提示词（含 Qwen Edit 等节点）
        - LoRA（class_type 名里包含 'lora' 的节点）
        """
        t = self.get_theme()
        try:
            data = json.loads(comfy_json)
            pos, neg = "", ""
            params = {}
            sampler_node = None

            # 只保留你关心的：Checkpoint / Diffusion Model 名称
            model_lines = []

            # Qwen Edit 等节点里可能直接有 prompt / negative_prompt
            qwen_pos_candidate = ""
            qwen_neg_candidate = ""

            # LoRA 信息
            lora_infos = []

            for key, node in data.items():
                ctype = node.get('class_type', '')
                inputs = node.get('inputs', {}) or {}
                ctype_lower = ctype.lower()

                # 1) Checkpoint
                if 'checkpointloader' in ctype_lower:
                    name = (
                        inputs.get('ckpt_name')
                        or inputs.get('model_name')
                        or inputs.get('ckpt_path')
                        or ''
                    )
                    if name:
                        line = f"Checkpoint: {name}"
                        if line not in model_lines:
                            model_lines.append(line)

                # 2) Diffusion Model（这里把原本的 UNet 名字改成 Diffusion Model 展示）
                if 'unet' in ctype_lower:
                    name = (
                        inputs.get('unet_name')
                        or inputs.get('model')
                        or inputs.get('name')
                        or ''
                    )
                    if name:
                        line = f"Diffusion Model: {name}"
                        if line not in model_lines:
                            model_lines.append(line)

                # 3) KSampler：采样设置
                if 'ksampler' in ctype_lower:
                    sampler_node = node
                    for k in ['seed', 'steps', 'cfg', 'sampler_name', 'scheduler', 'denoise']:
                        if k in inputs:
                            params[k.capitalize()] = inputs[k]

                # 4) LoRA 节点
                if 'lora' in ctype_lower:
                    name = (
                        inputs.get('lora_name')
                        or inputs.get('model')
                        or inputs.get('name')
                        or ''
                    )
                    sm = inputs.get('strength_model', None)
                    sc = inputs.get('strength_clip', None)

                    parts = []
                    if name:
                        parts.append(str(name))
                    if sm is not None:
                        parts.append(f"model: {sm}")
                    if sc is not None:
                        parts.append(f"clip: {sc}")
                    if parts:
                        lora_infos.append(" | ".join(parts))

                # 5) Qwen Edit / Qwen 相关节点：从 inputs 里直接抓 prompt
                if 'qwen' in ctype_lower:
                    p = inputs.get('prompt') or inputs.get('text') or ""
                    n = inputs.get('negative_prompt') or inputs.get('negative') or ""
                    if isinstance(p, str) and p.strip():
                        qwen_pos_candidate = p.strip()
                    if isinstance(n, str) and n.strip():
                        qwen_neg_candidate = n.strip()

            # == 从 KSampler 链接反推 正/负提示 ==
            if sampler_node:
                inputs = sampler_node.get('inputs', {}) or {}
                for key, prompt_type in [('positive', 'pos'), ('negative', 'neg')]:
                    ref = inputs.get(key)
                    if ref:
                        text_node = data.get(str(ref[0]), {})
                        text = text_node.get('inputs', {}).get('text', '')
                        if prompt_type == 'pos':
                            pos = text
                        else:
                            neg = text

            # == 兜底：遍历 CLIPTextEncode ==
            if not pos and not neg:
                for key, node in data.items():
                    if 'cliptextencode' in node.get('class_type', '').lower():
                        text = node.get('inputs', {}).get('text', '')
                        if not text:
                            continue
                        if any(x in text.lower() for x in ['quality', 'nsfw', 'worst']):
                            if not neg:
                                neg = text
                        else:
                            if not pos:
                                pos = text

            # == 再兜底：如果还是空，用 Qwen 节点里的 prompt ==
            if (not pos) and qwen_pos_candidate:
                pos = qwen_pos_candidate
            if (not neg) and qwen_neg_candidate:
                neg = qwen_neg_candidate

            self.current_pos_text, self.current_neg_text = pos, neg

            copy_style = (
                f"text-decoration:none; font-size:12px; color:{t['accent']}; "
                f"border:1px solid {t['accent']}; padding:2px 8px; border-radius:10px;"
            )

            def make_header(title, copy_link=None):
                btn = f"<a href='{copy_link}' style='{copy_style}'>{self.tr('copy_btn')}</a>" if copy_link else ""
                return (
                    "<div style='margin-bottom:6px; margin-top:16px;'>"
                    f"<span style='color:{t['text_sub']}; font-weight:bold; font-size:13px;'>{title}</span> &nbsp; {btn}</div>"
                )

            html = ""

            # --- 模型信息（Checkpoint / Diffusion Model） ---
            if model_lines:
                html += make_header(self.tr('model'))
                html += (
                    f"<div style='color:{t['accent']}; font-weight:bold;'>"
                    + "<br>".join(model_lines) +
                    "</div>"
                )

            # --- LoRA 信息 ---
            if lora_infos:
                html += make_header(self.tr('lora'))
                html += (
                    f"<div style='background:{t['code_bg']}; padding:10px; "
                    f"border-radius:6px; color:{t['text_sub']}; font-family:Consolas; font-size:12px;'>"
                    + "<br>".join(lora_infos)
                    + "</div>"
                )

            # --- 正向提示 ---
            if pos:
                html += make_header(self.tr('prompt'), 'copy_pos')
                html += (
                    f"<div style='background:{t['prompt_bg']}; padding:10px; "
                    f"border-radius:6px; line-height:1.5;'>{pos}</div>"
                )

            # --- 负向提示 ---
            if neg:
                html += make_header(self.tr('negative'), 'copy_neg')
                html += (
                    f"<div style='background:{t['neg_bg']}; padding:10px; "
                    f"border-radius:6px; line-height:1.5;'>{neg}</div>"
                )

            # --- 采样参数 ---
            if params:
                html += make_header(self.tr('params'))
                html += (
                    f"<div style='background:{t['code_bg']}; padding:10px; border-radius:6px; "
                    f"color:{t['text_sub']}; font-family:Consolas; font-size:12px;'>"
                    + " | ".join([f"{k}: {v}" for k, v in params.items()])
                    + "</div>"
                )
            return html
        except:
            return self.tr('comfy_err')

    def parse_metadata(self, img, path, w, h):
        """
        解析元数据：
        - ComfyUI JSON（img.info['prompt']）
        - A1111 'parameters' 文本（包含 Model / LoRA 信息）
        """
        t = self.get_theme()
        self.current_pos_text, self.current_neg_text = "", ""

        filename = os.path.basename(path)
        if self.current_file_list and 0 <= self.current_index < len(self.current_file_list):
            filename += f" ({self.current_index+1}/{len(self.current_file_list)})"

        html = (
            f"<div style='font-size:16px; font-weight:bold; color:{t['text_main']};'>"
            f"{filename}</div>"
        )
        html += (
            f"<div style='color:{t['text_sub']}; margin-bottom:15px;'>{w} x {h} px</div>"
            f"<hr style='border:0; border-top:1px solid {t['border']};'>"
        )

        info = img.info
        # --- ComfyUI ---
        if 'prompt' in info:
            html += self.parse_comfy_data(info['prompt'])

        # --- A1111 / NovelAI 等 'parameters' ---
        elif 'parameters' in info:
            text = info['parameters']
            parts = text.split("Negative prompt:")
            pos = parts[0].strip()
            neg = ""
            if len(parts) > 1:
                if "Steps:" in parts[1]:
                    neg = parts[1].split("Steps:")[0].strip()
                else:
                    neg = parts[1].strip()

            # 解析 Steps: 后面的参数整体
            full_params = ""
            if "Steps:" in text:
                full_params = "Steps:" + text.split("Steps:", 1)[1].strip()

            # ---- 从参数中先拆出 Model: xxx ----
            model_name = ""
            if full_params:
                idx_m = full_params.find("Model:")
                if idx_m != -1:
                    after = full_params[idx_m + len("Model:"):].lstrip()
                    end_m = after.find(",")
                    if end_m != -1:
                        model_name = after[:end_m].strip()
                        # 把 Model: 这一段从参数字符串中删掉
                        full_params = (
                            full_params[:idx_m].rstrip(" ,") + ", " +
                            after[end_m + 1:].lstrip()
                        ).strip(" ,")
                    else:
                        # Model: 后面一直到结尾
                        model_name = after.strip()
                        full_params = full_params[:idx_m].rstrip(" ,")

            # ---- 再从剩余参数里拆出 LoRA 信息 ----
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

            self.current_pos_text, self.current_neg_text = pos, neg

            copy_style = (
                f"text-decoration:none; font-size:12px; color:{t['accent']}; "
                f"border:1px solid {t['accent']}; padding:2px 8px; border-radius:10px;"
            )

            def make_header(title, copy_link=None):
                btn = f"<a href='{copy_link}' style='{copy_style}'>{self.tr('copy_btn')}</a>" if copy_link else ""
                return (
                    "<div style='margin-bottom:6px; margin-top:16px;'>"
                    f"<span style='color:{t['text_sub']}; font-weight:bold; font-size:13px;'>{title}</span> &nbsp; {btn}</div>"
                )

            # --- 模型信息（和 ComfyUI 一致的样式） ---
            if model_name:
                html += make_header(self.tr('model'))
                html += (
                    f"<div style='color:{t['accent']}; font-weight:bold;'>{model_name}</div>"
                )

            # --- 正向提示 ---
            html += make_header(self.tr('prompt'), 'copy_pos')
            html += (
                f"<div style='background:{t['prompt_bg']}; padding:10px; "
                f"border-radius:6px; line-height:1.5;'>{pos}</div>"
            )

            # --- 负向提示 ---
            if neg:
                html += make_header(self.tr('negative'), 'copy_neg')
                html += (
                    f"<div style='background:{t['neg_bg']}; padding:10px; "
                    f"border-radius:6px; line-height:1.5;'>{neg}</div>"
                )

            # --- LoRA 列表 ---
            if lora_list:
                html += make_header(self.tr('lora'))
                html += (
                    f"<div style='background:{t['code_bg']}; padding:10px; "
                    f"border-radius:6px; color:{t['text_sub']}; font-family:Consolas; font-size:12px;'>"
                    + "<br>".join(lora_list)
                    + "</div>"
                )

            # --- 其它参数（已经不含 Model / LoRA） ---
            if params_display:
                html += make_header(self.tr('params'))
                html += (
                    f"<div style='background:{t['code_bg']}; padding:10px; border-radius:10px; "
                    f"color:{t['text_sub']}; font-family:Consolas; font-size:12px; line-height:1.5;'>{params_display}</div>"
                )

        else:
            html += (
                f"<p style='color:{t['text_sub']}; margin-top:20px;'>{self.tr('no_data_desc')}</p>"
            )

        self.last_html = html
        self.info_text.setHtml(html)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.settings.setValue("theme", self.dark_mode)
        self.apply_style()
        if self.stacked_widget.currentIndex() == 1 and self.current_image_path:
            self.show_image_detail(self.current_image_path, keep_view=True)

    def apply_style(self):
        t = self.get_theme()
        btn_color = "rgba(255,255,255,0.7)" if self.dark_mode else "rgba(0,0,0,0.5)"
        btn_hover = "rgba(255,255,255,0.1)" if self.dark_mode else "rgba(0,0,0,0.05)"

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
                border-radius: 4px;
                padding: 6px 10px;
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
                border-radius: 6px;
                padding: 3px;
                margin: 2px;
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
            QTextBrowser {{
                background-color: {t['bg_panel']};
                border-left: 1px solid {t['border']};
                padding: 20px;
                font-size: 14px;
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
                background: #ccc;
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
        self.apply_fab_style()

    def apply_fab_style(self):
        if not hasattr(self, 'sort_fab'): return
        t = self.get_theme()
        
        icon_color = "#F5F6F8" if self.dark_mode else "#111111"
        self.sort_fab.setIcon(create_glyph_icon("⇅", icon_color, size=72))
        self.sort_fab.setToolTip(self.tr('sort'))
        
        self.sort_fab.setStyleSheet(f"""
            QToolButton#sort_fab {{
                background-color: {t['bg_panel']};
                border: 1px solid {t['border']};
                border-radius: 12px;
                color: {t['text_main']};
            }}
            QToolButton#sort_fab:hover {{
                background-color: {t['hover']};
            }}
            QToolButton#sort_fab:pressed {{
                background-color: {t['hover']};
            }}
            QToolButton#sort_fab::menu-indicator {{
                image: none;
            }}
        """)


if __name__ == "__main__":
    from PyQt6.QtCore import qInstallMessageHandler, QtMsgType

    def qt_message_handler(mode, context, message):
        # 彻底不显示这行警告
        if "QFont::setPointSize: Point size <= 0 (-1)" in message:
            return
        if mode != QtMsgType.QtDebugMsg:
            print(message)

    qInstallMessageHandler(qt_message_handler)

    app = QApplication(sys.argv)
    font = app.font()
    font.setFamily("Segoe UI")
    app.setFont(font)

    # 如果你有 app.ico，可以顺便让运行时窗口也用同一个图标
    def resource_path(relative_path: str) -> str:
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    icon_path = resource_path("app.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    win = MainWindow()
    win.show()
    sys.exit(app.exec())
