import pygame
import math

from src.config import (
    height, width, f_size, f_type, bg_color, fps_pos, fps_cap, fps_f_color,
    window_title, mapa_data, cell_w, cell_h, sprite_path, velocity,
    tile_w, tile_h, map_offset, min_zoom, max_zoom
)

import src.declarations


def main():
    from src.config import zoom_level

    pygame.init()

    # -----------------------------
    # WINDOW
    # -----------------------------
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(window_title)

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(f_type, f_size)

    # -----------------------------
    # MAPA
    # -----------------------------
    mapa = src.declarations.MapaIsometrico(
        mapa_data,
        tile_w,
        tile_h,
        offset=map_offset
    )

    # -----------------------------
    # CREAR BLOQUES (3D)
    # -----------------------------
    bloques = []

    for y, fila in enumerate(mapa.mapa):
        for x, tile in enumerate(fila):

            altura = 1
            if tile == 1:
                altura = 2
            elif tile == 2:
                altura = 3

            color = mapa.colores.get(tile, (255, 255, 255))

            bloque = src.declarations.Bloque(x, y, z=altura, color=color)
            bloques.append(bloque)

    # -----------------------------
    # JUGADOR
    # -----------------------------
    jugador = src.declarations.Jugador(
        posicion=(width // 2, 200),
        velocity=velocity,
        sprite_path=sprite_path,
        cell_w=cell_w,
        cell_h=cell_h,
        directions=[
            "up", "up-right", "right", "down-right",
            "down", "down-left", "left", "up-left"
        ],
        scale=3,
        debug=True
    )

    # -----------------------------
    # GAME LOOP
    # -----------------------------
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # -----------------------------
        # INPUT
        # -----------------------------
        keys = pygame.key.get_pressed()

        if keys[pygame.K_o]:
            zoom_level = max(min_zoom, zoom_level - 0.02)
        if keys[pygame.K_p]:
            zoom_level = min(max_zoom, zoom_level + 0.02)

        dx, dy = 0, 0
        if keys[pygame.K_UP]:    dy = -1
        if keys[pygame.K_DOWN]:  dy = 1
        if keys[pygame.K_LEFT]:  dx = -1
        if keys[pygame.K_RIGHT]: dx = 1

        # -----------------------------
        # COLISIÓN
        # -----------------------------
        if dx != 0 or dy != 0:
            norm_dx, norm_dy = dx, dy

            if dx != 0 and dy != 0:
                norm_dx /= math.sqrt(2)
                norm_dy /= math.sqrt(2)

            desired_px = norm_dx * velocity
            desired_py = norm_dy * velocity

            hw, hh = tile_w / 2, tile_h / 2

            iso_u = (desired_px / hw + desired_py / hh) / 2
            iso_v = (desired_py / hh - desired_px / hw) / 2

            u_px, u_py = iso_u * hw, iso_u * hh
            v_px, v_py = -iso_v * hw, iso_v * hh

            foot_x = jugador.posicion[0]
            foot_y = jugador.posicion[1] + (jugador.rect.height // 2)

            final_px, final_py = 0, 0

            tx, ty = mapa.pixel_to_tile(foot_x + desired_px, foot_y + desired_py)

            if mapa.es_caminable(tx, ty):
                final_px, final_py = desired_px, desired_py
            else:
                tx_u, ty_u = mapa.pixel_to_tile(foot_x + u_px, foot_y + u_py)
                if mapa.es_caminable(tx_u, ty_u):
                    final_px, final_py = u_px, u_py

                tx_v, ty_v = mapa.pixel_to_tile(foot_x + v_px, foot_y + v_py)
                if mapa.es_caminable(tx_v, ty_v):
                    final_px += v_px
                    final_py += v_py

            if abs(final_px) < 0.001: final_px = 0
            if abs(final_py) < 0.001: final_py = 0

            if final_px != 0 or final_py != 0:
                fake_dx = final_px / velocity
                fake_dy = final_py / velocity

                if fake_dx != 0 and fake_dy != 0:
                    fake_dx *= math.sqrt(2)
                    fake_dy *= math.sqrt(2)

                jugador.movimiento(fake_dx, fake_dy)
            else:
                jugador.movimiento(0, 0)
        else:
            jugador.movimiento(0, 0)

        # -----------------------------
        # CÁMARA
        # -----------------------------
        cam_x = (width / 2) - (jugador.posicion[0] * zoom_level)
        cam_y = (height / 2) - (jugador.posicion[1] * zoom_level)

        # -----------------------------
        # DIBUJO
        # -----------------------------
        screen.fill(bg_color)

        # ORDENAR POR PROFUNDIDAD
        bloques_ordenados = sorted(bloques, key=lambda b: (b.x + b.y, b.z))

        for bloque in bloques_ordenados:

            iso_x, iso_y = mapa.cart_to_iso(bloque.x, bloque.y)

            altura_px = bloque.z * (tile_h // 2)

            draw_x = (iso_x * zoom_level) + cam_x
            draw_y = ((iso_y - altura_px) * zoom_level) + cam_y

            if -tile_w*zoom_level < draw_x < width + tile_w*zoom_level and \
               -tile_h*zoom_level < draw_y < height + tile_h*zoom_level:

                bloque.draw_iso(screen, draw_x, draw_y, mapa, zoom_level)

        # -----------------------------
        # JUGADOR
        # -----------------------------
        orig_w, orig_h = jugador.image.get_size()
        player_scaled = pygame.transform.scale(
            jugador.image,
            (int(orig_w * zoom_level), int(orig_h * zoom_level))
        )

        player_rect = player_scaled.get_rect()
        player_rect.center = (
            jugador.posicion[0] * zoom_level + cam_x,
            jugador.posicion[1] * zoom_level + cam_y
        )

        screen.blit(player_scaled, player_rect)

        # -----------------------------
        # UI
        # -----------------------------
        fps_text = font.render(
            f"FPS: {round(clock.get_fps())} | Zoom: {round(zoom_level, 2)}",
            True,
            fps_f_color
        )
        screen.blit(fps_text, fps_pos)

        pygame.display.flip()
        clock.tick(fps_cap)

    pygame.quit()


if __name__ == "__main__":
    main()