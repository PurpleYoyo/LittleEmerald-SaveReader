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
  const tbody = document.querySelector('#pokedex-table tbody');
  tbody.innerHTML = '';
  for (const mon of data) {
    const row = document.createElement('tr');

    const baseStats = Object.entries(mon.base_stats).map(([key, val]) => `${key}: ${val}`).join('<br>');
    //const learnset = mon.learnset.map(l => `Lv ${l.level}: ${l.move}`).join('<br>');

    row.innerHTML = `
      <td>${mon.name}</td>
      <td>${mon.types.join('/')}</td>
      <td>${mon.abilities.join('/')}</td>
      <td>${baseStats}</td>
    `;

    //<td>${learnset}</td>
      

    tbody.appendChild(row);
  }
}
