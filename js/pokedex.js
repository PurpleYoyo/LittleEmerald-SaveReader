let pokemonData = [];

fetch('pokemon_data.json')
.then(res => res.json())
.then(data => {
    pokemonData = Object.entries(data).map(([name, info]) => ({
        name,
        ...info
    }));
        
    const datalist = document.getElementById('pokemon-suggestions');
    pokemonData.forEach(mon => {
        const option = document.createElement('option');
        option.value = mon.name;
        datalist.appendChild(option);
    });
});

document.getElementById('search-bar').addEventListener('input', function () {
  const value = this.value.toLowerCase();
  const match = pokemonData.find(mon => mon.name.toLowerCase() === value);
  if (match) {
    renderTable([match]);
  }
  else {
    clearTable();
  }
});

function clearTable() {
    document.querySelector('#pokedex-table tbody').innerHTML = '';
    document.querySelector('#learnset-table tbody').innerHTML = '';
}

function renderTable(data) {
  const learnset = document.querySelector('#learnset-table tbody');
  const tbody = document.querySelector('#pokedex-table tbody');
  tbody.innerHTML = '';
  learnset.innerHTML = '';

  for (const mon of data) {
    const row = document.createElement('tr');

    const baseStats = mon.base_stats ? Object.entries(mon.base_stats).map(([key, val]) => `${key}: ${val}`).join("<br>") : "Unknown";
    const types = mon.types.join("/") || "Unknown";
    const abilities = mon.abilities.join("/") || "Unknown";

    row.innerHTML = `
      <td>${mon.name}</td>
      <td>${types}</td>
      <td>${abilities}</td>
      <td>${baseStats}</td>
    `;
    tbody.appendChild(row);

    const levelup = mon.level_up_moves?.length ? mon.level_up_moves.map(l => `Lv ${l.level}: ${l.move}`).join('<br>') : "Unknown";
    const tm = mon.tm_moves?.length ? mon.tm_moves.join('<br>') : "None";
    const egg = mon.egg_moves?.length ? mon.egg_moves.join('<br>') : "None";
    const tutor = mon.tutor_moves?.length ? mon.tutor_moves.join('<br>') : "None";
    
    const maxRows = Math.max(levelup.length, tm.length, egg.length, tutor.length);
    for (let i = 0; i < maxRows; i++) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${levelup[i] || ""}</td>
            <td>${tm[i] || ""}</td>
            <td>${egg[i] || ""}</td>
            <td>${tutor[i] || ""}</td>
        `;
        learnset.appendChild(row);
    }
  }
}
