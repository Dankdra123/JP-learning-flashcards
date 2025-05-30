import sqlite3

DATABASE_NAME = 'flashcards.db' # Corrected variable name

def create_connection():
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME) # Corrected here
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(deck_name):
    """Create a new table (deck) if it doesn't exist."""
    conn = create_connection()
    if conn:
        try:
            # Table names cannot be parameterized directly, so we'll sanitize
            # For this simple app, we'll assume deck_name comes from trusted user input
            # In a production app, you'd add more robust input validation
            table_name_safe = ''.join(c for c in deck_name if c.isalnum() or c == '_')
            if not table_name_safe:
                raise ValueError("Deck name cannot be empty or contain only special characters.")

            cursor = conn.cursor()
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name_safe} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    japanese_word TEXT NOT NULL,
                    english_word TEXT NOT NULL
                );
            ''')
            conn.commit()
            print(f"Table '{table_name_safe}' created or already exists.")
        except sqlite3.Error as e:
            print(f"Error creating table {table_name_safe}: {e}")
        finally:
            conn.close()

def add_card(deck_name, japanese_word, english_word):
    """Add a new flashcard to a specified deck."""
    conn = create_connection()
    if conn:
        try:
            table_name_safe = ''.join(c for c in deck_name if c.isalnum() or c == '_')
            if not table_name_safe:
                raise ValueError("Deck name cannot be empty or contain only special characters.")

            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT INTO {table_name_safe} (japanese_word, english_word)
                VALUES (?, ?);
            ''', (japanese_word, english_word))
            conn.commit()
            print(f"Card added to {table_name_safe}: {japanese_word} - {english_word}")
            return True
        except sqlite3.Error as e:
            print(f"Error adding card to {table_name_safe}: {e}")
            return False
        finally:
            conn.close()
    return False

def get_all_decks():
    """Retrieve a list of all deck names (table names) in the database."""
    conn = create_connection()
    decks = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            # Filter out internal SQLite tables if any
            decks = [table[0] for table in tables if not table[0].startswith('sqlite_')]
        except sqlite3.Error as e:
            print(f"Error getting all decks: {e}")
        finally:
            conn.close()
    return decks

def get_cards_from_deck(deck_name):
    """Retrieve all flashcards from a specified deck, including their IDs."""
    conn = create_connection()
    cards = []
    if conn:
        try:
            table_name_safe = ''.join(c for c in deck_name if c.isalnum() or c == '_')
            if not table_name_safe:
                return []

            cursor = conn.cursor()
            # Fetch id, japanese_word, english_word
            cursor.execute(f"SELECT id, japanese_word, english_word FROM {table_name_safe};")
            cards = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving cards from {table_name_safe}: {e}")
        finally:
            conn.close()
    return cards

def delete_deck(deck_name):
    """Delete a deck (table) from the database."""
    conn = create_connection()
    if conn:
        try:
            table_name_safe = ''.join(c for c in deck_name if c.isalnum() or c == '_')
            if not table_name_safe:
                return False

            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {table_name_safe};")
            conn.commit()
            print(f"Deck '{table_name_safe}' deleted.")
            return True
        except sqlite3.Error as e:
            print(f"Error deleting deck {table_name_safe}: {e}")
            return False
        finally:
            conn.close()
    return False

def rename_deck(old_deck_name, new_deck_name):
    """Rename an existing deck (table) in the database."""
    conn = create_connection()
    if conn:
        try:
            old_table_name_safe = ''.join(c for c in old_deck_name if c.isalnum() or c == '_')
            new_table_name_safe = ''.join(c for c in new_deck_name if c.isalnum() or c == '_')

            if not old_table_name_safe or not new_table_name_safe:
                raise ValueError("Deck names cannot be empty or contain only special characters.")
            
            if old_table_name_safe == new_table_name_safe:
                return True # No actual change needed

            cursor = conn.cursor()
            cursor.execute(f"ALTER TABLE {old_table_name_safe} RENAME TO {new_table_name_safe};")
            conn.commit()
            print(f"Deck '{old_table_name_safe}' renamed to '{new_table_name_safe}'.")
            return True
        except sqlite3.Error as e:
            print(f"Error renaming deck {old_table_name_safe} to {new_table_name_safe}: {e}")
            return False
        finally:
            conn.close()
    return False

def delete_card_by_id(deck_name, card_id):
    """Delete a specific flashcard from a deck using its ID."""
    conn = create_connection()
    if conn:
        try:
            table_name_safe = ''.join(c for c in deck_name if c.isalnum() or c == '_')
            if not table_name_safe:
                return False

            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table_name_safe} WHERE id = ?;", (card_id,))
            conn.commit()
            print(f"Card with ID {card_id} deleted from deck '{table_name_safe}'.")
            return True
        except sqlite3.Error as e:
            print(f"Error deleting card with ID {card_id} from {table_name_safe}: {e}")
            return False
        finally:
            conn.close()
    return False

if __name__ == '__main__':
    # Example Usage (for testing the database module independently)
    # create_table("SampleDeck")
    # add_card("SampleDeck", "犬", "dog")
    # add_card("SampleDeck", "猫", "cat")
    # add_card("SampleDeck", "魚", "fish")
    # print("Cards in SampleDeck:", get_cards_from_deck("SampleDeck"))
    # # Assuming you know an ID, e.g., if get_cards_from_deck returns (1, '犬', 'dog')
    # # db.delete_card_by_id("SampleDeck", 1)
    # # print("Cards in SampleDeck after delete:", get_cards_from_deck("SampleDeck"))
    # # rename_deck("SampleDeck", "TestDeck")
    # # print("All decks after rename:", get_all_decks())
    # # delete_deck("TestDeck")
    # # print("All decks after deletion:", get_all_decks())
    pass