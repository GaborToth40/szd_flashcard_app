import logging
import sqlite3
from datetime import date

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QSpinBox, QLineEdit,
                               QStackedWidget)
from PySide6.QtGui import QFont

from translation import get
from database import insert_review_record, fetch_decks


class LearningWindow(QWidget):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection

        self.setWindowTitle(get("learning"))
        self.resize(400, 300)

        self.stacked_widget = QStackedWidget()
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stacked_widget)

        self.setup_screen = QWidget()
        self.session_screen = QWidget()

        self.init_setup_ui()
        self.init_session_ui()

        self.stacked_widget.addWidget(self.setup_screen)
        self.stacked_widget.addWidget(self.session_screen)

        self.cards = []
        self.current_index = 0

        self.last_quality = 0

    def init_setup_ui(self):
        layout = QVBoxLayout(self.setup_screen)

        layout.addWidget(QLabel(get("study_settings")))

        self.deck_combo = QComboBox()
        self.load_decks()
        layout.addWidget(QLabel(get("select_deck")))
        layout.addWidget(self.deck_combo)

        self.num_spin = QSpinBox()
        self.num_spin.setRange(1, 100)
        self.num_spin.setValue(10)
        layout.addWidget(QLabel(get("number_of_cards")))
        layout.addWidget(self.num_spin)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems([get("learning"), get("practice"), get("test")])
        layout.addWidget(QLabel(get("mode")))
        layout.addWidget(self.mode_combo)

        self.start_button = QPushButton(get("start_session"))
        self.start_button.clicked.connect(self.start_session)
        layout.addWidget(self.start_button)

    def init_session_ui(self):
        layout = QVBoxLayout(self.session_screen)

        self.card_question = QLabel(get("question"))
        self.card_question.setFont(QFont("Arial", 14, QFont.Bold))
        self.card_question.setWordWrap(True)
        layout.addWidget(self.card_question)

        self.answer_input = QLineEdit()
        layout.addWidget(self.answer_input)

        self.card_answer = QLabel("")
        self.card_answer.setWordWrap(True)
        self.card_answer.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.card_answer)

        self.card_note = QLabel("")
        self.card_note.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.card_note)

        btn_layout = QHBoxLayout()
        self.reveal_button = QPushButton(get("check_reveal"))
        self.reveal_button.clicked.connect(self.check_or_reveal)

        self.next_button = QPushButton(get("next"))
        self.next_button.clicked.connect(self.next_card)
        self.next_button.setEnabled(False)

        self.end_button = QPushButton(get("end_session"))
        self.end_button.clicked.connect(self.end_session)

        btn_layout.addWidget(self.reveal_button)
        btn_layout.addWidget(self.next_button)
        btn_layout.addWidget(self.end_button)
        layout.addLayout(btn_layout)

        self.stats_label = QLabel(get("progress"))
        layout.addWidget(self.stats_label)


    def load_decks(self):
        self.deck_combo.clear()
        decks = fetch_decks(self.connection)
        for deck in decks:
            self.deck_combo.addItem(deck["name"], deck["deck_id"])


    def start_session(self):
        mode_index = self.mode_combo.currentIndex()
        deck_id = self.deck_combo.currentData()
        limit = self.num_spin.value()

        try:
            if mode_index == 2:
                query = "SELECT * FROM cards WHERE deck_id = ? AND next_review <= ? LIMIT ?"
                self.cards = self.connection.execute(query, (deck_id, date.today().isoformat(), limit)).fetchall()
            elif mode_index == 1:
                query = "SELECT * FROM cards WHERE deck_id = ? ORDER BY RANDOM() LIMIT ?"
                self.cards = self.connection.execute(query, (deck_id, limit)).fetchall()
            else:
                query = "SELECT * FROM cards WHERE deck_id = ? LIMIT ?"
                self.cards = self.connection.execute(query, (deck_id, limit)).fetchall()
        except sqlite3.Error as e:
            logging.error(f"Failed to fetch cards for session: {e}")
            return

        if self.cards:
            self.current_index = 0
            self.stacked_widget.setCurrentIndex(1)
            self.show_card()
        else:
            self.card_question.setText(get("no_cards_found"))

    def show_card(self):
        card = self.cards[self.current_index]
        self.card_question.setText(card["question"])
        self.card_answer.hide()
        self.card_note.hide()
        self.answer_input.clear()
        self.answer_input.setStyleSheet("")

        self.answer_input.setVisible(self.mode_combo.currentIndex() != 0)

        self.stats_label.setText(f"{get("progress")}: {self.current_index + 1}/{len(self.cards)}")

    def check_or_reveal(self):
        card = self.cards[self.current_index]
        self.card_answer.setText(f"{get('correct_answer')}{card['answer']}")
        self.card_answer.show()
        self.card_note.setText(f"{get('note')}: {card['note']}")
        self.card_note.show()

        if self.mode_combo.currentIndex() == 2:
            user_answer = self.answer_input.text().strip().lower()
            real_answer = card["answer"].strip().lower()
            if user_answer == real_answer:
                self.answer_input.setStyleSheet("background-color: #c8e6c9;")
                self.last_quality = 2
            else:
                self.answer_input.setStyleSheet("background-color: #ffcdd2;")
                self.last_quality = 1

        self.next_button.setEnabled(True)
        self.reveal_button.setEnabled(False)


    def next_card(self):
        if self.mode_combo.currentIndex() == 2:
            card = self.cards[self.current_index]
            old_interval = card["interval"]
            old_weight = card["weight"]

            if self.last_quality == 1:
                new_interval = 1
                new_weight = max(1.3, old_weight - 0.2)
            elif self.last_quality == 2:
                new_interval = max(old_interval + 1, round(old_interval * old_weight))
                new_weight = old_weight
            else:
                new_interval = round(old_interval * old_weight * 1.3)
                new_weight = old_weight + 0.1

            query = """
                        UPDATE cards 
                        SET interval = ?, weight = ?, next_review = date('now', '+' || ? || ' days')
                        WHERE card_id = ?
                    """
            try:
                with self.connection:
                    self.connection.execute(query, (new_interval, new_weight, new_interval, card["card_id"]))
                    insert_review_record(self.connection, card["card_id"], self.last_quality)
            except sqlite3.Error as e:
                logging.error(f"Failed to update card {card['card_id']} after review: {e}")

        self.current_index += 1

        if self.current_index < len(self.cards):
            self.show_card()
        else:
            self.stacked_widget.setCurrentIndex(0)
            self.current_index = 0

        self.next_button.setEnabled(False)
        self.reveal_button.setEnabled(True)

    def end_session(self):
        self.stacked_widget.setCurrentIndex(0)
        self.cards = []
        self.current_index = 0
        self.next_button.setEnabled(False)
        self.reveal_button.setEnabled(True)
