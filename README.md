# Képgenerátor Aréna

![AI képgenerátorok összehasonlítása](docs/images/arena-battle.png)

## 🚀 Áttekintés

A Képgenerátor Aréna egy web-alapú alkalmazás, amely lehetővé teszi különböző AI képgenerátorok által létrehozott képek összehasonlítását és értékelését. A rendszer három fő módot kínál:

- **Arena Battle:** Két kép közvetlen összehasonlítása, ahol a felhasználók a jobbnak ítélt képre szavazhatnak
- **Side-by-Side:** Két kiválasztott modell képeinek összehasonlítása egymás mellett
- **Leaderboard:** A modellek ranglistája az ELO pontszámok és egyéb statisztikák alapján

## ✨ Funkciók

- 🏆 **ELO Rating:** Fejlett pontrendszer, amely figyelembe veszi az ellenfelek erősségét
- 🖼️ **Több formátum támogatása:** JPG, JPEG és PNG
- ⚙️ **Konfigurálhatóság:** Modellek, fájlformátumok és alapbeállítások külön konfigurációs fájlban
- 👁️‍🗨️ **Vak szavazás:** Arena Battle módban a modellek nevei csak a szavazás után jelennek meg
- 📊 **Részletes statisztikák:** ELO pontszámok, győzelmek, mérkőzések száma és győzelmi arányok

## 🛠️ Telepítés

### Követelmények

- Python 3.6+
- pip (Python csomagkezelő)
- Git (opcionális)

### Telepítési lépések

```bash
# 1. Klónozd vagy töltsd le a repository-t
git clone https://github.com/yourusername/image-leaderboard.git
cd image-leaderboard

# 2. Függőségek telepítése
pip install -r requirements.txt

# 3. Adatbázis inicializálása
python database.py

# 4. Alkalmazás indítása
flask run --host=0.0.0.0

# Az alkalmazás alapértelmezetten a következő címen érhető el:
# http://localhost:5000
```

## 📋 Használat

### 1. Arena Battle

Az Arena Battle a rendszer fő módja, ahol két véletlenszerűen kiválasztott modell által generált kép jelenik meg egymás mellett. A felhasználók kiválaszthatják, melyik kép tetszik jobban, vagy döntetlen/kihagyás opciót választhatnak.

A modellek nevei csak a szavazás után jelennek meg, így biztosítva az elfogulatlan értékelést.

### 2. Side-by-Side

A Side-by-Side módban a felhasználók maguk választhatják ki, melyik két modellt szeretnék összehasonlítani. Ez a mód elsősorban vizuális összehasonlításra szolgál, nincs szavazás.

### 3. Leaderboard

A Leaderboard a modellek ranglistáját mutatja ELO pontszám szerint csökkenő sorrendben. A táblázat tartalmazza az ELO értékeket, a győzelmek számát, az összes mérkőzés számát és a győzelmi arányt.

## ⚙️ Parancssori funkciók

### Szavazatok resetelése

```bash
python app.py reset-votes
```

Ez a parancs törli az összes eddigi szavazatot és visszaállítja az ELO pontszámokat az alapértelmezett értékre. Ezt akkor érdemes használni, ha:
- Teljesen új versenyt akarsz indítani
- Tesztadatok után szeretnéd az éles adatgyűjtést elkezdeni
- Problémás szavazatok kerültek a rendszerbe

## 📁 Rugalmas fájlkezelés

A rendszer képes rugalmasan kezelni a képfájlok kiterjesztéseit. Ez azt jelenti, hogy:

- ✅ Ugyanazon modell képei különböző kiterjesztésekkel szerepelhetnek különböző prompt mappákban
- ✅ Támogatott kiterjesztések: `.jpg`, `.jpeg`, `.png`
- ⚠️ A fájlnév alaprésze (kiterjesztés nélkül) mindig meg kell hogy egyezzen a konfigurációban beállítottal

Példa konfiguráció:
```python
# Modell nevek és a hozzájuk tartozó fájl alapnevek (kiterjesztés nélkül)
MODELS = {
    'Grok': 'grok',
    'Google Gemini Flash': 'gemini-flash',
    'Google Imagen 3': 'imagen3', 
    'ChatGPT GPT 4o': 'gpt4o',
    'Midjourney v6.1': 'midjourneyv61',
    'Midjourney v7': 'midjourneyv7',
    'Reve': 'reve'
}
```

## 🌟 Jelenleg támogatott modellek

- Grok
- Google Gemini Flash
- Google Imagen 3
- ChatGPT GPT 4o
- Midjourney
- Reve

## 📝 Licenc

[MIT](LICENSE)

## 📚 További dokumentáció

A részletes dokumentáció a `docs/index.html` fájlban található.