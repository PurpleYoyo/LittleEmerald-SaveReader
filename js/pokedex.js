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

    const searchBar = document.getElementById('search-bar');

    let defaults = [
        'Bulbasaur',
        'Charmander',
        'Squirtle',
    ];

    const pokemon = window.location.hash.substring(1).replace(/%20/g, ' ');
    searchBar.value = pokemon || defaults[Math.floor(defaults.length * Math.random())];

    var event = new Event('input', { bubbles: true });
    searchBar.dispatchEvent(event);
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

function formatName(name) {
    const special_cases = {
        'nidoran-f': 'Nidoran♀',
        'nidoran-m': 'Nidoran♂',
        'farfetchd-galar': "Farfetch’d Galar",
        'mime-jr': 'Mime Jr.',
        'type-null': 'Type: Null',
        'jangmo-o': 'Jangmo-o',
        'flabebe': 'Flabébé',
        'hp': 'HP',
    };
  
    if (special_cases[name]) {
      return special_cases[name];
    }
  
    return name
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
  }

  
function renderTable(data) {
    const learnset = document.querySelector('#learnset-table tbody');
    const tbody = document.querySelector('#pokedex-table tbody');
    const encounters = document.querySelector('#encounters-table tbody');
    tbody.innerHTML = '';
    learnset.innerHTML = '';
    encounters.innerHTML = '';
    const sprite = document.querySelector('#sprite');
    sprite.src = '';

    const megasDiv = document.getElementById('megas');
    megasDiv.innerHTML = '';
  
    for (const mon of data) {
        const row = document.createElement('tr');
    
        const baseStats = mon.base_stats ? Object.entries(mon.base_stats).map(([key, val]) => `${formatName(key)}: ${val}`).join("<br>") : "Unknown";
        const types = mon.types.map(type => {
            const typeLower = type.toLowerCase();
            let spriteName = typeLower;
            if (typeLower == 'fighting') {
                spriteName = 'fight';
            }
            return `<img src="https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${spriteName}.png" alt="${type}" title="${type}" style="height: 24px; margin-right: 4px;">`;
        }).join('');
          
        let abilities = mon.abilities.normal_abilities;
        if (mon.abilities.hidden_ability != "None") {
            abilities.push(`(H) ${mon.abilities.hidden_ability}`);
        }
        const name = formatName(mon.name);
    
        row.innerHTML = `
            <td>${name}</td>
            <td>${types}</td>
            <td>${abilities.join('<br>')}</td>
            <td>${baseStats}</td>
        `;
        tbody.appendChild(row);

        const base_forms = {
            'burmy-sandy' : 'burmy',
            'burmy-trash' : 'burmy',
            'deerling-autumn' : 'deerling',
            'deerling-summer' : 'deerling',
            'deerling-winter' : 'deerling',
            'petilil-fighting' : 'petilil',
            'eevee-fire' : 'eevee',
            'eevee-water' : 'eevee',
            'eevee-electric' : 'eevee',
            'eevee-dark' : 'eevee',
            'eevee-psychic' : 'eevee',
            'eevee-grass' : 'eevee',
            'eevee-ice' : 'eevee',
            'eevee-fairy' : 'eevee',
            'charcadet-psychic' : 'charcadet',
            'charcadet-ghost' : 'charcadet',
            'ralts-fighting' : 'ralts',
            'snorunt-ghost' : 'snorunt',
            'wurmple-poison' : 'wurmple',
            'nincada-ghost' : 'nincada',
            'exeggcute-dragon' : 'exeggcute',
            'koffing-fairy' : 'koffing',
            'rufflet-psychic' : 'rufflet',
            'goomy-steel' : 'goomy',
            'bergmite-rock' : 'bergmite',
            'froakie-special' : 'froakie',
            'rockruff-special' : 'rockruff',
            'feebas-fairy' : 'feebas',
        }
    
        let current_mon = mon;
        if (base_forms[mon.name]) {
            const base_name = base_forms[mon.name];
            const base_mon = pokemonData.find(p => p.name === base_name);
            if (base_mon) {
                current_mon = base_mon;
            }
        }

        let spriteName = current_mon.name.toLowerCase().replace(/ /g, '_');
        sprite.src = `https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${spriteName}.png`;

        if (current_mon.mega) {
            const megasDetails = document.createElement('details');
            megasDiv.appendChild(megasDetails);

            const megasSummary = document.createElement('summary');
            megasSummary.className = 'title';
            megasSummary.innerHTML = 'Mega Evolution';

            const megasTable = document.createElement('table');
            megasDetails.appendChild(megasTable);

            megasTable.innerHTML = `
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Types</th>
                        <th>Ability</th>
                        <th>Base Stats</th>
                    </tr>
                </thead>
            `;

            const megasTbody = document.createElement('tbody');
            megasTable.appendChild(megasTbody);

            let megas;

            if (
                current_mon.name == 'Tyrogue' ||
                current_mon.name == 'Mime Jr.' ||
                current_mon.name == 'Toxel'
            ) {
                megas = current_mon.mega;
            }
            else {
                megas = {
                    '': current_mon.mega
                };
            }

            Object.entries(megas).forEach(([mega, info]) => {
                const megaSprite = document.createElement('img');
                megaSprite.src = `https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${info.sprite}.png`;
                megasDetails.prepend(megaSprite);

                const megasRow = document.createElement('tr');

                if (mega != '') {
                    mega = `-${mega}`;
                }

                const megaName = `${formatName(mon.name)}-Mega${mega}`;
                const megaBaseStats = info.base_stats ? Object.entries(info.base_stats).map(([key, val]) => `${formatName(key)}: ${val}`).join("<br>") : "Unknown";
                const megaTypes = info.types.map(type => {
                    const typeLower = type.toLowerCase();
                    let spriteName = typeLower;
                    if (typeLower == 'fighting') {
                        spriteName = 'fight';
                    }
                    return `<img src="https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${spriteName}.png" alt="${type}" title="${type}" style="height: 24px; margin-right: 4px;">`;
                }).join('');
                const megaAbility = info.ability;

                megasRow.innerHTML = `
                    <td>${megaName}</td>
                    <td>${megaTypes}</td>
                    <td>${megaAbility}</td>
                    <td>${megaBaseStats}</td>
                `;
                megasTbody.appendChild(row);
            });

            megasDetails.prepend(megasSummary);
        }

        let levelup = current_mon.level_up_moves || ["Unknown"];
        levelup = levelup.map(l => `Lv ${l.level}: <a href="moves.html#${l.move}">${l.move}</a>`);

        let tm = (current_mon.tm_moves || ["None"]).map(move => `<a href="moves.html#${move}">${formatName(move)}</a>`);
        let egg = (current_mon.egg_moves || ["None"]).map(move => `<a href="moves.html#${move}">${formatName(move)}</a>`);
        let tutor = (current_mon.tutor_moves || ["None"]).map(move => `<a href="moves.html#${move}">${formatName(move)}</a>`);
        
        let maxRows = Math.max(levelup.length, tm.length, egg.length, tutor.length);
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

        let walking = (current_mon.locations.walking || ["None"]).map(loc => loc === 'None' ? 'None' : `<a href="locations.html#${loc}">${loc}</a>`);
        let surfing = (current_mon.locations.surfing || ["None"]).map(loc => loc === 'None' ? 'None' : `<a href="locations.html#${loc}">${loc}</a>`);
        let fishing = (current_mon.locations.fishing || ["None"]).map(loc => loc === 'None' ? 'None' : `<a href="locations.html#${move}">${loc}</a>`);
        let rocking = (current_mon.locations.rock_smash || ["None"]).map(loc => loc === 'None' ? 'None' : `<a href="locations.html#${move}">${loc}</a>`);
        
        maxRows = Math.max(walking.length, surfing.length, fishing.length, rocking.length);
        for (let i = 0; i < maxRows; i++) {
            const row = document.createElement('tr');
            row.innerHTML = `   
                <td>${walking[i] || ""}</td>
                <td>${surfing[i] || ""}</td>
                <td>${fishing[i] || ""}</td>
                <td>${rocking[i] || ""}</td>
            `;
            encounters.appendChild(row);
        }
    }
}  
  