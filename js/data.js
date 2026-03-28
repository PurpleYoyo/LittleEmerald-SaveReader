import { renderCards } from './pokedex.js';

export let pokemonData = [];
export let moveData = [];
export let locationData = [];
export let subareaMapping = {};

fetch('data/subarea_mapping.json');

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

    renderCards(pokemonData);
});

fetch('data/move_data.json')
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
    locationData.forEach(loc => {
        const option = document.createElement('option');
        option.value = `Location: ${loc.name}`;
        datalist.appendChild(option);
    });
});