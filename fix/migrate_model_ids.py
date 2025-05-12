# Egyszeri migrációs script: modellek nevéről ID-re váltás az adatbázisban
import sqlite3
import sys
import os

# Add the parent directory (project root) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DATABASE, MODELS

def main():
    # Név -> ID mapping
    name_to_id = {model['name']: model_id for model_id, model in MODELS.items()}
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    # votes tábla
    print('Votes tábla frissítése...')
    for col in ['winner', 'loser']:
        for name, model_id in name_to_id.items():
            cur.execute(f"UPDATE votes SET {col} = ? WHERE {col} = ?", (model_id, name))
    # model_elo tábla
    print('model_elo tábla frissítése...')
    for name, model_id in name_to_id.items():
        cur.execute("UPDATE model_elo SET model = ? WHERE model = ?", (model_id, name))
    # elo_history tábla
    print('elo_history tábla frissítése...')
    for name, model_id in name_to_id.items():
        cur.execute("UPDATE elo_history SET model = ? WHERE model = ?", (model_id, name))
    conn.commit()
    print('Migráció kész!')
    conn.close()

if __name__ == '__main__':
    main()
