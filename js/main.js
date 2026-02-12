import * as encounters from './encounters.js';
import * as trainers from './trainers.js';
import * as items from './items.js';

let locationData = [];
fetch('location_data.json')
.then(res => res.json())
.then(data => {
    locationData = Object.entries(data).map(([name, info]) => ({
        name,
        ...info
    }));
        
    const datalist = document.getElementById('location-suggestions');
    locationData.forEach(loc => {
        const option = document.createElement('option');
        option.value = loc.name;
        datalist.appendChild(option);
    });

    const searchBar = document.getElementById('search-bar');
    searchBar.value = 'Route 102';

    var event = new Event('input', { bubbles: true });
    searchBar.dispatchEvent(event);
});

document.getElementById('search-bar').addEventListener('input', function () {
    const value = this.value.toLowerCase();
    const match = locationData.find(loc => loc.name.toLowerCase() === value);
    if (match) {
        encounters.renderTable({ [match.name]: match });

        trainers.setCurrentMatch(match);
        trainers.loadMapImage();

        items.setCurrentMatch(match);
        items.loadMapImage();
    }
});
