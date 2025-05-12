import sqlite3
import sys
import os

# Add the parent directory (project root) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DATABASE

def fix_chatgpt_model_id_in_elo_history():
    """
    Frissíti az 'elo_history' táblát, lecserélve a 'ChatGPT GPT 4o' modellnevet
    a helyes 'model-004' ID-ra.
    """
    db_path = DATABASE
    old_model_name = "ChatGPT GPT 4o"
    new_model_id = "model-004"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM elo_history WHERE model = ?", (old_model_name,))
        count_before = cursor.fetchone()[0]
        
        if count_before == 0:
            print(f"Nem található '{old_model_name}' bejegyzés az 'elo_history' táblában. Nincs szükség frissítésre.")
            return

        print(f"'{old_model_name}' bejegyzések száma a frissítés előtt: {count_before}")

        cursor.execute("UPDATE elo_history SET model = ? WHERE model = ?", (new_model_id, old_model_name))
        updated_rows = cursor.rowcount 
        conn.commit()
        
        print(f"Sikeresen frissítve {updated_rows} sor az 'elo_history' táblában.")
        print(f"A '{old_model_name}' lecserélve erre: '{new_model_id}'.")

    except sqlite3.Error as e:
        print(f"Adatbázis hiba történt: {e}")
    except Exception as e:
        print(f"Egyéb hiba történt: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_chatgpt_model_id_in_elo_history()
