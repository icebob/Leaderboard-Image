import os
import random
import sqlite3
import sys
import glob
import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory, abort
from database import get_db, init_db, get_prompt_ids, update_elo
from config import DATA_DIR, ALLOWED_EXTENSIONS, DEFAULT_ELO, MODELS, REVEAL_DELAY_MS

app = Flask(__name__)
app.config['DATA_DIR'] = DATA_DIR # Flask konfigurációban is tároljuk

# Adatbázis inicializálása indításkor (ha szükséges)
with app.app_context():
    init_db()

AVAILABLE_PROMPTS = [] # Gyorsítótárazzuk a prompt ID-kat

def update_available_prompts():
    """Frissíti az elérhető prompt ID-k listáját."""
    global AVAILABLE_PROMPTS
    AVAILABLE_PROMPTS = get_prompt_ids()
    if not AVAILABLE_PROMPTS:
        print("Warning: No valid prompts found in data directory!")

# Új segédfüggvény a fájlok megtalálásához, ami nem veszi figyelembe a kiterjesztést
def find_model_file(prompt_id, model_base_name):
    """
    Megkeresi a megfelelő modell fájlt a megadott mappában, a kiterjesztéstől függetlenül.
    
    :param prompt_id: A prompt mappájának azonosítója
    :param model_base_name: A modell fájl alapneve kiterjesztés nélkül
    :return: A teljes fájlnév kiterjesztéssel, vagy None ha nem található
    """
    directory = os.path.join(app.config['DATA_DIR'], prompt_id)
    
    # Megnézzük az összes lehetséges kiterjesztéssel, hogy létezik-e a fájl
    for ext in ALLOWED_EXTENSIONS:
        potential_file = f"{model_base_name}{ext}"
        if os.path.exists(os.path.join(directory, potential_file)):
            return potential_file
    
    # Ha nem találtuk meg a pontos egyezést, próbáljuk meg fájlmintával
    pattern = os.path.join(directory, f"{model_base_name}.*")
    matching_files = glob.glob(pattern)
    
    # Szűrjük az eredményt csak az engedélyezett kiterjesztésekre
    for file in matching_files:
        # Ellenőrizzük, hogy a fájl kiterjesztése engedélyezett-e
        file_ext = os.path.splitext(file)[1].lower()
        if file_ext in ALLOWED_EXTENSIONS:
            return os.path.basename(file)
    
    return None


@app.before_request
def before_first_request_func():
    # Első kérés előtt (vagy fejlesztéskor minden kérés előtt, ha `debug=True`)
    # frissítjük a prompt listát, hogy az új mappák megjelenjenek újraindítás nélkül.
    # Éles környezetben ezt ritkábban is lehet futtatni.
    if app.debug: # Csak debug módban frissítsen minden kérésnél
       update_available_prompts()
    elif not AVAILABLE_PROMPTS: # Vagy ha még üres a lista
       update_available_prompts()

# Szavazatok resetelésére szolgáló függvény
def reset_votes():
    """Törli az összes szavazatot és visszaállítja az ELO pontszámokat az alapértelmezettre."""
    try:
        db = get_db()
        with db:
            # Szavazatok törlése
            db.execute('DELETE FROM votes')
            
            # ELO történeti adatok törlése
            db.execute('DELETE FROM elo_history')
            
            # ELO pontszámok visszaállítása az alapértelmezettre
            db.execute('UPDATE model_elo SET elo = ?', (DEFAULT_ELO,))
            
            # Kezdeti ELO értékek rögzítése a historikus táblában is
            current_timestamp = datetime.datetime.now()
            for model in MODELS.keys():
                db.execute('INSERT INTO elo_history (model, elo, timestamp) VALUES (?, ?, ?)', 
                          (model, DEFAULT_ELO, current_timestamp))
            
            db.commit()
        print("Sikeres adatbázis resetelés! Az összes szavazat és ELO előzmény törölve, ELO pontszámok visszaállítva.")
        return True
    except sqlite3.Error as e:
        print(f"Adatbázis hiba a resetelés közben: {e}")
        return False
    except Exception as e:
        print(f"Hiba a resetelés közben: {e}")
        return False


@app.route('/')
def index():
    """Főoldal megjelenítése."""
    return render_template('index.html', models=list(MODELS.keys()), reveal_delay_ms=REVEAL_DELAY_MS)


# Módosítás: Engedélyezzük a .jpeg kiterjesztést is
@app.route('/images/<prompt_id>/<filename>')
def serve_image(prompt_id, filename):
    """Képfájlok kiszolgálása a data mappából."""
    # Biztonsági ellenőrzés: csak az engedélyezett kiterjesztéseket engedélyezzük
    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        print(f"Access denied for filename: {filename}")
        abort(404)

    # Ellenőrizzük, hogy a prompt_id létezik-e
    if prompt_id not in AVAILABLE_PROMPTS:
        print(f"Access denied for prompt_id: {prompt_id}")
        abort(404)

    directory = os.path.join(app.config['DATA_DIR'], prompt_id)
    # `send_from_directory` biztonságosabb, mint kézzel összerakni az útvonalat
    try:
        return send_from_directory(directory, filename)
    except FileNotFoundError:
        print(f"Image not found: {directory}/{filename}")
        abort(404)


# --- API Endpoints ---


# Módosítás: Arena Battle mód - ne jelenítse meg a modellek nevét szavazás előtt
@app.route('/api/battle_data')
def get_battle_data():
    """Adatokat ad vissza az Arena Battle módhoz."""    
    if not AVAILABLE_PROMPTS:
        return jsonify({"error": "No prompts available"}), 500

    prompt_id = random.choice(AVAILABLE_PROMPTS)
    prompt_path = os.path.join(app.config['DATA_DIR'], prompt_id, 'prompt.txt')

    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_text = f.read().strip()
    except FileNotFoundError:
        return jsonify({"error": f"Prompt file not found for ID: {prompt_id}"}), 500
    except Exception as e:
         return jsonify({"error": f"Error reading prompt file: {e}"}), 500

    # Válassz két KÜLÖNBÖZŐ modellt véletlenszerűen
    model_keys = list(MODELS.keys())
    if len(model_keys) < 2:
        return jsonify({"error": "Not enough models defined for battle"}), 500
    model1_key, model2_key = random.sample(model_keys, 2)

    # Megkeressük a megfelelő képfájlokat, kiterjesztéstől függetlenül
    model1_file = find_model_file(prompt_id, MODELS[model1_key])
    model2_file = find_model_file(prompt_id, MODELS[model2_key])
    
    # Ha valamelyik fájl nem található, hibaüzenetet adunk vissza
    if not model1_file:
        return jsonify({"error": f"Image for model {model1_key} not found in prompt {prompt_id}"}), 500
    if not model2_file:
        return jsonify({"error": f"Image for model {model2_key} not found in prompt {prompt_id}"}), 500

    data = {
        "prompt_id": prompt_id,
        "prompt_text": prompt_text,
        "model1": {
            "key": model1_key,
            "image_url": f"/images/{prompt_id}/{model1_file}"
        },
        "model2": {
            "key": model2_key,
            "image_url": f"/images/{prompt_id}/{model2_file}"
        },
        "reveal_models": False  # Új mező: a modellek neveit csak szavazás után fedjük fel
    }
    return jsonify(data)

@app.route('/api/side_by_side_data')
def get_side_by_side_data():
    """Adatokat ad vissza az Arena Side-by-Side módhoz."""
    model1_key = request.args.get('model1')
    model2_key = request.args.get('model2')

    if not model1_key or not model2_key:
        return jsonify({"error": "Both model1 and model2 parameters are required"}), 400

    if model1_key not in MODELS or model2_key not in MODELS:
        return jsonify({"error": "Invalid model key provided"}), 400

    if not AVAILABLE_PROMPTS:
        return jsonify({"error": "No prompts available"}), 500

    # Itt is választhatunk véletlenszerű promptot
    prompt_id = random.choice(AVAILABLE_PROMPTS)
    prompt_path = os.path.join(app.config['DATA_DIR'], prompt_id, 'prompt.txt')

    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_text = f.read().strip()
    except FileNotFoundError:
        return jsonify({"error": f"Prompt file not found for ID: {prompt_id}"}), 500
    except Exception as e:
         return jsonify({"error": f"Error reading prompt file: {e}"}), 500

    # Megkeressük a megfelelő képfájlokat, kiterjesztéstől függetlenül
    model1_file = find_model_file(prompt_id, MODELS[model1_key])
    model2_file = find_model_file(prompt_id, MODELS[model2_key])
    
    # Ha valamelyik fájl nem található, hibaüzenetet adunk vissza
    if not model1_file:
        return jsonify({"error": f"Image for model {model1_key} not found in prompt {prompt_id}"}), 500
    if not model2_file:
        return jsonify({"error": f"Image for model {model2_key} not found in prompt {prompt_id}"}), 500

    data = {
        "prompt_id": prompt_id,
        "prompt_text": prompt_text,
        "model1": {
            "key": model1_key,
            "image_url": f"/images/{prompt_id}/{model1_file}"
        },
        "model2": {
            "key": model2_key,
            "image_url": f"/images/{prompt_id}/{model2_file}"
        }
    }
    return jsonify(data)


@app.route('/api/vote', methods=['POST'])
def record_vote():
    """Szavazat rögzítése az adatbázisban."""
    data = request.json
    prompt_id = data.get('prompt_id')
    winner = data.get('winner')
    loser = data.get('loser')

    if not all([prompt_id, winner, loser]):
        return jsonify({"error": "Missing data for vote"}), 400

    if winner not in MODELS or loser not in MODELS:
         return jsonify({"error": "Invalid model name in vote"}), 400

    try:
        db = get_db()
        with db:
            # Szavazat rögzítése
            db.execute(
                'INSERT INTO votes (prompt_id, winner, loser) VALUES (?, ?, ?)',
                (prompt_id, winner, loser)
            )
            
            # ELO értékek frissítése
            winner_new_elo, loser_new_elo = update_elo(db, winner, loser)
            db.commit()
            
        return jsonify({
            "success": True, 
            "message": f"Vote recorded for {winner} against {loser}",
            "winner_new_elo": round(winner_new_elo, 1),
            "loser_new_elo": round(loser_new_elo, 1)
        })
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database error while recording vote"}), 500
    except Exception as e:
        print(f"Error recording vote: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/api/leaderboard')
def get_leaderboard():
    """Leaderboard adatok lekérdezése és kiszámítása."""    
    try:
        db = get_db()
        # Összes győzelem számolása modellenként
        wins_cursor = db.execute('''SELECT winner, COUNT(*) as win_count FROM votes GROUP BY winner''')
        wins = {row['winner']: row['win_count'] for row in wins_cursor.fetchall()}

        # Összes meccs számolása modellenként (győztesként VAGY vesztesként)
        total_matches_cursor = db.execute('''SELECT model, COUNT(*) as match_count FROM (
                SELECT winner as model FROM votes
                UNION ALL
                SELECT loser as model FROM votes
            )
            GROUP BY model''')
        total_matches = {row['model']: row['match_count'] for row in total_matches_cursor.fetchall()}
        
        # ELO értékek lekérdezése a model_elo táblából
        elo_cursor = db.execute('SELECT model, elo FROM model_elo')
        elo_ratings = {row['model']: row['elo'] for row in elo_cursor.fetchall()}

        leaderboard = []
        all_model_keys = list(MODELS.keys())
        for model in all_model_keys:
            model_wins = wins.get(model, 0)
            model_matches = total_matches.get(model, 0)
            win_rate = (model_wins / model_matches * 100) if model_matches > 0 else 0
            elo = elo_ratings.get(model, DEFAULT_ELO)  # Ha nincs ELO érték, használjuk az alapértelmezettet

            leaderboard.append({
                "model": model,
                "wins": model_wins,
                "matches": model_matches,
                "win_rate": round(win_rate, 2),
                "elo": round(elo, 1)  # Egy tizedesjegyre kerekítjük az ELO értéket
            })

        # Rendezés ELO pontszám szerint csökkenő sorrendben
        leaderboard.sort(key=lambda x: x['elo'], reverse=True)

        return jsonify(leaderboard)

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database error while fetching leaderboard"}), 500
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/api/elo_history')
def get_elo_history():
    """Lekérdezi az ELO értékek időbeli változását a grafikonhoz."""
    try:
        db = get_db()
        cursor = db.execute('''
            SELECT model, elo, timestamp 
            FROM elo_history 
            ORDER BY timestamp ASC
        ''')
        history_data = cursor.fetchall()
        
        # Adatok átalakítása a grafikonhoz megfelelő formátumba
        # { model1: [{x: timestamp, y: elo}, ...], model2: [...] }
        chart_data = {}
        for row in history_data:
            model = row['model']
            if model not in chart_data:
                chart_data[model] = []
            chart_data[model].append({
                'x': row['timestamp'],
                'y': round(row['elo'], 1)
            })
            
        return jsonify(chart_data)
    except sqlite3.Error as e:
        print(f"Database error fetching ELO history: {e}")
        return jsonify({"error": "Database error while fetching ELO history"}), 500
    except Exception as e:
        print(f"Error fetching ELO history: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


if __name__ == '__main__':
    # Parancssori argumentumok kezelése
    if len(sys.argv) > 1 and sys.argv[1] == 'reset-votes':
        if reset_votes():
            print("A szavazatok sikeresen törölve!")
            sys.exit(0)
        else:
            print("Hiba történt a szavazatok törlése közben!")
            sys.exit(1)
    
    # Indítás előtt frissítjük a prompt listát
    update_available_prompts()
    # Debug mód fejlesztéshez, élesben False és használj pl. Gunicornt/Waitress-t
    app.run(debug=True, host='0.0.0.0')