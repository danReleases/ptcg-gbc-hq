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
		fname = "../"..mapfiles[id]
		if pos == "list" then
            x = client.screenwidth() - client.borderwidth() - width
            y = client.screenheight() - height			
        elseif pos == "main1" then            
            x = client.screenwidth() - client.borderwidth() - width
            y = client.screenheight() / 18
        elseif pos == "main2" then            
            x = client.borderwidth()
            y = client.screenheight() / 3.7
        elseif pos == "summary" then            
            x = client.borderwidth() + ((client.screenwidth() - (client.borderwidth() * 2)) / 3.5)
            y = client.screenheight() / 3.5
        end
        gui.drawImage(fname, x, y, width, height)
	end
end

local function draw_list_screen()
	mode = "list"
end

local function draw_main_screen()
    mode = "main"
end

local function draw_card_summary()
    mode = "summary"
end

event.onmemoryexecute(draw_list_screen, 21950, "list", "System Bus")
event.onmemoryexecute(draw_main_screen, 20385, "main", "ROM")

while true do
	clicked = input.getmouse()["Left"]
	if clicked then
		gui.clearGraphics()
    else
        id = tostring(memory.read_u8(52267, "System Bus")) -- cc2b
        if id ~= pokemon then
            pokemon_prev = pokemon
            pokemon = id
            if mode ~= nil then
                if mode == "main" then
                    draw_card(pokemon, "main1")
                    draw_card(pokemon_prev, "main2")
                else
                    draw_card(pokemon, mode)
                end
            end
        end        
    end
	emu.frameadvance()
end