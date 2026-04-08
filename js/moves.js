import { pokemonData } from './data.js';
import { buildFormattedArray, format } from './utils.js';

export function renderCards(data) {
    document.getElementById('map-container').innerHTML = '';
    
    const container = document.getElementById('cards-container');
    container.innerHTML = '';
    container.classList.remove('grid');

    Object.entries(data).forEach(([_, info]) => {
        const card = document.createElement('div');
        card.className = 'move-card';

        const sprite = info.type.toLowerCase().replace('fighting', 'fight');
        card.innerHTML = `
            <img class="type" src="https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${sprite}.png" alt="${info.type}">
            <div>${info.name}</div>
        `;

        card.addEventListener('click', () => {
            renderModal(info);
        });

        container.appendChild(card);
    });
}

function renderModal(move) {
    const modal = document.getElementById('move-modal');

    const movedex_body = document.getElementById('movedex-info');
    const learned_by_body = document.getElementById('learned-by-info');

    movedex_body.innerHTML = '';
    learned_by_body.innerHTML = '';

    buildMovedexTable(movedex_body, move);
    buildLearnedByTable(learned_by_body, move);

    modal.classList.remove('hidden');
    document.body.classList.add('modal-open');
}

function buildMovedexTable(body, move) {
    const typeSprite = move.type.toLowerCase().replace('fighting', 'fight');
    const type = `<img class="type" src="https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${typeSprite}.png" alt="${move.type}">`;
        
    let flags = [];

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

    let additional_effects = (move.additionalEffects || []).map(effect => {
        let text = effect.effect;

        if (effect.chance) {
            text = `${effect.chance} chance to ${effect.effect}`
        }

        if (effect.self) {
            text += ' (Affects User)'
        }

        return text;
    });
    
    body.innerHTML = `
        <details open>
            <summary class="title">Movedex</summary>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Description</th>
                        <th>Type</th>
                        <th>Base Power</th>
                        <th>Accuracy</th>
                        <th>PP</th>
                        <th>Target</th>
                        <th>Category</th>
                        <th>Priority</th>
                    </tr>
                </thead>

                <tbody>
                    <tr>
                        <td>${move.name}</td>
                        <td>${move.description}</td>
                        <td>${type}</td>
                        <td>${move.base_power}</td>
                        <td>${move.accuracy}</td>
                        <td>${move.pp}</td>
                        <td>${move.target}</td>
                        <td>${move.category}</td>
                        <td>${move.priority}</td>
                    </tr>
                </tbody>
            </table>
        </details>
    `;

    if (flags.length) {
        body.innerHTML += `
            <details>
                <summary class="caption">Flags<summary>
                <pre>${flags.join('<br>')}</pre>
            </details>
        `;
    }

    if (additional_effects.length) {
        body.innerHTML += `
            <details>
                <summary class="caption">Additional Effects</summary>
                <pre>${additional_effects.join('\n')}</pre>
            </details>
        `;
    }
}

function buildLearnedByTable(body, move) {
    const link = '<a href="index.html#value={0}&type=pokemon">{0}</a>';

    let level = move.learned_by.level.map(entry => {
        const name = pokemonData[entry.species]?.name ?? 'None';
        return name === 'None' ? 'None' : `Lv ${entry.level}: ${format(link, name)}`
    });
    if (!level.length) {
        level = ['None'];
    }

    const tm = buildFormattedArray(move.learned_by.tm, link, pokemonData);
    const egg = buildFormattedArray(move.learned_by.egg, link, pokemonData);
    const tutor = buildFormattedArray(move.learned_by.tutor, link, pokemonData);
    
    let mons = [];

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
        mons.push(row);
    }

    body.innerHTML = `
        <details>
            <summary class="title">Learned By</summary>
            <table>
                <thead>
                    <tr>
                        <th>Via Level-Up</th>
                        <th>Via TM/HM</th>
                        <th>Via Egg</th>
                        <th>Via Tutor</th>
                    </tr>
                </thead>

                <tbody>
                    ${mons.join('\n')}
                </tbody>
            </table>
        </details>
    `;
}
