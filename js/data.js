import { renderCards } from './pokedex.js';

export let pokemonData = [];
export let moveData = [];
export let locationData = [];
export let subareaMapping = {};
export let abilityData = [];

fetch('data/subarea_mapping.json')
.then(res => res.json())
.then(data => {
    subareaMapping = data;
});

fetch('data/pokemon_data.json')
.then(res => res.json())
.then(data => {
    pokemonData = data;
        
    const datalist = document.getElementById('suggestions');
    Object.entries(data).forEach(([_, info]) => {
        const option = document.createElement('option');
        option.value = `Pokémon: ${info.name}`;
        datalist.appendChild(option);
    });

    renderCards(pokemonData);
});

fetch('data/move_data.json')
.then(res => res.json())
.then(data => {
    moveData = data;
        
    const datalist = document.getElementById('suggestions');
    Object.entries(data).forEach(([_, info]) => {
        const option = document.createElement('option');
        option.value = `Move: ${info.name}`;
        datalist.appendChild(option);
    });
});

fetch('data/location_data.json')
.then(res => res.json())
.then(data => {
    locationData = data;
        
    const datalist = document.getElementById('suggestions');
    Object.entries(data).forEach(([_, info]) => {
        const option = document.createElement('option');
        option.value = `Location: ${info.name}`;
        datalist.appendChild(option);
    });
});

fetch('data/ability_data.json')
.then(res => res.json())
.then(data => {
    abilityData = data;
        
    const datalist = document.getElementById('suggestions');
    Object.entries(data).forEach(([_, info]) => {
        const option = document.createElement('option');
        option.value = `Ability: ${info.name}`;
        datalist.appendChild(option);
    });
});
