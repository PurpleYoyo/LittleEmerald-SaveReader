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

    const moves_row = document.createElement('tr');

    const levelup = mon.level_up_moves?.length ? mon.level_up_moves.map(l => `Lv ${l.level}: ${l.move}`).join('<br>') : "Unknown";
    const tm = mon.tm_moves?.length ? mon.tm_moves.join('<br>') : "None";
    const egg = mon.egg_moves?.length ? mon.egg_moves.join('<br>') : "None";
    const tutor = mon.tutor_moves?.length ? mon.tutor_moves.join('<br>') : "None";
    
    moves_row.innerHTML = `
    <td>${levelup}</td>
    <td>${tm}</td>
    <td>${egg}</td>
    <td>${tutor}</td>
    `;

    learnset.appendChild(moves_row);
  }
}
