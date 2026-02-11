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

const tooltip = document.getElementById('tooltip');
const canvas = document.getElementById('trainer-map');
let mapImg = null;
let ctx = canvas.getContext('2d');

let trainers = null;
let trainerRects = [];
let hoverHighlighted = null;
let clickHighlighted = null;
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

        renderTrainer(hovered);
    }
    else {
        hideTooltip();
    }

    const newHiglight = hovered ? hovered.full_name : null;

    if (newHiglight !== hoverHighlighted) {
        hoverHighlighted = newHiglight;

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

    const {x: horizontal_offset, y: vertical_offset} = mapData.offsets;
    trainers = mapData.trainers;

    if (!trainers) return;

    trainerRects = [];    
    Object.values(trainers).forEach(trainer => {
        const [x,y] = trainer.coordinates;
        
        trainerRects.push({
            full_name: trainer.full_name,
            sets: trainer.sets,
            x: x * tile_width + horizontal_offset,
            y: (y * tile_width + vertical_offset) - tile_width,
            w: tile_width,
            h: tile_width * 2
        });
    });

    trainerRects.forEach(rect => {
        ctx.strokeStyle = (hoverHighlighted === rect.full_name) ? 'red' : 'black';
        ctx.strokeRect(rect.x, rect.y, rect.w, rect.h);
    });
}

function renderTrainer(data) {
    const container = document.getElementById('trainer-data');
    container.innerHTML = '';

    const setContainer = document.createElement('details');
    setContainer.className = 'trainer-sets';

    const caption = document.createElement('summary');
    caption.textContent = formatName(data.full_name);
    caption.className = 'caption';

    setContainer.appendChild(caption);

    const table = document.createElement('table');
    table.className = 'sets-table';

    const tbody = document.createElement('tbody');

    ['pok', 'level', 'item', 'nature', 'ivs', 'moves'].forEach(field => {
        const row = document.createElement('tr');

        for (const [pok, set] of Object.entries(data.sets)) {
            const cell = document.createElement('td');

            if (field === 'pok') {
                cell.textContent = pok;
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
