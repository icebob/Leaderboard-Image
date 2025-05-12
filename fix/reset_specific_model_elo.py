import sqlite3
import datetime
import sys
import os

# Add the parent directory (project root) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DATABASE, DEFAULT_ELO

def reset_model_elo_and_history(model_id_to_reset):
    """
    Törli egy adott modell ELO előzményeit, visszaállítja az ELO pontszámát az alapértelmezettre,
    létrehoz egy új, kezdeti ELO bejegyzést az előzményekben, és törli a modellhez kapcsolódó szavazatokat.
    """
    db_path = DATABASE
    current_timestamp = datetime.datetime.now()

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. ELO előzmények törlése a megadott modellhez
        cursor.execute("DELETE FROM elo_history WHERE model = ?", (model_id_to_reset,))
        deleted_history_rows = cursor.rowcount
        print(f"Törölve {deleted_history_rows} ELO előzmény bejegyzés a '{model_id_to_reset}' modellhez.")

        # 2. Szavazatok törlése a megadott modellhez (győztesként vagy vesztesként)
        cursor.execute("DELETE FROM votes WHERE winner = ? OR loser = ?", (model_id_to_reset, model_id_to_reset))
        deleted_votes_rows = cursor.rowcount
        print(f"Törölve {deleted_votes_rows} szavazat bejegyzés, ahol a '{model_id_to_reset}' modell szerepelt.")

        # 3. ELO pontszám visszaállítása a model_elo táblában
        cursor.execute("UPDATE model_elo SET elo = ?, last_updated = ? WHERE model = ?", 
                       (DEFAULT_ELO, current_timestamp, model_id_to_reset))
        updated_elo_rows = cursor.rowcount
        if updated_elo_rows > 0:
            print(f"A '{model_id_to_reset}' modell ELO pontszáma visszaállítva {DEFAULT_ELO}-ra a 'model_elo' táblában.")
        else:
            # Ha a modell még nem létezik a model_elo táblában (nem valószínű, de kezeljük le)
            cursor.execute("INSERT INTO model_elo (model, elo, last_updated) VALUES (?, ?, ?)",
                           (model_id_to_reset, DEFAULT_ELO, current_timestamp))
            print(f"A '{model_id_to_reset}' modell hozzáadva a 'model_elo' táblához {DEFAULT_ELO} ELO pontszámmal.")

        # 4. Új, kezdeti ELO bejegyzés létrehozása az elo_history táblában
        cursor.execute("INSERT INTO elo_history (model, elo, timestamp) VALUES (?, ?, ?)",
                       (model_id_to_reset, DEFAULT_ELO, current_timestamp))
        print(f"Új kezdeti ELO bejegyzés ({DEFAULT_ELO}) létrehozva a '{model_id_to_reset}' modellhez az 'elo_history' táblában.")

        conn.commit()
        print(f"A '{model_id_to_reset}' modell ELO-jának, előzményeinek és szavazatainak nullázása sikeres.")

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
    model_to_reset = "model-004" # Itt add meg a nullázni kívánt modell ID-ját
    print(f"Kísérlet a(z) '{model_to_reset}' modell ELO-jának és előzményeinek nullázására...")
    reset_model_elo_and_history(model_to_reset)
