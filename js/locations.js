// Load Data

let trainerData = {};
fetch('trainer_data.json')
.then(res => res.json())
.then(data => {
    trainerData = data;
});

let locationData = [];
fetch('location_data.json')
.then(res => res.json())
.then(data => {
    locationData = Object.entries(data).map(([name, info]) => ({
        name,
        ...info
    }));
        
    const datalist = document.getElementById('location-suggestions');
    locationData.forEach(loc => {
        const option = document.createElement('option');
        option.value = loc.name;
        datalist.appendChild(option);
    });

    const searchBar = document.getElementById('search-bar');
    searchBar.value = 'Route 102';

    var event = new Event('input', { bubbles: true });
    searchBar.dispatchEvent(event);
});

// Trainer Data

const tooltip = document.getElementById('tooltip');
const canvas = document.getElementById('map');
let mapImg = null;
let ctx = canvas.getContext('2d');

let trainers = null;
let trainerRects = [];
let highlighted = null;
let currentMatch = null;

const tile_width = 16;
const scale = 0.9;

canvas.addEventListener('mousemove', e => {
    const mouse = getMousePos(e, canvas);
    let hovered = null;

    for (const rect of trainerRects) {
        if (
            mouse.x >= rect.x &&
            mouse.x <= rect.x + rect.w &&
            mouse.y >= rect.y &&
            mouse.y <= rect.y + rect.h
        ) {
            hovered = rect;
            break;
        }
    }

    canvas.style.cursor = hovered ? 'pointer' : 'default';
    
    if (hovered) {
        showTooltip(hovered.full_name, e.clientX, e.clientY);
    }
    else {
        hideTooltip();
    }

    const newHiglight = hovered ? hovered.full_name : null;

    if (newHiglight !== highlighted) {
        highlighted = newHiglight;

        drawMap();
    }
});

function getMousePos(evt, canvas) {
    const rect = canvas.getBoundingClientRect();
    return {
        x: ((evt.clientX - rect.left) * (canvas.width / rect.width)) / scale,
        y: ((evt.clientY - rect.top) * (canvas.height / rect.height)) / scale
    };
}

function showTooltip(text, x, y) {
    tooltip.textContent = text;
    tooltip.style.left = x + 10 + 'px';
    tooltip.style.top = y + 10 + 'px';
    tooltip.style.display = 'block';
}

function hideTooltip() {
    tooltip.style.display = 'none';
}

document.getElementById('search-bar').addEventListener('input', function () {
    const value = this.value.toLowerCase();
    const match = locationData.find(loc => loc.name.toLowerCase() === value);
    if (match) {
        currentMatch = match;
        loadMapImage();

        renderTable({ [match.name]: match });
    }
    else {
        clearTable();
    }
});

function loadMapImage() {
    mapImg = new Image();
    mapImg.onload = drawMap;
    mapImg.src = `locations/${currentMatch.name.toLowerCase().replace(' ', '_')}.png`;
}

function drawMap() {
    if (!currentMatch) return;
    
    if (!canvas) return;

    canvas.width = mapImg.width * scale;
    canvas.height = mapImg.height * scale;

    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(mapImg, 0, 0);

    const mapData = trainerData[currentMatch.name];
    const {x: horizontal_offset, y: vertical_offset} = mapData.offsets;
    trainers = mapData.trainers;

    if (!trainers) return;

    trainerRects = [];    
    Object.values(trainers).forEach(trainer => {
        const [x,y] = trainer.coordinates;
        
        trainerRects.push({
            full_name: trainer.full_name,
            x: x * tile_width + horizontal_offset,
            y: (y * tile_width + vertical_offset) - tile_width,
            w: tile_width,
            h: tile_width * 2
        });
    });

    trainerRects.forEach(rect => {
        ctx.strokeStyle = (highlighted === rect.full_name) ? 'red' : 'black';
        ctx.strokeRect(rect.x, rect.y, rect.w, rect.h);
    });
}

// Encounter Data

function clearTable() {
    const container = document.getElementById('encounter-table');
    container.innerHTML = '';
}

function formatName(name) {
    if (name.includes("route")) {
        return "Route " + name.slice(5);
    }
    name = name.replace(/\b([br]?\d+f?)\b/gi, match => match.toUpperCase());
    return name
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function mapChance(index, method) {
    let indexToChanceWalking = {
        0: "20%",
        1: "20%",
        2: "10%",
        3: "10%",
        4: "10%",
        5: "10%",
        6: "5%",
        7: "5%",
        8: "4%",
        9: "4%",
        10: "1%",
        11: "1%",
    };
    let indexToChanceSurfingAndRockSmash = {
        0: "60%",
        1: "30%",
        2: "5%",
        3: "4%",
        4: "1%",
    };
    let indexToChanceFishing = {
        0: "70%",
        1: "30%",
        2: "60%",
        3: "20%",
        4: "20%",
        5: "40%",
        6: "40%",
        7: "15%",
        8: "4%",
        9: "1%",
    };

    switch (method) {
        case "walking":
            return indexToChanceWalking[index];
        case "surfing":
        case "rock_smash":
            return indexToChanceSurfingAndRockSmash[index];
        case "fishing":
            return indexToChanceFishing[index];
        default:
            return "?%"
    }
}
  
function getFishingLabel(index) {
    const labels = {
        0: "Old Rod",
        2: "Good Rod",
        5: "Super Rod"
    };
    return labels[index] || null;
}

function renderTable(data) {
    const container = document.getElementById('encounter-table');
    container.innerHTML = '';

     for (const [area, methods] of Object.entries(data)) {  
        const methodKeys = ['walking', 'surfing', 'fishing', 'rock_smash'];
        const availableMethods = methodKeys.filter(m => methods[m] && methods[m].length > 0);

        for (const method of availableMethods) {
            const methodContainer = document.createElement('details');
            methodContainer.className = 'method-container';

            const mons = methods[method];
            const table = document.createElement('table');
            table.className = "encounter-method";

            const caption = document.createElement('summary');
            caption.textContent = formatName(method.replace("_", " "));
            caption.className = 'caption';

            const line_break = document.createElement('br');

            methodContainer.appendChild(caption);
            methodContainer.appendChild(line_break);

            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            ['Min Lvl', 'Max Lvl', 'Sprite', 'Species', 'Chance'].forEach(label => {
                const th = document.createElement('th');
                th.textContent = label;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);

            const tbody = document.createElement('tbody');

            for (let i = 0; i < mons.length; i++) {
                if (method === 'fishing') {
                    const label = getFishingLabel(i);
                    if (label) {
                        const labelRow = document.createElement('tr');
                        const td = document.createElement('td');
                        td.colSpan = 5;
                        td.textContent = label;
                        td.className = "fishing-label";
                        labelRow.appendChild(td);
                        tbody.appendChild(labelRow);
                    }
                }

                const mon = mons[i];

                const base_forms = {
                    'burmy-sandy' : 'burmy',
                    'burmy-trash' : 'burmy',
                    'deerling-autumn' : 'deerling',
                    'deerling-summer' : 'deerling',
                    'deerling-winter' : 'deerling',
                    'petilil-fighting' : 'petilil',
                    'eevee-fire' : 'eevee',
                    'eevee-water' : 'eevee',
                    'eevee-electric' : 'eevee',
                    'eevee-dark' : 'eevee',
                    'eevee-psychic' : 'eevee',
                    'eevee-grass' : 'eevee',
                    'eevee-ice' : 'eevee',
                    'eevee-fairy' : 'eevee',
                    'charcadet-psychic' : 'charcadet',
                    'charcadet-ghost' : 'charcadet',
                    'ralts-fighting' : 'ralts',
                    'snorunt-ghost' : 'snorunt',
                    'wurmple-poison' : 'wurmple',
                    'nincada-ghost' : 'nincada',
                    'exeggcute-dragon' : 'exeggcute',
                    'koffing-fairy' : 'koffing',
                    'rufflet-psychic' : 'rufflet',
                    'goomy-steel' : 'goomy',
                    'bergmite-rock' : 'bergmite',
                    'froakie-special' : 'froakie',
                    'rockruff-special' : 'rockruff',
                    'feebas-fairy' : 'feebas',
                }
            
                let current_mon = formatName(mon.species.replace('SPECIES_', '')).toLowerCase();
                let species = formatName(mon.species.replace('SPECIES_', ''));
                if (base_forms[species]) {
                    current_mon = base_forms[species];
                }

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${mon.min_level}</td>
                    <td>${mon.max_level}</td>
                    <td><img src="https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${current_mon.toLowerCase().replace('_', '-')}.png"></td>
                    <td>${formatName(current_mon.replace('_', '-'))}</td>
                    <td>${mapChance(i, method)}</td>
                `;
                tbody.appendChild(row);
            }

            table.appendChild(tbody);
            methodContainer.appendChild(table);
            container.appendChild(methodContainer);
        }
    }
}  
