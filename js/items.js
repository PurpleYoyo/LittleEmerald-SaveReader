let itemData = {};
fetch('item_data.json')
.then(res => res.json())
.then(data => {
    itemData = data;
});

const tooltip = document.getElementById('tooltip');
const canvas = document.getElementById('item-map');
let mapImg = null;
let ctx = canvas.getContext('2d');

let items = null;
let itemRects = [];
let hoverHighlighted = null;
let clickHighlighted = null;
let currentMatch = null;

const tile_width = 16;
const scale = 0.9;

canvas.addEventListener('mousemove', e => {
    const mouse = getMousePos(e, canvas);
    let hovered = null;

    for (const rect of itemRects) {
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
        showTooltip(hovered.name, e.clientX, e.clientY);
    }
    else {
        hideTooltip();
    }

    const newHiglight = hovered ? hovered.name : null;

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

    const mapData = itemData[currentMatch.name];
    if (!mapData) return;

    const {x: horizontal_offset, y: vertical_offset} = mapData.offsets;
    items = mapData.items;

    if (!items) return;

    itemRects = [];    
    Object.values(items).forEach(item => {
        const [x,y] = item.coordinates;
        
        itemRects.push({
            name: item.name,
            x: x * tile_width + horizontal_offset,
            y: y * tile_width + vertical_offset,
            w: tile_width,
            h: tile_width
        });
    });

    itemRects.forEach(rect => {
        ctx.strokeStyle = (hoverHighlighted === rect.name) ? 'red' : 'black';
        ctx.strokeRect(rect.x, rect.y, rect.w, rect.h);
    });
}
