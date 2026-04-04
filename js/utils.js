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
    return (original || ['None']).map(val => {
        let name;
        if (subareaMapping[original]) {
            name = data[subareaMapping[val]];
        }
        else {
            name = data[val]?.name ?? 'None';
            console.log(val);
            console.log(data);
        }
        return name == 'None' ? 'None' : format(link, name)
    });
}