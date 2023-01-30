---@meta

---@class iup
---@field list IupList
---@field text IupText
---@field toggle IupToggle
---@field button IupButton
---@field progressdlg IupProgressDlg
---@field messagedlg IupMessageDlg
---@field filedlg IupFileDlg
---@field gridbox IupGridBox
---@field vbox IupVbox
---@field label IupLabel
iup = {
    ["MASK_UINT"] = 0,
    ["CLOSE"] = 0,
    ["K_ESC"] = 0,
}

---@param msg string
---@param x? number
---@param y? number
function iup.Popup(msg, x, y) end

---@param msg string
function iup.Destroy(msg) end

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

---@class IupGridBox

---@class IupLabel
---@field title string

---@class IupVbox