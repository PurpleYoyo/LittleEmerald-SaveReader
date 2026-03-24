import * as pokedex from './pokedex.js';
import * as moves from './moves.js';
import * as locations from './locations.js';
import * as data from './data.js';

function readURI() {
    const searchBar = document.getElementById('search-bar');

    const pok = decodeURIComponent(window.location.hash.substring(1));
    searchBar.value = pok || '';

    var event = new Event('input', { bubbles: true });
    searchBar.dispatchEvent(event);
}

document.getElementById('search-bar').addEventListener('input', function () {
    let value = this.value;
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
        filtered = data.pokemonData.filter(mon =>
            mon.name.includes(value.replace('Pokémon', ''))
        );

        pokedex.renderCards(filtered);
    }
    else if (selected === 'moves') {
        filtered = data.moveData.filter(move =>
            move.name.includes(value.replace('Move: ', ''))
        );

        moves.renderCards(filtered);
    }
    else if (selected === 'locations') {
        filtered = data.locationData.filter(loc =>
            loc.name.includes(value.replace('Location: ', ''))
        );

        locations.renderMap(filtered);
    }
    else if (value.includes('Ability: ')) {
    }
});

document.getElementById('pokemon').addEventListener('input', pokedex.renderCards(data.pokemonData));
document.getElementById('moves').addEventListener('input', moves.renderCards(data.moveData));
document.getElementById('locations').addEventListener('input', locations.renderMap(data.locationData));
