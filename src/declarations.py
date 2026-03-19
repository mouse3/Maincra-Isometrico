import pygame
from math import sqrt


class Jugador:

    def __init__(self, posicion, velocity, sprite_path, cell_w, cell_h, debug,
                directions, scale):
        """
        Inicializa un jugador con hoja de sprites modular.
        :param posicion: (x, y) inicial en pantalla
        :param velocity: velocidad de movimiento
        :param sprite_path: ruta al sprite sheet
        :param cell_w: ancho de cada frame
        :param cell_h: alto de cada frame
        :param directions: lista de nombres de direcciones, cada una corresponde a una fila en el sprite sheet
        :param scale: factor de escalado de cada frame
        :param debug: activa prints y overlay de debug
        """
        self.posicion = self.posicion = [float(posicion[0]), float(posicion[1])]
        self.velocity = velocity
        self.debug = False

        # Hoja de sprites
        sheet = pygame.image.load(sprite_path).convert_alpha()
        sheet_w, sheet_h = sheet.get_size()

        # Si no se pasan direcciones, usar 8 clásicas
        if directions is None:
            directions = ["up", "up-right", "right", "down-right",
                          "down", "down-left", "left", "up-left"]

        self.directions = directions
        self.frames = {d: [] for d in directions}

        # Cortar la hoja de sprites
        for row, direction in enumerate(directions):
            y1 = row * cell_h
            if y1 >= sheet_h:
                # Fila no existe, crear placeholder
                placeholder = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
                placeholder.fill((255, 0, 255))
                self.frames[direction].append(placeholder)
                continue

            for col in range(sheet_w // cell_w):
                x1 = col * cell_w
                if x1 + cell_w > sheet_w:
                    continue
                frame = sheet.subsurface((x1, y1, cell_w, cell_h))
                if scale != 1:
                    frame = pygame.transform.scale(
                        frame,
                        (int(frame.get_width() * scale),
                         int(frame.get_height() * scale))
                    )
                self.frames[direction].append(frame)

            # Si no hay frames, agregar placeholder
            if len(self.frames[direction]) == 0:
                placeholder = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
                placeholder.fill((255, 0, 255))
                self.frames[direction].append(placeholder)

        if debug:
            for d in directions:
                print(f"DEBUG- Frames detectados en {d}: {len(self.frames[d])}")

        # Estado inicial
        self.direction = directions[0]
        self.frame_index = 0
        self.animation_speed = 0.2
        self.cell_w = cell_w
        self.cell_h = cell_h
        self.image = self.frames[self.direction][0]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (int(self.posicion[0]), int(self.posicion[1]))

    # -----------------------------
    def movimiento(self, dx, dy):

        # Normalizar diagonal
        if dx != 0 and dy != 0:
            dx /= sqrt(2)
            dy /= sqrt(2)

        self.posicion[0] += dx * self.velocity
        self.posicion[1] += dy * self.velocity

        self.rect.topleft = (int(self.posicion[0]), int(self.posicion[1]))

        # -------------------------
        # DIRECCIONES
        # -------------------------
        if dx == 0 and dy < 0:
            self.direction = "up" if "up" in self.directions else self.direction
        elif dx > 0 and dy < 0:
            self.direction = "up-right" if "up-right" in self.directions else self.direction
        elif dx > 0 and dy == 0:
            self.direction = "right" if "right" in self.directions else self.direction
        elif dx > 0 and dy > 0:
            self.direction = "down-right" if "down-right" in self.directions else self.direction
        elif dx == 0 and dy > 0:
            self.direction = "down" if "down" in self.directions else self.direction
        elif dx < 0 and dy > 0:
            self.direction = "down-left" if "down-left" in self.directions else self.direction
        elif dx < 0 and dy == 0:
            self.direction = "left" if "left" in self.directions else self.direction
        elif dx < 0 and dy < 0:
            self.direction = "up-left" if "up-left" in self.directions else self.direction

        # -------------------------
        # ANIMACIÓN
        # -------------------------
        if dx != 0 or dy != 0:
            self.animar()
        else:
            self.frame_index = 0
            self.image = self.frames[self.direction][0]

    # -----------------------------
    def animar(self):
        frames = self.frames[self.direction]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(frames):
            self.frame_index = 0
        self.image = frames[int(self.frame_index)]

    # ----------------------------- 
    def dibujar_debug(self, surface): #Debug/ histbox
        if not self.debug:
            return
        pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)


class MapaIsometrico:

    def __init__(
        self,
        mapa=None,
        tile_w=64,
        tile_h=32,
        offset=(0, 0),
        colores=None,
        walkable=None
    ):

        self.mapa = mapa or []

        self.tile_w = tile_w
        self.tile_h = tile_h

        self.offset_x = offset[0]
        self.offset_y = offset[1]

        self.colores = colores or {
            0: (60, 180, 75),
            1: (220, 200, 120),
            2: (50, 120, 220)
        }

        self.walkable = walkable or {0, 1}

    # ------------------------------------------------
    # CARTESIANO → ISOMÉTRICO
    # ------------------------------------------------
    def cart_to_iso(self, x, y):

        iso_x = (x - y) * (self.tile_w // 2)
        iso_y = (x + y) * (self.tile_h // 2)

        return (
            iso_x + self.offset_x,
            iso_y + self.offset_y
        )

    # ------------------------------------------------
    # ISOMÉTRICO → CARTESIANO
    # ------------------------------------------------
    def iso_to_cart(self, iso_x, iso_y):

        iso_x -= self.offset_x
        iso_y -= self.offset_y

        x = (iso_x / (self.tile_w/2) + iso_y / (self.tile_h/2)) / 2
        y = (iso_y / (self.tile_h/2) - iso_x / (self.tile_w/2)) / 2

        return round(x), round(y)

    # ------------------------------------------------
    # TILE DESDE PIXEL
    # ------------------------------------------------
    def pixel_to_tile(self, px, py):

        tx, ty = self.iso_to_cart(px, py)

        return tx, ty

    # ------------------------------------------------
    # OBTENER TILE
    # ------------------------------------------------
    def get_tile(self, x, y):

        if not self.mapa:
            return None

        if y < 0 or y >= len(self.mapa):
            return None

        if x < 0 or x >= len(self.mapa[y]):
            return None

        return self.mapa[y][x]

    # ------------------------------------------------
    # COMPROBAR CAMINABLE
    # ------------------------------------------------
    def es_caminable(self, x, y):

        tile = self.get_tile(x, y)

        #if tile is None:
        #    return False

        return tile in self.walkable

    # ------------------------------------------------
    # DIBUJAR TILE
    # ------------------------------------------------
# En src/declarations.py (dentro de MapaIsometrico)

    def draw_tile(self, surface, color, x, y, zoom=1.0):
        # Multiplicamos el ancho y alto del tile por el zoom
        hw = (self.tile_w // 2) * zoom
        hh = (self.tile_h // 2) * zoom
    
        puntos = [
            (x, y - hh),
            (x + hw, y),
            (x, y + hh),
            (x - hw, y)
        ]
    
        pygame.draw.polygon(surface, color, puntos)
        pygame.draw.polygon(surface, (0, 0, 0), puntos, 1) # Borde

    # ------------------------------------------------
    # DIBUJAR MAPA
    # ------------------------------------------------
    def draw(self, surface):

        if not self.mapa:
            return

        for y, fila in enumerate(self.mapa):

            for x, tile in enumerate(fila):

                iso_x, iso_y = self.cart_to_iso(x, y)

                color = self.colores.get(tile, (255,255,255))

                self.draw_tile(surface, color, iso_x, iso_y)