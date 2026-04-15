from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
                               QComboBox, QCheckBox, QMessageBox)

from translation import get
from database import insert_card, fetch_cards, delete_card, update_card, fetch_decks

class CardsWindow(QWidget):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection

        self.setWindowTitle(get("flashcards"))
        self.resize(800, 400)

        self.next_id = 1

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([get("select"), get("id"), get("question"), get("answer"), get("note"), get("weight"), get("deck")])
        layout.addWidget(self.table)

        buttons_layout = QHBoxLayout()
        layout.addLayout(buttons_layout)

        self.save_button = QPushButton(get("save"))
        self.save_button.clicked.connect(self.save_clicked)
        buttons_layout.addWidget(self.save_button)

        self.delete_button = QPushButton(get("delete"))
        self.delete_button.clicked.connect(self.delete_selected_rows)
        buttons_layout.addWidget(self.delete_button)

        self.load_decks()
        self.load_cards()

        self.table.setColumnHidden(1, True)

    def showEvent(self, event):
        self.load_decks()
        self.load_cards()
        super().showEvent(event)

    def load_decks(self):
        self.decks = fetch_decks(self.connection)


    def load_cards(self):
        self.table.setRowCount(0)
        cards = fetch_cards(self.connection)

        for card in cards:
            self.add_table_row(
                card["card_id"],
                card["question"],
                card["answer"],
                card["note"],
                card["weight"],
                card["deck_id"]
            )

        if not self.is_last_row_empty():
            self.add_empty_row()

    def add_table_row(self, card_id, question, answer, note, weight, deck_id=None):
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setCellWidget(row, 0, QCheckBox())
        self.table.setItem(row, 1, QTableWidgetItem(str(card_id)))
        self.table.setItem(row, 2, QTableWidgetItem(question))
        self.table.setItem(row, 3, QTableWidgetItem(answer))
        self.table.setItem(row, 4, QTableWidgetItem(note))
        self.table.setItem(row, 5, QTableWidgetItem(str(weight)))
        combo = QComboBox()
        for deck in self.decks:
            combo.addItem(deck["name"], deck["deck_id"])
        if deck_id:
            index = next((i for i, d in enumerate(self.decks) if d["deck_id"] == deck_id), 0)
            combo.setCurrentIndex(index)
        self.table.setCellWidget(row, 6, combo)

    def add_empty_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setCellWidget(row, 0, QCheckBox())
        self.table.setItem(row, 1, QTableWidgetItem(""))
        for col in range(2, 6):
            self.table.setItem(row, col, QTableWidgetItem())
        combo = QComboBox()
        for deck in self.decks:
            combo.addItem(deck["name"], deck["deck_id"])
        self.table.setCellWidget(row, 6, combo)

    def save_clicked(self):
        for row in range(self.table.rowCount()):
            card_id_item = self.table.item(row, 1)
            card_id_text = card_id_item.text().strip() if card_id_item else ""
            card_id = int(card_id_text) if card_id_text else None
            question = self.table.item(row, 2).text().strip()
            answer = self.table.item(row, 3).text().strip()
            note = self.table.item(row, 4).text().strip()
            weight_text = self.table.item(row, 5).text().strip()
            try:
                weight = float(weight_text) if weight_text else 0.0
            except ValueError:
                weight = 0.0

            combo = self.table.cellWidget(row, 6)
            deck_id = combo.currentData() if isinstance(combo, QComboBox) else None

            if not question and not answer:
                continue

            if card_id:
                update_card(self.connection, card_id, question, answer, note, weight, deck_id)
            else:
                insert_card(self.connection, question, answer, note, weight, deck_id)

        self.load_cards()


    def delete_selected_rows(self):
        reply = QMessageBox.question(self, get("confirm"), "Are you sure you want to delete the selected cards?")
        if reply != QMessageBox.StandardButton.Yes:
            return
        for row in reversed(range(self.table.rowCount())):
            checkbox = self.table.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                card_id_item = self.table.item(row, 1)
                if card_id_item and card_id_item.text().strip():
                    delete_card(self.connection, int(card_id_item.text()))
                self.table.removeRow(row)

        if not self.is_last_row_empty():
            self.add_empty_row()


    def is_last_row_empty(self):
        if self.table.rowCount() == 0:
            return False
        last_row = self.table.rowCount() - 1
        item = self.table.item(last_row, 2)
        return not (item and item.text().strip())
