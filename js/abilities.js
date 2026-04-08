import { pokemonData } from './data.js';
import { buildFormattedArray } from './utils.js';

export function renderCards(data) {
    document.getElementById('map-container').innerHTML = '';
    
    const container = document.getElementById('cards-container');
    container.innerHTML = '';
    container.classList.remove('grid');

    Object.entries(data).forEach(([_, info]) => {
        const card = document.createElement('div');
        card.className = 'ability-card';

        card.innerHTML = `
            <div>${info.name}</div>
        `;

        card.addEventListener('click', () => {
            renderModal(info);
        });

        container.appendChild(card);
    });
}

function renderModal(ability) {
    const modal = document.getElementById('ability-modal');

    const ability_body = document.getElementById('ability-info');
    const pokemon_with_body = document.getElementById('pokemon-with-info');

    ability_body.innerHTML = '';
    pokemon_with_body.innerHTML = '';

    buildAbilityTable(ability_body, ability);
    buildPokemonWithTable(pokemon_with_body, ability);

    modal.classList.remove('hidden');
    document.body.classList.add('modal-open');
}

function buildAbilityTable(body, ability) {
    const description = !ability.detailed_description ? ability.description : ability.detailed_description;
    
    body.innerHTML = `
        <details open>
            <summary class="title">Movedex</summary>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Description</th>
                    </tr>
                </thead>

                <tbody>
                    <tr>
                        <td>${ability.name}</td>
                        <td>${description}</td>
                    </tr>
                </tbody>
            </table>
        </details>
    `;
}

function buildPokemonWithTable(body, ability) {
    const link = '<a href="index.html#value={0}&type=pokemon">{1}</a>';

    const normal = buildFormattedArray(ability.pokemon_with.normal, link, pokemonData);
    const hidden = buildFormattedArray(ability.pokemon_with.hidden, link, pokemonData);
    
    let mons = [];

    let maxRows = Math.max(normal.length, hidden.length);
    for (let i = 0; i < maxRows; i++) {
        let row = `
            <tr>
                <td>${normal[i] || ''}</td>
                <td>${hidden[i] || ''}</td>
            </tr>
        `;
        mons.push(row);
    }

    body.innerHTML = `
        <details>
            <summary class="title">Pokémon With</summary>
            <table>
                <thead>
                    <tr>
                        <th>Normal</th>
                        <th>Hidden</th>
                    </tr>
                </thead>

                <tbody>
                    ${mons.join('\n')}
                </tbody>
            </table>
        </details>
    `;
}
