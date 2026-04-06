import { subareaMapping } from './data.js';

function formatSubarea(name) {  
    return name
        .toLowerCase()
        .replace(/^map_/, '')
        .split('_')
        .map(word => {
            let formatted = word.charAt(0).toUpperCase() + word.slice(1);
            formatted = formatted.replace(/(\d+)f$/i, (_, num) => num + 'F');
            return formatted;
        })
        .join(' ');
}

function formatMega(name) {
    return name.includes('MEGA') ?
        title(name.split('_').slice(name.split('_').indexOf('MEGA')).join('-')).replace(' ', '-')
        : null;
}

export function title(name) {  
    return name
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

export function format(str, ...args) {
    return str.replace(/{(\d+)}/g,
        (match, index) => args[index] ?? match
    );
}

export function buildFormattedArray(original, link, data) {
    if (!original) return ['None'];
    console.log(original);
    console.log(!original);

    return (original).map(val => {
        const sub = subareaMapping[val] ?? val;
        const mega = formatMega(val);
        const name = data[sub]?.name ?? 'None';
        return mega ?
                format(link, name, `${name} ${mega}`)
            : sub === val ?
                format(link, name)
                : format(link, name, formatSubarea(val));
    });
}