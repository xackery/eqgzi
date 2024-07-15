
local lfs = require "lfs"
local eqg = require "luaeqg"
local obj = require "gui/obj"
local version = require("gui/version")
require "gui/loader"

dir = {}

function assert(result, msg)
	if result then return result end
	io.stdout:write(msg .. "\n")
	io.flush()
end

function error_popup(msg)
	io.stdout:write(msg .. "\n")
	io.flush()
end

function log_write(...)
	io.stdout:write(... .. "\n")
end

function Split(s, delimiter)
    result = {};
    for match in (s..delimiter):gmatch("(.-)"..delimiter) do
        table.insert(result, match);
    end
    return result;
end


function dump(o)
	if type(o) == 'table' then
	   local s = '{ '
	   for k,v in pairs(o) do
		  if type(k) ~= 'number' then k = '"'..k..'"' end
		  s = s .. '['..k..'] = ' .. dump(v) .. ','
	   end
	   return s .. '} '
	else
	   return tostring(o)
	end
 end

function obj_import(shortname)
	-- local shortname = eqg_path:match("([%s%w_]+)%.eqg$")
	if not shortname then
		error("obj_import: no shortname provided")
	end

	shortname = shortname:lower()

	local obj_path = "cache/" .. shortname .. ".obj"
	local eqg_path = "out/" .. shortname .. ".eqg"

	local s, dir = pcall(eqg.WriteDirectory, eqg_path, {})
	if not s then
		error("failed creating new EQG file: " .. dir)
	end

	dir = {}
	open_path = eqg_path
	open_dir = dir
	ter_name = shortname .. ".ter"

	pos = 1
	dir[pos] = {pos = pos, name = shortname .. ".ter"}
	by_name[shortname .. ".ter"] = dir[pos]

	DirNames(dir)


	local lights = {}
	--table.insert(lights, {name = "test", x = 1, y = 2, z = 3, r = 1, g = 2, b = 3, radius = 3})

	local f = io.open("cache/" .. shortname .. "_light.txt", "rb")
	if f then
		f:close()
		local lineNumber = 0
		for line in io.lines("cache/" .. shortname .. "_light.txt") do
			lineNumber = lineNumber + 1
			lines = Split(line, " ")
			if not #lines == 8 then
				error("expected 8 entries, got " .. #lines)
			end
			table.insert(lights, {name = lines[1],
			x = lines[2], y = lines[3], z = lines[4],
			r = lines[5], g = lines[6], b = lines[7],
			radius = lines[8]})
		end
		log_write("Added " .. #lights .. " lights based on out/" .. shortname .. "_light.txt")
	end


	local regions = {}
	local f = io.open("cache/" ..shortname .. "_region.txt", "rb")
	if f then
		f:close()
		local lineNumber = 0
		for line in io.lines("cache/" ..shortname .. "_region.txt") do
			lineNumber = lineNumber + 1
			lines = Split(line, " ")
			if not #lines == 10 then
				error("expected 10 entries, got " .. #lines)
			end
			-- log_write(#lines)

			table.insert(regions, {name = lines[1],
			center_x = lines[2], center_y = lines[3], center_z = lines[4],
			extent_x = lines[5], extent_y = lines[6], extent_z = lines[7],
			unknownA = lines[8], unknownB = lines[9], unknownC = lines[10],
		})
		end
		log_write("Added " .. #regions .. " regions based on out/" .. shortname .. "_region.txt")
	end

	local models = {ter_name}
	local objects = {{name = ter_name:sub(1, -5), id = 0, x = 0, y = 0, z = 0, rotation_x = 0, rotation_y = 0, rotation_z = 0, scale = 1}}

	local f = io.open("cache/" ..shortname .. "_mod.txt", "rb")
	if f then
		f:close()
		local lineNumber = 0
		for line in io.lines("cache/" ..shortname .. "_mod.txt") do
			lineNumber = lineNumber + 1
			lines = Split(line, " ")
			if not #lines == 9 then
				error("expected 9 entries, got " .. #lines)
			end

			local modelName = string.gsub(lines[1], ".obj", ".mod")

			local modelIndex = -1
			for i = 1, #models do
				if models[i] == modelName then
					modelIndex = i
				end
			end
			if modelIndex == -1 then

				table.insert(models, modelName)
				modelIndex = #models
				-- log_write("Inserted " .. lines[1] .. " as index " .. modelIndex)
			end

			-- log_write("Found " .. lines[1] .. " as index " .. modelIndex)

			table.insert(objects, {name = lines[2],
				id = modelIndex-1,
				x = lines[3], y = lines[4], z = lines[5],
				rotation_x = lines[8], rotation_y = lines[7], rotation_z = lines[6],
				scale = lines[9],
			})
		end
		log_write("Added " .. #models .. " models, " .. #objects .. " objects based on " .. shortname .. "_mod.txt")
	end

	local f = io.open("cache/" ..shortname .. "_doors.txt", "rb")
	if f then
		local doorCount = 0
		f:close()
		local lineNumber = 0
		for line in io.lines("cache/" ..shortname .. "_doors.txt") do
			lineNumber = lineNumber + 1
			lines = Split(line, " ")
			if not #lines == 2 then
				error("expected 2 entries, got " .. #lines)
			end

			local modelName = string.gsub(lines[1], ".obj", ".mod")

			local modelIndex = -1
			for i = 1, #models do
				if models[i] == modelName then
					modelIndex = i
				end
			end
			if modelIndex == -1 then
				table.insert(models, modelName)
				modelIndex = #models
				doorCount = doorCount + 1
				-- log_write("Inserted " .. lines[1] .. " as index " .. modelIndex)
			end

			-- log_write("Found " .. lines[1] .. " as index " .. modelIndex)

		end
		log_write("Added " .. doorCount .. " door based on " .. shortname .. "_doors.txt")
	end

	local ter_data = obj.Import(obj_path, dir, true, shortname)

	local zon_data = {
		models = models,
		objects = objects,
		regions = regions,
		lights = lights,
	}



	pos = 1
	dir[pos] = {pos = pos, name = ter_name}
	by_name[ter_name] = dir[pos]

	local s, ter_ent = pcall(ter.Write, ter_data, ter_name, eqg.CalcCRC(ter_name))
	if not s then
		error("ter.write " .. ter_name .. " failed: " .. ter_ent)
	end

	ter_ent.pos = pos
	dir[pos] = ter_ent


	for i = 2, #models do

		pos = #dir + 1

		local modelBaseName = string.gsub(models[i], ".mod", "")
		local modelName = models[i]

		dir[pos] = {pos = pos, name = modelName .. ".mod"}
		--by_name[modelName .. ".mod"] = dir[pos]

		log_write("Attempting to save '" .. modelName .. "' as '" .. modelName)

		local mod_ent = obj.Import("cache/" .. modelBaseName .. ".obj", dir, true, shortname)
		mod_ent.bones = {}
		mod_ent.bone_assignments = {}
		s, mod_data = pcall(mod.Write, mod_ent, modelName, eqg.CalcCRC(modelName))
		if not s then
			error("mod.write " .. modelName .. ".mod failed: "..err)
		end
		mod_data.name = modelName
		mod_data.pos = pos
		dir[pos] = mod_data
	end

	local zon_name = shortname .. ".zon"
	pos = #dir+1
	--log_write("zon pos: "..pos)
	dir[pos] = {pos = pos, name = zon_name}
	by_name[zon_name] = dir[pos]

	local s, zon_ent = pcall(zon.Write, zon_data, zon_name, eqg.CalcCRC(zon_name))
	if not s then
		error("zon.write " .. zon_name .. " failed: " .. zon_ent)
	end

	zon_ent.pos = pos
	dir[pos] = zon_ent


	DirNames(dir)

	s, data = pcall(eqg.WriteDirectory, eqg_path, dir)
	if not s then
		error("eqg.write " .. eqg_path .. " failed: " .. data)
	end

	log_write("Saved successfully to " .. eqg_path)
end

function main_cmd(arg1, arg2, arg3)
	io.stdout:write("executing eqgzi " .. version.Build)

	local args = ""
	if arg1 and string.len(arg1) then
		io.stdout:write(" " .. arg1)
		args = arg1
	end

	if arg2 and string.len(arg2) then
		io.stdout:write(" " .. arg2)
		args = args .. " " .. arg2
	end

	if arg3 and string.len(arg3) then
		io.stdout:write(" " .. arg3)
		args = args .. " " .. arg3
	end

	io.stdout:write("\n")

	local cmdType = ""
	local eqg_path = ""
	local shortname = ""
	local obj_path = ""

	for cmd in string.gmatch(args, "%S+") do
		log_write(cmd)
		if cmd:lower() == "version" then
			print("eqgzi " .. version.Build)
			return
		elseif cmd:lower() == "import" then
			cmdType = "import"
		elseif cmd == "" then

		elseif string.find(cmd:lower(), ".eqg$") then
			eqg_path = cmd
		elseif string.find(cmd:lower(), ".obj$") then
			obj_path = cmd
		else
			shortname = cmd
		end
	end

	if cmdType == "import" then
		if shortname == "" then
			print("eqgzi " .. version.Build)
			error("usage: eqgzi import <zone>")
		end

		obj_import(shortname)
		return
	end

	print("eqgzi " .. version.Build)
	log_write("usage: eqgzi [import <zone>]")
end
