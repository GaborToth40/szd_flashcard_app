import logging

from PySide6.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout

from translation import get
from database import get_connection
from decks_window import DecksWindow
from cards_window import CardsWindow
from learning_window import LearningWindow
from statistics_window import StatisticsWindow
from about_window import AboutWindow
from search_window import SearchWindow
from settings_window import SettingsWindow


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.setWindowTitle(get("flashcard_application"))
        self.resize(300, 200)

        self.database_connection = get_connection("database.db")

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu(get("file"))

        quit_action = file_menu.addAction(get("exit"))
        quit_action.triggered.connect(self.quit_app)

        settings_action = menu_bar.addAction(get("settings"))
        settings_action.triggered.connect(self.settings_open)

        about_action = menu_bar.addAction(get("about"))
        about_action.triggered.connect(self.about_open)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        central_widget.setLayout(self.main_layout)

        button_decks = QPushButton(get("decks"))
        self.main_layout.addWidget(button_decks)
        button_decks.clicked.connect(self.decks_open)

        button_cards = QPushButton(get("cards"))
        self.main_layout.addWidget(button_cards)
        button_cards.clicked.connect(self.cards_open)

        button_learning = QPushButton(get("learning"))
        self.main_layout.addWidget(button_learning)
        button_learning.clicked.connect(self.learning_open)

        button_search = QPushButton(get("search"))
        self.main_layout.addWidget(button_search)
        button_search.clicked.connect(self.search_open)

        button_statistics = QPushButton(get("statistics"))
        self.main_layout.addWidget(button_statistics)
        button_statistics.clicked.connect(self.statistics_open)

        self.deckswindow = DecksWindow(self.database_connection)
        self.cardswindow = CardsWindow(self.database_connection)
        self.learningwindow = LearningWindow(self.database_connection)
        self.searchwindow = SearchWindow(self.database_connection)
        self.statisticswindow = StatisticsWindow(self.database_connection)
        self.aboutwindow = AboutWindow()
        self.settingswindow = SettingsWindow()

        self.main_layout.addStretch(1)


    def quit_app(self):
        self.app.quit()

    def decks_open(self):
        self.deckswindow.show()

    def cards_open(self):
        self.cardswindow.show()

    def learning_open(self):
        self.learningwindow.show()

    def statistics_open(self):
        self.statisticswindow.show()

    def search_open(self):
        self.searchwindow.show()

    def about_open(self):
        self.aboutwindow.show()

    def settings_open(self):
        self.settingswindow.show()

    def closeEvent(self, event):
        self.deckswindow.close()
        self.cardswindow.close()
        self.learningwindow.close()
        self.searchwindow.close()
        self.statisticswindow.close()
        self.aboutwindow.close()
        self.settingswindow.close()

        if self.database_connection:
            self.database_connection.close()

        logging.info("Application closed")
        super().closeEvent(event)
