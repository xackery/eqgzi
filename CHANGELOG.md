# 2022-01-11 v1.8.0
- eqgzi: added animation support

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