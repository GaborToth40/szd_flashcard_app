import logging
import spacy
from spacy.cli import download
from youtube_transcript_api import YouTubeTranscriptApi
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel,
                               QMessageBox, QListWidget, QListWidgetItem, QDialog, QStackedWidget,
                               QRadioButton, QHBoxLayout, QLineEdit)

from translation import get
from database import fetch_cards, insert_card

try:
    nlp = spacy.load("en_core_web_sm")
    logging.info("spacy has been loaded")
except OSError:
    try:
        download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
        logging.info("\"en_core_web_sm\" for spacy has been installed")
    except (OSError, SystemExit) as e:
        nlp = None
        logging.error(f"Error during the initialization of spacy: {e}")

class SearchWindow(QWidget):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection

        self.setWindowTitle(get("search"))
        self.resize(500, 600)

        layout = QVBoxLayout(self)

        radio_layout = QHBoxLayout()
        self.radio_manual = QRadioButton(get("manual"))
        self.radio_auto = QRadioButton(get("automatic"))
        self.radio_manual.setChecked(True)

        radio_layout.addWidget(self.radio_manual)
        radio_layout.addWidget(self.radio_auto)
        layout.addLayout(radio_layout)

        self.input_stack = QStackedWidget()
        layout.addWidget(self.input_stack)

        self.manual_widget = QWidget()
        manual_layout = QVBoxLayout(self.manual_widget)
        manual_layout.setContentsMargins(0, 0, 0, 0)
        self.text_input = QTextEdit()
        manual_layout.addWidget(self.text_input)
        self.input_stack.addWidget(self.manual_widget)

        self.auto_widget = QWidget()
        auto_layout = QVBoxLayout(self.auto_widget)
        auto_layout.setContentsMargins(0, 0, 0, 0)

        auto_layout.addWidget(QLabel(get("youtube_id")))

        self.auto_input = QLineEdit()
        auto_layout.addWidget(self.auto_input)

        auto_layout.addStretch()
        self.input_stack.addWidget(self.auto_widget)

        self.radio_manual.toggled.connect(self.toggle_input_mode)

        self.scan_button = QPushButton(get("check_words"))
        self.scan_button.clicked.connect(self.run_scan)
        layout.addWidget(self.scan_button)

        layout.addWidget(QLabel(get("new_words_found")))
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)

        self.add_button = QPushButton(get("add_to_database"))
        self.add_button.setEnabled(False)
        self.add_button.clicked.connect(self.add_to_db)
        layout.addWidget(self.add_button)

        self.show_list_button = QPushButton(get("show_word_list"))
        self.show_list_button.setEnabled(False)
        self.show_list_button.clicked.connect(self.show_word_list)
        layout.addWidget(self.show_list_button)

        self.discovered_words = []


    def toggle_input_mode(self):
        if self.radio_manual.isChecked():
            self.input_stack.setCurrentIndex(0)
        else:
            self.input_stack.setCurrentIndex(1)


    def run_scan(self):
        if nlp is None:
            QMessageBox.critical(self, get("error"),"spacy model 'en_core_web_sm' not found."
                                               "\nRun \"python -m spacy download en_core_web_sm to\" download")
            return

        if self.radio_manual.isChecked():
            raw_text = self.text_input.toPlainText().strip()
        else:
            video_id = self.auto_input.text().strip()
            if not video_id: return

            try:
                ytt_api = YouTubeTranscriptApi()
                text = ytt_api.fetch(video_id)

                cleaned_text: str = ""
                for snippet in text:
                    cleaned_text += snippet.text
                    cleaned_text += " "
                raw_text = cleaned_text

            except Exception as e:
                QMessageBox.warning(self, get("youtube_error"), f"{get("could_not_fetch_transcipt") }{str(e)}")
                return

        if not raw_text:
            return

        existing_cards = fetch_cards(self.connection)

        known_lemmas = {card["question"].lower().strip() for card in existing_cards}

        input_string = nlp(raw_text.lower())
        new_lemmas = set()
        for token in input_string:
            if token.is_alpha and token.pos_ != "PROPN" and not token.is_stop:
                lemma = token.lemma_
                if len(lemma) > 2 and lemma not in known_lemmas:
                    new_lemmas.add(lemma)

        self.discovered_words = sorted(list(new_lemmas))
        self.results_list.clear()
        for word in self.discovered_words:
            item = QListWidgetItem(word)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.results_list.addItem(item)
        self.add_button.setEnabled(len(self.discovered_words) > 0)

        self.show_list_button.setEnabled(len(self.discovered_words) > 0)


    def add_to_db(self):
        added_count = 0
        for i in range(self.results_list.count()):
            item = self.results_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                insert_card(self.connection, item.text(), "", "", 2.5, 1)
                added_count += 1

        QMessageBox.information(self, get("success"), f" {added_count} {get("words_added")}.")
        self.results_list.clear()
        self.discovered_words = []
        self.add_button.setEnabled(False)
        self.show_list_button.setEnabled(False)


    def show_word_list(self):
        raw_text = "\n".join(self.discovered_words)

        dialog = QDialog(self)
        dialog.setWindowTitle(get("word_list"))
        dlg_layout = QVBoxLayout(dialog)

        text_area = QTextEdit()
        text_area.setPlainText(raw_text)
        text_area.setReadOnly(True)

        dlg_layout.addWidget(text_area)
        dialog.resize(300, 400)
        dialog.exec()
