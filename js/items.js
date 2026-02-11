let itemData = {};
fetch('item_data.json')
.then(res => res.json())
.then(data => {
    itemData = data;
});

const itemTooltip = document.getElementById('tooltip');
const itemCanvas = document.getElementById('item-map');
let itemMapImg = null;
let itemCtx = itemCanvas.getContext('2d');

let items = null;
let itemRects = [];

itemCanvas.addEventListener('mousemove', e => {
    const mouse = getMousePos(e, itemCanvas);
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

    itemCanvas.style.cursor = hovered ? 'pointer' : 'default';
    
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

function getMousePos(evt, itemCanvas) {
    const rect = itemCanvas.getBoundingClientRect();
    return {
        x: ((evt.clientX - rect.left) * (itemCanvas.width / rect.width)) / scale,
        y: ((evt.clientY - rect.top) * (itemCanvas.height / rect.height)) / scale
    };
}

function showTooltip(text, x, y) {
    itemTooltip.textContent = text;
    itemTooltip.style.left = x + 10 + 'px';
    itemTooltip.style.top = y + 10 + 'px';
    itemTooltip.style.display = 'block';
}

function hideTooltip() {
    itemTooltip.style.display = 'none';
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
    itemMapImg = new Image();
    itemMapImg.onload = drawMap;
    itemMapImg.src = `locations/${currentMatch.name.toLowerCase().replace(' ', '_')}.png`;
}

function drawMap() {
    if (!currentMatch) return;
    
    if (!itemCanvas) return;

    itemCanvas.width = itemMapImg.width * scale;
    itemCanvas.height = itemMapImg.height * scale;

    itemCtx.setTransform(scale, 0, 0, scale, 0, 0);
    itemCtx.clearRect(0, 0, itemCanvas.width, itemCanvas.height);
    itemCtx.drawImage(itemMapImg, 0, 0);

    const mapData = itemData[currentMatch.name];
    if (!mapData) return;

    const {x: horizontal_offset, y: vertical_offset} = mapData.offsets;
    items = mapData.items;

    if (!items) return;

    itemRects = [];    
    items.forEach(item => {
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
        itemCtx.strokeStyle = (hoverHighlighted === rect.name) ? 'red' : 'black';
        itemCtx.strokeRect(rect.x, rect.y, rect.w, rect.h);
    });
}
