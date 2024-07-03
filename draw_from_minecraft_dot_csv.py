import amulet
import csv
from math import sqrt, floor
from amulet.api.block import Block
from time import time
from typing import Any, List, Tuple


level = amulet.load_level('/Users/wilsonjusuf/my-minecraft-world')
filename = 'minecraftDot.csv'
GAME_VERSION = ("java", (1,20,1))
DIMENSION = "minecraft:overworld"

print("Map loaded. Editing...")



top_x, top_y, top_z = -186, 200,-3022


# negative y (up down), 
#positive z (left right)
#
# two directions are: y and z.
#x_direction_from_top = 1
z_direction_from_top = -1
y_direction_from_top = -1
#top_y -= 32 + 5
#top_y += 40
#top_z -= 10-10
#top_x += 28 - 5 - 7 -5 - 7 - 5 - 6
#top_y += 5+1 + 10

#top_y += 6 + 5 - 2
#top_z += 5 + 5 + 4

#x_direction_from_top = 1

data = list(csv.reader(open(filename)))

for y in range(1, len(data)):
    if len(data[y]) == 0:
        # encountered the end of the picture.
        break
    for x in range(1, len(data[0])):
        block = Block.from_string_blockstate(data[y][x])
        #block = Block.from_string_blockstate("minecraft:air")
        level.set_version_block(
            top_x,
            #top_x + (x * x_direction_from_top),
            top_y +(y * y_direction_from_top),
            #top_z,
            top_z + (x * z_direction_from_top),
            DIMENSION,
            GAME_VERSION,
            block 
        )

level.save()
level.close()




