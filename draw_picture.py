import amulet
import cv2
from collections import Counter
from math import sqrt, floor
from amulet.api.block import Block
from time import time
from typing import Any, List, Tuple


level = amulet.load_level("C:\\Users\\wilsonjusuf\\AppData\\Roaming\\.minecraft\\saves\\my-minecraft-world-master") 
GAME_VERSION = ("java", (1,20,1))
DIMENSION = "minecraft:overworld"



def get_block_from_pixel(pixel: Any, is_air=False) -> Block:
    def l2(p1: Tuple[int,int,int], p2: Tuple[int,int,int]) -> float:
        return sqrt( 
            ((p1[0] - p2[0])**2) +
            ((p1[1] - p2[1])**2) +
            ((p1[2] - p2[2])**2) 
        )
    if is_air:
        return Block.from_string_blockstate("minecraft:air")

    # check closest values
    red = [199,0,35]
    black = [0,0,0]
    white = [250,250,250]
    red_L2 = l2(red, pixel)
    black_L2 = l2(black, pixel)
    white_L2 = l2(white, pixel)
    #if red_L2 < black_L2 and red_L2 < white_L2
    #    return Block.from_string_blockstate("minecraft:red_concrete")
    #if black_L2 < red_L2 and black_L2 < white_L2:
    if black_L2 < white_L2 or red_L2 < white_L2:
        return Block.from_string_blockstate("minecraft:black_concrete")
    return Block.from_string_blockstate("minecraft:white_concrete")

print("Map loaded. Editing...")
img = cv2.imread("astars.png", cv2.IMREAD_COLOR)


#top_x, y , top_z = 176,77,-3293
top_x,top_y,top_z = 452, 80+24, -3287

# negative y (up down), 
#positive z (left right)
#
# two directions are: y and z.
z_direction_from_top = 1
y_direction_from_top = -1

for y in range(img.shape[0]):
    for z in range(img.shape[1]):
        block = get_block_from_pixel(img[y][z])
        level.set_version_block(
            top_x,
            top_y +(y * y_direction_from_top),
            top_z + (z_direction_from_top * z),
            DIMENSION,
            GAME_VERSION,
            block 
        )

level.save()
level.close()




