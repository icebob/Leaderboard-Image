// filepath: d:\AI\Leaderboard-Image\static\js\battle.js
import { fetchData } from './api.js';
import { getRevealDelayMs } from './config.js';

// DOM elemek
const battleModeDiv = document.getElementById('battle-mode');
const battlePrompt = document.getElementById('battle-prompt');
const battleModel1Name = document.getElementById('battle-model1-name');
const battleImage1 = document.getElementById('battle-image1');
const voteBtn1 = document.getElementById('vote-btn1');
const battleModel2Name = document.getElementById('battle-model2-name');
const battleImage2 = document.getElementById('battle-image2');
const voteBtn2 = document.getElementById('vote-btn2');
const tieBtn = document.getElementById('tie-btn');
const skipBtn = document.getElementById('skip-btn');

// Állapot
let currentBattleData = null;

// Segédfüggvények
function resetModelNameStyles() {
    battleModel1Name.classList.remove('text-success');
    battleModel2Name.classList.remove('text-success');
    battleModel1Name.style.fontWeight = 'normal';
    battleModel2Name.style.fontWeight = 'normal';
}

function disableVoting(disabled) {
    voteBtn1.disabled = disabled;
    voteBtn2.disabled = disabled;
    tieBtn.disabled = disabled;
    skipBtn.disabled = disabled;
}

// Fő funkciók
export async function loadBattleData() {
    battleImage1.src = "";
    battleImage2.src = "";
    battlePrompt.textContent = "Új prompt betöltése...";
    
    resetModelNameStyles();
    battleModel1Name.textContent = "Modell A";
    battleModel2Name.textContent = "Modell B";
    
    disableVoting(true);
    const data = await fetchData('/api/battle_data');
    if (data) {
        currentBattleData = data;
        battlePrompt.textContent = `Prompt: "${data.prompt_text}" (ID: ${data.prompt_id})`;
        
        if (data.reveal_models) {
            battleModel1Name.textContent = data.model1.key;
            battleModel2Name.textContent = data.model2.key;
        }
        
        battleImage1.src = data.model1.image_url;
        battleImage2.src = data.model2.image_url;
        disableVoting(false);
    } else {
        battlePrompt.textContent = "Hiba a prompt betöltése közben.";
    }
}

async function handleVote(winner, loser) {
    if (!currentBattleData) return;
    disableVoting(true);
    
    const voteData = {
        prompt_id: currentBattleData.prompt_id,
        winner: winner,
        loser: loser
    };
    
    const result = await fetchData('/api/vote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(voteData)
    });
    
    if (result && result.success) {
        console.log("Vote successful:", result.message);
        
        battleModel1Name.textContent = currentBattleData.model1.key;
        battleModel2Name.textContent = currentBattleData.model2.key;
        
        if (winner === currentBattleData.model1.key) {
            battleModel1Name.classList.add('text-success');
            battleModel1Name.style.fontWeight = 'bold';
        } else if (winner === currentBattleData.model2.key) {
            battleModel2Name.classList.add('text-success');
            battleModel2Name.style.fontWeight = 'bold';
        }
        
        setTimeout(() => {
            loadBattleData();
        }, getRevealDelayMs());
    } else {
        alert("Hiba történt a szavazás rögzítésekor.");
        disableVoting(false);
    }
}

// Event listeners
export function initBattleMode() {
    voteBtn1.addEventListener('click', () => {
        if (currentBattleData) {
            handleVote(currentBattleData.model1.key, currentBattleData.model2.key);
        }
    });

    voteBtn2.addEventListener('click', () => {
        if (currentBattleData) {
            handleVote(currentBattleData.model2.key, currentBattleData.model1.key);
        }
    });

    tieBtn.addEventListener('click', () => {
        if (currentBattleData) {
            battleModel1Name.textContent = currentBattleData.model1.key;
            battleModel2Name.textContent = currentBattleData.model2.key;
            setTimeout(() => {
                loadBattleData();
            }, getRevealDelayMs());
        } else {
            loadBattleData();
        }
    });

    skipBtn.addEventListener('click', () => {
        if (currentBattleData) {
            battleModel1Name.textContent = currentBattleData.model1.key;
            battleModel2Name.textContent = currentBattleData.model2.key;
            setTimeout(() => {
                loadBattleData();
            }, getRevealDelayMs());
        } else {
            loadBattleData();
        }
    });
}
