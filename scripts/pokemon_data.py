import json
import re

from .utils import ALL_POKEMON, ALL_TUTORS, ALL_TMHMS
from .utils import SPECIAL_NAMES
from .utils import format_sprite, format_type, get_learnset

with open('scripts/config.json', 'r', encoding = 'utf-8') as file:
    CONFIG = json.load(file)

INPUTS = CONFIG['inputs']
OUTPUTS = CONFIG['outputs']

with open('scripts/absolute_path.txt', 'r') as file:
    ABSOLUTE_PATH = file.read()
    
pokemon_data = []
for path in INPUTS['pokemon_data']:
    with open(f'{ABSOLUTE_PATH}{path}', 'r', encoding = 'utf-8') as file:
        pokemon_data.extend(file.readlines())
with open('scripts/pokemon_templates.txt', 'r', encoding = 'utf-8') as file:
    pokemon_data.extend(file.readlines())

learnset_data = []
for path in INPUTS['learnset_data']:
    with open(f'{ABSOLUTE_PATH}{path}', 'r', encoding = 'utf-8') as file:
        learnset_data.extend(file.readlines())
        
data = {}
for pok in ALL_POKEMON:
    IS_MEGA = True if '_MEGA' in pok else False
        
    current_data = {
        'learnset' : {
            'level'     : [],
            'tm'        : [],
            'tutor'     : [],
            'egg'       : [],
        }
    }
    
    entry: list[str] = re.findall(r'\[' + pok + r'\].+?    \},', '\n'.join(pokemon_data), re.S)
    
    if not entry:
        print(f'Unable to find entry for {pok}.')
        continue
        
    entry = entry[0].split('\n\n')
    for line in entry:
        line: str
        
        line = line.strip()
        
        if line.startswith(f'.speciesName'):
            name = line[line.find('= ') + 2:-1].replace('_("', '').replace('")', '')
            
            if 'ALOLA' in pok:
                name += '-Alola'
            if 'GALAR' in pok:
                name += '-Galar'
            if 'HISUI' in pok:
                name += '-Hisui'
            if 'PALDEA' in pok:
                name += '-Paldea'
            
            if pok in SPECIAL_NAMES:
                name = SPECIAL_NAMES[pok]
            
            current_data['name'] = name
        
        if line.startswith(f'.categoryName'):
            current_data['category'] = line[line.find('= ') + 2:-1].replace('_("', '').replace('")', '')
        
        if line.startswith(f'.frontPic ='):
            sprite = line[line.find('= ') + 2:-1].replace('gMonFrontPic_', '')
            
            if '-SPRING' in pok:
                current_data['sprite'] = 'deerling-spring'
            elif '-AUTUMN' in pok:
                current_data['sprite'] = 'deerling-autumn'
            elif '-WINTER' in pok:
                current_data['sprite'] = 'deerling-winter'
            elif '-SUMMER' in pok:
                current_data['sprite'] = 'deerling-summer'
            else:    
                current_data['sprite'] = format_sprite(sprite)
            
        base_stats = {
            'hp'                : 0,
            'attack'            : 0,
            'defense'           : 0,
            'special-attack'    : 0,
            'special-defense'   : 0,
            'speed'             : 0,
        }
        for stat in base_stats:
            stat_name = stat.replace('-', ' ').title().replace(' ',  '').replace('Special', 'Sp').replace('Hp', 'HP')
            if line.startswith(f'.base{stat_name}'):
                if not 'base_stats' in current_data:
                    current_data['base_stats'] = {}
                    
                value = line[line.find('= ') + 2:-1]
                if 'P_UPDATED_STATS' in value:
                    value = value[value.find('? ') + 2:value.find(' :')]
                    
                if 'CORSOLA_HP - 5' in value:
                    value = '60'
                if 'CORSOLA_DEFENSES + 5' in value:
                    value = '100'
                if 'FARFETCHD_ATTACK + 5' in value:
                    value = '195'
                
                current_data['base_stats'][stat] = int(value)
        
        if line.startswith(f'.abilities') and not 'abilities' in current_data:
            abilities = line[line.find('= ') + 2:-1].replace('{ ', '').replace(' }', '').split(', ')
            
            normal_abilities = [
                abilities[0]
            ]
            hidden_ability = ''
            
            if not abilities[1] == 'ABILITY_NONE':
                normal_abilities.append(abilities[1])
            
            if not abilities[2] == 'ABILITY_NONE':
                hidden_ability = abilities[2]
            
            if '_MEGA' in pok:
                current_data['ability'] = abilities[0]
            else:
                current_data['abilities'] = {
                    'normal_abilities'  : normal_abilities,
                    'hidden_ability'    : hidden_ability,
                }
        
        if line.startswith(f'.types') and not 'types' in current_data:
            if 'MON_TYPES(' in line:
                types = line[line.find('= ') + 2:-1].replace('MON_TYPES(', '').replace(')', '').split(', ')
            else:
                types = line[line.find('= ') + 2:-1].replace('{ ', '').replace(' }', '').split(', ')
                
            if pok == 'SPECIES_CLEFFA':
                types = ['TYPE_FAIRY']
            if pok == 'SPECIES_IGGLYBUFF':
                types = ['TYPE_NORMAL', 'TYPE_FAIRY']
            if pok == 'SPECIES_TOGEPI':
                types = ['TYPE_FAIRY']
            if pok == 'SPECIES_TOGEPI_MEGA':
                types = ['TYPE_FAIRY', 'TYPE_FLYING']
            if pok == 'SPECIES_RALTS':
                types = ['TYPE_PSYCHIC', 'TYPE_FAIRY']
            if pok == 'SPECIES_COTTONEE':
                types = ['TYPE_GRASS', 'TYPE_FAIRY']
                
            current_data['types'] = [
                format_type(types[0])
            ]
            
            if len(types) == 2:
                current_data['types'].append(format_type(types[1]))
                
        if line.startswith(f'.levelUpLearnset'):
            learnset = line[line.find('= ') + 2:-1]
            current_data['learnset']['level'].extend(get_learnset(learnset_data, learnset))
        
        if line.startswith(f'.teachableLearnset'):
            learnset = line[line.find('= ') + 2:-1]
            tm, tutor = get_learnset(learnset_data, learnset)
            current_data['learnset']['tm'].extend(tm)
            current_data['learnset']['tutor'].extend(tutor)
        
        if line.startswith(f'.eggMoveLearnset'):
            learnset = line[line.find('= ') + 2:-1]
            current_data['learnset']['egg'].extend(get_learnset(learnset_data, learnset))
        
        if not IS_MEGA:
            level_moves = [m['move'] for m in current_data['learnset']['level']]
            
            current_data['learnset']['egg'] = [
                move for move in current_data['learnset']['egg']
                if not move in level_moves
            ]
            
            current_data['learnset']['tm'] = [
                move for move in level_moves
                if move in ALL_TMHMS
                and not move in current_data['learnset']['tm']
            ]
            
            current_data['learnset']['tutor'] = [
                move for move in level_moves
                if move in ALL_TUTORS
                and not move in current_data['learnset']['tutor']
            ]
            
            for key in ['tm', 'tutor']:
                current_data['learnset'][key] = list(set(current_data['learnset'][key]))
                    
    if IS_MEGA:
        base_pok = pok[:pok.find('_MEGA')]
        mega_name = pok.replace(base_pok, '').replace('_', '-').lower()[1:]
        
        if not 'mega_evolutions' in data[base_pok]:
            data[base_pok]['mega_evolutions'] = {}
            
        data[base_pok]['mega_evolutions'][mega_name] = current_data
    else:
        data[pok] = current_data
            
with open(OUTPUTS['pokemon_data'], 'w') as file:
    json.dump(data, file, indent = 4)