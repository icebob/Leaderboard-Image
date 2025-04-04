# Leaderboard Probléma Javítása

## Észlelt Hiba
A Leaderboard nem megfelelően jeleníti meg a modelleket. A következő problémák láthatók:

1. A config.py fájlban szereplő modellek és a Leaderboardon megjelenő modellek nem konzisztensek.
2. A Leaderboardon egy általános "Midjourney" modell szerepel, míg a config.py fájlban két külön verzió van: "Midjourney v6.1" és "Midjourney v7".
3. Vannak képfájlok a data mappában (pl. "flux11ultra" és "ideogram3"), amelyek nem vagy nem megfelelően szerepelnek a config.py fájlban.

## Megoldási Javaslat

1. **Szinkronizáljuk a modellneveket a config.py fájlban és az adatbázisban**: 
   - Frissítsük a config.py fájlt, hogy pontosan azok a modellek szerepeljenek benne, amelyek a data mappában megtalálhatók.
   - Adjuk hozzá a "flux11ultra" modellt a config.py fájlhoz, ha használni szeretnénk.
   - Vegyük ki a megjegyzésből az "Ideogram 3" modellt, ha az a data mappában aktívan szerepel.

2. **Adatbázis Reset**: 
   - Az új konfiguráció után futtassuk a `python app.py reset-votes` parancsot az adatbázis visszaállításához, hogy a modellek megfelelően jelenjenek meg a leaderboardon.

3. **Teszteljük a változtatások után**:
   - Ellenőrizzük, hogy a leaderboard most már az összes modellt megfelelően jeleníti-e meg.
   - Próbáljunk ki néhány szavazást, hogy meggyőződjünk arról, hogy az ELO értékek megfelelően frissülnek-e.

## Probléma a Modellek Konfigurációjával

A config.py fájlban a modellek a következőképpen vannak beállítva:
```python
MODELS = {
    'Grok': 'grok',
    'Google Gemini Flash': 'gemini-flash',
    'Google Imagen 3': 'imagen3',
    'ChatGPT GPT 4o': 'gpt4o',
    'Midjourney v6.1': 'midjourneyv61',
    'Midjourney v7': 'midjourneyv7',
    'Reve': 'reve', 
    #'Ideogram 3': 'ideogram'
}
```

A leaderboardon azonban ez jelenik meg:
```
# 	Modell 	                ELO Rating 	Győzelmek 	Meccsek száma 	Győzelmi arány
1 	Grok 	                1500 	    0 	        0 	            0%
2 	Google Gemini Flash 	1500 	    0 	        0 	            0%
3 	Google Imagen 3 	    1500 	    0 	        0 	            0%
4 	ChatGPT GPT 4o 	        1500 	    0 	        0 	            0%
5 	Midjourney 	            1500 	    0 	        0 	            0%
6 	Reve 	                1500 	    0 	        0 	            0%
```

A "Midjourney" összevont érték valószínűleg annak az eredménye, hogy a model_elo táblában a modellnevek nem frissültek megfelelően, vagy a tábla létrehozásakor régebbi konfigurációs értékek voltak érvényben. Az adatbázis resetelése megoldhatja ezt a problémát.

## További Teendők

Ha új modelleket szeretnénk hozzáadni, vagy modelleket szeretnénk eltávolítani, mindig kövessük ezeket a lépéseket:

1. Frissítsük a config.py fájlt a megfelelő modellnevekkel és fájlnevekkel.
2. Futtassuk a `python app.py reset-votes` parancsot az adatbázis frissítéséhez.
3. Ellenőrizzük a leaderboardot, hogy a megfelelő modellek jelennek-e meg.