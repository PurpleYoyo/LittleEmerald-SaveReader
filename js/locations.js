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
    document.querySelector('#encounter-table tbody').innerHTML = '';
    document.querySelector('#encounter-table th').innerHTML = '';
}

function formatName(name) {
    return name
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
  }

  
function renderTable(data) {
    const container = document.getElementById('encounter-table');
    container.innerHTML = '';

    for (const [area, methods] of Object.entries(data)) {
        const areaTitle = document.createElement('h2');
        areaTitle.textContent = area;
        container.appendChild(areaTitle);
  
        const availableMethods = Object.keys(methods).filter(m => methods[m].length > 0);
        const table = document.createElement('table');
  
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        for (const method of availableMethods) {
            const th1 = document.createElement('th');
            th1.colSpan = 3;
            th1.textContent = method.charAt(0).toUpperCase() + method.slice(1);
            headerRow.appendChild(th1);
        }
        thead.appendChild(headerRow);
  
        const subHeaderRow = document.createElement('tr');
        for (const _ of availableMethods) {
            ['Min', 'Max', 'Species'].forEach(label => {
                const th = document.createElement('th');
                th.textContent = label;
                subHeaderRow.appendChild(th);
            });
        }
        thead.appendChild(subHeaderRow);
        table.appendChild(thead);
  
        const maxRows = Math.max(...availableMethods.map(m => methods[m].length));
  
        const tbody = document.createElement('tbody');
        for (let i = 0; i < maxRows; i++) {
            const row = document.createElement('tr');
            for (const method of availableMethods) {
                const mon = methods[method][i];
                if (mon) {
                    row.innerHTML += `
                        <td>${mon.min_level}</td>
                        <td>${mon.max_level}</td>
                        <td>${mon.species.replace("SPECIES_", "").toLowerCase()}</td>
                        `;
                } else {
                    row.innerHTML += `<td></td><td></td><td></td>`;
                }
            }
            tbody.appendChild(row);
        }
  
        table.appendChild(tbody);
        container.appendChild(table);
    }
}  
  