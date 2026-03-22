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

    renderCards(pokemonData);
});

document.getElementById('search-bar').addEventListener('input', function () {
  const value = this.value.toLowerCase();

  const filtered = pokemonData.filter(mon =>
    mon.name.toLowerCase().includes(value)
  );
  
  renderCards(filtered);
});

function renderCards(data) {
    const container = document.getElementById('pokemon-container');
    container.innerHTML = '';

    data.forEach(mon => {
        const card = document.createElement('div');
        card.className = 'pokemon-card';

        card.innerHTML = `
            <img src="https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${mon.sprite}.png">
            <div>${mon.name}</div>
            <div class="small">${mon.category}</div>
        `;

        card.addEventListener('click', () => {
            renderModal(mon);
        });

        container.appendChild(card);
    });
}

function title(name) {
    return name
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join('-');
  }

document.getElementById('close-modal').onclick = () => {
    document.getElementById('pokemon-modal').classList.add('hidden');
};

window.onclick = (e) => {
    const modal = document.getElementById('pokemon-modal');
    if (e.target === modal) {
        modal.classList.add('hidden');
    }
};

function renderModal(mon) {
    const modal = document.getElementById('pokemon-modal');
    
    const pokedex_body = document.getElementById('pokedex-info');
    const megas_body = document.getElementById('megas-info');
    const learnset_body = document.getElementById('learnset-info');
    const encounter_body = document.getElementById('encounter-info');

    pokedex_body.innerHTML = '';
    megas_body.innerHTML = '';
    learnset_body.innerHTML = '';
    encounter_body.innerHTML = '';

    buildPokedexTable(pokedex_body, mon);
    buildLearnsetTable(learnset_body, mon);
    buildEncounterTable(encounter_body, mon);

    if (mon.mega_evolutions) {
        buildMegasTable(megas_body, mon);
    }

    modal.classList.remove('hidden');
}
  
function buildPokedexTable(body, mon) {
    const base_stats = mon.base_stats ? Object.entries(mon.base_stats)
        .map(([key, val]) => `${title(key)}: ${val}`)
        .join('<br>') : 'MISSING';

    const types = mon.types.map(type => {
        const sprite = type.toLowerCase().replace('fighting', 'fight');
        return `<img class="type" src="https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${sprite}.png" alt="${type}">`;
    }).join('');
      
    let abilities = [...mon.abilities.normal_abilities];
    if (mon.abilities.hidden_ability != 'None' && mon.hidden_ability != '') {
        abilities.push(`(H) ${mon.abilities.hidden_ability}`);
    }

    const sprite = `<img class="sprite" src="https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${mon.sprite}.png" alt="${mon.name}">`;

    body.innerHTML = `
        <details open>
            <summary class="title">Pokédex</summary>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Sprite</th>
                        <th>Types</th>
                        <th>Abilities</th>
                        <th>Base Stats</th>
                    </tr>
                </thead>

                <tbody>
                    <tr>
                        <td>${mon.name}</td>
                        <td>${sprite}</td>
                        <td>${types}</td>
                        <td>${abilities.join('<br>')}</td>
                        <td>${base_stats}</td>
                    </tr>
                </tbody>
            </table>
        </details>
    `;
}

function buildLearnsetTable(body, mon) {
    let level = Object.entries(mon.learnset.level).map(([move, level]) => {
        return `Lv ${level}: <a href="moves.html#${move}">${move}</a>`
    });
    if (level.length === 0) {
        level = ['None'];
    }

    let tm = (mon.learnset.tm || ['None'])
        .map(move => `<a href="moves.html#${move}">${move}</a>`);

    let egg = (mon.learnset.egg || ['None'])
        .map(move => `<a href="moves.html#${move}">${move}</a>`);

    let tutor = (mon.learnset.tutor || ['None'])
        .map(move => `<a href="moves.html#${move}">${move}</a>`);
    
    let moves = [];

    let maxRows = Math.max(level.length, tm.length, egg.length, tutor.length);
    for (let i = 0; i < maxRows; i++) {
        let row = `   
            <tr>
                <td>${level[i] || ''}</td>
                <td>${tm[i] || ''}</td>
                <td>${egg[i] || ''}</td>
                <td>${tutor[i] || ''}</td>
            </tr>
        `;
        moves.push(row);
    }

    body.innerHTML = `
        <details>
            <summary class="title">Learnset</summary>
            <table>
                <thead>
                    <tr>
                        <th>Level-Up</th>
                        <th>TM/HM</th>
                        <th>Egg</th>
                        <th>Tutor</th>
                    </tr>
                </thead>

                <tbody>
                    ${moves.join('\n')}
                </tbody>
            </table>
        </details>
    `;
}

function buildEncounterTable(body, mon) {
    let walking = (mon.locations.walking || ['None'])
        .map(loc => loc === 'None' ? 'None' : `<a href="locations.html#${loc}">${loc}</a>`);

    let surfing = (mon.locations.surfing || ['None'])
        .map(loc => loc === 'None' ? 'None' : `<a href="locations.html#${loc}">${loc}</a>`);

    let fishing = (mon.locations.fishing || ['None'])
        .map(loc => loc === 'None' ? 'None' : `<a href="locations.html#${loc}">${loc}</a>`);

    let rock_smash = (mon.locations.rock_smash || ['None'])
        .map(loc => loc === 'None' ? 'None' : `<a href="locations.html#${loc}">${loc}</a>`);
    
    let encounters = [];

    maxRows = Math.max(walking.length, surfing.length, fishing.length, rock_smash.length);
    for (let i = 0; i < maxRows; i++) {
        let row = `
            <tr>
                <td>${walking[i] || ""}</td>
                <td>${surfing[i] || ""}</td>
                <td>${fishing[i] || ""}</td>
                <td>${rock_smash[i] || ""}</td>
            </tr>
        `;
        encounters.push(row);
    }

    body.innerHTML = `
        <details>
            <summary class="title">Encounters</summary>
            <table>
                <thead>
                    <tr>
                        <th>Walking</th>
                        <th>Surfing</th>
                        <th>Fishing</th>
                        <th>Rock Smash</th>
                    </tr>
                </thead>

                <tbody>
                    ${encounters.join('\n')}
                </tbody>
            </table>
        </details>
    `;
}

function buildMegasTable(body, mon) {
    let megas = [];

    Object.entries(mon.mega_evolutions).forEach(([mega, info]) => {
        const sprite = `<img class="sprite" src="https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${info.sprite}.png alt="${megaName}">`;
        
        const base_stats = info.base_stats ? Object.entries(info.base_stats)
            .map(([key, val]) => `${title(key)}: ${val}`)
            .join('<br>') : 'MISSING';
            
        const types = info.types.map(type => {
            const sprite = type.toLowerCase().replace('fighting', 'fight');
            return `<img class="type" src="https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${sprite}.png" alt="${type}">`;
        }).join('');

        let row = `
            <tr>
                <td>${mon.name}-${title(mega)}</td>
                <td>${sprite}</td>
                <td>${types}</td>
                <td>${info.ability}</td>
                <td>${base_stats}</td>
            </tr>
        `;
        megas.push(row);
    });

    let plurality = mon.mega_evolutions.length === 1? 'Mega Evolution' : 'Mega Evolutions';

    body.innerHTML = `
        <details>
            <summary class="title">${plurality}</summary>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Sprite</th>
                        <th>Types</th>
                        <th>Abilities</th>
                        <th>Base Stats</th>
                    </tr>
                </thead>

                <tbody>
                    ${megas.join('\n')}
                </tbody>
            </table>
        </details>
    `;
}
