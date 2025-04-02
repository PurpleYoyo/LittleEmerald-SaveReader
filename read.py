import asyncio
import pyodide_http
from pyodide import http
import struct

async def read(save_data, level: int = 100, evs: bool = False) -> str:
    pyodide_http.patch_all()
    
    response = await http.pyfetch('https://PurpleYoyo.github.io/LittleEmerald-SaveReader/mons.txt')
    mons = await response.string()
    response = await http.pyfetch('https://PurpleYoyo.github.io/LittleEmerald-SaveReader/moves.txt')
    moves = await response.string()

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

    box_offset = (20480 + 4 + total_offset) % 57344
    party_offset = (total_offset + 4096 + 0x238) % 57344
    party_data = save[party_offset:party_offset + 600]
    
    box_data = party_data
    for n in range(9):
        box_start = ((n * 4096) + box_offset) % 57344
        pc_box = save[box_start:box_start + 4096]
        box_data += pc_box
        
    trainer_string = "\x02\x02"
    mon_count = 0
    box_suboffset = 0
    import_data = ""
    last_found_at = 0
    n = 0
    while n < len(box_data):
        data = box_data[n:n + 2]
        if data != trainer_string:
            n += 2
            next
        else:
            try:
                mon_data = box_data[n - 18:n + 62]
                pid = struct.unpack('<I', mon_data[0:4])[0]
                tid = struct.unpack('<I', mon_data[4:8])[0]
                mask = 0b11111
                modded_nature = (struct.unpack('<H', mon_data[8:10])[0] >> 13) & mask
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
            species_id = struct.unpack("<H", struct.pack("<I", decrypted[growth_index * 3]))[0] & 0x07FF
            if species_id > 899:
                species_id += 7
            exp = decrypted[growth_index * 3 + 1]
            lvl = level
            nature_byte = struct.unpack("<H", struct.pack("<I", decrypted[misc_index * 3]))[1]
            nature = 'Hardy' #RomInfo.natures[(nature_byte & 31744) >> 10]

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

            move1 = all_moves[struct.unpack("<H", struct.pack("<I", decrypted[moves_index * 3]))[0] & 0x07FF]
            move2 = all_moves[struct.unpack("<H", struct.pack("<I", decrypted[moves_index * 3]))[1] & 0x07FF]
            move3 = all_moves[struct.unpack("<H", struct.pack("<I", decrypted[moves_index * 3 + 1]))[0] & 0x07FF]
            move4 = all_moves[struct.unpack("<H", struct.pack("<I", decrypted[moves_index * 3 + 1]))[1] & 0x07FF]
            moves = [move1, move2, move3, move4]

            if None in moves or len(list(filter(lambda x: x != "None", moves))) != len(set(filter(lambda x: x != "None", moves))):
                n += 2
                continue
                
            set = {}
            try:
                import_data += all_mons[species_id].strip + is_party + "\n"
                last_found_at = n
            except Exception as e:
                print(f'Error: {e}')

            import_data += f'Level: {level}\n'
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
            mon_count += 1
            n += 44
    
    debug_info = {save_index_a: save_index_a, save_index_b: save_index_b }
    return import_data
