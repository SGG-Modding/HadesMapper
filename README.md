# HadesMapper
Encodes and Decodes the game Hades' binary map files into JSON and JSON back out into binary.

# What is this?
This is a tool to read the game's binary map files and decompile them to a JSON file, and also allows compiling JSON files back to map binaries.

# Installation
Download the latest [Release](https://github.com/SGG-Modding/HadesMapper/releases). Open command prompt and cd into the directory of the wheel and pip install it, remember to have .whl at the end of the name.

# How to use this?
The script has 2 modes, encode and decode, as well as 2 submodes for Hades I and Hades II. **When inputting file names do not put their extension, the script automatically handles that (files must have the extension `.thing_text` or `.thing_bin`)**.

## Hades 2
To encode or decode any map binaries to or from Hades II, add `-s` or `-sequel` as a flag. Defaults to using Hades I formating.

## Encode mode (JSON to binaries)
```
HadesMapper ec
```
Defaults to an input of `input` and output of `output`.

## Decode Mode (Binaries to JSON)
```
HadesMapper dc
```
Defaults to an input of `input` and output of `output`.

## Arguments
Both commands share the same arguments which are
* `-i` or `-input`: changes the input file the script reads from, automatically adds `.thing_text` or `.thing_bin` to the name given.
* `-o` or `-output`: changes the output file the script writes to, automatically adds `.thing_text` or `.thing_bin` to the name given.

# Putting it in Game
To put a new binary in the game, name your new binary to whatever your map name is, for example `MyNewMap.thing_bin`. Put it in your mod folder and put 2 lines in your modfile.txt which read:
```
To "Win/Maps/MyNewMap.thing_bin"
Replace "MyNewMap.thing_bin"
```
You need a .map_text file as well, but those are quite hard to create by hand, so it's recommended when creating a new room, to copy both the binary and the .map_text file from another already existing map and modify the binary as needed. To import the .map_text add 2 lines to your modfile.txt which read:
```
To "Maps/MyNewMap.map_text"
Replace "MyNewMap.map_text"
```
then in your Lua script call this line whenever you want to load your map 
```
LoadMap({ Name = "MyNewMap"})
```

# Binary Information
For the most up to date information on how the binaries work, refer to this spreadsheet
https://docs.google.com/spreadsheets/d/1EIqwRIcjqb6rKikrbKpjK-iHWXav6UJWX-TTRfb65SA/edit?usp=sharing