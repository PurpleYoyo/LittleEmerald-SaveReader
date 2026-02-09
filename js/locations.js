const canvas = document.getElementById("map-canvas");
const ctx = canvas.getContext("2d");
const img = document.getElementById("map");
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
});

document.getElementById('search-bar').addEventListener('input', function () {
    const value = this.value.toLowerCase();
    const match = locationData.find(loc => loc.name.toLowerCase() === value);
    if (match) {
        renderTable({ [match.name]: match });
        //img.src = match.map;
        //for (let i = 0; i < match.trainers.length; i++) {
        //    ctx.rect(match.trainers[i].coordinates.x, match.trainers[i].coordinates.y, 20, 20);
        //}
    }
    else {
        clearTable();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const value = 'Route 103'.toLowerCase();
    const match = locationData.find(loc => loc.name.toLowerCase() === value);
    renderTable({ [match.name]: match });
});

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
        const areaTitle = document.createElement('h2');
        areaTitle.textContent = formatName(area) + " Encounters";
        areaTitle.className = "title";
        container.appendChild(areaTitle);
  
        const methodKeys = ['walking', 'surfing', 'fishing', 'rock_smash'];
        const availableMethods = methodKeys.filter(m => methods[m] && methods[m].length > 0);

        const methodContainer = document.createElement('div');
        methodContainer.className = "method-container";

        for (const method of availableMethods) {
            const mons = methods[method];
            const table = document.createElement('table');
            table.className = "encounter-method";

            const caption = document.createElement('caption');
            caption.textContent = formatName(method.replace("_", " "));
            table.appendChild(caption);

            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            ['Min Lvl', 'Max Lvl', 'Species', 'Chance'].forEach(label => {
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
                        td.colSpan = 4;
                        td.textContent = label;
                        td.className = "fishing-label";
                        labelRow.appendChild(td);
                        tbody.appendChild(labelRow);
                    }
                }

                const mon = mons[i];
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${mon.min_level}</td>
                    <td>${mon.max_level}</td>
                    <td>${formatName(mon.species.replace("SPECIES_", "").toLowerCase())}</td>
                    <td>${mapChance(i, method)}</td>
                `;
                tbody.appendChild(row);
            }
            table.appendChild(tbody);
            methodContainer.appendChild(table);
        }
        container.appendChild(methodContainer);
    }
}  
  