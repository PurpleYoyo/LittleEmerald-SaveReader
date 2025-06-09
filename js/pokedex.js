let pokemonData = [];

fetch('pokemon_data.json')
  .then(res => res.json())
  .then(data => {
    const pokemonArray = Object.entries(data).map(([name, info]) => ({
      name,
      ...info
    }));
    renderTable(pokemonArray);
  });

document.getElementById('search-bar').addEventListener('input', function () {
  const value = this.value.toLowerCase();
  const filtered = pokemonData.filter(mon => mon.name.toLowerCase().includes(value));
  renderTable(filtered);
});

function renderTable(data) {
  const learnset = document.querySelector('#learnset-table tbody');
  const tbody = document.querySelector('#pokedex-table tbody');
  tbody.innerHTML = '';
  for (const mon of data) {
    const row = document.createElement('tr');

    let types;
    let abilities;
    let baseStats;
    try {
        baseStats = Object.entries(mon.base_stats).map(([key, val]) => `${key}: ${val}`).join('<br>');
    }
    catch {
        baseStats = "Unknown";
    }
    try {
        types = mon.types.join("/");
    }
    catch {
        types = "Unknown";
    }
    try {
        abilities = mon.abilities.join("/");    
    }
    catch {
        abilities = "Unknown";
    }

    row.innerHTML = `
      <td>${mon.name}</td>
      <td>${types}</td>
      <td>${abilities}</td>
      <td>${baseStats}</td>
    `;

    tbody.appendChild(row);

    const moves_row = document.createElement('tr');
    let levelup;
    let tm;
    let egg;
    let tutor;
    try {
        levelup = mon.level_up_moves.map(l => `Lv ${l.level}: ${l.move}`).join('<br>');
    }
    catch {
        levelup = "Unknown";
    }
    try {
        tm = mon.tm_moves.join('<br>');
    }
    catch {
        tm = "None";
    }
    try {
        egg = mon.egg_moves.join('<br>');
    }
    catch {
        egg = "None";
    }
    try {
        tutor = mon.tutor_moves.join('<br>');
    }
    catch {
        tutor = "None";
    }
    moves_row.innerHTML = `
    <td>${levelup}</td>
    <td>${tm}</td>
    <td>${egg}</td>
    <td>${tutor}</td>
    `;

    learnset.appendChild(moves_row);
  }
}
