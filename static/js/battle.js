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
        battleModel1Name.textContent = data.model1.name;
        battleModel2Name.textContent = data.model2.name;
        battleImage1.src = data.model1.image_url;
        battleImage2.src = data.model2.image_url;
        disableVoting(false);
    } else {
        battlePrompt.textContent = "Hiba a prompt betöltése közben.";
    }
}

async function handleVote(winnerId, loserId) {
    if (!currentBattleData) return;
    disableVoting(true);
    const voteData = {
        prompt_id: currentBattleData.prompt_id,
        winner: winnerId,
        loser: loserId
    };
    const result = await fetchData('/api/vote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(voteData)
    });
    if (result && result.success) {
        battleModel1Name.textContent = currentBattleData.model1.name;
        battleModel2Name.textContent = currentBattleData.model2.name;
        if (winnerId === currentBattleData.model1.id) {
            battleModel1Name.classList.add('text-success');
            battleModel1Name.style.fontWeight = 'bold';
        } else if (winnerId === currentBattleData.model2.id) {
            battleModel2Name.classList.add('text-success');
            battleModel2Name.style.fontWeight = 'bold';
        }
        setTimeout(() => {
            loadBattleData();
        }, getRevealDelayMs());
    } else {
        disableVoting(false);
    }
}

export function initBattleMode() {
    voteBtn1.addEventListener('click', () => {
        if (currentBattleData) {
            handleVote(currentBattleData.model1.id, currentBattleData.model2.id);
        }
    });
    voteBtn2.addEventListener('click', () => {
        if (currentBattleData) {
            handleVote(currentBattleData.model2.id, currentBattleData.model1.id);
        }
    });
    tieBtn.addEventListener('click', () => {
        if (currentBattleData) {
            battleModel1Name.textContent = currentBattleData.model1.name;
            battleModel2Name.textContent = currentBattleData.model2.name;
            setTimeout(() => {
                loadBattleData();
            }, getRevealDelayMs());
        } else {
            loadBattleData();
        }
    });
    skipBtn.addEventListener('click', () => {
        if (currentBattleData) {
            battleModel1Name.textContent = currentBattleData.model1.name;
            battleModel2Name.textContent = currentBattleData.model2.name;
            setTimeout(() => {
                loadBattleData();
            }, getRevealDelayMs());
        } else {
            loadBattleData();
        }
    });
}
