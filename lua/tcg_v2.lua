duel_pokemons = {nil, nil}
other_pokemon = nil

mode = nil
mapfiles = require("sets/custom")
gui.use_surface("client")

local function draw_card(id, pos)
    width = 880/2
	height = 660/2
    x = 0
    y = 0
	if mapfiles[id] ~= nil then
		fname = ""..mapfiles[id]
		if pos == "list" then
            x = client.screenwidth() - client.borderwidth() - width
            y = client.screenheight() - height			
        elseif pos == "main_1" then            
            x = client.screenwidth() - client.borderwidth() - width
            y = client.screenheight() / 18
        elseif pos == "main_2" then            
            x = client.borderwidth()
            y = client.screenheight() / 3.7
        elseif pos == "summary" then       
            x = client.borderwidth() + ((client.screenwidth() - (client.borderwidth() * 2)) / 3.4)
            y = client.screenheight() / 4.6
        elseif pos == "large_card" then         
            x = client.borderwidth() + ((client.screenwidth() - (client.borderwidth() * 2)) / 3.4)
            y = client.screenheight() / 6
        elseif pos == "in_pa_1" then            
            x = client.borderwidth() + ((client.screenwidth() - (client.borderwidth() * 2)) / 3.4)
            y = client.screenheight() / 9
        elseif pos == "in_pa_2" then                        
            x = client.borderwidth() + ((client.screenwidth() - (client.borderwidth() * 2)) / 3.4)
            y = client.screenheight() / 2
        elseif pos == "your_pa" then              
            x = client.borderwidth() + ((client.screenwidth() - (client.borderwidth() * 2)) / 3.4)
            y = client.screenheight() / 9
        elseif pos == "opp_pa" then             
            x = client.borderwidth() + ((client.screenwidth() - (client.borderwidth() * 2)) / 3.4)
            y = client.screenheight() / 3.6
        end
        gui.drawImage(fname, x, y, width, height)
	end
end

local function draw_list_screen()
    -- draw cards screen
	mode = "list"
end

local function draw_main_screen()
    -- main duel screen (2 Pokemon)
    mode = "main"
end

local function draw_card_summary()
    -- card when looking at deck
    mode = "summary"
end

local function large_card()
    -- card shown when it's drawn
    mode = "large_card"
end

local function in_play_area()
    -- cards shown in the play area (2 cards)
    mode = "in_pa"
    gui.clearGraphics()        
    draw_card(duel_pokemons[2], "in_pa_1")
    draw_card(duel_pokemons[1], "in_pa_2")
end

local function your_play_area()
    -- card in your play area (1 card)
    mode = "your_pa"
    gui.clearGraphics()        
    draw_card(duel_pokemons[1], mode)
end

local function opponent_play_area()
    -- card in opponent's play area (1 card)
    mode = "opp_pa"
    gui.clearGraphics()        
    draw_card(duel_pokemons[2], mode)
end

local function set_pokemon()
    id = tostring(memory.read_u8(52267, "System Bus")) -- cc2b
    gui.clearGraphics()       
    if mode ~= "in_pa" and mode ~= "your_pa" and mode ~= "opp_pa" then 
        if mode == "main" then
            if id ~= duel_pokemons[2] then
                duel_pokemons[1] = duel_pokemons[2]
                duel_pokemons[2] = id
            end
            draw_card(duel_pokemons[2], "main_1")
            draw_card(duel_pokemons[1], "main_2")
        else
            if id ~= other_pokemon then
                other_pokemon = id
            end
            draw_card(other_pokemon, mode)
        end
    end
end

local function clear_all()
    gui.clearGraphics()
end

local function offset_rom(address, rom_bank)
    if rom_bank <= 0 then
        return address
    end
    -- address = rom_bank * rom_bank_size + system_bus_address - banked_rom_start_in_system_bus
    rom_bank_size = 16384 -- 0x4000
    offset = rom_bank * rom_bank_size
    banked_rom_start_in_system_bus = 16384 -- 0x4000 for Pokemon TCG GBC
    return offset + address - banked_rom_start_in_system_bus 
end

event.onmemoryexecute(draw_list_screen, 22002, "list", "ROM") -- DrawCardList
event.onmemoryexecute(draw_main_screen, 20385, "main", "ROM") -- DrawDuelMainScene.draw
event.onmemoryexecute(set_pokemon, 22990, "set", "System Bus")  -- LoadLoded1CardGFX
event.onmemoryexecute(large_card, 24256, "large_card", "System Bus")  -- LargeCardTileData
event.onmemoryexecute(draw_card_summary, 22413, "summary", "System Bus") -- OpenCardPage

offset_in_play_area = offset_rom(17103, 2) -- 0x42CF : ROM2
offset_your_play_area = offset_rom(16466, 2) -- 0x4052 : ROM2
offset_opp_play_area = offset_rom(16639, 2) -- 0x40FF : ROM2

event.onmemoryexecute(in_play_area, offset_in_play_area, "in_pa", "ROM") -- In Play Area
event.onmemoryexecute(your_play_area, offset_your_play_area, "your_pa", "ROM") -- Your (Player) Play Area
event.onmemoryexecute(opponent_play_area, offset_opp_play_area, "opp_pa", "ROM") -- Opponent Play Area

-- clear screen
offset_glossary = offset_rom(17901, 6) -- 0x45ED : ROM6

event.onmemoryexecute(clear_all, 25881, "poke_power", "ROM") -- DisplayUsePokemonPowerScreen
event.onmemoryexecute(clear_all, 24651, "poke_list", "ROM") -- DisplayPlayAreaScreen
event.onmemoryexecute(clear_all, offset_glossary, "glossary", "ROM") -- OpenGlossaryScreen

while true do
	clicked = input.getmouse()["Left"]
	if clicked then
		gui.clearGraphics()     
    end
	emu.frameadvance()
end