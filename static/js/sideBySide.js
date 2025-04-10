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

// Fő funkciók
function updateSbsSelection() {
    currentSbsModel1 = sbsModel1Select.value;
    currentSbsModel2 = sbsModel2Select.value;
}

async function loadSideBySideData() {
    if (!currentSbsModel1 || !currentSbsModel2) {
        alert("Kérlek válassz ki mindkét modellt!");
        return;
    }
    if (currentSbsModel1 === currentSbsModel2) {
        alert("Kérlek válassz két különböző modellt!");
        return;
    }

    sbsImage1.src = "";
    sbsImage2.src = "";
    sbsPrompt.textContent = "Prompt betöltése...";
    sbsModel1Name.textContent = currentSbsModel1;
    sbsModel2Name.textContent = currentSbsModel2;
    sbsLoadBtn.disabled = true;

    // Elküldjük az előző prompt ID-t is, hogy ne kapjuk újra ugyanazt
    let apiUrl = `/api/side_by_side_data?model1=${currentSbsModel1}&model2=${currentSbsModel2}`;
    if (currentPromptId) {
        apiUrl += `&previous_prompt_id=${currentPromptId}`;
    }
    
    const data = await fetchData(apiUrl);
    if (data) {
        // Aktualizáljuk a jelenlegi prompt ID-t
        currentPromptId = data.prompt_id;
        
        sbsPrompt.textContent = `Prompt: "${data.prompt_text}" (ID: ${data.prompt_id})`;
        sbsImage1.src = data.model1.image_url;
        sbsImage2.src = data.model2.image_url;
    } else {
        sbsPrompt.textContent = "Hiba a prompt betöltése közben.";
    }
    sbsLoadBtn.disabled = false;
}

// Event listeners
export function initSideBySideMode() {
    sbsModel1Select.addEventListener('change', updateSbsSelection);
    sbsModel2Select.addEventListener('change', updateSbsSelection);
    sbsLoadBtn.addEventListener('click', loadSideBySideData);
    updateSbsSelection();
}
