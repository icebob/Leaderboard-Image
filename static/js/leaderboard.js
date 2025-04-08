import { fetchData } from './api.js';

// DOM elemek
const leaderboardTableBody = document.getElementById('leaderboard-table-body');
const refreshLeaderboardBtn = document.getElementById('refresh-leaderboard-btn');

// Fő funkciók
export async function loadLeaderboardData() {
    leaderboardTableBody.innerHTML = '<tr><td colspan="6" class="text-center">Leaderboard betöltése...</td></tr>';
    refreshLeaderboardBtn.disabled = true;

    const data = await fetchData('/api/leaderboard');
    if (data) {
        leaderboardTableBody.innerHTML = '';
        if (data.length === 0) {
            leaderboardTableBody.innerHTML = '<tr><td colspan="6" class="text-center">Még nincsenek szavazatok.</td></tr>';
        } else {
            data.forEach((row, index) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${row.model}</td>
                    <td><strong>${row.elo}</strong></td>
                    <td>${row.wins}</td>
                    <td>${row.matches}</td>
                    <td>${row.win_rate}%</td>
                `;
                leaderboardTableBody.appendChild(tr);
            });
        }
    } else {
        leaderboardTableBody.innerHTML = '<tr><td colspan="6" class="text-center">Hiba a leaderboard betöltése közben.</td></tr>';
    }
    refreshLeaderboardBtn.disabled = false;
}

// Event listeners
export function initLeaderboardMode() {
    refreshLeaderboardBtn.addEventListener('click', loadLeaderboardData);
}
