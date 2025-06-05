import asyncio
import pyodide_http
from pyodide import http
import struct
from typing import Optional

growth_rates = {
    'fast' : 0,
    'medium' : 1,              # Medium Fast
    'medium-slow' : 2,
    'slow' : 3,
    'slow-then-very-fast' : 4, # Erractic
    'fast-then-very-slow' : 5, # Fluctuating
}

new_forms = {
    # the new forms have the same growth rateb as their base species
    'deerling-autumn' : 'deerling',
    'deerling-summer' : 'deerling',
    'deerling-winter' : 'deerling',
    'petilil-fighting' : 'petilil',
    'eevee-fire' : 'eevee',
    'eevee-water' : 'eevee',
    'eevee-electric' : 'eevee',
    'eevee-dark' : 'eevee',
    'eevee-psychic' : 'eevee',
    'eevee-grass' : 'eevee',
    'eevee-ice' : 'eevee',
    'eevee-fairy' : 'eevee',
    'charcadet-psychic' : 'charcadet',
    'charcadet-ghost' : 'charcadet+',
    'ralts-fighting' : 'ralts',
    'snorunt-ghost' : 'snorunt',
    'wurmple-poison' : 'wurmple',
    'nincada-ghost' : 'nincada',
    'exeggcute-dragon' : 'exeggcute',
    'koffing-fairy' : 'koffing',
    'rufflet-psychic' : 'rufflet',
    'goomy-steel' : 'goomy',
    'bergmite-rock' : 'bergmite',
    'froakie-special' : 'froakie',
    'rockruff-special' : 'rockruff',
    'feebas-fairy' : 'feebas',
}

async def get_growth_rate(species_id: int, all_mons: list[str,]) -> Optional[int]:
    species_name = all_mons[species_id].lower().strip().replace(' ', '-')
    if species_name in new_forms:
        species_name = new_forms[species_name]
    url = f'https://pokeapi.co/api/v2/pokemon-species/{species_name}/'
    response = await http.pyfetch(url)
    if response.status == 200:
        data = await response.json()
        growth_rate = data.get('growth_rate', {}).get('name', None)
        # PokeAPI has this as 'slow' but it should be 'medium' (Medium Fast)
        if species_name == 'poltchageist':
            growth_rate = 'medium'
        print(f'Growth Rate: {growth_rate}')
        return growth_rates[growth_rate]
    else:
        return print(f"Failed to fetch data for species {species_name}")

def get_level_from_exp(exp: int, growth_rate: Optional[int]) -> Optional[int]:
    # 0: Fast
    # 1: Medium
    # 2: Medium Slow
    # 3: Slow
    # 4: Erratic
    # 5: Fluctuating

    if growth_rate is None:
        return

    # Clamp experience to max for level 100 (generally known max exp for 100)
    MAX_EXP = 1000000  
    exp = min(exp, MAX_EXP)

    for level in range(1, 101):
        if growth_rate == 0:  # Fast
            required_exp = int(4 * (level ** 3) / 5)
        elif growth_rate == 1:  # Medium
            required_exp = level ** 3
        elif growth_rate == 2:  # Medium Slow
            required_exp = int((6/5) * (level ** 3) - 15 * (level ** 2) + 100 * level - 140)
        elif growth_rate == 3:  # Slow
            required_exp = int(5 * (level ** 3) / 4)
        elif growth_rate == 4:  # Erratic
            if level <= 50:
                required_exp = int(level ** 3 * (100 - level) / 50)
            elif level <= 68:
                required_exp = int(level ** 3 * (150 - level) / 100)
            elif level <= 98:
                required_exp = int(level ** 3 * ((1911 - 10 * level) / 3) / 500)
            else:
                required_exp = int(level ** 3 * (160 - level) / 100)
        elif growth_rate == 5:  # Fluctuating
            if level <= 15:
                required_exp = int(level ** 3 * ((level + 1) / 3 + 24) / 50)
            elif level <= 36:
                required_exp = int(level ** 3 * (level + 14) / 50)
            else:
                required_exp = int(level ** 3 * ((level // 2) + 32) / 50)
        else:
            raise ValueError("Invalid growth rate")

        if exp < required_exp:
            return max(1, level - 1)

    return 100
    
def middle_bits_from_index(number, m, n):
    # Create a mask to extract 'n' bits
    mask = (1 << n) - 1
    # Shift the mask to align it with the desired starting bit and extract those bits
    return (number >> m) & mask

order_formats = [
    [1,2,3,4],            
    [1,2,4,3],            
    [1,3,2,4],            
    [1,3,4,2],            
    [1,4,2,3],            
    [1,4,3,2],            
    [2,1,3,4],
    [2,1,4,3],
    [2,3,1,4],
    [2,3,4,1],
    [2,4,1,3],
    [2,4,3,1],
    [3,1,2,4],
    [3,1,4,2],
    [3,2,1,4],
    [3,2,4,1],
    [3,4,1,2],
    [3,4,2,1],
    [4,1,2,3],
    [4,1,3,2],
    [4,2,1,3],
    [4,2,3,1],
    [4,3,1,2],
    [4,3,2,1],
]

async def get_import_data(mon_data: bytes, all_mons: list[str,], all_moves: list[str,], evs: bool = False) -> Optional[bytes]:
    try:
        pid = struct.unpack('<I', mon_data[0:4])[0]
        tid = struct.unpack('<I', mon_data[4:8])[0]
        mask = 0b11111
    except Exception as e:
        print(f'Error: {e}')

    print(f'EVs: {evs}')
    sub_order = order_formats[pid % 24]
    key = tid ^ pid
    showdown_data = mon_data[32:]
    decrypted = []
    for m in range(12):
        start = m * 4
        block = struct.unpack('<I', showdown_data[start:start + 4])[0]
        decrypted.append(block ^ key)
                              
    growth_index = sub_order.index(1)
    moves_index = sub_order.index(2)
    evs_index = sub_order.index(3)
    misc_index = sub_order.index(4)
    start = growth_index * 3
    block_bytes = b''.join(struct.pack('<I', decrypted[i]) for i in range(start, start + 3))
    species_id_bytes = block_bytes[0:2]  # or the correct offset if known
    species_id = struct.unpack('<H', species_id_bytes)[0] & 0x07FF
    u32_0, u32_1, u32_2 = struct.unpack('<III', block_bytes)
    exp = u32_1 & 0x1FFFFF # mask lower 21 bits
    print(f'EXP: {exp}')
    growth_rate = await get_growth_rate(species_id, all_mons)
    lvl = get_level_from_exp(exp, growth_rate)
    if lvl is None:
        lvl = 100
    personality = struct.unpack('<I', mon_data[:4])[0]
    # hiddenNatureModifier is stores in the upper 5 bits of the 18th byte
    hiddenNatureModifier = (mon_data[18] >> 3) & 0x1F
    natures = [
        "Hardy", "Lonely", "Brave", "Adamant", "Naughty",
        "Bold", "Docile", "Relaxed", "Impish", "Lax",
        "Timid", "Hasty", "Serious", "Jolly", "Naive",
        "Modest", "Mild", "Quiet", "Bashful", "Rash",
        "Calm", "Gentle", "Sassy", "Careful", "Quirky"
    ]
    # personality % 25 is the original nature
    nature = natures[(personality % 25) ^ hiddenNatureModifier]

    int1 = decrypted[evs_index * 3]
    int2 = decrypted[evs_index * 3]
    ev_spread = {}
    ev_spread["HP"] = (int1 & 0xFF)
    ev_spread["Atk"] = ((int1 >> 8) & 0xFF)
    ev_spread["Def"] = ((int1 >> 16) & 0xFF)
    ev_spread["Spe"]= ((int1 >> 24) & 0xFF)
    ev_spread["SpA"] = (int2 & 0xFF)
    ev_spread["SpD"] = ((int2 >> 8) & 0xFF)
    ivs = [decrypted[misc_index * 3 + 1]][0]
    iv_stats = ["HP", "Atk", "Def", "Spe", "SpA", "SpD"]
    spread = {}
    for i, stat in enumerate(iv_stats):
        spread[stat] = middle_bits_from_index(ivs, i * 5, 5)
        
    ability_slot = (decrypted[misc_index * 3 + 2] & 96) >> 5
    try:
        move1 = all_moves[decrypted[moves_index * 3] & 0x07FF]
    except IndexError:
        move1 = 'Unknown'
    try:
        move2 = all_moves[(decrypted[moves_index * 3] >> 16) & 0x07FF]
    except IndexError:
        move2 = 'Unknown'
    try:
        move3 = all_moves[decrypted[moves_index * 3 + 1] & 0x07FF]
    except IndexError:
        move3 = 'Unknown'
    try:
        move4 = all_moves[(decrypted[moves_index * 3 + 1] >> 16) & 0x07FF]
    except IndexError:
        move4 = 'Unknown'
    moves = [move1, move2, move3, move4]
        
    import_data = ''
    try:
        import_data += all_mons[species_id].strip() + "\n"
        print(f'Species: {all_mons[species_id].strip())}')
    except IndexError:
        import_data += 'Unknown\n'
    import_data += f'Level: {lvl}\n'
    import_data += f'{nature} Nature\n'
    if evs:
        import_data += 'EVs: '
        for stat in iv_stats:
            import_data += f'{ev_spread[stat]} {stat} / '
        import_data = import_data[0:-4]
        import_data += '\n'
    
    import_data += 'IVs: '
    for stat in iv_stats:
        import_data += f'{spread[stat]} {stat} / '
    import_data = import_data[0:-4]
    import_data += '\n'
    import_data += f'Ability: {ability_slot}\n'
    for move in moves:
        import_data += f'- {move}\n'
    import_data += '\n'
    return import_data
    
async def read(save_data, evs: bool = False) -> str:
    pyodide_http.patch_all()
    all_mons_response = await http.pyfetch('https://PurpleYoyo.github.io/LittleEmerald-SaveReader/mons.txt')
    all_moves_response = await http.pyfetch('https://PurpleYoyo.github.io/LittleEmerald-SaveReader/moves.txt')
    all_mons = await all_mons_response.string()
    all_moves = await all_moves_response.string()
    all_mons = all_mons.splitlines()
    all_moves = all_moves.splitlines()
    
    save = save_data
    
    save_index_a_offset = 0xffc
    save_block_b_offset = 0x00E000
    save_index_b_offset = save_block_b_offset + save_index_a_offset
    save_index_a = struct.unpack('<H', save[save_index_a_offset:save_index_a_offset + 2])[0]
    save_index_b = struct.unpack('<H', save[save_index_b_offset:save_index_b_offset + 2])[0]

    block_offset = 0
    if save_index_b > save_index_a or save_index_a == 65535:
        block_offset = save_block_b_offset
    save = save[block_offset:block_offset + 57344]

    save_index = save_index_a if save_index_b == 65535 else max([save_index_a, save_index_b])
    save_index = save_index_b if save_index_a == 65535 else max([save_index_a, save_index_b])

    rotation = (save_index % 14) 
    total_offset = rotation * 4096

    trainer_id_offset = 0xa
    new_trainer_id_offset = total_offset + trainer_id_offset
    trainer_id = struct.unpack('<I', save[new_trainer_id_offset:new_trainer_id_offset + 4])[0]
    print(trainer_id & 0xFFFF)

    box_offset = (20480 + 4 + total_offset) % 57344
    party_offset = (total_offset + 4096 + 0x238) % 57344

    import_data = ''
    
    # read the party
    party_data = save[party_offset:party_offset + 600] # 600 bytes
    for n in range(6):
        # party pokemon are 100 bytes
        start = n * 100
        end = start + 100
        mon_data = party_data[start:end]
        if mon_data[0] != 0 or mon_data[1] != 0:
            print(f"Slot {n}: Non-zero personality, likely valid Pokémon")
            new_data = await get_import_data(mon_data, all_mons, all_moves, evs)
            if new_data is not None:
                import_data += new_data

    for n in range(1):
        box_start = n * 2400 + box_offset
        pc_box = save[box_start:box_start + 4096]
        for m in range(30):
            # box pokemon are 80 bytes
            start = m * 80
            end = start + 80
            mon_data = pc_box[start:end]
            if mon_data[0] != 0 or mon_data[1] != 0:
                print(f"Box {n}, Slot {m}: Non-zero personality, likely valid Pokémon")
                new_data = await get_import_data(mon_data, all_mons, all_moves, evs)
                if new_data is not None:
                    import_data += new_data

    return import_data
