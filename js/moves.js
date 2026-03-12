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
    const learned_by = document.querySelector('#learned-by-table tbody');
    const tbody = document.querySelector('#movedex-table tbody');
    tbody.innerHTML = '';
    learned_by.innerHTML = '';
  
    for (const move of data) {
        const row = document.createElement('tr');
          
        const basePower = move.base_power;
        const name = move.name;
        const description = move.description;
        const accuracy = move.accuracy;
        const pp = move.pp;
        const target = move.target;
        const category = move.category;

        const typeName = move.type;
        const type = `<img src="https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${typeName.toLowerCase()}.png" alt="${typeName}" title="${typeName}" style="height: 24px; margin-right: 4px;">`;

        const priority = move.priority;
        
        const flags = [
            `Contact: ${move.makesContact}`,
        ];
        if (move.soundMove) {
            flags.push('Sound Move: True');
        }
        if (move.pulseMove) {
            flags.push('Pulse Move: True');
        }
        if (move.bitingMove) {
            flags.push('Biting Move: True');
        }
        if (move.punchingMove) {
            flags.push('Punching Move: True');
        };
        if (move.ballMove) {
            flags.push('Ball Move: True');
        };

        const additionalEffects = move.additionalEffects;
    
        innerHTML = [
            `<td>${name}</td>`,
            `<td>${description}</td>`,
            `<td>${type}</td>`,
            `<td>${basePower}</td>`,
            `<td>${accuracy}</td>`,
            `<td>${pp}</td>`,
            `<td>${target}</td>`,
            `<td>${category}</td>`,
            `<td>${flags.join('\n')}</td>`,
        ];

        if (priority !== 0) {
            innerHTML.push(`<td>${priority}</td`);
        }

        innerHTML.push(`<td>${additionalEffects}</td`);

        row.innerHTML = innerHTML.join('\n');
        tbody.appendChild(row);

        //let levelup = current_mon.level_up_moves || ["Unknown"];
        //levelup = levelup.map(l => `Lv ${l.level}: ${l.move}`);
        //let tm = current_mon.tm_moves || ["None"];
        //let egg = current_mon.egg_moves || ["None"];
        //let tutor = current_mon.tutor_moves || ["None"];
        //
        //const maxRows = Math.max(levelup.length, tm.length, egg.length, tutor.length);
        //for (let i = 0; i < maxRows; i++) {
        //    const row = document.createElement('tr');
        //    row.innerHTML = `
        //        <td>${levelup[i] || ""}</td>
        //        <td>${tm[i] || ""}</td>
        //        <td>${egg[i] || ""}</td>
        //        <td>${tutor[i] || ""}</td>
        //    `;
        //    learnset.appendChild(row);
        //}
    }
}  
  