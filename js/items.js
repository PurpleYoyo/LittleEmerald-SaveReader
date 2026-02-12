let itemData = {};
fetch('item_data.json')
.then(res => res.json())
.then(data => {
    itemData = data;
});

const tooltip = document.getElementById('item-tooltip');
const canvas = document.getElementById('item-map');
let mapImg = null;
let ctx = canvas.getContext('2d');

let items = null;
let itemRects = [];
let hoverHighlighted = null;
let currentMatch = null;

const tile_width = 16;
const scale = 0.9;

export function setCurrentMatch(match) {
    currentMatch = match;
}

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
        showTooltip(hovered.name, e);
    }
    else {
        hideTooltip();
    }

    const newHiglight = hovered ? hovered.id : null;

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

function showTooltip(text, event) {
    tooltip.textContent = text;
    tooltip.style.left = (event.pageX + 10) + 'px';
    tooltip.style.top = (event.pageY + 10) + 'px';
    tooltip.style.display = 'block';
}

function hideTooltip() {
    tooltip.style.display = 'none';
}

export function loadMapImage() {
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

    items = mapData.items;

    if (!items) return;

    itemRects = [];    
    items.forEach(item => {
        const [x,y] = item.coordinates;
        
        itemRects.push({
            id: `${x}${y}`,
            name: item.item,
            x: x * tile_width,
            y: y * tile_width,
            w: tile_width,
            h: tile_width
        });
    });

    itemRects.forEach(rect => {
        ctx.strokeStyle = (hoverHighlighted === rect.id) ? 'red' : 'black';
        ctx.strokeRect(rect.x, rect.y, rect.w, rect.h);
    });
}
