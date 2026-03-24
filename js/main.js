import * as pokedex from './pokedex.js';
import * as moves from './moves.js';
import * as locations from './locations.js';

const tile_width = 16;
const scale = 0.9;

let pokemonData = [];
let moveData = [];
let locationData = [];

fetch('data/pokemon_data.json')
.then(res => res.json())
.then(data => {
    pokemonData = Object.entries(data).map(([name, info]) => ({
        name,
        ...info
    }));
        
    const datalist = document.getElementById('suggestions');
    pokemonData.forEach(mon => {
        const option = document.createElement('option');
        option.value = `Pokémon: ${mon.name}`;
        datalist.appendChild(option);
    });
});

fetch('data/moves_info.json')
.then(res => res.json())
.then(data => {
    moveData = Object.entries(data).map(([name, info]) => ({
        name,
        ...info
    }));
        
    const datalist = document.getElementById('suggestions');
    moveData.forEach(move => {
        const option = document.createElement('option');
        option.value = `Move: ${move.name}`;
        datalist.appendChild(option);
    });
});

fetch('data/location_data.json')
.then(res => res.json())
.then(data => {
    locationData = Object.entries(data).map(([name, info]) => ({
        name,
        ...info
    }));
        
    const datalist = document.getElementById('suggestions');
    pokemonData.forEach(loc => {
        const option = document.createElement('option');
        option.value = `Location: ${loc.name}`;
        datalist.appendChild(option);
    });
});

function title(name) {  
    return name
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

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
        filtered = pokemonData.filter(mon =>
            mon.name.includes(value.replace('Pokémon', ''))
        );

        pokedex.renderCards(filtered);
    }
    else if (selected === 'moves') {
        filtered = moveData.filter(move =>
            move.name.includes(value.replace('Move: ', ''))
        );

        moves.renderCards(filtered);
    }
    else if (selected === 'locations') {
        filtered = locationData.filter(loc =>
            loc.name.includes(value.replace('Location: ', ''))
        );

        locations.renderMap(filtered);
    }
    else if (value.includes('Ability: ')) {
    }
});
