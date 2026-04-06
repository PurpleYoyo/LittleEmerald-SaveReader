import * as pokedex from './pokedex.js';
import * as moves from './moves.js';
import * as locations from './locations.js';
import * as abilities from './abilities.js';
import * as data from './data.js';

window.addEventListener('hashChange', () => {
    readURI();
});

function readURI() {
    ['pokemon', 'move', 'location', 'ability'].forEach(id => {
        document.getElementById(`${id}-modal`).classList.add('hidden');
    });

    const searchBar = document.getElementById('search-bar');

    const params = new URLSearchParams(window.location.hash.substring(1));

    const type = params.get('type');
    ['pokemon', 'moves', 'locations', 'abilities'].forEach(id => {
        if (type === id) {
            const radio = document.getElementById(id);
            radio.checked = true;
            radio.dispatchEvent(new Event('input', { bubbles: true }));
        }
    });

    searchBar.value = params.get('value') || '';
    searchBar.dispatchEvent(new Event('input', { bubbles: true }));
}

document.getElementById('search-bar').addEventListener('input', function () {
    let value = this.value.trim();
    let filtered;

    let selected;
    const radios = document.getElementsByName('item-selector');
    for (let i = 0; i < radios.length; i++) {
        if (radios[i].checked) {
            selected = radios[i].value;
            break;
        }
    }

    if (selected === 'pokemon') {
        filtered = Object.entries(data.pokemonData).filter(([name, _]) =>
            name.toLowerCase().includes(value.replace(/^pokémon:\s*/i, '').toLowerCase())
        ).map(([name, info]) => ({
            name,
            ...info
        }));

        pokedex.renderCards(filtered);
    }
    else if (selected === 'moves') {
        filtered = Object.entries(data.moveData).filter(([name, _]) =>
            name.toLowerCase().includes(value.replace(/move:\s*/i, '').toLowerCase())
        ).map(([name, info]) => ({
            name,
            ...info
        }));

        moves.renderCards(filtered);
    }
    else if (selected === 'locations') {
        filtered = Object.entries(data.locationData).filter(([name, _]) =>
            name.toLowerCase().includes(value.replace(/location:\s*/i, '').toLowerCase())
        ).map(([name, info]) => ({
            name,
            ...info
        }));

        locations.renderMap(filtered);
    }
    else if (selected === 'abilities') {
        filtered = Object.entries(data.moveData).filter(([name, _]) =>
            name.toLowerCase().includes(value.replace(/ability:\s*/i, '').toLowerCase())
        ).map(([name, info]) => ({
            name,
            ...info
        }));

        abilities.renderCards(filtered);
    }
});

document.getElementById('pokemon').addEventListener('input', () => pokedex.renderCards(data.pokemonData));
document.getElementById('moves').addEventListener('input', () => moves.renderCards(data.moveData));
//document.getElementById('locations').addEventListener('input', () => locations.renderMap(data.locationData));
document.getElementById('abilities').addEventListener('input', () => abilities.renderCards(data.abilityData));

window.addEventListener('click', (e) => {
    document.querySelectorAll('.modal').forEach(modal => {
        if (e.target === modal) {
            modal.classList.add('hidden');
            document.body.classList.remove('modal-open');
        }
    });
});

document.querySelectorAll('.close-modal').forEach(btn => {
    btn.addEventListener('click', () => {
        const modal = btn.closest('.modal');
        if (modal) {
            modal.classList.add('hidden');
            document.body.classList.remove('modal-open');
        }
    });
});
