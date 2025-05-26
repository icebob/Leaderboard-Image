# -* - coding: utf-8 -* -
import sqlite3
import os

# Fontos: Mielőtt futtatod ezt a szkriptet, KÉSZÍTS BIZTONSÁGI MÁSOLATOT
# a 'votes.db' adatbázis fájlról!
# Ez a szkript módosításokat hajt végre az adatbázisban.

# -----------------------------------------------------------------------------
# FELHASZNÁLÓI KONFIGURÁCIÓ: MODELL AZONOSÍTÓK MEGFELELTETÉSE
# -----------------------------------------------------------------------------
# Itt add meg a régi model ID-k (amelyek a logokban szerepelnek és az adatbázisban vannak)
# és az új, config.py-ban definiált 'model-XXX' ID-k közötti megfeleltetést.
#
# Ha egy régi ID-hez nincs egyértelmű új megfelelő (mert pl. törölni kellene,
# vagy még nem döntötted el, melyik új ID-re map-olod), akkor az új ID helyére írj 'None'-t.
# Ebben az esetben a szkript kihagyja az adott régi ID frissítését.
#
# Győződj meg róla, hogy az itt megadott 'új_id'-k VALÓBAN LÉTEZNEK KULCSKÉNT
# a `config.py` fájlban lévő `MODELS` szótárban!

ID_MAP = {
    # Példák a logjaid alapján (KÉRLEK, ELLENŐRIZD ÉS PONTOSÍTSD EZEKET!):
    "grok": "model-001",              # Ellenőrizd, hogy 'model-001' valóban a 'Grok' a config.py-ban
    "gemini-flash": "model-002",      # Ellenőrizd, hogy 'model-002' a 'Google Gemini Flash 2.0'
    "Google Gemini Flash": "model-002", # Valószínűleg ugyanaz, mint fent
    "midjourney": "model-005",        # Pl. 'Midjourney v7'-re ('model-006'). Ellenőrizd a config.py-t!
    "Midjourney": "model-005",        # Valószínűleg ugyanaz, mint fent

    # Az alábbiakhoz valószínűleg pontosítás szükséges a config.py alapján,
    # vagy új modelleket kell felvenned a config.py-ba, ha ezek különálló entitások.
    # Ha nincs megfelelő új ID, hagyd None-on, vagy add meg a helyes 'model-XXX' ID-t.

    "gemini-25pro": "model-003",             # NINCS EGYÉRTELMŰ MEGFELELŐ A JELENLEGI config.py-ban.
                                      # Add meg a helyes 'model-XXX' ID-t, ha tudod, vagy hagyd None-on a kihagyáshoz.
                                      # Lehet, hogy ez a 'Google Gemini 2.5 Pro'? Ha igen, és van neki ID a config.py-ban, azt írd ide.

    "Google Gemini 2.5 Pro": "model-003",    # Ugyanaz, mint fent.

    "gpt4o": "model-004",             # Feltételezve, hogy 'model-004' ('GPT Image 1' a config.py-ban) a cél. Ellenőrizd!
                                      # Ha a 'gpt4o' egy külön modell, annak saját 'model-XXX' ID-t kell kapnia a config.py-ban.

    "ChatGPT GPT 4o": "model-004",    # Ugyanaz, mint fent.

    # Ide vedd fel az összes többi régi ID-t, amit migrálni szeretnél,
    # a logokban látott figyelmeztetések alapján:
    # "régi_id_az_adatbázisban": "új_model_id_a_config_py_bol_vagy_None",
}

# Adatbázis fájl neve. Ennek meg kell egyeznie a config.py-ban lévő DATABASE változó értékével.
# Ha a szkript nem a projekt gyökérkönyvtárából fut, akkor abszolút vagy relatív elérési utat adj meg.
DATABASE_FILE = 'votes.db'
# -----------------------------------------------------------------------------

def migrate_ids():
    print("FIGYELEM: Ez a szkript módosítani fogja a(z) '{}' adatbázis fájlt.".format(DATABASE_FILE))
    print("Mielőtt folytatnád, KÉSZÍTS BIZTONSÁGI MÁSOLATOT az adatbázisról!")
    print("\nAz alábbi megfeleltetési tábla (ID_MAP) alapján történik a frissítés:")
    for old, new in ID_MAP.items():
        print(f"  Régi ID: '{old}' ---> Új ID: '{new if new is not None else 'KIHAGYVA (None)'}'")

    print("\nNyomj Enter-t a folytatáshoz, vagy Ctrl+C-t és Enter-t a megszakításhoz...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nFolyamat megszakítva.")
        return

    if not os.path.exists(DATABASE_FILE):
        print(f"Hiba: Az adatbázis fájl ({DATABASE_FILE}) nem található ezen az elérési úton.")
        print("Ellenőrizd a DATABASE_FILE változót és a szkript futtatási helyét.")
        return

    conn = None
    updated_counts = {"model_elo": {}, "elo_history": {}}

    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        print("\n--- Model ID-k migrációja megkezdődött ---")
        for old_id, new_id in ID_MAP.items():
            if new_id is None:
                print(f"Kihagyva: A '{old_id}' régi ID frissítése, mert nincs új ID megadva (None).")
                continue

            print(f"Frissítés folyamatban: '{old_id}' lecserélése erre: '{new_id}'")

            # model_elo tábla frissítése
            try:
                cursor.execute("SELECT elo FROM model_elo WHERE model = ?", (old_id,))
                old_elo_data = cursor.fetchone()

                if old_elo_data:
                    old_elo_score = old_elo_data[0]
                    
                    # Ellenőrizzük, hogy az új ID létezik-e már
                    cursor.execute("SELECT model FROM model_elo WHERE model = ?", (new_id,))
                    new_id_exists = cursor.fetchone()

                    if new_id_exists:
                        print(f"  '{old_id}' (ELO: {old_elo_score}) létezik. '{new_id}' is létezik a 'model_elo' táblában.")
                        print(f"  '{new_id}' ELO-ja frissítésre kerül {old_elo_score}-ra, és '{old_id}' törölve lesz.")
                        
                        # Új ID ELO-jának frissítése és last_updated beállítása
                        cursor.execute("UPDATE model_elo SET elo = ?, last_updated = datetime('now', 'localtime') WHERE model = ?", 
                                       (old_elo_score, new_id))
                        # Régi ID törlése
                        cursor.execute("DELETE FROM model_elo WHERE model = ?", (old_id,))
                        
                        updated_elo_rows = 1 # Egy logikai művelet történt: összefésülés
                        updated_counts["model_elo"][old_id] = updated_counts["model_elo"].get(old_id, 0) + updated_elo_rows
                        print(f"  '{old_id}' ELO-ja átvíve '{new_id}'-re, és '{old_id}' törölve a 'model_elo' táblából.")
                    else:
                        # Ha az új ID valamiért mégsem létezne (kevésbé valószínű), akkor átnevezzük a régit
                        print(f"  '{old_id}' (ELO: {old_elo_score}) létezik. '{new_id}' NEM létezik a 'model_elo' táblában.")
                        print(f"  '{old_id}' átnevezése '{new_id}'-re.")
                        cursor.execute("UPDATE model_elo SET model = ?, elo = ?, last_updated = datetime('now', 'localtime') WHERE model = ?", 
                                       (new_id, old_elo_score, old_id))
                        updated_elo_rows = cursor.rowcount
                        updated_counts["model_elo"][old_id] = updated_counts["model_elo"].get(old_id, 0) + updated_elo_rows
                        if updated_elo_rows > 0:
                             print(f"  '{old_id}' -> '{new_id}': {updated_elo_rows} sor frissítve (átnevezve) a 'model_elo' táblában.")

                else:
                    print(f"  '{old_id}' nem található a 'model_elo' táblában (nincs teendő).")
            except sqlite3.Error as e:
                print(f"  Hiba a 'model_elo' tábla frissítésekor ('{old_id}' -> '{new_id}'): {e}")


            # elo_history tábla frissítése
            try:
                sql_update_history = "UPDATE elo_history SET model = ? WHERE model = ?"
                cursor.execute(sql_update_history, (new_id, old_id))
                updated_history_rows = cursor.rowcount
                updated_counts["elo_history"][old_id] = updated_counts["elo_history"].get(old_id, 0) + updated_history_rows
                if updated_history_rows > 0:
                    print(f"  '{old_id}' -> '{new_id}': {updated_history_rows} sor frissítve az 'elo_history' táblában.")
                else:
                    print(f"  '{old_id}' nem található az 'elo_history' táblában (vagy már '{new_id}'-re van állítva).")
            except sqlite3.Error as e:
                print(f"  Hiba az 'elo_history' tábla frissítésekor ('{old_id}' -> '{new_id}'): {e}")
            print("-" * 20)


        conn.commit()
        print("\n--- Migráció befejezve ---")
        print("Az adatbázis módosításai sikeresen mentve lettek.")
        
        print("\nÖsszesítés a frissített sorokról:")
        for table_name, changes in updated_counts.items():
            print(f"  Tábla: {table_name}")
            for old_id_key, count in changes.items():
                if count > 0:
                     print(f"    '{old_id_key}' lecserélve: {count} sorban.")
        
        print("\nJavaslat: Ellenőrizd az alkalmazás működését és a szerver logokat, hogy minden rendben van-e.")
        print("Ha problémát tapasztalsz, állítsd vissza az adatbázist a biztonsági mentésből.")

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"\nADATBÁZIS HIBA TÖRTÉNT: {e}")
        print("A módosítások visszavonva. Az adatbázis eredeti állapotában maradt (a hiba előtti utolsó commitig).")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\nEgyéb, nem várt hiba történt: {e}")
        print("A módosítások visszavonva.")
    finally:
        if conn:
            conn.close()
            print("Adatbázis kapcsolat lezárva.")

if __name__ == '__main__':
    migrate_ids()
