import { subareaMapping } from './data.js';

export function title(name) {  
    return name
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

export function format(str, ...args) {
    return str.replace(/{(\d+)}/g, (match, index) => args[index] ?? match)
}

export function buildFormattedArray(original, link, data) {
    if (!original) return ['None'];

    return (original).map(val => {
        const sub = subareaMapping[val] ?? val;
        const name = data[sub]?.name ?? 'None';
        const new_link = sub === val ? format(link, name) : format(link, name, sub)
        return name == 'None' ? 'None' : new_link
    });
}