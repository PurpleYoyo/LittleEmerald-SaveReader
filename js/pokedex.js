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
    tbody.innerHTML = '';
    learnset.innerHTML = '';
    const sprite = document.querySelector('#sprite');
  
    for (const mon of data) {
        const row = document.createElement('tr');
    
        const baseStats = mon.base_stats ? Object.entries(mon.base_stats).map(([key, val]) => `${formatName(key)}: ${val}`).join("<br>") : "Unknown";
        const types = mon.types.map(type => {
            const typeLower = type.toLowerCase();
            return `<img src="https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${typeLower}.png" alt="${type}" title="${type}" style="height: 24px; margin-right: 4px;">`;
        }).join('');
          
        const abilities = mon.abilities.join("<br>") || "Unknown";
        const name = formatName(mon.name);

        sprite.src = `https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${mon.name}.png`;
    
        row.innerHTML = `
            <td>${name}</td>
            <td>${types}</td>
            <td>${abilities}</td>
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
    
        if (base_forms[mon.name]) {
            const base_name = base_forms[mon.name];
            const base_mon = pokemonData.find(p => p.name === base_name);
            if (base_mon) {
                mon = base_mon;
            }
        }

        let levelup = mon.level_up_moves || ["Unknown"];
        levelup = levelup.map(l => `Lv ${l.level}: ${l.move}`);
        let tm = mon.tm_moves || ["None"];
        let egg = mon.egg_moves || ["None"];
        let tutor = mon.tutor_moves || ["None"];
        
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
  