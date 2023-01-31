---@meta

---@class util
util = {}

---@class Vertices
---@field count number
---@field version number
---@field data table

---@param vertices Vertices
---@param index number
---@return number, number, number, number, number, number, number, number
function util.GetVertex(vertices, index) end

---@return string
function util.ExeDir() end

---@return boolean
function util.IsConsole() end

---@param triangles Triangles
---@param i number
---@return number, number, number, number 
function util.GetTriangle(triangles, i) end