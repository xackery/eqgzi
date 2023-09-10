# 2023-09-10 v1.8.2
- eqgzi: Fixed a bug where if in edit mode and exporting it will crash if any modifiers
- eqgzi: Repaired some spawngroup logic, more improvements will come soon
- eqgzi: Fixed some bugs with different file types not being detected for textures
- eqgzi: Added new bool checks on process to ensure only valid zone meshes are exported
- eqgzi: Downgraded eqgzi.exe and eqgzi-gui.exe to v140 (VS2015) and Win10 10.0.22000.0 requirements

# 2023-01-29 v1.8.1
- eqgzi: Added arg passing to allow eqgzi-manager to call a zone
# 2022-01-11 v1.8.0
- eqgzi: added animation support
- eqgzi: added fix for diffuse1 material parsing
- convert.py: added fix for model placement rotation

# 2022-01-08 v1.7.1
- eqgzi: fixed model placement data to properly put models rotation

# 2022-01-02 v1.7
- eqgzi: Added door support
- convert.py: Adjusted how string manipulation is lower required python version
- convert.py: Fixed how rotations are done, so doors properly rotate
- convert.py: Fixed a bug with material parsing

# 2021-12-31 v1.6
- Created subfolder-based creation, e.g. cache/, sql/, and out/
- convert.py: shader custom property is now fx
- convert.py: added *.emt (sound emitter) support
- eqgzi: eqg is now created from scratch on import

# 2021-12-26 v1.5
- convert.py: Added _emit.txt support (custom property "emit" on any object in blender generates it)
- convert.py: Lights auto prefix LIB_ to them if no LIB_ or LIT_ is found
- convert.py: all modifiers get applied for script run
- convert.py: loose support for linked objects, still WIP
- eqgzi: Added exe icons
- eqgzi: When a scene is loaded the title is changed to just the zone short name
- eqgzi: Added e_TextureSecond0 support
- eqgzi-gui: When you click the triangles tab, a dump of zonename_triangle.txt is generated in eqgi dir



# 2021-12-23 v1.4
- Adds new command line app eqgzi.exe
- convert.py: Added support for _light.txt
- convert.py: Added support for _region.txt