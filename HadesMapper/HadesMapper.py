from asyncio.windows_events import NULL
import json
import math
import string
import struct

inputFileContent = ""

FORMATTER_32_BIT = '{:032b}'
FORMATTER_8_BIT = '{:08b}'

DATA_TYPES = ["Text", "Obstacle", "Unit", "Prefab", "Weapon", "Unknown", "Projectile", "Count", "Animation", "Component"]

f = None

#read a 4 byte int
def ReadInt32():
    intBytes = f.read(4)

    return int.from_bytes(intBytes, "little", signed=True)

#read a 4 byte uint
def ReadUInt32():
    intBytes = f.read(4)

    return int.from_bytes(intBytes, "little", signed=False)

#read 1 byte and if its not 0 return ture
def ReadBoolean():
    boolByte = f.read(1)
    
    return boolByte != b"\0"

#read 4 bytes and use struct to pack them into a float
def ReadSingle():
    floatBytes = f.read(4)
    
    return struct.unpack('f', floatBytes)[0]

#read a color which consists of 4 (R, G, B, A) 1 byte Uint numbers
def ReadColor():
    newColor = {"R" : 0, "G" : 0, "B" : 0, "A" : 0}

    newColor["R"] = int.from_bytes(f.read(1), "big", signed=False)
    newColor["G"] = int.from_bytes(f.read(1), "little", signed=False)
    newColor["B"] = int.from_bytes(f.read(1), "little", signed=False)
    newColor["A"] = int.from_bytes(f.read(1), "little", signed=False)

    return newColor

#read a string which consists of a 4 byte uint length before the characters then the number of characters given by the length bytes
def ReadString():
    newString = ""

    stringLength = int.from_bytes(f.read(4), "little", signed=False)
    for i in range(stringLength):
        newString = newString + f.read(1).decode('utf-8')

    return newString 

#read a string with a bool flag before it, where if the flag is false it is a null string
def ReadStringAllowNull():
    doReadString = ReadBoolean()

    if doReadString:
        return ReadString()

#read a nullable boolean, that for some reason is 4 bytes long but only the first byte is read, work in progress to figure out how 0,1, and 2 maps to true, false, and undefined 
#this program assumes they are in the order of 0 is true, 1 is undefined, and 2 is false
def ReadTriBoolean():
    newBool = f.read(4)

    if newBool[0] == 0:
        return True
    elif newBool[0] == 2:
        return False
    
    return None

#read 4 bytes (only use first like tribool) that correspond to data type, work in progress to figure out how this works
#possible values are Text, Obstacle, Unit, Prefab, Weapon, Unknown, Projectile, Count, Animation, and Component
#this program assumes that they are in order, so 0 is Text, 1 is Obstacle, 2 is Unit, etc.
def ReadDataType():
    intBytes = f.read(4)
    
    return DATA_TYPES[intBytes[0]]

#write a 4 byte int
def WriteInt32(number):
    #turn number into binary
    bR = number.to_bytes(4, byteorder='big')
    bR = [bR[3], bR[2], bR[1], bR[0]]

    f.write(bytes(bR))

#write a 1 byte bool
def WriteBoolean(value):
    binaryByte = [int(value == True)]
    #turn bool into binary
    f.write(bytes(binaryByte))

#write a tri bool, which is a bool that can be undefined, and has 3 null bytes that aren't used but must be there after its first byte, 
#currently in progress of finding how 0, 1, and 2 maps to true, false, and undefined
#this program assumes they are in the order of 0 is true, 1 is undefined, and 2 is false
def WriteTriBoolean(value):
    boolByte = 1
    if value == True:
        boolByte = 0
    elif value == False:
        boolByte = 2

    binaryBytes = [boolByte, 0, 0, 0]

    f.write(bytes(binaryBytes))

#write a float using struct
def WriteSingle(inp):
    if inp != 0:
        binaryRep =''.join('{:0>8b}'.format(c) for c in struct.pack('!f', inp))
        #store binary as 2 chunks of 16
        sections = ["",""]
        for i in range(8, 33, 8):
            byte = binaryRep[i-8:i]
            sections[(i - 1) // 16] += byte

        #write in order of D C B A
        for section in reversed(sections):
            sectionBytes = [int(section[8:16], 2), int(section[0:8], 2)]
            f.write(bytes(sectionBytes))

    else:
        #Empty float print all null bytes
        emptyBytes = [0, 0, 0, 0]
        f.write(bytes(emptyBytes))

#collect R,G,B, and A and write them into the binary
def WriteColor(colorTable):
    r = colorTable["R"]
    g = colorTable["G"]
    b = colorTable["B"]
    a = colorTable["A"]
    colorBytes = [r, g, b, a]
    f.write(bytes(colorBytes))
    
#write a string
def WriteString(string):
    #add length of string to array
    bR = len(string).to_bytes(4, byteorder='big')
    stringBytes = [bR[3], bR[2], bR[1], bR[0]]
    #add each character to array to be converted
    for c in string:
        stringBytes.append(ord(c))
    #write converting each into bytes representation
    f.write(bytes(stringBytes))

#write a string that has a bool flag before it to show if the string is null or not
def WriteStringAllowNull(string):
    #if string is null print null (shows engine no string values to read)
    if string == None or string == "":
        WriteBoolean(False)
    #if string is not null print true to show to read string and then read string like normal
    else:
        WriteBoolean(True)
        WriteString(string)

#write 4 bytes (only use first like tribool) that correspond to data type, work in progress to figure out how this works
#possible values are Text, Obstacle, Unit, Prefab, Weapon, Unknown, Projectile, Count, Animation, and Component
#this program assumes that they are in order, so 0 is Text, 1 is Obstacle, 2 is Unit, etc.
def WriteDataType(type):
    dataTypeBytes = [DATA_TYPES.index(type), 0, 0, 0]
    f.write(bytes(dataTypeBytes))


#read a binary file and write it to JSON
def DecodeBinaries(inputFilePath, outputFilePath, issequel):
    global f
    f =  open(inputFilePath + ".thing_bin", "rb")
    f.read(4) #read SGB1, whatever it is
    f.read(4) #always going be 12, put need to read it to get it out of the way
    obstacleCount = ReadUInt32()
    obstacleTable = {"Obstacles": []}
    for i in range(obstacleCount):
        ReadBoolean() #read do create flag
        newObstacle = {}
        
        if issequel == False:
            newObstacle["ActivateAtRange"] = ReadBoolean()
            newObstacle["ActivationRange"] = ReadSingle()

        newObstacle["Active"] = ReadBoolean()
        newObstacle["AllowMovementReaction"] = ReadBoolean()
        newObstacle["Ambient"] = ReadSingle()
        newObstacle["Angle"] = ReadSingle()
        
        newObstacle["AttachedIDs"] = []
        attachedIdLength = ReadInt32()
        for x in range(attachedIdLength):
           newObstacle["AttachedIDs"].append(ReadInt32())
        
        newObstacle["AttachToID"] = ReadInt32()
        newObstacle["CausesOcculsion"] = ReadBoolean()
        newObstacle["Clutter"] = ReadBoolean()
        newObstacle["Collision"] = ReadBoolean()
        
        newObstacle["Color"] = ReadColor()
        newObstacle["Comments"] = ReadStringAllowNull()
        
        newObstacle["CreatesShadows"] = ReadTriBoolean()
        newObstacle["DataType"] = ReadDataType()
        newObstacle["DrawVfxOnTop"] = ReadTriBoolean()

        newObstacle["FlipHorizontal"] = ReadBoolean()
        newObstacle["FlipVertical"] = ReadBoolean()

        newObstacle["GroupNames"] = []
        groupNamesLength = ReadInt32()
        for x in range(groupNamesLength):
            if issequel == False: ReadSingle() #for whatever reason the engine reads 4 bytes and just ... does nothing with them
            isStringNull = ReadBoolean()
            if not isStringNull:
                newObstacle["GroupNames"].append("")
            else:
                newObstacle["GroupNames"].append(ReadString())
        
        newObstacle["HelpTextID"] = ReadStringAllowNull()
        newObstacle["Hue"] = ReadSingle()
        newObstacle["Saturation"] = ReadSingle()
        newObstacle["Value"] = ReadSingle()
        newObstacle["Id"] = ReadInt32()
        newObstacle["IgnoreGridManager"] = ReadBoolean()
        newObstacle["Invert"] = ReadBoolean()

        newObstacle["Location"] = {"X": ReadSingle(), "Y": ReadSingle()}

        newObstacle["Name"] = ReadStringAllowNull()

        newObstacle["OffsetZ"] = ReadSingle()
        newObstacle["ParallaxAmount"] = ReadSingle()

        newObstacle["Points"] = []
        pointsLength = ReadInt32()
        for x in range(pointsLength):
            newObstacle["Points"].append({"X": ReadSingle(), "Y": ReadSingle()})
        
        newObstacle["Scale"] = ReadSingle()
        newObstacle["SkewAngle"] = ReadSingle()
        newObstacle["SkewScale"] = ReadSingle()
        newObstacle["SortIndex"] = ReadInt32()
        newObstacle["StopsLight"] = ReadTriBoolean()
        newObstacle["Tallness"] = ReadSingle()
        newObstacle["UseBoundsForSortArea"] = ReadTriBoolean()

        obstacleTable["Obstacles"].append(newObstacle)

    f.close()

    jsonString = json.dumps(obstacleTable, sort_keys=True, indent=4)
    with open(outputFilePath + ".thing_text", "w+") as oid:
        oid.write(jsonString)

#read a json file and write it to binaries
def EncodeBinaries(inputFilePath, outputFilePath, issequel):
    global f

    f = open(outputFilePath + ".thing_bin", "wb+")

    inputFileContent = ""
    with open(inputFilePath + ".thing_text") as fid:
        lines = fid.readlines()
        inputFileContent = "".join(lines)

    data = json.loads(inputFileContent)
    obstacles = data["Obstacles"]

    f.write(b"SGB1") #write whatever this is
    WriteInt32(12)  #write the version number, this is always 12
    WriteInt32(len(obstacles))

    for item in obstacles:
        WriteBoolean(True)

        if issequel == False:
            WriteBoolean(item["ActivateAtRange"])
            WriteSingle(item["ActivationRange"])

        WriteBoolean(item["Active"])

        if "AllowMovementReaction" in item:
            WriteBoolean(item["AllowMovementReaction"])
        else:
            WriteBoolean(True)
        if "Material" in item and item["Material"] != None:
             WriteSingle(item["Material"]["Ambient"])
        else:
            WriteSingle(0)
        WriteSingle(item["Angle"])
        
        WriteInt32(len(item["AttachedIDs"]))
        for attachedID in item["AttachedIDs"]:
            WriteInt32(attachedID)
        WriteInt32(item["AttachToID"])


        if "CausesOcculsion" in item:
            WriteBoolean(item["CausesOcculsion"])
        else:
            WriteBoolean(True)
        
        if "Clutter" in item:
            WriteBoolean(item["Clutter"])
        else:
            WriteBoolean(False)
        WriteBoolean(item["Collision"])

        WriteColor(item["Color"])

        if "Comments" in item:
            WriteStringAllowNull(item["Comments"])
        else:
            WriteStringAllowNull("")

        if "CreatesShadows" in item:
            WriteTriBoolean(item["CreatesShadows"])
        else:
            WriteTriBoolean(True)

        if item["DataType"] != "MapArea":
            WriteDataType(item["DataType"])
        else:
            WriteDataType("Obstacle")

        if "DrawVfxOnTop" in item:
            WriteTriBoolean(item["DrawVfxOnTop"])
        else:
            WriteTriBoolean(True)

        
        WriteBoolean(item["FlipHorizontal"])
        WriteBoolean(item["FlipVertical"])

        WriteInt32(len(item["GroupNames"]))
        for group in item["GroupNames"]:
            if issequel == False: f.write(bytes([0,0,0,0]))
            WriteStringAllowNull(group)
        
        if "HelpTextID" in item:
            WriteStringAllowNull(item["HelpTextID"])
        else:
            WriteStringAllowNull("")
        
        if "Hue" in item:
            WriteSingle(item["Hue"])
            WriteSingle(item["Saturation"])
            WriteSingle(item["Value"])
        else:
            WriteSingle(0)
            WriteSingle(0)
            WriteSingle(0)

        WriteInt32(item["Id"])

        WriteBoolean(item["IgnoreGridManager"])
        WriteBoolean(item["Invert"])

        WriteSingle(item["Location"]["X"])
        WriteSingle(item["Location"]["Y"])

        if "Name" in item:
            WriteStringAllowNull(item["Name"])
        else:
            WriteStringAllowNull("")

        WriteSingle(item["OffsetZ"])
        WriteSingle(item["ParallaxAmount"])

        if "Points" in item:
            WriteInt32(len(item["Points"]))
            for point in item["Points"]:
                WriteSingle(point["X"])
                WriteSingle(point["Y"])
        else:
            WriteInt32(0)
        
        WriteSingle(item["Scale"])
        if "SkewAngle" in item:
            WriteSingle(item["SkewAngle"])
        else:
            WriteSingle(0)

        if "SkewScale" in item:
            WriteSingle(item["SkewScale"])
        else:
            WriteSingle(0)

        WriteInt32(item["SortIndex"])

        if "StopsLight" in item:
            WriteTriBoolean(item["StopsLight"])
        else:
            WriteTriBoolean(True)
    
        if "Tallness" in item:
            WriteSingle(item["Tallness"])
        else:
            WriteSingle(0)

        if "UseBoundsForSortArea" in item:
            WriteTriBoolean(item["UseBoundsForSortArea"])
        else:
            WriteTriBoolean(False)
    f.close()