from asyncio.windows_events import NULL
import json
import math
import string
import struct
inputFilePath = "input.thing_bin"
outputFilePath = "output.thing_text"
inputFileContent = ""

FORMATTER_32_BIT = '{:032b}'
FORMATTER_8_BIT = '{:08b}'

f = open(inputFilePath, "rb")

def ReadInt32():
    intBytes = f.read(4)

    return int.from_bytes(intBytes, "little", signed=True)

def ReadUInt32():
    intBytes = f.read(4)

    return int.from_bytes(intBytes, "little", signed=False)

def ReadBoolean():
    boolByte = f.read(1)
    
    return boolByte != b"\0"

def ReadSingle():
    floatBytes = f.read(4)

    return struct.unpack('f', floatBytes)[0]


def ReadColor():
    newColor = {"R" : 0, "G" : 0, "B" : 0, "A" : 0}

    newColor["R"] = int.from_bytes(f.read(1), "big", signed=False)
    newColor["G"] = int.from_bytes(f.read(1), "little", signed=False)
    newColor["B"] = int.from_bytes(f.read(1), "little", signed=False)
    newColor["A"] = int.from_bytes(f.read(1), "little", signed=False)

    return newColor

def ReadString():
    newString = ""

    stringLength = int.from_bytes(f.read(4), "little", signed=False)
    print(stringLength)
    for i in range(stringLength):
        newString = newString + f.read(1).decode('utf-8')

    print(newString)
    return newString 

def ReadStringAllowNull():
    doReadString = ReadBoolean()
    print(doReadString)

    if doReadString:
        return ReadString()

def ReadTriBoolean():
    newBool = f.read(4)

    return newBool != b"\0"

ReadSingle() #read SGB1, whatever it is
version = ReadUInt32() #always gonna be 12, put need to read it to get it out of the way

def readFile():
    obstacleCount = ReadUInt32()
    obstacleTable = {"Obstacles": []}
    for i in range(obstacleCount):
        ReadBoolean() #read do create flag
        newObstacle = {}
        newObstacle["ActivateAtRange"] = ReadBoolean()
        newObstacle["ActivateAtRange"] = ReadSingle()
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
        
        newObstacle["CreateShadows"] = ReadTriBoolean()
        newObstacle["????"] = ReadTriBoolean()
        newObstacle["DrawVfxOnTop"] = ReadTriBoolean()

        newObstacle["FlipHorizontal"] = ReadBoolean()
        newObstacle["FlipVertical"] = ReadBoolean()

        newObstacle["GroupNames"] = []
        groupNamesLength = ReadInt32()
        for x in range(groupNamesLength):
            ReadSingle() #for whatever reason the engine reads 4 bytes and just ... does nothing with them
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

    jsonString = json.dumps(obstacleTable, sort_keys=True, indent=4)
    with open(outputFilePath, "w+") as oid:
        oid.write(jsonString)


readFile()

f.close()