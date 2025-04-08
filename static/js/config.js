// Konfigurációs beállítások és konstansok
export const colorPalette = [
    '#0d6efd', '#6f42c1', '#d63384', '#fd7e14', '#ffc107', 
    '#198754', '#20c997', '#0dcaf0', '#6c757d', '#adb5bd'
];

// Alapértelmezett késleltetési idő, amire visszaesik, ha nem lenne máshogy beállítva
export const DEFAULT_REVEAL_DELAY_MS = 1500;

// A késleltetési időt dinamikusan olvassuk ki
export function getRevealDelayMs() {
    return parseInt(document.documentElement.dataset.revealDelay) || DEFAULT_REVEAL_DELAY_MS;
}
