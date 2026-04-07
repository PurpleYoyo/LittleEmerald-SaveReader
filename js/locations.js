import { locationData, pokemonData } from './data.js'

const tile_width = 16;
const scale = 0.9;

let trainers = null;
let trainerRects = [];
let hoveredTrainer = null;
let clickedTrainer = null;
let trainerImg = null;

let items = null;
let itemRects = [];
let hoveredItem = null;
let clickedItem = null;
let itemImg = null;

let currentLocation = null;

export function renderMap(filtered) {
    const canvas = document.getElementById('locations-map');
    const ctx = canvas.getContext('2d');

    if (!canvas) return;

    const img = new Image();
    img.src = 'locations/FullMap.png';

    canvas.width = img.width * scale;
    canvas.height = img.height * scale;

    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);

    //if (filtered) {}

    //locationData.forEach
}

document.getElementById('testing').onclick = () => {
    const value = 'route 102';
    const match = locationData.find(loc => loc.name.toLowerCase() === value);
    if (match) {
        renderModal(match);
    }
};

function renderModal(loc) {
    const modal = document.getElementById('location-modal');
    
    const encounter_body = document.getElementById('encounter-info');
    encounter_body.innerHTML = '';

    const trainer_map = document.getElementById('trainer-map');
    const item_map = document.getElementById('item-map');

    currentLocation = loc;

    buildEncounterTables(encounter_body, loc);

    trainerImg = new Image();
    trainerImg.onload = function() {
        drawTrainerMap(trainerImg, trainer_map, loc);
    };
    trainerImg.src = loc.image;

    itemImg = new Image();
    itemImg.onload = function() {
        drawItemMap(itemImg, item_map, loc);
    }
    itemImg.src = loc.image;

    modal.classList.remove('hidden');
    document.body.classList.add('modal-open');
}

function buildEncounterTables(body, loc) {
    let encounterTables = [];

    ['walking', 'surfing', 'fishing', 'rock_smash'].forEach(method => {
        encounterTables.push(buildEncounterTable(method, loc));
    });

    body.innerHTML = encounterTables.join('\n');
}

function buildEncounterTable(method, loc) {
    const table = document.createElement('table');
    
    const encounters = loc.encounters[method] || null;
    
    if (!encounters) return;

    let rows = [];

    for (let i = 0; i < encounters.length; i++) {
        const encounter = pokemonData[encounters[i].species] || 'UNKNOWN';
        let row;
        let label = null;

        if (method == 'fishing') {
            label = getFishingLabel(i);
            if (label) {
                row = `
                    <tr>
                        <td class="fishing-label" colspan="5">${label}</td>
                    </tr>
                `;
            }
        }
        if (!label) {
            row = `
                <tr>
                    <td>${encounters[i].min_level}</td>
                    <td>${encounters[i].max_level}</td>
                    <td>
                        <a href="pokedex.html#value=${encounter.name}type=pokemon">${encounter.name}</a>
                        ${encounters[i].sprite}
                    </td>
                    <td>${getEncounterChance(i, method)}</td>
                </tr>
            `;
            rows.push(row);
        }
    }

    table.innerHTML= `
        <thead>
            <tr>
                <th>Min Lvl</th>
                <th>Max Lvl</th>
                <th>Species</th>
                <th>Chance</th>
            </tr>
        </thead>

        <tbody>
            ${rows.join('\n')}
        </tbody>
    `;

    return table;
}

function getEncounterChance(index, method) {
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

function drawTrainerMap(img, canvas, loc) {
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    trainers = loc.trainers;
    if (!trainers) return;

    canvas.width = img.width * scale;
    canvas.height = img.height * scale;

    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);

    trainerRects = [];
    Object.values(trainers).forEach(trainer => {
        const [x, y] = trainer.coordinates;

        trainerRects.push({
            id: `${x}-${y}`,
            name: trainer.full_name,
            sets: trainer.sets,
            x: x * tile_width,
            y: y * tile_width,
            w: tile_width,
            h: tile_width * 2
        });
    });

    trainerRects.forEach(rect => {
        ctx.strokeStyle = (hoveredTrainer === rect.id || clickedTrainer === rect.id) ? 'red' : 'black';
        ctx.strokeRect(rect.x, rect.y, rect.w, rect.h)
    });
}

function drawItemMap(img, canvas, loc) {
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    items = loc.items;
    if (!items) return;

    canvas.width = img.width * scale;
    canvas.height = img.height * scale;

    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);

    itemRects = [];
    Object.values(items).forEach(item => {
        const [x, y] = item.coordinates;

        itemRects.push({
            id: `${x}-${y}`,
            name: item.item,
            x: x * tile_width,
            y: y * tile_width,
            w: tile_width,
            h: tile_width
        });
    });

    itemRects.forEach(rect => {
        ctx.strokeStyle = (hoveredItem === rect.id || clickedItem === rect.id) ? 'red' : 'black';
        ctx.strokeRect(rect.x, rect.y, rect.w, rect.h)
    });
}

document.getElementById('trainer-map').addEventListener('mousemove', event => {
    const tooltip = document.getElementById('trainer-tooltip');
    hoverHighlight(event, 'trainer-map', trainerRects, tooltip);
});
document.getElementById('item-map').addEventListener('mousemove', event => {
    const tooltip = document.getElementById('item-tooltip');
    hoverHighlight(event, 'item-map', itemRects, tooltip);
});

function hoverHighlight(event, canvas_id, rects, tooltip) { 
    const canvas = document.getElementById(canvas_id);

    const mouse = getMousePos(event, canvas);
    let hovered = null;

    for (const rect of rects) {
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
        showTooltip(tooltip, hovered.name, event);
    }
    else {
        hideTooltip(tooltip);

        if (!clickedTrainer) {
            const container = document.getElementById('set-data');
            container.innerHTML = '';
        }
    }

    const newHiglight = hovered ? hovered.id : null;

    if (canvas_id === 'trainer-map') {
        if (newHiglight !== hoveredTrainer) {
            hoveredTrainer = newHiglight;

            drawTrainerMap(trainerImg, canvas, currentLocation);
        }
    }
    else if (canvas_id === 'item-map') {
        if (newHiglight !== hoveredItem) {
            hoveredItem = newHiglight;

            drawItemMap(itemImg, canvas, currentLocation);
        }
    }
}

document.getElementById('trainer-map').addEventListener('click', event => {
    clickHighlight(event);
});

function clickHighlight(event) {
    const canvas = document.getElementById('trainer-map');

    const mouse = getMousePos(event, canvas);
    let clicked = null;

    for (const rect of trainerRects) {
        if (
            mouse.x >= rect.x &&
            mouse.x <= rect.x + rect.w &&
            mouse.y >= rect.y &&
            mouse.y <= rect.y + rect.h
        ) {
            clicked = rect;
            break;
        }
    }
    
    if (clicked) {
        buildSetsTable(document.getElementById('sets-info'), clicked);
    }

    const newHiglight = clicked ? clicked.id : null;

    if (newHiglight !== clickedTrainer) {
        clickedTrainer = newHiglight;

        drawTrainerMap();
    }
}

function getMousePos(event, canvas) {
    const rect = canvas.getBoundingClientRect();

    return {
        x: ((event.clientX - rect.left) * (canvas.width / rect.width)) / scale,
        y: ((event.clientY - rect.top) * (canvas.height / rect.height)) / scale
    };
}

function showTooltip(tooltip, text, event) {
    tooltip.textContent = text;
    tooltip.style.left = (event.pageX + 10) + 'px';
    tooltip.style.top = (event.pageY + 10) + 'px';
    tooltip.style.display = 'block';
}

function hideTooltip(tooltip) {
    tooltip.style.display = 'none';
}

function getStatName(stat) {
    switch (stat) {
        default:
        case 'hp':
            return 'HP';
        case 'at':
            return 'Atk';
        case 'df':
            return 'Def';
        case 'sa':
            return 'SpA';
        case 'sd':
            return 'SpD';
        case 'sp':
            return 'Spe';
    }
}

function buildSetsTable(body, trainer) {
    let sets = [];

    for (const [pok, set] of Object.entries(trainer.sets)) {
        const pokemon = pokemonData[pok];

        const sprite = `<img src="https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${pokemon.sprite}.png" alt="${pokemon.name}">`;

        let ivs = [];
        Object.entries(set.ivs).forEach(([stat, value]) => {
            ivs.push(`${value} ${getStatName(stat)}`);
        });

        let moves = [];
        set.moves.forEach(move => {
            if (move !== '(No Move)') {
                moves.push(move);
            }
        })

        let row = `
            <tr>
                <td>${pokemon.name} ${sprite}</td>
                <td>${set.level}</td>
                <td>${set.nature}</td>
                <td>${set.ability}</td>
                <td>${set.item}</td>
                <td>${ivs.join(' / ')}</td>
                <td>- ${moves.join('\n- ')}</td>
            </tr>
        `;
        sets.push(row);
    }

    body.innerHTML = `
        <details open>
            <summary class="title">Trainer Sets</summary>
            <table>
                <thead>
                    <tr>
                        <th>Pokémon</th>
                        <th>Level</th>
                        <th>Nature</th>
                        <th>Ability</th>
                        <th>Held Item</th>
                        <th>IVs</th>
                        <th>Moves</th>
                    </tr>
                </thead>

                <tbody>
                    ${sets.join('\n')}
                </tbody>
            </table>
        </details>
    `;
}