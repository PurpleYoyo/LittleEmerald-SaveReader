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
    }
    else {
        clearTable();
    }
});

function clearTable() {
    const container = document.getElementById('encounter-table');
    container.innerHTML = '';
}

function formatName(name) {
    if (name.includes("route")) {
        return name.slice(0, 5) + " " + name.slice(5);
    }
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
  
function renderTable(data) {
    const container = document.getElementById('encounter-table');
    container.innerHTML = '';

    for (const [area, methods] of Object.entries(data)) {
        const areaTitle = document.createElement('h2');
        areaTitle.textContent = formatName(area) + "Encounters";
        container.appendChild(areaTitle);
  
        const availableMethods = Object.keys(methods).filter(m => methods[m].length > 0);
        const table = document.createElement('table');
  
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        for (const method of availableMethods) {
            const th1 = document.createElement('th');
            th1.colSpan = 4;
            th1.textContent = formatName(method.replace("_", " "));
            headerRow.appendChild(th1);
        }
        thead.appendChild(headerRow);
  
        const subHeaderRow = document.createElement('tr');
        for (const _ of availableMethods) {
            ['Min Lvl', 'Max Lvl', 'Species', 'Chance'].forEach(label => {
                const th = document.createElement('th');
                th.textContent = label;
                subHeaderRow.appendChild(th);
            });
        }
        thead.appendChild(subHeaderRow);
        table.appendChild(thead);
  
        const maxRows = Math.max(...availableMethods.map(m => methods[m].length));
  
        const tbody = document.createElement('tbody');

        const rodLabels = {
            2: "Old Rod",
            5: "Good Rod",
            10: "Super Rod"
        };

        for (let i = 0; i < maxRows; i++) {
            const row = document.createElement('tr');
            for (const method of availableMethods) {
                const mon = methods[method][i];
                if (mon && mon.species) {
                    row.innerHTML += `
                        <td>${mon.min_level}</td>
                        <td>${mon.max_level}</td>
                        <td>${formatName(mon.species.replace("SPECIES_", "").toLowerCase())}</td>
                        <td>${mapChance(i, method)}</td>
                        `;
                } else {
                    row.innerHTML += `<td></td><td></td><td></td>`;
                }
            }
            tbody.appendChild(row);

            if (availableMethods.includes('fishing') && rodLabels[i]) {
                const labelRow = document.createElement('tr');
                for (const method of availableMethods) {
                    if (method === 'fishing') {
                        const labelCell = document.createElement('td');
                        labelCell.colSpan = 4;
                        labelCell.textContent = rodLabels[i];
                        labelCell.style.textAlign = 'center';
                        labelRow.appendChild(labelCell);
                    } else {
                        // Empty cells for other columns
                        for (let j = 0; j < 4; j++) {
                            labelRow.appendChild(document.createElement('td'));
                        }
                    }
                }
            }
            tbody.appendChild(labelRow);
        }
        table.appendChild(tbody);
        container.appendChild(table);
    }
}  
  