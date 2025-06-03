import asyncio
import pyodide_http
from pyodide import http
import struct
from typing import Optional

pyodide_http.patch_all()
response = await http.pyfetch('https://PurpleYoyo.github.io/LittleEmerald-SaveReader/mons.txt')
all_mons = await (response.string()).splitlines()
response = await http.pyfetch('https://PurpleYoyo.github.io/LittleEmerald-SaveReader/moves.txt')
all_moves = await (response.string()).splitlines()

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

def get_import_data(mon_data: bytes, evs: bool = False) -> Optional[bytes]:
    try:
        pid = struct.unpack('<I', mon_data[0:4])[0]
        tid = struct.unpack('<I', mon_data[4:8])[0]
        mask = 0b11111
    except Exception as e:
        print(f'Error: {e}')
        
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
    exp = decrypted[growth_index * 3 + 1]
    lvl = 100
    nature_byte = (decrypted[misc_index * 3] >> 10) & 0x1F
    natures = [
        "Hardy", "Lonely", "Brave", "Adamant", "Naughty",
        "Bold", "Docile", "Relaxed", "Impish", "Lax",
        "Timid", "Hasty", "Serious", "Jolly", "Naive",
        "Modest", "Mild", "Quiet", "Bashful", "Rash",
        "Calm", "Gentle", "Sassy", "Careful", "Quirky"
    ]
    nature = natures[(nature_byte & 31744) >> 10]

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
        print(all_mons[species_id].strip())
    except IndexError:
        import_data += 'Unknown\n'
    import_data += f'Level: 100\n'
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
            new_data = get_import_data(mon_data, evs)
            if new_data is not None:
                import_data += new_data

    for n in range(8):
        box_start = ((n * 4096) + box_offset) % 57344
        pc_box = save[box_start:box_start + 4096]
        for m in range(30):
            # box pokmeon are 80 bytes
            start = m * 80
            end = start + 80
            mon_data = pc_box[start:end]
            if mon_data[0] != 0 or mon_data[1] != 0:
                print(f"Box {n}, Slot {m}: Non-zero personality, likely valid Pokémon")
                new_data = get_import_data(mon_data, evs)
                if new_data is not None:
                    import_data += new_data

    return import_data
