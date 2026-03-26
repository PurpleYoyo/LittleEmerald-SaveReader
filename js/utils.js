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
    original.map(val => {
        val = data[val].name || 'None';
        return val == 'None' ? 'None' : format(link, val)
    });
}