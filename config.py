# Konfigurációs beállítások a képkereső alkalmazáshoz

# Adatbázis fájl neve
DATABASE = 'votes.db'

# Az adatmappák elérési útja
DATA_DIR = 'data'

# Modell nevek és a hozzájuk tartozó adatok
# Minden modell egy szótár, ami tartalmazza:
# - 'filename': A fájlnév alaprésze kiterjesztés nélkül
# - 'open_source': Boolean érték, True ha letölthető/open source modell, False ha zárt/nem letölthető
MODELS = {
    'Grok': {'filename': 'grok', 'open_source': False},
    'Google Gemini Flash 2.0': {'filename': 'gemini-flash', 'open_source': False},
    'Google Imagen 3': {'filename': 'imagen3', 'open_source': False},
    'ChatGPT GPT 4o': {'filename': 'gpt4o', 'open_source': False},
    'Midjourney v6.1': {'filename': 'midjourneyv61', 'open_source': False},
    'Midjourney v7': {'filename': 'midjourneyv7', 'open_source': False},
    'Reve': {'filename': 'reve', 'open_source': False},
    'HiDream-I1': {'filename': 'hidreami1', 'open_source': True},
    'Lumina-Image-2.0': {'filename': 'lumina2', 'open_source': True},
    'Capcut Dreamina Image 2.0 Pro': {'filename': 'dreamina-image20pro', 'open_source': False},
    'Juggernaut XI': {'filename': 'juggernautxl', 'open_source': True},
    'Fluxmania V': {'filename': 'fluxmaniaV', 'open_source': True},
    'Tengr.ai': {'filename': 'tengrai', 'open_source': False},
    'Tengr.ai Quantum': {'filename': 'tengrai-q', 'open_source': False},
    'Adobe Firefly Image 4': {'filename': 'firefly4', 'open_source': False},
    'Dreamina Seedream 3.0': {'filename': 'dreamina-image3', 'open_source': False},
    'Ideogram 3.0': {'filename': 'ideogram3', 'open_source': False},
    'Piclumen Realistic V2': {'filename': 'piclumen-realistic-v2', 'open_source': False},
    'F Lite Standard': {'filename': 'f-lite-standard', 'open_source': True},
    'Google Gemini Flash 2.0 Preview 0507': {'filename': 'gemini-2.0-flash-0507', 'open_source': False},
    'Midjourney v7 20250501': {'filename': 'midjourneyv7-20250501', 'open_source': False},
}

# Engedélyezett képkiterjesztések listája
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

# ELO Rating beállítások
DEFAULT_ELO = 1500  # Alapértelmezett ELO érték új modellekhez
K_FACTOR = 32       # K-faktor - a magasabb érték nagyobb változást eredményez győzelemkor/vereségkor

# Felhasználói élmény beállítások
REVEAL_DELAY_MS = 2500  # Szavazás után a modellek neveinek megjelenítési ideje milliszekundumban