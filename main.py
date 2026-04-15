import sys
import logging

from PySide6.QtWidgets import QApplication

from main_window import MainWindow
from database import create_database


def main():
    logging.basicConfig(
        level=logging.INFO,
        filename="app.log",
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    app = QApplication(sys.argv)

    create_database()

    window = MainWindow(app)
    window.show()

    logging.info("Application started")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
