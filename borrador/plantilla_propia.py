import pygame
import sys

"""
Aplicar creación de mapa procedural.
"""


# -------------------------
# CONFIGURACIÓN INICIAL
# -------------------------
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Isométrico con sprite y límites")

clock = pygame.time.Clock()
FPS = 60

# Colores
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)

# -------------------------
# CONFIGURACIÓN ISOMÉTRICA
# -------------------------
TILE_WIDTH = 64
TILE_HEIGHT = 32
MAP_WIDTH = 10
MAP_HEIGHT = 10

# -------------------------
# FUNCIONES AUXILIARES
# -------------------------
def cart_to_iso(cart_x, cart_y):
    """Convierte coordenadas cartesianas a isométricas."""
    iso_x = (cart_x - cart_y) * (TILE_WIDTH // 2)
    iso_y = (cart_x + cart_y) * (TILE_HEIGHT // 2)
    return iso_x, iso_y

def draw_map():
    """Dibuja el mapa isométrico en pantalla."""
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tile = tile_map[y][x]
            iso_x, iso_y = cart_to_iso(x, y)
            iso_x += SCREEN_WIDTH // 2 - TILE_WIDTH // 2
            iso_y += 50
            
            color = GREEN if tile == 0 else BLUE
            points = [
                (iso_x, iso_y + TILE_HEIGHT // 2),
                (iso_x + TILE_WIDTH // 2, iso_y),
                (iso_x + TILE_WIDTH, iso_y + TILE_HEIGHT // 2),
                (iso_x + TILE_WIDTH // 2, iso_y + TILE_HEIGHT)
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, WHITE, points, 1)

def get_tile_under_player(px, py):
    """
    Determina el tile donde está el jugador a partir de su posición en píxeles.
    """
    adj_x = px - (SCREEN_WIDTH // 2 - TILE_WIDTH // 2)
    adj_y = py - 50

    cart_x = (adj_y / (TILE_HEIGHT/2) + adj_x / (TILE_WIDTH/2)) / 2
    cart_y = (adj_y / (TILE_HEIGHT/2) - adj_x / (TILE_WIDTH/2)) / 2

    tile_x = int(cart_x)
    tile_y = int(cart_y)

    if 0 <= tile_x < MAP_WIDTH and 0 <= tile_y < MAP_HEIGHT:
        return tile_map[tile_y][tile_x]
    return 0  # default tierra

def clamp_player(px, py):
    """
    Limita al jugador dentro de los bordes del mapa formando un rombo exacto.
    """
    # Esquinas del mapa en píxeles
    top_x, top_y = cart_to_iso(0, 0)
    bottom_x, bottom_y = cart_to_iso(MAP_WIDTH-1, MAP_HEIGHT-1)
    left_x, left_y = cart_to_iso(0, MAP_HEIGHT-1)
    right_x, right_y = cart_to_iso(MAP_WIDTH-1, 0)

    # Ajuste al centro de pantalla
    top_x += SCREEN_WIDTH // 2 - TILE_WIDTH // 2
    top_y += 50
    bottom_x += SCREEN_WIDTH // 2 - TILE_WIDTH // 2
    bottom_y += 50
    left_x += SCREEN_WIDTH // 2 - TILE_WIDTH // 2
    left_y += 50
    right_x += SCREEN_WIDTH // 2 - TILE_WIDTH // 2
    right_y += 50

    # Centro del rombo
    center_x = (top_x + bottom_x) / 2
    center_y = (top_y + bottom_y) / 2

    # Semi-dimensiones (ancho y alto del rombo)
    half_width = right_x - center_x
    half_height = bottom_y - center_y

    # Evitar división por cero
    if half_width == 0 or half_height == 0:
        return px, py

    dx = px - center_x
    dy = py - center_y

    # Limitar al borde del rombo usando la fórmula |dx/half_width| + |dy/half_height| <= 1
    factor = abs(dx)/half_width + abs(dy)/half_height
    if factor > 1:
        dx *= 1 / factor
        dy *= 1 / factor
        px = center_x + dx
        py = center_y + dy

    return px, py

# -------------------------
# PERSONAJE
# -------------------------
# Cargar sprite
# Cargar sprite
player_sprite = pygame.image.load("sprite/player.png").convert_alpha()

# Obtener tamaño original
original_width = player_sprite.get_width()
original_height = player_sprite.get_height()

# Definir factor de escala (0.5 = 50% del tamaño original)
scale_factor = 0.5

# Calcular nuevo tamaño manteniendo la proporción
new_width = int(original_width * scale_factor)
new_height = int(original_height * scale_factor)

# Redimensionar sprite
player_sprite = pygame.transform.scale(player_sprite, (new_width, new_height))
player_rect = player_sprite.get_rect()

# Posición inicial (píxeles)
player_x = SCREEN_WIDTH // 2
player_y = 200
player_speed = 150  # píxeles por segundo en tierra
water_slow_factor = 0.5  # velocidad en agua

# -------------------------
# BUCLE PRINCIPAL
# -------------------------
running = True
while running:
    dt = clock.tick(FPS) / 1000  # Delta time en segundos

    # --- EVENTOS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- ENTRADAS ---
    keys = pygame.key.get_pressed()
    current_tile = get_tile_under_player(player_x, player_y)
    speed = player_speed * (water_slow_factor if current_tile == 1 else 1)

    if keys[pygame.K_LEFT]:
        player_x -= speed * dt
    if keys[pygame.K_RIGHT]:
        player_x += speed * dt
    if keys[pygame.K_UP]:
        player_y -= speed * dt
    if keys[pygame.K_DOWN]:
        player_y += speed * dt

    # Limitar al rombo del mapa
    player_x, player_y = clamp_player(player_x, player_y)

    # -------------------------
    # DIBUJADO
    # -------------------------
    screen.fill((0,0,0))
    draw_map()
    # Dibujar sprite centrado en su posición
    screen.blit(player_sprite, player_sprite.get_rect(center=(int(player_x), int(player_y))))
    pygame.display.flip()

pygame.quit()
sys.exit()