from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from translation import get


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(get("about"))
        self.resize(350, 250)

        layout = QVBoxLayout(self)

        title = QLabel("Flashcard Application")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        description = QLabel(get("desktop_flashcard"))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)

        layout.addStretch()
