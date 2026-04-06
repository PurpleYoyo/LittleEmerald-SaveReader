import json

with open('scripts/config.json', 'r', encoding = 'utf-8') as file:
    CONFIG = json.load(file)

INPUTS = CONFIG['inputs']
OUTPUTS = CONFIG['outputs']

with open('scripts/absolute_path.txt', 'r') as file:
    ABSOLUTE_PATH = file.read()
    
with open(f"{ABSOLUTE_PATH}{INPUTS['ability_data']}", 'r', encoding = 'utf-8') as file:
    ability_data = file.readlines()

with open(OUTPUTS['pokemon_data'], 'r') as file:
    pokemon_data = json.load(file)

current_ability = None
data = {}
for i, line in enumerate(ability_data):
    if line.strip().startswith('[ABILITY_'):
        current_ability = line.replace('[', '').replace('] =', '').strip()
        
        if current_ability and current_ability != 'ABILITY_NONE':
            data[current_ability] = {
                'detailed_description' : ''
            }
    
    if not current_ability or current_ability == 'ABILITY_NONE':
        continue
    
    if line.strip().startswith('.name'):
        data[current_ability]['name'] = line[line.find('= ') + 2:-1].replace('_("', '').replace('"),', '')

    if line.strip().startswith('.description'):
        data[current_ability]['description'] = line[line.find('= ') + 2:-1].replace('COMPOUND_STRING("', '').replace('"),', '')

for ability in data:
    normal_abilities = []
    hidden_abilities = []
    
    for pok in pokemon_data:
        if ability in pokemon_data[pok]['abilities']['normal_abilities']:
            normal_abilities.append(pok)
            
            if 'mega_evolutions' in pokemon_data[pok]:
                for mega in pokemon_data[pok]['mega_evolutions']:
                    formatted_mega = str(mega).replace('-', '_').upper()
                    mega_ability = pokemon_data[pok]['mega_evolutions'][mega]['ability']
                    
                    if ability == mega_ability:
                        normal_abilities.append(f'{pok}_{formatted_mega}')
        
        if ability == pokemon_data[pok]['abilities']['hidden_ability']:
            hidden_abilities.append(pok)
        
        data[ability]['pokemon_with'] = {
            'normal' : normal_abilities,
            'hidden' : hidden_abilities,
        }
            
with open(OUTPUTS['ability_data'], 'w') as file:
    json.dump(data, file, indent = 4)