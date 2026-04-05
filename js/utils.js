import { subareaMapping } from './data.js';

export function title(name) {  
    return name
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

export function format(str, ...args) {
    return str.replace(/{(\d+)}/g, (match, index) => args[index])
}

export function buildFormattedArray(original, link, data) {
    if (!original) {
        return ['None'];
    }

    return (original || ['None']).map(val => {
        const sub = subareaMapping[val] ?? val;
        const name = data[sub]?.name ?? 'None';
        return name == 'None' ? 'None' : format(link, name)
    });
}