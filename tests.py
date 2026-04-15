import sqlite3
import pytest
from database import (
    create_table_decks, create_table_cards, create_table_review_history,
    insert_card, fetch_cards, delete_card, update_card,
    insert_deck, fetch_decks, delete_deck, update_deck,
    insert_review_record
)

# run tests with pytest tests.py

@pytest.fixture
def connection():
    conn = sqlite3.connect(":memory:")
    conn.isolation_level = None
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    create_table_decks(conn)
    create_table_cards(conn)
    create_table_review_history(conn)
    conn.execute("INSERT INTO decks (deck_id, name, description) VALUES (1, 'Default', 'Default')")
    yield conn
    conn.close()


def test_insert_deck(connection):
    deck_id = insert_deck(connection, "Test Deck", "A test deck")
    assert deck_id is not None

def test_fetch_decks(connection):
    insert_deck(connection, "Deck A", "First")
    insert_deck(connection, "Deck B", "Second")
    decks = fetch_decks(connection)
    assert len(decks) == 3  # Default + 2

def test_fetch_decks_empty(connection):
    decks = fetch_decks(connection)
    assert len(decks) == 1  # Only default

def test_update_deck(connection):
    deck_id = insert_deck(connection, "Old Name", "Old Desc")
    update_deck(connection, deck_id, name="New Name", description="New Desc")
    decks = fetch_decks(connection, f"deck_id = {deck_id}")
    assert decks[0]["name"] == "New Name"
    assert decks[0]["description"] == "New Desc"

def test_delete_deck(connection):
    deck_id = insert_deck(connection, "To Delete", "Bye")
    delete_deck(connection, deck_id)
    decks = fetch_decks(connection, f"deck_id = {deck_id}")
    assert len(decks) == 0

def test_delete_default_deck(connection):
    delete_deck(connection, 1)
    decks = fetch_decks(connection, "deck_id = 1")
    assert len(decks) == 1  # Default deck should still exist


def test_insert_card(connection):
    card_id = insert_card(connection, "Q1", "A1", "Note", 2.5, 1)
    assert card_id is not None

def test_fetch_cards(connection):
    insert_card(connection, "Q1", "A1", "N1", 2.5, 1)
    insert_card(connection, "Q2", "A2", "N2", 2.5, 1)
    cards = fetch_cards(connection)
    assert len(cards) == 2

def test_fetch_cards_empty(connection):
    cards = fetch_cards(connection)
    assert len(cards) == 0

def test_fetch_cards_with_condition(connection):
    deck_id = insert_deck(connection, "Other", "Other deck")
    insert_card(connection, "Q1", "A1", "N1", 2.5, 1)
    insert_card(connection, "Q2", "A2", "N2", 2.5, deck_id)
    cards = fetch_cards(connection, f"deck_id = {deck_id}")
    assert len(cards) == 1
    assert cards[0]["question"] == "Q2"

def test_update_card(connection):
    card_id = insert_card(connection, "Old Q", "Old A", "Old N", 2.5, 1)
    update_card(connection, card_id, question="New Q", answer="New A", note="New N", weight=3.0)
    cards = fetch_cards(connection, f"card_id = {card_id}")
    assert cards[0]["question"] == "New Q"
    assert cards[0]["answer"] == "New A"
    assert cards[0]["note"] == "New N"
    assert cards[0]["weight"] == 3.0

def test_update_card_partial(connection):
    card_id = insert_card(connection, "Q", "A", "N", 2.5, 1)
    update_card(connection, card_id, question="Updated Q")
    cards = fetch_cards(connection, f"card_id = {card_id}")
    assert cards[0]["question"] == "Updated Q"
    assert cards[0]["answer"] == "A"

def test_delete_card(connection):
    card_id = insert_card(connection, "Q1", "A1", "N1", 2.5, 1)
    delete_card(connection, card_id)
    cards = fetch_cards(connection)
    assert len(cards) == 0


def test_insert_review_record(connection):
    card_id = insert_card(connection, "Q1", "A1", "N1", 2.5, 1)
    insert_review_record(connection, card_id, 2)
    rows = connection.execute("SELECT * FROM review_history WHERE card_id = ?", (card_id,)).fetchall()
    assert len(rows) == 1
    assert rows[0]["quality"] == 2

def test_review_history_cascade_delete(connection):
    card_id = insert_card(connection, "Q1", "A1", "N1", 2.5, 1)
    insert_review_record(connection, card_id, 2)
    insert_review_record(connection, card_id, 1)
    delete_card(connection, card_id)
    rows = connection.execute("SELECT * FROM review_history WHERE card_id = ?", (card_id,)).fetchall()
    assert len(rows) == 0


def test_spaced_repetition_wrong_answer(connection):
    card_id = insert_card(connection, "Q", "A", "N", 2.5, 1)
    connection.execute("UPDATE cards SET interval = 5, weight = 2.5 WHERE card_id = ?", (card_id,))

    old_weight = 2.5
    new_interval = 1
    new_weight = max(1.3, old_weight - 0.2)

    connection.execute("UPDATE cards SET interval = ?, weight = ? WHERE card_id = ?",
                       (new_interval, new_weight, card_id))

    card = connection.execute("SELECT * FROM cards WHERE card_id = ?", (card_id,)).fetchone()
    assert card["interval"] == 1
    assert card["weight"] == 2.3

def test_spaced_repetition_correct_answer(connection):
    card_id = insert_card(connection, "Q", "A", "N", 2.5, 1)
    connection.execute("UPDATE cards SET interval = 5, weight = 2.5 WHERE card_id = ?", (card_id,))

    old_interval = 5
    old_weight = 2.5
    new_interval = max(old_interval + 1, round(old_interval * old_weight))
    new_weight = old_weight

    connection.execute("UPDATE cards SET interval = ?, weight = ? WHERE card_id = ?",
                       (new_interval, new_weight, card_id))

    card = connection.execute("SELECT * FROM cards WHERE card_id = ?", (card_id,)).fetchone()
    assert card["interval"] == 12
    assert card["weight"] == 2.5

def test_spaced_repetition_wrong_new_card(connection):
    card_id = insert_card(connection, "Q", "A", "N", 2.5, 1)

    old_interval = 0
    old_weight = 2.5
    new_interval = 1
    new_weight = max(1.3, old_weight - 0.2)

    connection.execute("UPDATE cards SET interval = ?, weight = ? WHERE card_id = ?",
                       (new_interval, new_weight, card_id))

    card = connection.execute("SELECT * FROM cards WHERE card_id = ?", (card_id,)).fetchone()
    assert card["interval"] == 1
    assert card["weight"] == 2.3

def test_spaced_repetition_correct_new_card(connection):
    card_id = insert_card(connection, "Q", "A", "N", 2.5, 1)

    old_interval = 0
    old_weight = 2.5
    new_interval = max(old_interval + 1, round(old_interval * old_weight))
    new_weight = old_weight

    connection.execute("UPDATE cards SET interval = ?, weight = ? WHERE card_id = ?",
                       (new_interval, new_weight, card_id))

    card = connection.execute("SELECT * FROM cards WHERE card_id = ?", (card_id,)).fetchone()
    assert card["interval"] == 1
    assert card["weight"] == 2.5

def test_spaced_repetition_weight_below_floor(connection):
    card_id = insert_card(connection, "Q", "A", "N", 1.3, 1)
    connection.execute("UPDATE cards SET interval = 3, weight = 1.3 WHERE card_id = ?", (card_id,))

    new_weight = max(1.3, 1.3 - 0.2)

    connection.execute("UPDATE cards SET weight = ? WHERE card_id = ?", (new_weight, card_id))

    card = connection.execute("SELECT * FROM cards WHERE card_id = ?", (card_id,)).fetchone()
    assert card["weight"] == 1.3
