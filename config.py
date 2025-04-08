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
    'Midjourney v6.1': 'midjourneyv61',
    'Midjourney v7': 'midjourneyv7',
    'Reve': 'reve',
    'HiDream-I1':'hidreami1'
    #'Ideogram 3': 'ideogram3',
    #'Flux 11 Ultra': 'flux11ultra'
}

# Engedélyezett képkiterjesztések listája
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png']

# ELO Rating beállítások
DEFAULT_ELO = 1500  # Alapértelmezett ELO érték új modellekhez
K_FACTOR = 32       # K-faktor - a magasabb érték nagyobb változást eredményez győzelemkor/vereségkor

# Felhasználói élmény beállítások
REVEAL_DELAY_MS = 2500  # Szavazás után a modellek neveinek megjelenítési ideje milliszekundumban