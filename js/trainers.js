let locationData = [];
fetch('location_data.json')
.then(res => res.json())
.then(data => {
    locationData = Object.entries(data).map(([name, info]) => ({
        name,
        ...info
    }));
});

let trainerData = {};
fetch('trainer_data.json')
.then(res => res.json())
.then(data => {
    trainerData = data;
});

const tooltip = document.getElementById('trainer-tooltip');
const canvas = document.getElementById('trainer-map');
let mapImg = null;
let ctx = canvas.getContext('2d');

let trainers = null;
let trainerRects = [];
let hoverHighlighted = null;
let clickHighlighted = null;
let currentMatch = 'Route 102';

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
        showTooltip(hovered.full_name, e);
    }
    else {
        hideTooltip();

        if (!clickHighlighted) {
            const container = document.getElementById('set-data');
            container.innerHTML = '';
        }
    }

    const newHiglight = hovered ? hovered.full_name : null;

    if (newHiglight !== hoverHighlighted) {
        hoverHighlighted = newHiglight;

        drawMap();
    }
});

canvas.addEventListener('click', e => {
    const mouse = getMousePos(e, canvas);
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
        renderTrainer(clicked);
    }

    const newHiglight = clicked ? clicked.full_name : null;

    if (newHiglight !== clickHighlighted) {
        clickHighlighted = newHiglight;

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

function showTooltip(text, event) {
    tooltip.textContent = text;
    tooltip.style.left = (event.pageX + 10) + 'px';
    tooltip.style.top = (event.pageY + 10) + 'px';
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
    if (!mapData) return;

    trainers = mapData.trainers;

    if (!trainers) return;

    trainerRects = [];    
    Object.values(trainers).forEach(trainer => {
        const [x,y] = trainer.coordinates;
        
        trainerRects.push({
            full_name: trainer.full_name,
            sets: trainer.sets,
            x: x * tile_width,
            y: y * tile_width - tile_width,
            w: tile_width,
            h: tile_width * 2
        });
    });

    trainerRects.forEach(rect => {
        ctx.strokeStyle = (hoverHighlighted === rect.full_name || clickHighlighted === rect.full_name) ? 'red' : 'black';
        ctx.strokeRect(rect.x, rect.y, rect.w, rect.h);
    });
}

function map_stat_name(stat) {
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

function renderTrainer(data) {
    const container = document.getElementById('set-data');
    container.innerHTML = '';

    const setContainer = document.createElement('details');
    setContainer.className = 'trainer-sets';
    setContainer.open = true;

    const caption = document.createElement('summary');
    caption.textContent = data.full_name;
    caption.className = 'caption';

    setContainer.appendChild(caption);

    const table = document.createElement('table');
    table.className = 'sets-table';

    const tbody = document.createElement('tbody');

    ['pok', 'level', 'item', 'nature', 'ivs', 'moves'].forEach(field => {
        const row = document.createElement('tr');

        const headerCell = document.createElement('td');
        headerCell.textContent = field === 'pok' ? 'Pokémon' : field === 'item' ? 'Held Item' : field === 'ivs' ? 'IVs' : field.charAt(0).toUpperCase() + field.slice(1);
        headerCell.style.fontWeight = 'bold';
        row.appendChild(headerCell);

        for (const [pok, set] of Object.entries(data.sets)) {
            const cell = document.createElement('td');

            if (field === 'pok') {
                cell.textContent = pok;
            }
            else if (field === 'ivs') {
                let ivs = [];
                Object.entries(set.ivs).forEach(([stat, value]) => {
                    ivs.push(`${value} ${map_stat_name(stat)}`);
                });
                cell.textContent = ivs.join(' / ');
            }
            else if (field === 'moves') {
                let moves = [];
                set.moves.forEach(move => {
                    if (move !== '(no Move)') {
                        moves.push(move);
                    }
                });
                cell.textContent = moves.join(' / ');
            }
            else {
                cell.textContent = set[field];
            }

            row.appendChild(cell);
        }

        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    setContainer.appendChild(table);
    container.appendChild(setContainer);
}  
