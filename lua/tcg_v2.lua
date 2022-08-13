pokemon = nil
pokemon_prev = nil
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
            gui.clearGraphics()              
            x = client.borderwidth() + ((client.screenwidth() - (client.borderwidth() * 2)) / 3.4)
            y = client.screenheight() / 6
        elseif pos == "large_card" then            
            gui.clearGraphics()                 
            x = client.borderwidth() + ((client.screenwidth() - (client.borderwidth() * 2)) / 3.4)
            y = client.screenheight() / 6
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

local function set_pokemon()
    id = tostring(memory.read_u8(52267, "System Bus")) -- cc2b
    if id ~= pokemon then
        pokemon_prev = pokemon
        pokemon = id
    end
    if mode == "main" then
        draw_card(pokemon, "main_1")
        draw_card(pokemon_prev, "main_2")
    else
        draw_card(pokemon, mode)
    end
end

event.onmemoryexecute(draw_list_screen, 21950, "list", "System Bus") -- DrawCardListScreenLayout
event.onmemoryexecute(draw_main_screen, 20385, "main", "ROM") -- DrawDuelMainScene.draw
event.onmemoryexecute(set_pokemon, 22990, "set", "System Bus")  -- LoadLoded1CardGFX
event.onmemoryexecute(large_card, 24256, "large_card", "System Bus")  -- LargeCardTileData
event.onmemoryexecute(draw_card_summary, 22413, "summary", "System Bus") -- OpenCardPage

while true do
	clicked = input.getmouse()["Left"]
	if clicked then
		gui.clearGraphics()     
    end
	emu.frameadvance()
end