import sqlite3
import logging

def get_connection(db_name):
    try:
        connection = sqlite3.connect(db_name)
        connection.isolation_level = None
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection
    except Exception as e:
        print(f"Error: {e}")
        raise


def create_table_cards(connection):
    query = """
    CREATE TABLE IF NOT EXISTS "cards" (
        "card_id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "question" TEXT,
        "answer" TEXT,
        "note" TEXT,
        "weight" REAL DEFAULT 2.5,
        "interval" INTEGER DEFAULT 0,
        "next_review" TEXT DEFAULT CURRENT_DATE,
        "deck_id" INTEGER DEFAULT 1,
        FOREIGN KEY ("deck_id") REFERENCES "decks"("deck_id")
    )
    """
    try:
        with connection:
            connection.execute(query)
        logging.info("Cards table was created/verified")
    except sqlite3.Error as e:
        logging.error(f"Failed to create or verify the cards table: {e}")

def insert_card(connection, question: str, answer: str, note: str, weight: float, deck_id: int = None):
    query = "INSERT INTO cards (question, answer, note, weight, deck_id) VALUES (?, ?, ?, ?, ?)"
    try:
        with connection:
            cursor = connection.execute(query, (question, answer, note, weight, deck_id))
            return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Failed to insert into cards: {e}")
        return None


def fetch_cards(connection, condition: str = None) -> list[tuple]:
    query = "SELECT * FROM cards"
    if condition:
        query += f" WHERE {condition}"
    try:
        with connection:
            rows = connection.execute(query).fetchall()
        return rows
    except sqlite3.Error as e:
        logging.error(f"Failed to fetch cards: {e}")
        return []


def delete_card(connection, card_id: int):
    query = "DELETE FROM cards WHERE card_id = ?"
    try:
        with connection:
            connection.execute(query, (card_id,))
    except sqlite3.Error as e:
        logging.error(f"Failed to delete from cards: {e}")


def update_card(connection, card_id: int, question=None, answer=None, note=None, weight=None, deck_id: int = None):
    try:
        with connection:
            if question is not None:
                connection.execute("UPDATE CARDS SET question = ? WHERE card_id = ?", (question, card_id))
            if answer is not None:
                connection.execute("UPDATE CARDS SET answer = ? WHERE card_id = ?", (answer, card_id))
            if note is not None:
                connection.execute("UPDATE CARDS SET note = ? WHERE card_id = ?", (note, card_id))
            if weight is not None:
                connection.execute("UPDATE CARDS SET weight = ? WHERE card_id = ?", (weight, card_id))
            if deck_id is not None:
                connection.execute("UPDATE CARDS SET deck_id = ? WHERE card_id = ?", (deck_id, card_id))
    except sqlite3.Error as e:
        logging.error(f"Failed to update cards: {e}")


def create_table_decks(connection):
    query = """
    CREATE TABLE IF NOT EXISTS "decks" (
        "deck_id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "name" TEXT,
        "description" TEXT
    )
    """
    try:
        with connection:
            connection.execute(query)
        logging.info("Decks table was created/verified")
    except sqlite3.Error as e:
        logging.error(f"Failed to create/verify the decks table {e}")


def insert_deck(connection, name: str, description: str):
    query = "INSERT INTO decks (name, description) VALUES (?, ?)"
    try:
        with connection:
            cursor = connection.execute(query, (name, description))
            return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Failed to insert into decks {e}")
        return None

def fetch_decks(connection, condition: str = None) -> list[tuple]:
    query = "SELECT * FROM decks"
    if condition:
        query += f" WHERE {condition}"
    try:
        with connection:
            rows = connection.execute(query).fetchall()
        return rows
    except sqlite3.Error as e:
        logging.error(f"Failed to fetch decks: {e}")
        return []

def delete_deck(connection, deck_id: int):
    if deck_id == 1:
        logging.warning("The default deck cannot be deleted")
        return
    query   = "DELETE FROM decks WHERE deck_id = ?"
    try:
        with connection:
            connection.execute(query, (deck_id,))
    except sqlite3.Error as e:
        logging.error(f"Failed to delete from decks: {e}")

def update_deck(connection, deck_id: int, name=None, description=None):
    try:
        with connection:
            if name is not None:
                connection.execute("UPDATE DECKS SET name = ? WHERE deck_id = ?", (name, deck_id))
            if description is not None:
                connection.execute("UPDATE DECKS SET description = ? WHERE deck_id = ?", (description, deck_id))
    except sqlite3.Error as e:
        logging.error(f"Failed to update decks: {e}")


def create_table_review_history(connection):
    query = """
    CREATE TABLE IF NOT EXISTS "review_history" (
        "history_id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "card_id" INTEGER,
        "review_date" TEXT DEFAULT CURRENT_DATE,
        "quality" INTEGER,
        FOREIGN KEY ("card_id") REFERENCES "cards"("card_id") ON DELETE CASCADE
    )
    """
    try:
        with connection:
            connection.execute(query)
        logging.info("Review history table created/verified")
    except sqlite3.Error as e:
        logging.error(f"Failed to create/verify the review history table: {e}")

def insert_review_record(connection, card_id: int, quality: int):
    query = "INSERT INTO review_history (card_id, quality) VALUES (?, ?)"
    try:
        with connection:
            connection.execute(query, (card_id, quality))
    except sqlite3.Error as e:
        logging.error(f"Failed to log review history for card {card_id}: {e}")


def create_database():
    connection = get_connection("database.db")
    try:
        logging.info("Database connected")
        create_table_decks(connection)
        create_table_cards(connection)
        create_table_review_history(connection)
        with connection:
            connection.execute(
                "INSERT OR IGNORE INTO decks (deck_id, name, description) VALUES (1, \"Default\", \"Default\")"
            )
    finally:
        connection.close()
