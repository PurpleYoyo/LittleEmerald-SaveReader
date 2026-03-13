let moveData = [];

fetch('moves_info.json')
.then(res => res.json())
.then(data => {
    moveData = Object.entries(data).map(([name, info]) => ({
        name,
        ...info
    }));
        
    const datalist = document.getElementById('move-suggestions');
    moveData.forEach(move => {
        const option = document.createElement('option');
        option.value = move.name;
        datalist.appendChild(option);
    });

    let defaults = [
        'Pound',
        'Tackle',
        'Scratch',
    ];

    const searchBar = document.getElementById('search-bar');
    searchBar.value = defaults[Math.floor(defaults.length * Math.random())];

    var event = new Event('input', { bubbles: true });
    searchBar.dispatchEvent(event);
});

document.getElementById('search-bar').addEventListener('input', function () {
  const value = this.value.toLowerCase();
  const match = moveData.find(move => move.name.toLowerCase() === value);
  if (match) {
    renderTable([match]);
  }
  else {
    clearTable();
  }
});

function clearTable() {
    document.querySelector('#movedex-table tbody').innerHTML = '';
    document.querySelector('#learned-by-table tbody').innerHTML = '';
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
    const learned_by_table = document.querySelector('#learned-by-table tbody');
    const tbody = document.querySelector('#movedex-table tbody');
    tbody.innerHTML = '';
    learned_by_table.innerHTML = '';

    const flagsDiv = document.getElementById('flags');
    const addEffDiv = document.getElementById('additional-effects');
    flagsDiv.innerHTML = '';
    addEffDiv.innerHTML = '';
  
    for (const move of data) {
        const row = document.createElement('tr');
          
        const basePower = move.base_power;
        const name = move.name;
        const description = move.description;
        const accuracy = move.accuracy;
        const pp = move.pp;
        const target = move.target;
        const category = move.category;

        const typeName = move.type.toLowerCase();
        let spriteName = typeName;
        if (typeName == 'fighting') {
            spriteName = 'fight';
        }
        const type = `<img src="https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${spriteName}.png" alt="${formatName(typeName)}" title="${formatName(typeName)}" style="height: 24px; margin-right: 4px;">`;

        const priority = move.priority;
        
        const flags = [];

        if (move.contact) {
            flags.push('Makes Contact &#9989;');
        }
        if (move.ignoresProtect) {
            flags.push('Ignores Protect &#9989;');
        }
        if (move.highCritRate) {
            flags.push('High Crit Rate &#9989;');
        }
        if (move.soundMove) {
            flags.push('Sound Move &#9989;');
        }
        if (move.pulseMove) {
            flags.push('Pulse Move &#9989;');
        }
        if (move.bitingMove) {
            flags.push('Biting Move &#9989;');
        }
        if (move.punchingMove) {
            flags.push('Punching Move &#9989;');
        }
        if (move.ballMove) {
            flags.push('Ball Move &#9989;');
        }
        if (move.healingMove) {
            flags.push('Healing Move &#9989;');
        }
        if (move.slicingMove) {
            flags.push('Slicing Move &#9989;');
        }
        if (move.danceMove) {
            flags.push('Dance Move &#9989;');
        }
        if (move.windMove) {
            flags.push('Wind Move &#9989;');
        }
        if (move.powderMove) {
            flags.push('Powder Move &#9989;');
        }
    
        const innerHTML = [
            `<td>${name}</td>`,
            `<td>${description}</td>`,
            `<td>${type}</td>`,
            `<td>${basePower}</td>`,
            `<td>${accuracy}</td>`,
            `<td>${pp}</td>`,
            `<td>${target}</td>`,
            `<td>${category}</td>`,
            `<td>${priority}</td>`,
        ];

        row.innerHTML = innerHTML.join('\n');
        tbody.appendChild(row);

        if (flags) {
            const flagsDetails = document.createElement('details');
            flagsDiv.appendChild(flagsDetails);

            const flagsSummary = document.createElement('summary');
            flagsSummary.className = 'caption';
            flagsSummary.innerHTML = 'Move Flags';
            flagsDetails.appendChild(flagsSummary);

            const flagsText = document.createElement('pre');
            flagsText.textContent = `${flags.join('\n')}`;
            flagsDetails.appendChild(flagsText);
        }

        let additionalEffects = [];
        Object.entries(move.additionalEffects).forEach(([effect, chance]) => {
            additionalEffects.push(`${chance} ${effect}`);
        });

        if (additionalEffects) {
            const addEffDetails = document.createElement('details');
            addEffDiv.appendChild(addEffDetails);

            const addEffSummary = document.createElement('summary');
            addEffSummary.className = 'caption';
            addEffSummary.innerHTML = 'Additional Effects';
            addEffDetails.appendChild(addEffSummary);

            const addEffText = document.createElement('pre');
            addEffText.textContent = `${effects.join('\n')}`;
            addEffDetails.appendChild(addEffText);
        }

        let learned_by = move.learned_by;

        let levelup = learned_by.level || { "None": "0" };
        let levelup_moves = [];
        Object.entries(levelup).forEach(([pok, level]) => {
            levelup_moves.push(`${formatName(pok)}: ${level}`);
        });
        
        let tm = (learned_by.tm || ["None"]).map(pok => formatName(pok));
        let egg = (learned_by.egg || ["None"]).map(pok => formatName(pok));
        let tutor = (learned_by.tutor || ["None"]).map(pok => formatName(pok));
        
        const maxRows = Math.max(levelup_moves.length, tm.length, egg.length, tutor.length);
        for (let i = 0; i < maxRows; i++) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${levelup_moves[i] || ""}</td>
                <td>${tm[i] || ""}</td>
                <td>${egg[i] || ""}</td>
                <td>${tutor[i] || ""}</td>
            `;
            learned_by_table.appendChild(row);
        }
    }
}  
  