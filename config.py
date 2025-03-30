# Konfigurációs beállítások a képkereső alkalmazáshoz

# Adatbázis fájl neve
DATABASE = 'votes.db'

# Az adatmappák elérési útja
DATA_DIR = 'data'

# Modell nevek és a hozzájuk tartozó fájl alapnevek (kiterjesztés nélkül)
# Fontos: Ezek csak a fájlok alapnevei, a kiterjesztés dinamikusan lesz meghatározva
MODELS = {
    'Grok': 'grok',
    'Google Gemini Flash': 'gemini-flash',
    'Google Imagen 3': 'imagen3',
    'ChatGPT GPT 4o': 'gpt4o',
    'Midjourney': 'midjourney',
    'Reve': 'reve'
}

# Engedélyezett képkiterjesztések listája
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png']

# ELO Rating beállítások
DEFAULT_ELO = 1500  # Alapértelmezett ELO érték új modellekhez
K_FACTOR = 32       # K-faktor - a magasabb érték nagyobb változást eredményez győzelemkor/vereségkor

# Felhasználói élmény beállítások
REVEAL_DELAY_MS = 1500  # Szavazás után a modellek neveinek megjelenítési ideje milliszekundumban