prev_pokemon = 0
mapfiles = require("sets/base1")
additional = require("sets/base4")
for k,v in pairs(additional) do 
	mapfiles[k] = v 
end

gui.use_surface("client")
while true do
    wx = client.screenwidth() - client.borderwidth()
	wy = client.screenheight()
	xdiff = 880
	ydiff = 660
	mem = tostring(memory.read_u8(52267))
	clicked = input.getmouse()["Left"]
	if clicked then
		gui.clearGraphics()
	elseif mem ~= prev_pokemon then
		prev_pokemon = mem	
		if mapfiles[prev_pokemon] ~= nil then
			fname = "../"..mapfiles[prev_pokemon]
			-- draw center:EMU
			-- gui.drawImage(fname, client.bufferwidth()/3.25, client.bufferheight()/4.25, 62, 46)			

			-- draw from full card:CLIENT
			-- "Pokemon": [65, 100, 470, 328],
			-- gui.drawImageRegion(fname, 65, 100, 470, 328, wx - xdiff, wy - ydiff, xdiff, ydiff)		

			-- draw bottom right:CLIENT
			-- gui.drawImage(fname, wx - xdiff, wy - ydiff, xdiff, ydiff)

			-- draw center:CLIENT
			gui.drawImage(fname, ((wx - client.borderwidth())/3.3) + client.borderwidth(), client.screenheight()/4.45, xdiff, ydiff)			
		else
			gui.clearGraphics()
		end
	end	
		emu.frameadvance()
end