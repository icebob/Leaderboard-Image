import { fetchData } from './api.js';
import { colorPalette } from './config.js';

const eloHistoryChartCanvas = document.getElementById('eloHistoryChart');
const refreshHistoryBtn = document.getElementById('refresh-history-btn');
let eloHistoryChart = null;

function formatDate(date, formatStr) {
    if (typeof date === 'string') date = new Date(date);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    if (formatStr === 'yyyy.MM.dd. HH:mm') return `${year}.${month}.${day}. ${hours}:${minutes}`;
    if (formatStr === 'yyyy.MM.dd.') return `${year}.${month}.${day}.`;
    if (formatStr === 'MM.dd.') return `${month}.${day}.`;
    if (formatStr === 'HH:mm') return `${hours}:${minutes}`;
    if (formatStr === 'yyyy.MM.') return `${year}.${month}.`;
    return `${year}.${month}.${day}. ${hours}:${minutes}`;
}

export async function loadEloHistoryData() {
    refreshHistoryBtn.disabled = true;
    const data = await fetchData('/api/elo_history');
    if (data) {
        renderEloHistoryChart(data);
    } else {
        console.error('Hiba az ELO előzmények betöltése közben.');
        if (eloHistoryChart) eloHistoryChart.destroy();
        const ctx = eloHistoryChartCanvas.getContext('2d');
        ctx.clearRect(0, 0, eloHistoryChartCanvas.width, eloHistoryChartCanvas.height);
        ctx.textAlign = 'center';
        ctx.fillText('Hiba a grafikon adatainak betöltése közben.', eloHistoryChartCanvas.width/2, eloHistoryChartCanvas.height/2);
    }
    refreshHistoryBtn.disabled = false;
}

function renderEloHistoryChart(apiData) {
    if (eloHistoryChart) eloHistoryChart.destroy();

    // 1. Collect all unique timestamps and sort them
    const allTimestamps = new Set();
    for (const model in apiData) {
        apiData[model].forEach(point => allTimestamps.add(new Date(point.x).getTime()));
    }
    const sortedTimestamps = Array.from(allTimestamps).sort((a, b) => a - b);

    // 2. Create labels for the category axis
    const labels = sortedTimestamps.map(ts => formatDate(new Date(ts), 'yyyy.MM.dd. HH:mm'));
    const timestampToIndex = new Map(sortedTimestamps.map((ts, index) => [ts, index]));

    // 3. Transform datasets for the category axis
    const datasets = [];
    let colorIndex = 0;
    for (const model in apiData) {
        const modelData = apiData[model];
        const categoryData = new Array(sortedTimestamps.length).fill(null);

        modelData.forEach(point => {
            const timestamp = new Date(point.x).getTime();
            const index = timestampToIndex.get(timestamp);
            if (index !== undefined) {
                categoryData[index] = point.y;
            }
        });

        // Optional: Fill nulls with the previous non-null value to make lines continuous
        // Remove this loop if you want gaps in lines when a model misses a timestamp
        let lastValue = null;
        for (let i = 0; i < categoryData.length; i++) {
            if (categoryData[i] !== null) {
                lastValue = categoryData[i];
            } else if (lastValue !== null) {
                 // Use previous value if current is null, remove if gaps are desired
                // categoryData[i] = lastValue; // Uncomment to fill gaps
            }
        }


        datasets.push({
            label: model,
            data: categoryData, // Use the transformed data
            borderColor: colorPalette[colorIndex % colorPalette.length],
            backgroundColor: colorPalette[colorIndex % colorPalette.length] + '33', // Optional: for area fill if needed
            tension: 0.1,
            fill: false,
            spanGaps: true // Connect points across null values
        });
        colorIndex++;
    }

    // 4. Render chart with category scale
    const ctx = eloHistoryChartCanvas.getContext('2d');
    eloHistoryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels, // Use generated labels
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Modellek ELO Pontszámának Változása (Sűrített Időskála)' // Updated title
                },
                legend: {
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        // Display ELO, use label (formatted date) for the title
                        label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y !== null ? ctx.parsed.y.toFixed(1) : 'N/A'} ELO`,
                        title: ctx => ctx[0]?.label || '' // Tooltip title is the category label
                    }
                }
            },
            scales: {
                x: {
                    // Use 'category' scale instead of 'time'
                    type: 'category',
                    title: {
                        display: true,
                        text: 'Időpont (csak frissítésekkel)'
                    }
                    // Removed time-specific formatting
                },
                y: {
                    title: {
                        display: true,
                        text: 'ELO Pontszám'
                    },
                    beginAtZero: false
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

export function initEloHistoryMode() {
    refreshHistoryBtn.addEventListener('click', loadEloHistoryData);
}
