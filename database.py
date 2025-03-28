import sqlite3
import os
import math
from config import DATABASE, DATA_DIR, MODELS, DEFAULT_ELO, K_FACTOR

# ELO rating számítás függvényei
def calculate_expected_score(rating_a, rating_b):
    """
    Kiszámítja az A játékos várható eredményét B játékossal szemben.
    A várható eredmény 0-1 közötti szám, ahol 1 a biztos győzelem, 0 a biztos vereség.
    """
    return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

def calculate_new_elo(rating, expected_score, actual_score, k_factor=K_FACTOR):
    """
    Kiszámítja az új ELO értéket a régi értékből és az eredményekből.
    
    :param rating: A jelenlegi ELO értéke a játékosnak
    :param expected_score: A várható eredmény (0-1 közötti szám)
    :param actual_score: A tényleges eredmény (1 győzelem, 0 vereség esetén)
    :param k_factor: K-faktor, amely befolyásolja a változás mértékét
    :return: Az új ELO érték
    """
    return rating + k_factor * (actual_score - expected_score)

def get_current_elo(db, model_name):
    """
    Lekérdezi a modell aktuális ELO értékét az adatbázisból.
    Ha még nincs ELO értéke, az alapértelmezett értéket adja vissza.
    """
    try:
        cur = db.execute('SELECT elo FROM model_elo WHERE model = ?', (model_name,))
        result = cur.fetchone()
        if result:
            return result['elo']
        else:
            # Ha nincs még ELO értéke, hozzáadjuk az alapértelmezett értékkel
            db.execute('INSERT INTO model_elo (model, elo) VALUES (?, ?)', 
                      (model_name, DEFAULT_ELO))
            db.commit()
            return DEFAULT_ELO
    except Exception as e:
        print(f"Error getting ELO for {model_name}: {e}")
        return DEFAULT_ELO

def update_elo(db, winner_model, loser_model):
    """
    Frissíti a nyertes és vesztes modellek ELO értékét egy mérkőzés után.
    """
    # Lekérdezzük a jelenlegi ELO értékeket
    winner_elo = get_current_elo(db, winner_model)
    loser_elo = get_current_elo(db, loser_model)
    
    # Várható eredmények számítása
    winner_expected = calculate_expected_score(winner_elo, loser_elo)
    loser_expected = calculate_expected_score(loser_elo, winner_elo)
    
    # Új ELO értékek számítása
    winner_new_elo = calculate_new_elo(winner_elo, winner_expected, 1)
    loser_new_elo = calculate_new_elo(loser_elo, loser_expected, 0)
    
    # Értékek frissítése az adatbázisban
    db.execute('UPDATE model_elo SET elo = ? WHERE model = ?', 
              (winner_new_elo, winner_model))
    db.execute('UPDATE model_elo SET elo = ? WHERE model = ?', 
              (loser_new_elo, loser_model))
    
    return winner_new_elo, loser_new_elo

def get_db():
    """Adatbázis kapcsolat létrehozása vagy visszaadása."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row # Sorok szótárként való eléréséhez
    return db

def init_db():
    """Adatbázis séma inicializálása (ha még nem létezik)."""
    if not os.path.exists(DATABASE):
        print("Initializing database...")
        db = get_db()
        with db:
            db.execute('''
                CREATE TABLE votes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id TEXT NOT NULL,
                    winner TEXT NOT NULL,
                    loser TEXT NOT NULL,
                    voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            db.execute('''
                CREATE INDEX idx_winner ON votes (winner);
            ''')
            db.execute('''
                CREATE INDEX idx_loser ON votes (loser);
            ''')
            
            # ELO értékek tárolására szolgáló tábla
            db.execute('''
                CREATE TABLE model_elo (
                    model TEXT PRIMARY KEY,
                    elo REAL NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Kezdeti ELO értékek minden modellhez
            for model in MODELS.keys():
                db.execute('INSERT INTO model_elo (model, elo) VALUES (?, ?)', 
                          (model, DEFAULT_ELO))
                
        print("Database initialized.")
    else:
        # Ellenőrizzük, hogy az ELO tábla létezik-e, és ha nem, létrehozzuk
        db = get_db()
        with db:
            # Ellenőrizzük, hogy létezik-e már az ELO tábla
            result = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='model_elo'").fetchone()
            if not result:
                print("Creating ELO rating table...")
                db.execute('''
                    CREATE TABLE model_elo (
                        model TEXT PRIMARY KEY,
                        elo REAL NOT NULL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                # Kezdeti ELO értékek minden modellhez
                for model in MODELS.keys():
                    db.execute('INSERT INTO model_elo (model, elo) VALUES (?, ?)', 
                              (model, DEFAULT_ELO))
        print("Database already exists.")

def get_prompt_ids():
    """Visszaadja az érvényes prompt ID-k (mappa nevek) listáját."""
    prompt_ids = []
    if not os.path.isdir(DATA_DIR):
        print(f"Error: Data directory '{DATA_DIR}' not found.")
        return []
    for item in os.listdir(DATA_DIR):
        item_path = os.path.join(DATA_DIR, item)
        # Ellenőrzi, hogy mappa-e és tartalmazza-e a szükséges fájlokat
        if os.path.isdir(item_path):
            # Ellenőrizhetjük, hogy minden modell kép és prompt.txt megvan-e
            # Egyszerűsítésként most csak azt nézzük, van-e prompt.txt
            prompt_file = os.path.join(item_path, 'prompt.txt')
            if os.path.exists(prompt_file):
                 prompt_ids.append(item)
            # else:
            #     print(f"Warning: Skipping directory '{item}' - missing prompt.txt")

    prompt_ids.sort() # Sorba rendezés (opcionális, de szebb)
    print(f"Found prompts: {prompt_ids}")
    return prompt_ids

if __name__ == '__main__':
    init_db()
    get_prompt_ids() # Csak teszteléshez induláskor