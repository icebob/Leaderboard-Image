import { fetchData } from './api.js';
import { colorPalette } from './config.js';

// DOM elemek
const eloHistoryChartCanvas = document.getElementById('eloHistoryChart');
const refreshHistoryBtn = document.getElementById('refresh-history-btn');
let eloHistoryChart = null;

// Dátum formázó függvények - natív JavaScript-tel
function formatDate(date, formatStr) {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    if (formatStr === 'yyyy.MM.dd. HH:mm') {
        return `${year}.${month}.${day}. ${hours}:${minutes}`;
    } else if (formatStr === 'yyyy.MM.dd.') {
        return `${year}.${month}.${day}.`;
    } else if (formatStr === 'MM.dd.') {
        return `${month}.${day}.`;
    } else if (formatStr === 'HH:mm') {
        return `${hours}:${minutes}`;
    } else if (formatStr === 'yyyy.MM.') {
        return `${year}.${month}.`;
    }
    
    return `${year}.${month}.${day}. ${hours}:${minutes}`;
}

// Fő funkciók
export { loadEloHistoryData, initEloHistoryMode };

async function loadEloHistoryData() {
    refreshHistoryBtn.disabled = true;
    const data = await fetchData('/api/elo_history');
    
    if (data) {
        renderEloHistoryChart(data);
    } else {
        console.error("Hiba az ELO előzmények betöltése közben.");
        if (eloHistoryChart) {
            eloHistoryChart.destroy();
        }
        const ctx = eloHistoryChartCanvas.getContext('2d');
        ctx.clearRect(0, 0, eloHistoryChartCanvas.width, eloHistoryChartCanvas.height);
        ctx.textAlign = 'center';
        ctx.fillText('Hiba a grafikon adatainak betöltése közben.', 
            eloHistoryChartCanvas.width / 2, eloHistoryChartCanvas.height / 2);
    }
    refreshHistoryBtn.disabled = false;
}

function renderEloHistoryChart(apiData) {
    if (eloHistoryChart) {
        eloHistoryChart.destroy();
    }
    
    const datasets = [];
    const modelColors = {};
    let colorIndex = 0;

    // Összegyűjtjük az összes időpontot és ELO változást
    const allPoints = [];
    for (const model in apiData) {
        apiData[model].forEach(point => {
            allPoints.push({
                date: new Date(point.x),
                elo: point.y,
                model: model
            });
        });
    }
    
    // Időpontok szerint rendezzük
    allPoints.sort((a, b) => a.date - b.date);

    // Számoljuk ki az időkülönbségeket és az ELO változásokat
    const changes = new Map();
    const dayInMs = 24 * 60 * 60 * 1000;
    
    for (let i = 1; i < allPoints.length; i++) {
        const currentDate = allPoints[i].date;
        const prevDate = allPoints[i-1].date;
        const dateKey = currentDate.toISOString().split('T')[0];
        
        if (!changes.has(dateKey)) {
            changes.set(dateKey, {
                count: 0,
                eloDiffs: []
            });
        }
        
        const dayData = changes.get(dateKey);
        dayData.count++;
        dayData.eloDiffs.push(Math.abs(allPoints[i].elo - allPoints[i-1].elo));
    }

    // Készítsünk szűrt adatpontokat minden modellhez
    for (const model in apiData) {
        if (!modelColors[model]) {
            modelColors[model] = colorPalette[colorIndex % colorPalette.length];
            colorIndex++;
        }
        
        const data = apiData[model];
        if (data.length <= 3) {
            datasets.push({
                label: model,
                data: data,
                borderColor: modelColors[model],
                backgroundColor: modelColors[model] + '33',
                tension: 0.1,
                fill: false
            });
            continue;
        }

        // Pontok szűrése az aktivitás alapján
        const filteredData = [];
        for (let i = 0; i < data.length; i++) {
            const current = new Date(data[i].x);
            const dateKey = current.toISOString().split('T')[0];
            const dayData = changes.get(dateKey);
            
            // Első és utolsó pont mindig kell
            if (i === 0 || i === data.length - 1) {
                filteredData.push(data[i]);
                continue;
            }

            const prev = new Date(data[i-1].x);
            const next = new Date(data[i+1].x);
            const timeToPrev = current - prev;
            const timeToNext = next - current;
            
            // Ha ez egy aktív nap vagy jelentős változás történt, megtartjuk
            if (dayData && (
                dayData.count >= 3 || // Aktív nap
                Math.max(...dayData.eloDiffs) > 0.5 || // Jelentős ELO változás
                timeToPrev > dayInMs * 7 || // Hosszú inaktív időszak előtte
                timeToNext > dayInMs * 7 // Hosszú inaktív időszak utána
            )) {
                filteredData.push(data[i]);
            }
        }

        datasets.push({
            label: model,
            data: filteredData,
            borderColor: modelColors[model],
            backgroundColor: modelColors[model] + '33',
            tension: 0.1,
            fill: false
        });
    }

    const ctx = eloHistoryChartCanvas.getContext('2d');
    eloHistoryChart = new Chart(ctx, {
        type: 'line',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 750
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Modellek ELO Pontszámának Változása az Időben'
                },
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)} ELO`;
                        },
                        title: function(context) {
                            return formatDate(context[0].parsed.x, 'yyyy.MM.dd. HH:mm');
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        minUnit: 'hour',
                        displayFormats: {
                            hour: 'HH:mm',
                            day: 'MM.dd.',
                            week: 'yyyy.MM.dd.',
                            month: 'yyyy.MM.'
                        }
                    },
                    ticks: {
                        source: 'auto',
                        maxRotation: 45,
                        autoSkip: true,
                        callback: function(value) {
                            const date = new Date(value);
                            const format = 
                                date.getHours() === 0 ? 'yyyy.MM.dd.' :
                                'HH:mm';
                            return formatDate(date, format);
                        }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'ELO Pontszám'
                    },
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(0);
                        }
                    }
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

// Event listeners
function initEloHistoryMode() {
    refreshHistoryBtn.addEventListener('click', loadEloHistoryData);
}
