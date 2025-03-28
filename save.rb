class Save:
	def self.read(save_data, static_level=100, game="inc_em", manual_offset=0, invert_save_index=false, evs_on=false)
		all_mons = File.read("mons.txt").split("\n")
		all_moves = File.read("moves.txt").split("\n")
		abils = JSON.parse(File.read('./Reference_Files/save_constants/rr_abils.json'))

		save_index_a_offset = 0xffc
		save_block_b_offset = 0x00E000
		trainer_id_offset = 0xa
		save_index_b_offset = save_block_b_offset + save_index_a_offset
		# if save_index odd should be at save_block B otherwise A
		save = save_data
		save_index_a = save[save_index_a_offset..save_index_a_offset + 1].unpack("S")[0]
		save_index_b = save[save_index_b_offset..save_index_b_offset + 1].unpack("S")[0]
		block_offset = 0
		if save_index_b > save_index_a || save_index_a == 65535 || invert_save_index
			block_offset = save_block_b_offset
		end
		# block_offset = save_block_b_offset
		save = save[block_offset..block_offset + 57343]
		save_index = [save_index_a, save_index_b].max
		save_index = save_index_a if save_index_b == 65535
		save_index = save_index_b if save_index_a == 65535
		# save_index = save_index_a
		save_index = save_index - manual_offset
		rotation = (save_index % 14) 
		total_offset = rotation * 4096

		new_trainer_id_offset = total_offset + trainer_id_offset
		trainer_id = save[new_trainer_id_offset..new_trainer_id_offset + 3].unpack("V")[0]
		box_offset = (20480 + 4 + total_offset) % 57344
		party_offset = (total_offset + 4096 + 0x238) % 57344

		box_data = ""
		# box_data = save[box_offset..box_offset + 33599]
		party_data = save[party_offset..party_offset + 599]
		box_data += party_data
		(0..8).each do |n|
			box_start = ((n * 4096) + box_offset) % 57344
			pc_box = save[box_start..box_start + 4095]
			box_data += pc_box
		end

		trainer_string = "\x02\x02"
		mon_count = 0
		box_suboffset = 0
		import_data = ""
		last_found_at = 0
		n = 0
		while n < box_data.length
			data = box_data[n..n+1]
			if data != trainer_string
				n += 2
				next
			else
				mon_data = box_data[n-18..n+61]
				begin
					pid = mon_data[0..3].unpack("V")[0]
					tid = mon_data[4..7].unpack("V")[0]
					mask = 0b11111
					modded_nature = (mon_data[8..9].unpack("vv")[0] >> 13) && mask
				rescue
					# binding.pry
				end
				sub_order = order_formats[pid % 24]
				key = tid ^ pid
				showdown_data = mon_data[32..-1]
				#decrypt with key
				decrypted = []
				(0..11).each do |m|
					start = m * 4
					block = showdown_data[start..start + 3].unpack("V")[0]
					decrypted << (block ^ key)
				end
				growth_index = sub_order.index(1)
				moves_index = sub_order.index(2)
				evs_index = sub_order.index(3)
				misc_index = sub_order.index(4)
				species_id = [decrypted[growth_index * 3]].pack('V').unpack('vv')[0] & 0x07FF
				if species_id > 899
					species_id += 7
				end
				exp = decrypted[growth_index * 3 + 1]
				lvl = static_level
				nature_byte = [decrypted[misc_index * 3]].pack('V').unpack('vv')[1]
				nature = RomInfo.natures[(nature_byte & 31744) >> 10]
				
				if game == "em_imp" || game == "scram_em" || game == "runandbun"
					nature = RomInfo.natures[pid % 25]

					if modded_nature <= 26
						nature = RomInfo.natures[modded_nature]
					end
				end

				
				int1 = decrypted[evs_index * 3]
				int2 = decrypted[evs_index * 3 + 1]

				ev_spread = {}



				ev_spread["HP"] = (int1 & 0xFF)
				ev_spread["Atk"] = ((int1 >> 8) & 0xFF)
				ev_spread["Def"] = ((int1 >> 16) & 0xFF)
				ev_spread["Spe"]= ((int1 >> 24) & 0xFF)
				ev_spread["SpA"] = (int2 & 0xFF)
				ev_spread["SpD"] = ((int2 >> 8) & 0xFF)


				
				move1 = all_moves[[decrypted[moves_index * 3]].pack('V').unpack('vv')[0] & 0x07FF]
				move2 = all_moves[[decrypted[moves_index * 3]].pack('V').unpack('vv')[1] & 0x07FF]
				move3 = all_moves[[decrypted[moves_index * 3 + 1]].pack('V').unpack('vv')[0] & 0x07FF]
				move4 = all_moves[[decrypted[moves_index * 3 + 1]].pack('V').unpack('vv')[1] & 0x07FF]

				ivs = [decrypted[misc_index * 3 + 1]][0]
				iv_stats = ["HP", "Atk", "Def", "Spe", "SpA", "SpD"]
				spread = {}

				iv_stats.each_with_index do |stat, i|
					spread[stat] = middle_bits_from_index(ivs, i * 5, 5)
				end
				ability_slot = (decrypted[misc_index * 3 + 2] & 96) >> 5


				# binding.pry

				# p species_id

				if game == "em_imp" || game == "runandbun"
					begin
						
						# p all_mons[species_id]
						# p decrypted[misc_index].to_s(2).rjust(32, '0')
						# p decrypted[misc_index + 1].to_s(2).rjust(32, '0')
						# p decrypted[misc_index * 3 + 2].to_s(2).rjust(32, '0')

						ability_slot = decrypted[misc_index * 3 + 2].to_s(2).rjust(32, '0')[1..2].to_i(2)
  

						# ability_slot = ((decrypted[misc_index + 2] & 0xFFFFFFFF) >> 29) & 0b11


						if game == "em_imp"

							if !abils[all_mons[species_id]]
								all_mons[species_id] = all_mons[species_id].gsub(" ", "-")
							end
							if abils[all_mons[species_id]]
								ability_slot = abils[all_mons[species_id]][ability_slot]
							end
						else
							ability_slot = rnb_abils[species_id].split(",")[ability_slot]
						end

						# p ability_slot





					rescue
						p "species_id unknown: #{species_id}"
					end



				end


				moves = [move1, move2, move3, move4]

				if moves.index(nil) || moves.reject { |str| str == "None" }.uniq.length != moves.reject { |str| str == "None" }.length
					n += 2
					next
				end
				
				set = {}

				is_party = ""
				if n <= 600 && game != "scram_em" && game != "em_imp"
					is_party = " |Party|"
				end
				
				begin

					import_data += all_mons[species_id].strip + is_party + "\n"
					last_found_at = n
				rescue
					p "Error: Species ID #{species_id}"
					import_data += "Unknown\n"
					# binding.pry
				end
				import_data += "Level: #{lvl}\n"
				import_data += "#{nature} Nature\n"

				if evs_on
					import_data += "EVs: "
					iv_stats.each do |stat|
						import_data += "#{ev_spread[stat]} #{stat} / "
					end
					import_data = import_data[0..-4]
					import_data += "\n"
				end
				

				import_data += "IVs: "
				iv_stats.each do |stat|
					import_data += "#{spread[stat]} #{stat} / "
				end
				import_data = import_data[0..-4]
				import_data += "\n"




				
				import_data += "Ability: #{ability_slot}\n"
				moves.each do |m|
					import_data += "- #{m}\n"
				end
				import_data += "\n"
				mon_count += 1
				n += 44
			end
		end
		debug_info = {save_index_a: save_index_a, save_index_b: save_index_b }
		

		if import_data == "" and game == "em_imp" and !invert_save_index
			p ("retrying with other save index #{manual_offset}")
			return read(save_data, 100, game, 0, true, evs_on)	
		end


		if import_data == "" and manual_offset != 1 && game != "em_imp"
			 p ("retrying with one more rotation #{manual_offset}")
			 return read(save_data, static_level=100, game, manual_offset=1)	 
		else
			return {import_data: import_data, debug_info: debug_info}
		end

	end
