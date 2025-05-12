import sqlite3
import sys
import os

# Add the parent directory (project root) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DATABASE

def fix_gemini_flash_id_in_elo_history():
    """
    Kijavítja a 'Google Gemini Flash' néven szereplő bejegyzéseket az elo_history táblában
    a megfelelő 'model-002' model ID-ra.
    """
    db_path = DATABASE
    old_name = "Google Gemini Flash"
    correct_model_id = "model-002"
    updated_rows = 0

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Ellenőrizzük, hogy létezik-e ilyen bejegyzés
        cursor.execute("SELECT COUNT(*) FROM elo_history WHERE model = ?", (old_name,))
        count = cursor.fetchone()[0]

        if count == 0:
            print(f"Nem található '{old_name}' nevű bejegyzés az 'elo_history' táblában. Nincs szükség javításra.")
            return

        # Frissítés végrehajtása
        cursor.execute("UPDATE elo_history SET model = ? WHERE model = ?", (correct_model_id, old_name))
        updated_rows = cursor.rowcount
        conn.commit()

        if updated_rows > 0:
            print(f"Sikeresen frissítve {updated_rows} sor az 'elo_history' táblában: '{old_name}' -> '{correct_model_id}'.")
        else:
            # Ez az ág elvileg nem futhat le a fenti ellenőrzés miatt, de biztonság kedvéért itt van
            print(f"Nem történt frissítés. Lehetséges, hogy a '{old_name}' bejegyzés már korábban javítva lett vagy nem létezik.")

    except sqlite3.Error as e:
        print(f"Adatbázis hiba történt: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"Egyéb hiba történt: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print(f"Kísérlet a 'Google Gemini Flash' ID javítására az 'elo_history' táblában...")
    fix_gemini_flash_id_in_elo_history()
