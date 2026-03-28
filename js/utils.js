import { subareaMapping } from "./data";

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
    return (original || ['None']).map(val => {
        let name;
        if (subareaMapping[original]) {
            name = data[subareaMapping[val]];
        }
        else {
            name = data[val]?.name ?? 'None';
        }
        return name == 'None' ? 'None' : format(link, name)
    });
}