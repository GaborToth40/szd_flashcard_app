import json
import os

CONFIG_FILE = "settings.json"
current_language = "en"

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        current_language = json.load(f).get("language", "en")

strings = {
    "en": {
        "flashcard_application": "Flashcard application",
        "application_title": "Flashcard Application",
        "decks": "Decks",
        "cards": "Cards",
        "learning": "Learning",
        "search": "Search for words",
        "statistics": "Statistics",
        "file": "File",
        "settings": "Settings",
        "about": "About",
        "help": "Help",
        "save": "Save",
        "delete": "Delete",
        "exit": "Exit",

        "select": "Select",
        "id": "ID",
        "deck_name": "Deck name",
        "description": "Description",
        "number_of_cards": "Number of cards",
        "export": "Export",
        "import": "Import",
        "selection": "Selection",
        "have_been_exported": "have been exported",
        "have_been_imported": "cards have been imported",
        "no_deck_selected": "No decks have been selected for export/import",
        "only_one_deck": "Only 1 deck can be selected for export/import",

        "question": "Question",
        "answer": "Answer",
        "note": "Note",
        "weight": "Weight",
        "deck": "Deck",
        "are_you_sure_delete_card": "Are you sure you want to delete the selected cards?",
        "confirm": "Confirm",

        "study_settings": "Study settings",
        "select_deck": "Select Deck:",
        "mode": "Mode",
        "practice": "Practice",
        "test": "Test",
        "start_session": "Start session",
        "check_reveal": "Check / Reveal",
        "next": "Next",
        "end_session": "End session",
        "progress": "Progress",
        "correct_answer": "Correct answer: ",
        "no_cards_found": "No cards found",

        "review_last_seven_days": "Reviews (last 7 Days)",
        "total_cards": "Total cards",
        "total_decks": "Total decks",
        "cards_due_today": "Cards due today",
        "reviews": "Reviews",

        "manual": "Manual",
        "automatic": "Automatic",
        "check_words": "Check words",
        "new_words_found": "New words found:",
        "add_to_database": "Add to database",
        "show_word_list": "Show word list",
        "word_list": "Word list",
        "words_added": "words added",
        "youtube_id": "Enter a Youtube video ID (the last 11 characters of the video's link):",
        "YouTube_error": "YouTube Error",
        "could_not_fetch_transcipt": "Could not fetch transcript: ",
        "error": "Error",
        "success": "Success",

        "language": "Language:",
        "english": "English",
        "hungarian": "Magyar",
        "save_settings": "Save settings",
        "successfully_saved": "Successfully saved",
        "please_restart": "Please restart the application for language changes to take effect",

        "desktop_flashcard": "This is a desktop flashcard application with a spaced repetition system."
    },

    "hu": {
        "flashcard_application": "Szókártya alkalmazás",
        "application_title": "Szókártya Alkalmazás",
        "decks": "Paklik",
        "cards": "Kártyák",
        "learning": "Tanulás",
        "search": "Szavak keresése",
        "statistics": "Statisztikák",
        "file": "Fájl",
        "settings": "Beállítások",
        "about": "Névjegy",
        "help": "Segítség",
        "save": "Mentés",
        "delete": "Törlés",
        "exit": "Kilépés",

        "select": "Kiválaszt",
        "id": "ID",
        "deck_name": "Pakli neve",
        "description": "Leírás",
        "number_of_cards": "Kártyák száma",
        "export": "Exportálás",
        "import": "Importálás",
        "selection": "Kiválasztás",
        "have_been_exported": "kártya exportálva",
        "have_been_imported": "kártya importálva",
        "no_deck_selected": "Nincs kiválasztva pakli exportálásra/importálásra",
        "only_one_deck": "Csak 1 paklit lehet kiválasztani exportálásra/importálásra",

        "question": "Kérdés",
        "answer": "Válasz",
        "note": "Megjegyzés",
        "weight": "Súlyozás",
        "deck": "Pakli",
        "are_you_sure_delete_card": "Biztos törölni akarja a kiválasztott kártyákat?",
        "confirm": "Megerősít",

        "study_settings": "Tanulás beállítása",
        "select_deck": "Pakli választás:",
        "mode": "Mód",
        "practice": "Gyakorlás",
        "test": "Teszt",
        "start_session": "Munkamenet elkezdése",
        "check_reveal": "Ellenőrzés / Felfedés",
        "next": "Következő",
        "end_session": "Munkamenet befejezése",
        "progress": "Haladás",
        "correct_answer": "Helyes megoldás: ",
        "no_cards_found": "Nincs talált kártya",

        "review_last_seven_days": "Tesztek (utolsó 7 nap)",
        "total_cards": "Összes kártya",
        "total_decks": "Összes pakli",
        "cards_due_today": "Ma esedékes kártyák",
        "reviews": "Áttekintés",

        "manual": "Manuális",
        "automatic": "Automatikus",
        "check_words": "Szavak ellenőrzése",
        "new_words_found": "Új talált szavak:",
        "add_to_database": "Hozzáadás az adatbázishoz",
        "show_word_list": "Szavak listájának mutatása",
        "word_list": "Szavak listája",
        "words_added": "szó hozzáadva",
        "youtube_id": "Írjon be egy Youtube ID-t (a videó linkjének az utolsó 11 karaktere):",
        "YouTube_error": "YouTube Hiba",
        "could_not_fetch_transcipt": "A felírat lekérése nem sikerült: ",
        "error": "Hiba",
        "success": "Siker",

        "language": "Nyelv:",
        "english": "English",
        "hungarian": "Magyar",
        "save_settings": "Beállítások mentése",
        "successfully_saved": "Sikeresen mentve",
        "please_restart": "Kérem indítsa újra az alkalmazást, hogy a nyelvi változások érvénybe lépjenek",

        "desktop_flashcard": "Ez egy asztali szókártya akalmazás időközönkénti ismétléses rendszerrel."
    }
}

def get(key):
    return strings[current_language].get(key, key)

def get_language():
    return current_language

def set_language(lang):
    global current_language
    current_language = lang
    with open(CONFIG_FILE, "w") as f:
        json.dump({"language": lang}, f)
