local lfs = require "lfs"
local eqg = require "luaeqg"

local obj = {}

local tonumber = tonumber
local insert = table.insert
local pcall = pcall

local function ReadMTL(path)
    log_write("Attempting to read MTL file from '" .. path .. "'")
    local f = assert(io.open(path, "r"))
    local out = {}
    local cur

    for line in f:lines() do
        local cmd, args = line:match("%s*(%S+)%s([^\n]+)")
        if cmd and args then
            cmd = cmd:lower()
            if cmd == "newmtl" then
                cur = {}
                out[args] = cur
            elseif cmd == "map_kd" then
                local name = args:match("[%w_]+%.%w+")
                cur.diffuse_map = name
            elseif cmd == "map_bump" then
                local name = args:match("[%w_]+%.%w+")
                cur.e_TextureNormal0 = name
            end
        end
    end

    f:close()
    log_write "Finished reading MTL file"
    return out
end

local function WriteO(f, obj)
    f:write("\n", obj.name, " = {from = ", obj.from, ", to = ", obj.to)
    for i, v in ipairs(obj) do
        f:write(", ", v)
    end
    f:write("}")
end

function Split(s, delimiter)
    result = {}
    for match in (s .. delimiter):gmatch("(.-)" .. delimiter) do
        table.insert(result, match)
    end
    return result
end

function obj.Import(path, dir, appending, shortname)
    log_write("import " .. path .. ": starting")
    local f, err = io.open(path, "r")
    if err then
        error("import " .. path .. ": " .. err)
    end
    local fstr = f:read("*a")
    f:seek("set")
    local line_count = 0
    for n in fstr:gmatch("\n") do
        line_count = line_count + 1
    end

    -- Parse _material.txt to get flags and shaders early
    local material_flags = {}
    local fm = io.open("cache/" .. shortname .. "_material.txt", "rb")
    if fm then
        fm:close()
        local lineNumber = 0
        for line in io.lines("cache/" .. shortname .. "_material.txt") do
            lineNumber = lineNumber + 1
            local lines = Split(line, " ")
            if not lines[1] == "m" and not lines[1] == "e" then
                error("failed to parse " .. shortname .. "_material.txt:" .. lineNumber .. " unknown definition " .. lines[1])
            end
            if lines[1] == "m" then
                if not #lines == 4 then
                    error("failed to parse " .. shortname .. "_material.txt:" .. lineNumber .. " due to number of entries should be 4, got " .. #lines)
                end
                material_flags[lines[2]] = { flag = tonumber(lines[3]), shader = lines[4] }
                log_write("Material " .. lines[2] .. ": flag=" .. lines[3] .. ", shader=" .. lines[4])
            end
            if lines[1] == "e" then
                if not #lines == 5 and not #lines == 4 then
                    error("failed to parse " .. shortname .. "_material.txt:" .. lineNumber .. " due to number of entries should be 4 or 5, got " .. #lines)
                end
                if #lines == 5 then
                    material_flags[lines[2]][lines[3]] = lines[4] .. " " .. lines[5]
                end
                if #lines == 4 then
                    material_flags[lines[2]][lines[3]] = lines[4]
                end
            end
        end
        log_write("Added " .. #material_flags .. " flags based on " .. shortname .. "_material.txt")
    end

    -- Default .obj import logic (unchanged except moved material_flags up)
    local materials = {}
    local vertices = {}
    local triangles = {}
    local vert_src = {}
    local uv_src = {}
    local norm_src = {}
    local vert_mem = {}
    local in_object, mat_src
    local mat_index = {}
    local cur_index

    local cur_obj
    local data_file = assert(io.open(util.ExeDir() .. "/data/" .. shortname .. ".lua", "w+"))

    local face = function(str)
        local a = vert_mem[str]
        if a then
            return a
        end
        local v, t, n = str:match("(%d+)/(%d*)/(%d+)")
        local vert = vert_src[tonumber(v)]
        local norm = norm_src[tonumber(n)]
        local out = {x = vert.x, y = vert.y, z = vert.z, i = norm.i, j = norm.j, k = norm.k}
        t = tonumber(t)
        if t then
            local tex = uv_src[t]
            out.u = tex.u
            out.v = tex.v
        end
        a = #vertices
        insert(vertices, out)
        vert_mem[str] = a
        return a
    end

    local progress = iup.progressdlg{count = 0, totalcount = line_count, description = "Importing model..."}
    if not util.IsConsole() then
        progress:show()
    end

    local last_material = { flag = 65536, shader = "Opaque_MaxCB1.fx" }
    for line in f:lines() do
        local cmd, args = line:match("%s*(%S+)%s([^\n]+)")
        if cmd and args then
            cmd = cmd:lower()
            if mat_src then
                if cmd == "v" then
                    local x, y, z = args:match("(%-?%d+%.%d+) (%-?%d+%.%d+) (%-?%d+%.%d+)")
                    if x and y and z then
                        insert(vert_src, {x = tonumber(x), y = tonumber(y), z = tonumber(z)})
                    end
                elseif cmd == "vt" then
                    local u, v = args:match("(%-?%d+%.%d+) (%-?%d+%.%d+)")
                    if u and v then
                        insert(uv_src, {u = tonumber(u), v = tonumber(v)})
                    end
                elseif cmd == "vn" then
                    local i, j, k = args:match("(%-?%d+%.%d+) (%-?%d+%.%d+) (%-?%d+%.%d+)")
                    if i and j and k then
                        insert(norm_src, {i = tonumber(i), j = tonumber(j), k = tonumber(k)})
                    end
                elseif cmd == "usemtl" then
                    cur_index = mat_index[args]
                    last_material = material_flags[args] or { flag = 65536, shader = "Opaque_MPLBump2UV.fx" }
                    if not cur_index then
                        cur_index = #materials
                        mat_index[args] = cur_index
                        local mat = mat_src[args]
                        if mat then
                            local tbl = {name = args, shader = last_material.shader, flag = last_material.flag}
                            if mat.diffuse_map then
                                local v = mat.diffuse_map:lower()
                                tbl[1] = {name = "e_TextureDiffuse0", type = 2, value = v}
                            end
                            for key, value in pairs(last_material) do
                                if string.sub(key, 1, 2) == "e_" then
                                    local entries = Split(value, " ")
                                    if not #entries == 2 then
                                        error("expected two values for " .. key .. ", got " .. #entries)
                                    end
                                    log_write("adding to " .. args .. " " .. key .. " with value " .. entries[2])
                                    insert(tbl, {name = key, type = entries[1], value = entries[2]})
                                end
                            end
                            insert(materials, tbl)
                        end
                    end
                    if cur_obj then
                        insert(cur_obj, cur_index)
                    end
                    log_write("Material " .. args .. ": flag=" .. last_material.flag .. ", shader=" .. last_material.shader)
                elseif cmd == "f" then
                    local v1, v2, v3 = args:match("(%d+/%d*/%d+) (%d+/%d*/%d+) (%d+/%d*/%d+)")
                    if v1 and v2 and v3 then
                        local a, b, c = face(v1), face(v2), face(v3)
                        insert(triangles, {
                            [1] = a,
                            [2] = b,
                            [3] = c,
                            material = cur_index,
                            flag = last_material.flag,
                        })
                    end
                elseif cmd == "o" then
                    local t = #triangles
                    if cur_obj then
                        cur_obj.to = t
                        WriteO(data_file, cur_obj)
                    end
                    cur_obj = {name = args, from = t + 1}
                end
            elseif cmd == "mtllib" then
                mat_src = ReadMTL(path:gsub("[^\\/]+%.%w+$", args))
            end
        end
        if not util.IsConsole() then
            progress.inc = 1
        end
    end

    for name, flags in pairs(material_flags) do
        for key, value in pairs(flags) do
            if string.sub(key, 1, 2) == "e_" then
                local entries = Split(value, " ")
                if not #entries == 2 then
                    error("expected two values for " .. key .. ", got " .. #entries)
                end
                log_write("flags " .. name .. " key " .. key .. ": " .. entries[2])
                if not mat_src[name] then
                    mat_src[name] = {}
                end
                mat_src[name][key] = entries[2]
            end
        end
    end

    f:close()
    log_write "Finished reading OBJ vertices, normals, texture coordinates and faces"

    if cur_obj then
        cur_obj.to = #triangles
        WriteO(data_file, cur_obj)
    end
    data_file:write("\n")
    data_file:close()

    if mat_src then
        local folder = path:match("^.+[\\/]") or "./"
        log_write("Searching for texture files to import from directory '" .. folder .. "'")
        local append_pos = (#dir + 1)
        local load_img = function(name)
            local mat_path = folder .. name
            log_write("load_img " .. name .. " looking at " .. mat_path)
            name = name:lower()
            local pos
            for i, ent in ipairs(dir) do
                if ent.name == name then
                    pos = i
                    break
                end
            end
            if not pos then
                pos = append_pos
                append_pos = append_pos + 1
            end
            local s, err = pcall(eqg.ImportFlippedImage, mat_path, name, dir, pos)
            if not s then
                log_write("load_img " .. name .. " failed: " .. err)
            end
            dir[pos].pos = pos
        end

        local anim_img_func = function(name)
            name = string.gsub(name, ".dds", "")
            local txt_path = "cache/" .. name .. ".txt"
            local fmanim = io.open(txt_path, "rb")
            if fmanim then
                fmanim:close()
                for line in io.lines(txt_path) do
                    if string.find(line:lower(), ".dds$") then
                        load_img(line)
                    end
                end
                local pos = append_pos
                append_pos = append_pos + 1
                local s, err = pcall(eqg.ImportFile, txt_path, name .. ".txt", dir, pos)
                if not s then
                    log_write("anim_img " .. name .. ".txt failed: " .. err)
                else
                    log_write("found " .. name .. ".txt at " .. txt_path)
                    by_name[name .. ".txt"] = dir[pos]
                end
            end
        end

        for mat_name, mat in pairs(mat_src) do
            local name = mat.diffuse_map
            if name then
                load_img(name)
                anim_img_func(name)
            end
            name = mat.e_TextureNormal0
            if name then
                load_img(name)
            end
            name = mat.e_TextureEnvironment0
            if name then
                load_img(name)
            end
            name = mat.e_TextureSecond0
            if name then
                load_img(name)
            end
            name = mat.e_TextureDiffuse1
            if name then
                load_img(name)
            end
        end
    end

    if not util.IsConsole() then
        progress:hide()
        iup.Destroy(progress)
    end

    log_write "Import from OBJ complete"
    return {
        materials = materials,
        vertices = vertices,
        triangles = triangles,
    }
end

local format = string.format
local util = util

function obj.Export()
    -- ... (unchanged export function)
end

return obj