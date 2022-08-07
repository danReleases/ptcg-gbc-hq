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
	mem = memory.read_u8(52267)
	if mem ~= prev_pokemon then
		gui.clearGraphics()
		gui.clearImageCache()
		prev_pokemon = tostring(mem)	
		if mapfiles[prev_pokemon] ~= nil then
			fname = "../"..mapfiles[prev_pokemon]
			-- "Pokemon": [65, 100, 470, 328],
			gui.drawImageRegion(fname, 65, 100, 470, 328, wx - xdiff, wy - ydiff, xdiff, ydiff)		
		end
	end	
		emu.frameadvance()
end