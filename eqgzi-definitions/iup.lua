---@meta

---@class iup
---@field list IupList
---@field text IupText
---@field toggle IupToggle
---@field button IupButton
---@field progressdlg IupProgressDlg
---@field messagedlg IupMessageDlg
---@field filedlg IupFileDlg
---@field dialog IupDialog
---@field gridbox IupGridBox
---@field vbox IupVbox
---@field label IupLabel
---@field menu string[]
---@field tabs IupTabs
---@field submenu IupSubmenu
---@field item IupItem
---@field separator table
---@field hbox IupHbox
iup = {
    ["MASK_UINT"] = 0,
    ["MASK_FLOAT"] = "[+/-]?(/d+/.?/d*|/./d+)",
    ["BUTTON3"] = 0,
    ["CLOSE"] = 0,
    ["K_ESC"] = 0,
}

---@param msg string
---@param x? number
---@param y? number
function iup.Popup(msg, x, y) end

---@param msg string
function iup.Destroy(msg) end

---@param key string
---@return string
function iup.GetGlobal(key) end

function iup.Close() end

---@param toggle_grid boolean
---@param toggle IupToggle
function iup.Append(toggle_grid, toggle) end

function iup.MainLoop() end

---@class IupList
---@field visiblecolumns number
---@field dropdown "YES" | "NO"
---@field visible_items number

---@class IupText
---@field visiblecolumns number
---@field mask number

---@class IupToggle
---@field value "ON" | "OFF"

---@class IupButton
---@field title string
---@field padding string

---@class IupProgressDlg
---@field count number
---@field totalcount number
---@field description string

---@class IupMessageDlg
---@field title string
---@field value string
---@field dialogtype "WARNING" | "ERROR"

---@class IupFileDlg
---@field title string
---@field dialogtype "FILE" | "SAVE" | "DIR"
---@field extfilter string

---@class IupDialog
---@field title string
---@field menu table

---@class IupGridBox

---@class IupLabel
---@field title string

---@class IupVbox

---@class IupTabs
---@field padding string

---@class IupSubmenu
---@field title string

---@class IupItem
---@field title string
---@field action function

---@class IupHbox
---@field nmargin string