import { fetchData } from './api.js';

// DOM elemek
const sbsModeDiv = document.getElementById('side-by-side-mode');
const sbsModel1Select = document.getElementById('sbs-model1-select');
const sbsModel2Select = document.getElementById('sbs-model2-select');
const sbsLoadBtn = document.getElementById('sbs-load-btn');
const sbsPrompt = document.getElementById('sbs-prompt');
const sbsModel1Name = document.getElementById('sbs-model1-name');
const sbsImage1 = document.getElementById('sbs-image1');
const sbsModel2Name = document.getElementById('sbs-model2-name');
const sbsImage2 = document.getElementById('sbs-image2');

// Állapot
let currentSbsModel1 = '';
let currentSbsModel2 = '';
let currentPromptId = null; // Az aktuális prompt azonosítója

// Új funkció kép betöltéséhez modellváltáskor
async function fetchModelImage(modelName, promptId, imageElement, modelNameElement) {
    if (!promptId || !modelName) return; // Ne csináljon semmit, ha nincs prompt vagy modell

    modelNameElement.textContent = modelName; // Azonnal frissítjük a nevet
    const currentSrc = imageElement.src; // Mentsük el a jelenlegi src-t a visszaállításhoz hiba esetén
    imageElement.src = ""; // Töröljük az előző képet / loading state
    imageElement.alt = `${modelName} képének betöltése...`;

    try {
        // Feltételezünk egy új API végpontot: /api/get_image?model=...&prompt_id=...
        const apiUrl = `/api/get_image?model=${encodeURIComponent(modelName)}&prompt_id=${promptId}`;
        const data = await fetchData(apiUrl);
        if (data && data.image_url) {
            imageElement.src = data.image_url;
            imageElement.alt = `${modelName} képe`; // Sikeres betöltés utáni alt text
        } else {
            console.error("Hiba a kép URL lekérésekor vagy hiányzó image_url:", data);
            imageElement.alt = "Kép betöltése sikertelen"; // Hiba jelzése
            // Hiba esetén visszaállíthatjuk az előző képet, ha volt
            // if (currentSrc) imageElement.src = currentSrc;
            // Vagy placeholder: imageElement.src = "/static/images/placeholder.png";
        }
    } catch (error) {
        console.error(`Hiba a(z) ${modelName} képének betöltésekor:`, error);
        imageElement.alt = "Kép betöltése sikertelen";
         // Hiba esetén visszaállíthatjuk az előző képet, ha volt
         // if (currentSrc) imageElement.src = currentSrc;
         // Vagy placeholder: imageElement.src = "/static/images/placeholder.png";
    }
}

// Fő funkciók
async function loadSideBySideData() {
    // Kezdeti modellek beolvasása a select elemekből
    const selectedModel1 = sbsModel1Select.value;
    const selectedModel2 = sbsModel2Select.value;

    if (!selectedModel1 || !selectedModel2) {
        alert("Kérlek válassz ki mindkét modellt!");
        return;
    }
    if (selectedModel1 === selectedModel2) {
        alert("Kérlek válassz két különböző modellt!");
        // Opcionálisan visszaállíthatjuk a selecteket az előző állapotra, ha tároltuk őket
        return;
    }

    // Állapot frissítése a kiválasztottakkal
    currentSbsModel1 = selectedModel1;
    currentSbsModel2 = selectedModel2;

    sbsImage1.src = "";
    sbsImage2.src = "";
    sbsImage1.alt = "Kép betöltése...";
    sbsImage2.alt = "Kép betöltése...";
    sbsPrompt.textContent = "Prompt betöltése...";
    sbsModel1Name.textContent = currentSbsModel1;
    sbsModel2Name.textContent = currentSbsModel2;
    sbsLoadBtn.disabled = true;

    // Mindig új promptot kérünk a "Betöltés" gombbal
    let apiUrl = `/api/side_by_side_data?model1=${currentSbsModel1}&model2=${currentSbsModel2}`;
    // Nem küldjük a previous_prompt_id-t, hogy a szerver új promptot adjon.
    // Ha mégis a régi promptot kéne használni, ha van, akkor a currentPromptId-t nem nulláznánk
    // és hozzáadnánk a previous_prompt_id paramétert, ha currentPromptId létezik.
    // currentPromptId = null; // Ezt nem kell nullázni, a válaszban kapott ID felülírja

    const data = await fetchData(apiUrl);
    if (data && data.prompt_id) { // Ellenőrizzük, hogy kaptunk-e prompt_id-t
        // Aktualizáljuk a jelenlegi prompt ID-t
        currentPromptId = data.prompt_id;

        sbsPrompt.textContent = `Prompt: "${data.prompt_text}" (ID: ${data.prompt_id})`;
        sbsImage1.src = data.model1.image_url;
        sbsImage2.src = data.model2.image_url;
        sbsImage1.alt = `${currentSbsModel1} képe`;
        sbsImage2.alt = `${currentSbsModel2} képe`;
        // Név frissítése itt is, bár már fentebb megtörtént
        sbsModel1Name.textContent = currentSbsModel1;
        sbsModel2Name.textContent = currentSbsModel2;

    } else {
        sbsPrompt.textContent = "Hiba a prompt betöltése közben.";
        console.error("Hiba a side-by-side adatok lekérésekor:", data);
        currentPromptId = null; // Hiba esetén nullázzuk
        sbsModel1Name.textContent = currentSbsModel1; // Nevek maradjanak? Vagy töröljük?
        sbsModel2Name.textContent = currentSbsModel2;
        sbsImage1.alt = "Hiba";
        sbsImage2.alt = "Hiba";
    }
    sbsLoadBtn.disabled = false;
}

// Következő prompt betöltése (nem random, hanem ID szerint)
async function loadNextPromptData() {
    // Lekérjük az összes prompt ID-t a szervertől
    const promptListData = await fetchData('/api/prompt_ids');
    if (!promptListData || !Array.isArray(promptListData.prompt_ids)) {
        alert('Nem sikerült lekérni a prompt listát!');
        return;
    }
    const promptIds = promptListData.prompt_ids;
    if (!promptIds.length) {
        alert('Nincs elérhető prompt!');
        return;
    }
    // Ha nincs még prompt, az elsőt töltjük be
    let nextPromptId;
    if (!currentPromptId) {
        nextPromptId = promptIds[0];
    } else {
        const idx = promptIds.indexOf(currentPromptId);
        if (idx === -1 || idx === promptIds.length - 1) {
            nextPromptId = promptIds[0]; // Körbe érünk
        } else {
            nextPromptId = promptIds[idx + 1];
        }
    }
    // Modellek lekérése
    const selectedModel1 = sbsModel1Select.value;
    const selectedModel2 = sbsModel2Select.value;
    if (!selectedModel1 || !selectedModel2) {
        alert('Kérlek válassz ki mindkét modellt!');
        return;
    }
    if (selectedModel1 === selectedModel2) {
        alert('Kérlek válassz két különböző modellt!');
        return;
    }
    // Prompt szöveg lekérése
    const promptData = await fetchData(`/api/prompt_text?prompt_id=${nextPromptId}`);
    if (!promptData || !promptData.prompt_text) {
        alert('Nem sikerült lekérni a prompt szövegét!');
        return;
    }
    // Képek lekérése a két modellhez
    const [img1, img2] = await Promise.all([
        fetchData(`/api/get_image?model=${encodeURIComponent(selectedModel1)}&prompt_id=${nextPromptId}`),
        fetchData(`/api/get_image?model=${encodeURIComponent(selectedModel2)}&prompt_id=${nextPromptId}`)
    ]);
    // Állapot frissítése
    currentPromptId = nextPromptId;
    currentSbsModel1 = selectedModel1;
    currentSbsModel2 = selectedModel2;
    // UI frissítés
    sbsPrompt.textContent = `Prompt: "${promptData.prompt_text}" (ID: ${nextPromptId})`;
    sbsImage1.src = img1 && img1.image_url ? img1.image_url : '';
    sbsImage2.src = img2 && img2.image_url ? img2.image_url : '';
    sbsImage1.alt = `${currentSbsModel1} képe`;
    sbsImage2.alt = `${currentSbsModel2} képe`;
    sbsModel1Name.textContent = currentSbsModel1;
    sbsModel2Name.textContent = currentSbsModel2;
}

// Event listeners
export function initSideBySideMode() {
    // Eseményfigyelők a modellek kiválasztásához
    sbsModel1Select.addEventListener('change', async (event) => {
        const newModel1 = event.target.value;
        // Ellenőrizzük, hogy a választott modell eltér-e a másik oldalon lévőtől
        if (newModel1 === currentSbsModel2) {
            alert("A két modell nem lehet azonos!");
            event.target.value = currentSbsModel1; // Visszaállítjuk az előzőre
            return;
        }
        // Csak akkor csinálunk bármit, ha ténylegesen változott a modell
        if (newModel1 !== currentSbsModel1) {
            const oldModel1 = currentSbsModel1;
            currentSbsModel1 = newModel1; // Frissítjük az állapotot

            // Csak akkor töltjük újra a képet, ha már van betöltött prompt
            if (currentPromptId) {
                 // Azonnal frissítjük a nevet és elindítjuk a képbetöltést
                 await fetchModelImage(currentSbsModel1, currentPromptId, sbsImage1, sbsModel1Name);
            }
            // Ha még nincs prompt betöltve (pl. oldalbetöltés után), nem csinálunk semmit
            // a kép újratöltésével, csak az állapotot frissítettük. A "Betöltés" gomb hozza majd az első képeket.
        }
    });

    sbsModel2Select.addEventListener('change', async (event) => {
        const newModel2 = event.target.value;
        // Ellenőrizzük, hogy a választott modell eltér-e a másik oldalon lévőtől
        if (newModel2 === currentSbsModel1) {
            alert("A két modell nem lehet azonos!");
            event.target.value = currentSbsModel2; // Visszaállítjuk az előzőre
            return;
        }
         // Csak akkor csinálunk bármit, ha ténylegesen változott a modell
        if (newModel2 !== currentSbsModel2) {
            const oldModel2 = currentSbsModel2;
            currentSbsModel2 = newModel2; // Frissítjük az állapotot

            // Csak akkor töltjük újra a képet, ha már van betöltött prompt
            if (currentPromptId) {
                 // Azonnal frissítjük a nevet és elindítjuk a képbetöltést
                 await fetchModelImage(currentSbsModel2, currentPromptId, sbsImage2, sbsModel2Name);
            }
             // Ha még nincs prompt betöltve, nem csinálunk semmit.
        }
    });

    // Eseményfigyelő a "Betöltés" gombra
    sbsLoadBtn.addEventListener('click', loadSideBySideData);

    // Következő prompt gomb eseménykezelő
    const sbsNextBtn = document.getElementById('sbs-next-btn');
    if (sbsNextBtn) {
        sbsNextBtn.addEventListener('click', loadNextPromptData);
    }

    // Kezdeti modellek beállítása az oldalbetöltéskor (ha vannak alapértelmezett értékek a HTML-ben)
    // Ezeket az értékeket a loadSideBySideData fogja használni az első kattintáskor.
    currentSbsModel1 = sbsModel1Select.value;
    currentSbsModel2 = sbsModel2Select.value;
}

// Megjegyzés: A `fetchData` importálva van a './api.js'-ből.
// Szükség van egy új backend végpontra: /api/get_image?model=...&prompt_id=...
// amely visszaad egy JSON objektumot `{ "image_url": "..." }` formátumban.
