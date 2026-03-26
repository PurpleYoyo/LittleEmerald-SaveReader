import json

from .utils import TARGET_MAPPING, MOVE_EFFECT_MAPPING
from .utils import build_stat_effect

with open('scripts/config.json', 'r', encoding = 'utf-8') as file:
    CONFIG = json.load(file)

INPUTS = CONFIG['inputs']
OUTPUTS = CONFIG['outputs']

with open('scripts/absolute_path.txt', 'r') as file:
    ABSOLUTE_PATH = file.read()
    
with open(f"{ABSOLUTE_PATH}{INPUTS['move_data']}", 'r') as file:
    moves_info = file.readlines()

with open(OUTPUTS['pokemon_data'], 'r') as file:
    pokemon_data = json.load(file)
    
print_max_moves = False
print_description_references = False

current_move = None
data = {}
for i, line in enumerate(moves_info):
    if line.strip().startswith('[MOVE_'):
        current_move = line.replace('[', '').replace('] =', '').strip()
    
    if not current_move or current_move == 'MOVE_NONE' or '_MAX_' in current_move:
        if current_move and '_MAX_' in current_move:
            if print_max_moves:
                print(f'Max Move: {current_move}')
            
        continue
    
    if line.strip().startswith('[MOVE_'):
        data[current_move] = {}
        
    if line.strip().startswith('.name'):
        data[current_move]['name'] = line[line.find('= ') + 2:-1].replace('COMPOUND_STRING("', '').replace('"),', '')

    if line.strip().startswith('.power'):
        base_power = line.strip()[line.strip().find('= ') + 2:-1]
        if 'B_UPDATED_MOVE_DATA' in base_power:
            base_power = base_power[base_power.find('? ') + 2:base_power.find(' :')]
        
        data[current_move]['base_power'] = base_power
    
    if line.strip().startswith('.accuracy'):
        accuracy = line.strip()[line.strip().find('= ') + 2:-1]
        if 'B_UPDATED_MOVE_DATA' in accuracy:
            accuracy = accuracy[accuracy.find('? ') + 2:accuracy.find(' :')]
        
        data[current_move]['accuracy'] = accuracy
    
    if line.strip().startswith('.pp'):
        pp = line.strip()[line.strip().find('= ') + 2:-1]
        if 'B_UPDATED_MOVE_DATA' in pp:
            pp = pp[pp.find('? ') + 2:pp.find(' :')]
        
        data[current_move]['pp'] = pp
    
    if line.strip().startswith('.type'):
        move_type = line.strip()[line.strip().find('= ') + 2:-1].replace('TYPE_', '').lower().title()
        if 'P_UPDATED_MOVE_DATA' in move_type:
            move_type = move_type[move_type.find('? ') + 2:move_type.find(' :')]
                    
        data[current_move]['type'] = move_type
    
    if line.strip().startswith('.target'):
        data[current_move]['target'] = TARGET_MAPPING.get(line.strip()[line.strip().find('= ') + 2:-1], 'MISSING')
    
    if line.strip().startswith('.priority'):
        priority = line.strip()[line.strip().find('= ') + 2:-1]
        if 'B_UPDATED_MOVE_DATA' in priority:
            priority = priority[priority.find('? ') + 2:priority.find(' :')]
        
        data[current_move]['priority'] = priority
    
    if line.strip().startswith('.makesContact'):
        data[current_move]['contact'] = True
     
    if line.strip().startswith('.category'):
        category = line.strip()[line.strip().find('= ') + 2:-1].replace('DAMAGE_CATEGORY_', '').lower().title()
        if 'B_UPDATED_MOVE_DATA' in category.upper():
            category = category[category.find('? ') + 2:category.find(' :')]
        
        data[current_move]['category'] = category
    
    if line.strip().startswith('.criticalHitStage'):
        data[current_move]['highCritRate'] = True
        
    if line.strip().startswith('.pulseMove'):
        data[current_move]['pulseMove'] = True
    
    if line.strip().startswith('.bitingMove'):
        data[current_move]['bitingMove'] = True
        
    if line.strip().startswith('.ballisticMove'):
        data[current_move]['ballMove'] = True
    
    if line.strip().startswith('.slicingMove'):
        data[current_move]['slicingMove'] = True
    
    if line.strip().startswith('.danceMove'):
        data[current_move]['danceMove'] = True
        
    if line.strip().startswith('.soundMove'):
        data[current_move]['soundMove'] = True
    
    if line.strip().startswith('.healingMove'):
        data[current_move]['healingMove'] = True
    
    if line.strip().startswith('.punchingMove'):
        data[current_move]['punchingMove'] = True
    
    if line.strip().startswith('.windMove'):
        data[current_move]['windMove'] = True
    
    if line.strip().startswith('.powderMove'):
        data[current_move]['powderMove'] = True
    
    if line.strip().startswith('.ignoresProtect'):
        data[current_move]['ignoresProtect'] = True

    if line.strip().startswith('.description'):
        starting_point = i
        
        if '= s' in line.strip():
            reference = line.strip()[line.strip().find('= ') + 2:-1]
            
            if print_description_references:
                if not 'sNullDescription' in line.strip():
                    print(f'Description reference for {current_move}: {reference}.')
            
            for x, l in enumerate(moves_info):
                if l.startswith('static') and reference in l:
                    starting_point = x
                    
        description = []
        n = 1
        while not moves_info[starting_point + n].strip().startswith('.') and not moves_info[starting_point + n].strip() == '':
            description.append(moves_info[starting_point + n].strip().replace('\\n"', '').replace('"','').replace('),', '').replace(');', ''))
            n += 1
        move_description = ' '.join(description)
        if '#if B_UPDATED_MOVE_DATA' in move_description:
            if '#endif' in move_description:
                move_description = move_description.replace('>', '>=')
                move_description = move_description[:move_description.find('#if B_UPDATED_MOVE_DATA ')] + move_description[move_description.find('#if B_UPDATED_MOVE_DATA ') + 32:move_description.find(' #else')]
            else:
                move_description = move_description[:move_description.find('#if B_UPDATED_MOVE_DATA ')]
            
        move_description = move_description.replace('BINDING_TURNS', '4 or 5')
        
        data[current_move]['description'] = move_description
    
    if line.strip().startswith('.additionalEffects'):
        n = 0
        while not moves_info[i + n].strip().startswith('}),'):
            subline = moves_info[i + n].strip()
            
            if subline.endswith('{'):
                effect = None
                chance = None
                effect_self = False
                
                m = n
                while not moves_info[i + m].strip().startswith('},'):
                    inner = moves_info[i + m].strip()
            
                    if inner.startswith('.chance'):
                        chance = inner[inner.find('= ') + 2:-1] + '%'
                        if 'B_UPDATED_MOVE_DATA' in chance:
                            chance = chance[chance.find('? ') + 2:chance.find(' :')]

                    if inner.startswith('.moveEffect'):
                        effect = inner[inner.find('= ') + 2:-1]
                        if 'B_UPDATED_MOVE_DATA' in effect:
                            effect = effect[effect.find('? ') + 2:effect.find(' :')]

                    if inner.startswith('.self'):
                        effect_self = True
                            
                    m += 1
            
                if effect:
                    if effect in MOVE_EFFECT_MAPPING:
                        effect = MOVE_EFFECT_MAPPING[effect]
                    elif 'MINUS' in effect or 'PLUS' in effect:
                        effect = build_stat_effect(effect)
                    
                    if not 'additionalEffects' in data[current_move]:
                        data[current_move]['additionalEffects'] = []
                
                    effect_entry = {
                        'effect' : effect,
                        'chance' : chance,
                    }
                    
                    if effect_self:
                        effect_entry['self'] = True
                    
                    data[current_move]['additionalEffects'].append(effect_entry)
            
            n += 1
    
    if not 'learned_by' in data[current_move]:
        data[current_move]['learned_by'] = {
            'level'     : [],
            'tm'        : [],
            'tutor'     : [],
            'egg'       : [],
        }
    
        for pok in pokemon_data:
            moves: list[str] = [move['move'] for move in pokemon_data[pok]['learnset']['level']]
            if current_move in moves:
                if not pok in data[current_move]['learned_by']['level']:
                    levels = [move['level'] for move in pokemon_data[pok]['learnset']['level']]
                    data[current_move]['learned_by']['level'].append({
                        'species'   : pok,
                        'level'     : levels[moves.index(current_move)],
                    })

            if current_move in pokemon_data[pok]['learnset']['tm']:
                if not pok in data[current_move]['learned_by']['tm']:
                    data[current_move]['learned_by']['tm'].append(pok)

            if current_move in pokemon_data[pok]['learnset']['tutor']:
                if not pok in data[current_move]['learned_by']['tutor']:
                    data[current_move]['learned_by']['tutor'].append(pok)

            if current_move in pokemon_data[pok]['learnset']['egg']:
                if not pok in data[current_move]['learned_by']['egg']:
                    data[current_move]['learned_by']['egg'].append(pok)
        
with open(OUTPUTS['move_data'], 'w') as file:
    json.dump(data, file, indent = 4)