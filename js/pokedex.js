let pokemonData = [];

fetch('pokemon_data.json')
  .then(res => res.json())
  .then(data => {
    pokemonData = data;
    renderTable(pokemonData);
  });

document.getElementById('search').addEventListener('input', function () {
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
      <td>${mon}</td>
      <td>${baseStats}</td>
    `;
    // <td>${mon.types.join(', ')}</td>
    //  <td>${mon.abilities.join(', ')}</td>
    //<td>${learnset}</td>
      

    tbody.appendChild(row);
  }
}
