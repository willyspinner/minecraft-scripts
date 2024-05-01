import amulet
import cv2
from collections import Counter
from math import sqrt, floor
from amulet.api.block import Block
from time import time
from typing import Any, List, Tuple
# read/write the world data here
# load the level
# this will automatically find the wrapper that can open the world and set everything up for you.
t1 = time()
level = amulet.load_level("C:\\Users\\wilsonjusuf\\AppData\\Roaming\\.minecraft\\saves\\my-minecraft-world-master") 
t2 = time()
print("Level loading took: ", t2-t1, " seconds")
# bottom left: 

GAME_VERSION = ("java", (1,20,1))
DIMENSION = "minecraft:overworld"

print("Map loaded. Editing...")

img = cv2.imread("track_map_scaled.png", 0)
#img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
#cv2.imwrite("track_map_scaled.png", img)

# TODO: make a minecraft utils folder probably
def get_track_line(img: Any, follow_line_color: int, start_coord: Tuple[int, int], iter_max: int=100000) -> List[Tuple[int,int]]:
    """
    Retrieves track outline (list of pixel coords ordered by progression in traack) of a track map following a 
    naive adjacent line-following algorithm.

    Line following algorithm assumes a counter-clockwise oriented track and searches greedily for follow_line_color
    in adjacent pixels counter-clockwise starting from east. Backtracks if no viable next paths. Essentially we're doing a DFS.

    Stops after looping iter_max times (to prevent timeout), or finds start_coord

    """
    x,y = start_coord
    outline = [start_coord]
    visited_coords = set([start_coord])
    if img[y][x] != follow_line_color:
        raise Exception(f"Unable to get track outline: invalid starting coordinate. Not in color of {follow_line_color} (Got {img[y][x]})")
    # NOTE: forgot to check OOB lmao
    for _ in range(iter_max):
        new_path = False
        for new_x, new_y in [ (x+1,y), (x+1, y-1), (x,y-1), (x-1,y-1), (x-1,y), (x-1,y+1), (x,y+1), (x+1, y+1)]:
            if (new_x, new_y) == start_coord:
                # end of algorithm
                return outline
            if img[new_y][new_x] == follow_line_color and (new_x,new_y) not in  visited_coords:
                x, y = new_x, new_y
                visited_coords.add((x,y))
                outline.append((x,y))
                new_path = True
                break

        # if no found, backtrack before the current one.
        if not new_path:
            #print(f"Backtracking from {(x,y)} to {outline[-2]}")
            x, y = outline[-2]
    return outline
    

def get_elevation_for_track_line(track_line: List[Tuple[int,int]], elevation_list: List[Tuple[float, float]]) -> List[int]:
    """
    Computes the relative elevation (btwn 0 to 1) for each point in the track line w.r.t. 
    a list of corresponding (relative completion, relative elevation) tuples. 

    relative elevation for each point is computed by linearly scaling relative elevation between ith and i+1th elevation_list entries according to the 
    point's overall progression w.r.t. track_line (relative completion).

    e.g. 
    [ 
        (0.0, 0.35),
        # turn 1
        (0.1, 0.35),
        (0.15, 0.50)
        # turn 2 to turn 5
        (0.2, 0.50),
        (0.4, 0.00),
        # main straight
        (1, 0.35)
    ]

    """
    
    j = 0
    relative_elevations = []
    for i in range(len(track_line)):
        progression = i / len(track_line)
        while j < len(elevation_list) -1 and not (progression >= elevation_list[j][0]and progression <=elevation_list[j+1][0]):
            j += 1
        if j == len(elevation_list) - 1:
            # reached the end of the list
            relative_elevations.append(elevation_list[-1][1])
        else:
            # linearly scale elevation with relative progression in between the ith and i+1th elevation_lists.
            progression_scale = (progression - elevation_list[j][0]) / (elevation_list[j+1][0] - elevation_list[j][0])
            relative_elevation = elevation_list[j][1] + (progression_scale * (elevation_list[j+1][1] - elevation_list[j][1]))
            relative_elevations.append(relative_elevation)
    return relative_elevations



def get_nearest_track_line_index(track_line: List[Tuple[int,int]], coord: Tuple[int,int]) -> int:
    """
    Naive linear search to get nearest track line position
    """
    def dist(c1: Tuple[int,int], c2: Tuple[int,int]) -> float:
        return sqrt(((tl[0] - coord[0])**2) +((tl[1] - coord[1])**2))

    best_distance_score = 1000000000
    best_index = -1
    for i, tl in enumerate(track_line):
        distance_score = dist(tl, coord)
        if best_index == -1 or distance_score < best_distance_score:
            best_distance_score = distance_score
            best_index = i
    return best_index


def set_circuit_block(x:int, y_base:int, elevation_gain: float, z:int, is_erase: bool=False) -> None:
    # NOTE: use air_block to erase if needed.
    y_final = y_base + floor(elevation_gain)
    block_type = "top" if elevation_gain - floor(elevation_gain) > 0.5 else "bottom"
    if is_erase:
        circuit_block = Block.from_string_blockstate("minecraft:air")
    else:
        circuit_block = Block.from_string_blockstate(f"minecraft:stone_slab[type={block_type}]")
    print("Setting block at ",x, y_final,z)
    level.set_version_block(
        x,
        y_final,
        z,
        DIMENSION,
        GAME_VERSION,
        circuit_block
    )

# NOTE: img is (y,x) or (h,w)
start_coord = 223,334 # (x,y) or (w,h) right before T1 of Laguna seca
follow_line_color = 195

laguna_track_line = get_track_line(img, follow_line_color, start_coord)

# visualization for progression
#for i, (x,y) in enumerate(laguna_track_outline):
#    progress = round(i / len(laguna_track_outline) * 255)
#    img = cv2.circle(img, (x,y), radius=0, color=progress, thickness=3)
    

# TODO: either these are messed up our my track line algorithm is wrong. supposed to descend right after corkscrew

# FINDINGS:
# trackline is continuous except for 0 and 1 (start and finish). thats a quick fix 
RETTILINEO = 0
ANDRETTI_SECOND_APEX = 0.1
TURN_5_APEX = 0.3
TURN_6_APEX = 0.475 
CORKSCREW = 0.62
END_OF_CORKSCREW = 0.665
TURN_11_BRAKING_ZONE = 0.84
END_OF_STRAIGHT=0.95

laguna_relative_elevations = [ 
    (RETTILINEO, 0.42),
    (ANDRETTI_SECOND_APEX, 0.15),
    (TURN_5_APEX, 0),
    (TURN_6_APEX, 0.28),
    (CORKSCREW, 1),
    (END_OF_CORKSCREW, 0.58),
    (TURN_11_BRAKING_ZONE, 0.25),
    (END_OF_STRAIGHT, 0.25),
    (0.999, 0.42)
    ]


track_line_elevations = get_elevation_for_track_line(laguna_track_line, laguna_relative_elevations)
LAGUNA_SECA_ELEVATION_METERS = 28

# relative from bottom left
x_direction = 1
z_direction =  1
#x1,y1,z1 = 201,85,-3179
#x1,y1,z1 = 2500, -60, 2500 
#x1,y1,z1 = 4000, -60, 4000 
x1,y1,z1 = 209, 70, -3188
x1 += 260 # 
z1 -= 15 # not too close to railroad stn
x1 -= img.shape[1]
z1 -= img.shape[0]
print("height:", img.shape[0],", width: ", img.shape[1])
t3 = time()
for h in range(img.shape[0]):
    for w in range(img.shape[1]):
        pixel = img[h][w]
        # is track color
        if pixel< 200:
            trackline_index = get_nearest_track_line_index(laguna_track_line, (w,h))
            elevation_gain = (LAGUNA_SECA_ELEVATION_METERS * track_line_elevations[trackline_index])
            x = x1 + (w * x_direction)
            z = z1   + (h * z_direction)
            set_circuit_block(
                x, 
                y1, 
                elevation_gain, 
                z,
                is_erase=False)
                
t4 = time()
print("Edit done. Editing took ", t4-t3, " seconds")


print("Saving...")
# save the changes to the world
level.save()

# close the world
level.close()
t5 = time()
print("Saving done. Took ", t5-t4, " seconds")

print("Overall script executed in ", t5- t1, " seconds")


