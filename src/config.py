from math import sqrt
# SCREEN
height = 600
width = 800
window_title = "Jueguito"


# FONT
f_type = "Arial"
f_size = 20


# BACKGROUND
bg_color = (128, 0, 128)


# FPS
fps_pos = (10, 10)
fps_cap = 60
fps_f_color = (255, 255, 255)

# SPRITE
velocity = 0.75 # ud. arbitraria, no tne. magnitud.
proporcion = 0.5 #if p=0.5 -> alpha = 45º
# cell_h = cell_w/2 para q alpha=45º, i.e. cellw > cellh
cell_w = 16  # El píxel nº cell_w se incluye.
cell_h = cell_w*proporcion  # El píxel nº cell_h se incluye.
sprite_path = "sprite/player2.png"

#MAP
# 0: grass
# 1: sand
# 2: water
#tile_w > tile_h para q se vea hacia arriba
# tile_h = tile_w/2 para q alpha=45º
tile_w = 64
tile_h = tile_w*proporcion

map_offset = (width//2,150)

mapa_data = [
[2,0,0,0,0,0,0,2],
[0,0,1,1,1,0,0,0],
[0,1,1,2,1,1,0,0],
[0,1,2,2,2,1,0,0],
[0,1,1,2,1,1,0,0],
[0,0,1,1,1,0,0,0],
[0,0,0,0,0,0,0,2],
[0,0,0,0,0,0,0,0],
[1,1,1,1,1,1,1,1],
[0,0,0,0,0,0,0,0]
]


# CÁMARA

zoom_level = 1.0
min_zoom = 0.5
max_zoom = 2.5