# Konfigurációs beállítások a képkereső alkalmazáshoz

# Adatbázis fájl neve
DATABASE = 'votes.db'

# Az adatmappák elérési útja
DATA_DIR = 'data'

# Modell nevek és a hozzájuk tartozó fájlkiterjesztések/nevek
# Fontos: A kulcsoknak meg kell egyezniük a fájlnevekben használtakkal (kiterjesztés nélkül)
# és azokkal, amiket a frontend/backend logikában használsz.
MODELS = {
    'grok': 'grok.jpg',
    'gemini-flash': 'gemini-flash.jpeg',
    'gemini-25pro': 'gemini-25pro.jpg',
    'gpt4o': 'gpt4o.png',
    'midjourney': 'midjourney.png'  # Figyelj arra, hogy ez PNG kiterjesztést használ
}

# Engedélyezett képkiterjesztések listája
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png']

# ELO Rating beállítások
DEFAULT_ELO = 1500  # Alapértelmezett ELO érték új modellekhez
K_FACTOR = 32       # K-faktor - a magasabb érték nagyobb változást eredményez győzelemkor/vereségkor