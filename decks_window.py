import csv

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QCheckBox,
                               QPushButton, QFileDialog, QMessageBox)

from translation import get
from database import update_deck, delete_deck, fetch_decks, insert_deck, fetch_cards, insert_card


class DecksWindow(QWidget):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection

        self.setWindowTitle(get("decks"))
        self.resize(800, 400)

        self.next_id = 1

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([get("select"), get("id"), get("deck_name"), get("description"), get("number_of_cards")])
        layout.addWidget(self.table)

        self.load_decks()

        buttons_layout = QHBoxLayout()
        layout.addLayout(buttons_layout)

        self.save_button = QPushButton(get("save"))
        self.save_button.clicked.connect(self.save_clicked)
        buttons_layout.addWidget(self.save_button)

        self.delete_button = QPushButton(get("delete"))
        self.delete_button.clicked.connect(self.delete_selected_rows)
        buttons_layout.addWidget(self.delete_button)

        self.export_button = QPushButton(get("export"))
        buttons_layout.addWidget(self.export_button)
        self.export_button.clicked.connect(self.export_deck)

        self.import_button = QPushButton(get("import"))
        buttons_layout.addWidget(self.import_button)
        self.import_button.clicked.connect(self.import_deck)

        self.table.setColumnHidden(1, True)

    def load_decks(self):
        self.table.setRowCount(0)
        raw_decks = fetch_decks(self.connection) or []
        self.decks = raw_decks

        for deck in raw_decks:
            d_id = deck["deck_id"]
            name = deck["name"]
            description = deck["description"]

            with self.connection:
                query = "SELECT COUNT(*) FROM cards WHERE deck_id=?"
                cards_count = self.connection.execute(query, (d_id,)).fetchone()[0]

            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setCellWidget(row, 0, QCheckBox())
            self.table.setItem(row, 1, QTableWidgetItem(str(d_id)))
            self.table.setItem(row, 2, QTableWidgetItem(name))
            self.table.setItem(row, 3, QTableWidgetItem(description))
            self.table.setItem(row, 4, QTableWidgetItem(str(cards_count)))

            self.next_id = max(self.next_id, d_id + 1)

        if not self.is_last_row_empty():
            self.add_empty_row()

    def add_empty_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setCellWidget(row, 0, QCheckBox())
        self.table.setItem(row, 1, QTableWidgetItem(""))

        for col in range(2, 5):
            self.table.setItem(row, col, QTableWidgetItem())

    def save_clicked(self):
        for row in range(self.table.rowCount()):
            deck_id_item = self.table.item(row, 1)
            name_item = self.table.item(row, 2)
            description_item = self.table.item(row, 3)

            deck_id_text = deck_id_item.text().strip() if deck_id_item else ""
            deck_id = int(deck_id_text) if deck_id_text else None

            name = name_item.text().strip() if name_item else ""
            description = description_item.text().strip() if description_item else ""

            if not name and not description:
                continue

            if deck_id:
                update_deck(self.connection, deck_id, name=name, description=description)
            else:
                insert_deck(self.connection, name, description)

        self.load_decks()

    def delete_selected_rows(self):
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Confirm", "Are you sure you want to delete the seleceted decks?")
        if reply != QMessageBox.StandardButton.Yes:
            return
        for row in reversed(range(self.table.rowCount())):
            checkbox = self.table.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                deck_id_item = self.table.item(row, 1)
                if deck_id_item and deck_id_item.text().strip():
                    delete_deck(self.connection, int(deck_id_item.text()))
                self.table.removeRow(row)

        if not self.is_last_row_empty():
            self.add_empty_row()


    def export_deck(self):
        row = self.get_selected_row()
        if row is None:
            return

        deck_id = int(self.table.item(row, 1).text())
        deck_name = self.table.item(row, 2).text()

        file_path, _ = QFileDialog.getSaveFileName(self, "Export Deck", f"{deck_name}.csv",
                                                   "CSV files (*csv)")
        if not file_path:
            return

        cards = fetch_cards(self.connection, f"deck_id = {deck_id}")

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["question", "answer", "note"])
            for card in cards:
                writer.writerow([card["question"], card["answer"], card["note"]])

        QMessageBox.information(self, get("export"), f"{len(cards)} {get("have_been_exported")}.")


    def import_deck(self):
        row = self.get_selected_row()
        if row is None:
            return

        deck_id = int(self.table.item(row, 1).text())

        file_path, _ = QFileDialog.getOpenFileName(self, "Import Cards", "", "CSV Files (*.csv)")
        if not file_path:
            return

        added = 0
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_data in reader:
                insert_card(self.connection, row_data.get("question", ""),
                            row_data.get("answer", ""),
                            row_data.get("note", ""), 2.5, deck_id)
                added += 1

        QMessageBox.information(self, get("import"), f"{added} {get("have_been_imported")}.")
        self.load_decks()


    def get_selected_row(self):
        selected = []
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                deck_id_item = self.table.item(row, 1)
                if deck_id_item and deck_id_item.text().strip():
                    selected.append(row)

        if len(selected) == 0:
            QMessageBox.warning(self, get("selection"), get("no_deck_selected"))
            return None
        if len(selected) > 1:
            QMessageBox.warning(self, get("selection"), get("only_one_deck"))
            return None
        return selected[0]


    def is_last_row_empty(self):
        if self.table.rowCount() == 0:
            return False
        last_row = self.table.rowCount() - 1
        item = self.table.item(last_row, 2)
        return not (item and item.text().strip())
