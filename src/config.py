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
velocity = 1 # ud. arbitraria.
cell_w = 16  # El píxel nº cell_w se incluye.
cell_h = 16  # El píxel nº cell_h se incluye.
sprite_path = "sprite/player2.png"

#MAP

# 0: grass
# 1: sand
# 2: water
tile_w = 64*2
tile_h = 32*2

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