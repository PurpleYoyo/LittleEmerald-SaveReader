import { locationData } from './data.js'
import { title } from './utils.js';

const tile_width = 16;
const scale = 0.9;

export function renderMap(filtered = null) {
    const canvas = document.getElementById('locations-map');
    const ctx = canvas.getContext('2d');
    const img = 'locations/FullMap.png';

    if (!canvas) return;

    canvas.width = img.width * scale;
    canvas.height = img.height * scale;

    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);

    //if (filtered) {}

    //locationData.forEach
}

function closeModal() {
    document.getElementById('location-modal').classList.add('hidden');
    document.body.classList.remove('modal-open'); 
}

document.getElementById('close-modal').onclick = () => {
    closeModal();
};

window.onclick = (e) => {
    const modal = document.getElementById('location-modal');
    if (e.target === modal) {
        closeModal();
    }
};

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

    // clear canvases

    buildEncounterTables(encounter_body, loc);

    drawTrainerMap(trainer_map, loc);
    drawItemMap(item_map, loc);

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
    
    const encounters = loc.encounters[type] || null
    
    if (!encounters) return;

    let rows = [];

    for (let i = 0; i < method.length; i++) {
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
                    <td>${method[i].min_level}</td>
                    <td>${method[i].max_level}</td>
                    <td><a href="pokedex.html#${method[i].species}">${method[i].species}</a></td>
                    <td>${method[i].sprite}</td>
                    <td>${getEncounterChance(i, method)}</td>
                </tr>
            `;
        }
    }

    table.innerHTML= `
        <thead>
            <tr>
                <th>Min Lvl</th>
                <th>Max Lvl</th>
                <th>Species</th>
                <th>Sprite</th>
                <th>Chance</th>
            </tr>
        </head>

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

function drawTrainerMap(canvas, loc) {}

function drawItemMap(canvas, loc) {}