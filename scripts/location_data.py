import json
import os
import re

from .utils import TM_NAMES, SPECIFIC_ITEM_CASES
from .utils import get_parent_name

with open('scripts/config.json', 'r', encoding = 'utf-8') as file:
    CONFIG = json.load(file)

INPUTS = CONFIG['inputs']
OUTPUTS = CONFIG['outputs']

with open('scripts/absolute_path.txt', 'r') as file:
    ABSOLUTE_PATH = file.read()
    
with open(f"{ABSOLUTE_PATH}{INPUTS['location_data']['encounter_data']}", 'r') as file:
    encounters_data = json.load(file)

with open(OUTPUTS['set_data'], 'r') as f:
    set_data = json.load(f)

with open(OUTPUTS['pokemon_data'], 'r') as f:
    pokemon_data = json.load(f)

maps = {}
for i in os.scandir(f"{ABSOLUTE_PATH}{INPUTS['location_data']['maps_path']}"):
    if i.is_dir():
        MAP_PATH = f"{ABSOLUTE_PATH}{INPUTS['location_data']['maps_path']}/{i.name}/map.json"
        with open(MAP_PATH) as file:
            maps[i.name] = json.load(file)
            
data = {}
for area in encounters_data['wild_encounter_groups'][0]['encounters']:
    raw_name = area['map']
    formatted_name: str = area['base_label'][1:]
    
    if raw_name == 'MAP_ALTERING_CAVE':
        formatted_name = 'AlteringCave'
    
    subname = None
    parent = None
    pname = None
    if '_' in formatted_name:
        if formatted_name.count('_') == 2:
            subcount = -2
        else:
            subcount = -1
            
        pname = ''.join(formatted_name.split('_')[:subcount])
        subname = '_'.join(formatted_name.split('_')[subcount:])
        parent = get_parent_name(raw_name, subname)
    
    current_data = {
        'image'         : f'locations/{formatted_name}.png',
        'encounters'    : {
            'walking'       : [],
            'surfing'       : [],
            'fishing'       : [],
            'rock_smash'    : [],
        },
        'items'         : [],
        'trainers'      : [],
    }
    if not subname:
        current_data['sub-areas'] = {}
    
    if 'land_mons' in area:
        current_data['encounters']['walking'] = area['land_mons']['mons']
        
    if 'water_mons' in area:
        current_data['encounters']['surfing'] = area['water_mons']['mons']
    
    if 'fishing_mons' in area:
        current_data['encounters']['fishing'] = area['fishing_mons']['mons']
    
    if 'rock_smash_mons' in area:
        current_data['encounters']['rock_smash'] = area['rock_smash_mons']['mons']
    
    for method in ['walking', 'surfing', 'fishing', 'rock_smash']:
        for enc in current_data['encounters'][method]:
            pok = enc['species']
            
            if pok == 'SPECIES_SHELLOS_WEST':
                pok = 'SPECIES_SHELLOS_EAST'
            if pok == 'SPECIES_SHELLOS':
                pok = 'SPECIES_SHELLOS_EAST'
            if pok == 'SPECIES_SINISTEA':
                pok = 'SPECIES_SINISTEA_ANTIQUE'
            if pok == 'SPECIES_POLTCHAGEIST':
                pok = 'SPECIES_POLTCHAGEIST_COUNTERFEIT'
            if 'SPECIES_FLABEBE' in pok:
                pok = 'SPECIES_FLABEBE_TEMPLATE'
            if pok == 'SPECIES_SCATTERBUG':
                pok = 'SPECIES_SCATTERBUG_TEMPLATE'
            if pok == 'SPECIES_GIMMIGHOUL':
                pok = 'SPECIES_GIMMIGHOUL_ROAMING'
            if pok == 'SPECIES_PUMPKABOO':
                pok = 'SPECIES_PUMPKABOO_SUPER'
                
            if not 'locations' in pokemon_data[pok]:
                pokemon_data[pok]['locations'] = {
                    'walking'       : [],
                    'surfing'       : [],
                    'fishing'       : [],
                    'rock_smash'    : [],
                }

            pokemon_data[pok]['locations'][method].append(raw_name)
            pokemon_data[pok]['locations'][method] = list(set(pokemon_data[pok]['locations'][method]))
    try:
        if subname:
            to_use = f'{pname}_{subname}'
        else:
            to_use = formatted_name
            
        map_data = maps[to_use]
    except KeyError:
        print(f'{to_use} not located in maps.\nsubname: {subname}\npname: {pname}\nparent: {parent}')
        continue
    
    if not 'object_events' in map_data:
        continue
        
    for e in map_data['object_events']:
        if e['trainer_type'] == 'TRAINER_TYPE_NORMAL':
                graphics_id = e['graphics_id']
                    
                trainer_name: str = e['script']
                trainer_name = trainer_name.split('_')[-1]
                
                trainer_sets = {}
                full_names = {}
                for pok in set_data:
                    for trainer in set_data[pok]:
                        if trainer_name in trainer:
                            trainer_sets[pok] = set_data[pok][trainer]
                            full_names[trainer_name] = trainer
                    
                full_name = re.sub(r"\s*Lvl\s*\d+", "", full_names.get(trainer_name, trainer_name)).strip()
                
                current_data['trainers'].append({
                    'coordinates'           : (e['x'], e['y']),
                    'graphics_id'           : graphics_id,
                    'trainer_name'          : trainer_name,
                    'full_name'             : full_name,
                    'sets'                  : trainer_sets,
                })
                
        if e['graphics_id'] in ['OBJ_EVENT_GFX_ITEM_BALL', 'OBJ_EVENT_GFX_BERRY_TREE', 'OBJ_EVENT_GFX_TM_BALL']:
            item_or_berry: str = e['trainer_sight_or_berry_tree_id']
            if 'BERRY' in item_or_berry:
                full = item_or_berry.replace('_', ' ').lower().split()
                if str(full[-1]).isnumeric():
                    item = f'{full[-2].title()} Berry'
                else:
                    item = f'{full[-1].title()} Berry'
            else:
                item = item_or_berry.replace('ITEM_', '').replace('_', ' ').lower().title()

            if str(item) == "0":
                continue
            
            if 'Soil' in item:
                continue
            
            if item in SPECIFIC_ITEM_CASES:
                item = SPECIFIC_ITEM_CASES[item]

            if item in TM_NAMES:
                item = TM_NAMES[item]

            current_data['items'].append({
                'coordinates'           : (e['x'], e['y']),
                'item'                  : item,
            })
            
    for e in map_data['bg_events']:
        if not e['type'] == 'hidden_item':
            continue
        
        item: str = e['item']
        item = item.replace('ITEM_', '').replace('_', ' ').lower().title()
        
        if item in SPECIFIC_ITEM_CASES:
            item = SPECIFIC_ITEM_CASES[item]
            
        if item in TM_NAMES:
            item = TM_NAMES[item]
                
        current_data['items'].append({
            'coordinates'           : (e['x'], e['y']),
            'item'                  : item,
        })

    if subname:
        if not parent in data:
            data[parent] = {
                'sub-areas' : {}
            }
        
        data[parent]['sub-areas'][subname] = current_data
    else:
        if not raw_name in data:
            data[raw_name] = current_data
            
with open(OUTPUTS['location_data'], 'w') as f:
    json.dump(data, f, indent = 4)

with open(OUTPUTS['pokemon_data'], 'w') as f:
    json.dump(pokemon_data, f, indent = 4)
