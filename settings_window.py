from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QPushButton, QMessageBox

from translation import set_language, get_language
from translation import get

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(get("settings"))
        self.resize(400, 200)

        layout = QVBoxLayout(self)

        language_layout = QHBoxLayout()
        language_layout.addWidget(QLabel(get("language")))

        self.language_combo = QComboBox()
        self.language_combo.addItems(["Hungarian", "English"])
        language_layout.addWidget(self.language_combo)

        language_layout.addStretch()
        layout.addLayout(language_layout)
        layout.addStretch()

        self.save_button = QPushButton(get("save_settings"))
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

    def save_settings(self):
        language_map = {"English": "en", "Hungarian": "hu"}
        new_language = language_map[self.language_combo.currentText()]
        if new_language != get_language():
            set_language(new_language)
            QMessageBox.information(self, get("settings"),
                                    f"{get('successfully_saved')}\n{get('please_restart')}")
        else:
            QMessageBox.information(self, get("settings"), get("successfully_saved"))

        self.close()


    def show(self):
        language_display = {"en": "English", "hu": "Hungarian"}
        current = language_display.get(get_language(), "English")
        self.language_combo.setCurrentText(current)
        super().show()
