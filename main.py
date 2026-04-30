# main.py

import pygame
from math import sqrt, atan2, sin, cos

from src.config import (
    height, width, f_size, f_type, bg_color, fps_pos, fps_cap, fps_f_color,
    window_title, mapa_data, cell_w, cell_h, sprite_path, velocity,
    tile_w, tile_h, map_offset, min_zoom, max_zoom, proporcion, radio_disparo
)

import src.declarations

def main():
    from src.config import zoom_level
    pygame.init()

    screen = pygame.display.set_mode((width, height), 
                                    pygame.SCALED | pygame.DOUBLEBUF, 
                                    vsync=1)
    #screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(window_title)

    clock = pygame.time.Clock() 
    font = pygame.font.SysFont(f_type, f_size) 

    # Creación de entidades
    mapa = src.declarations.MapaIsometrico(
        mapa_data,
        tile_w,
        tile_h,
        offset=map_offset
    )

    jugador = src.declarations.Jugador(
        posicion=(width//2, 200),
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
    enemigo1 = src.declarations.Enemigo(
        posicion=(width//2, 200),
        velocity=velocity,
        sprite_path="sprite/full_black.png",
        cell_w=cell_w,
        cell_h=cell_h,
        directions=[
            "up", "up-right", "right", "down-right",
            "down", "down-left", "left", "up-left"
        ],
        scale=3,
        debug=True
    )

    # Grupo para las balas
    balas_group = pygame.sprite.Group()


    # LOOP
    running = True

    while running:
        # Offset de cámara (necesario antes de procesar clicks)
        cam_x = (width / 2) - (jugador.posicion[0] * zoom_level)
        cam_y = (height / 2) - (jugador.posicion[1] * zoom_level)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Disparo con clic izquierdo
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # Rueda hacia arriba 
                    zoom_level = min(max_zoom, zoom_level + 0.03)

                if event.button == 5: # Rueda hacia arriba 
                    zoom_level = max(min_zoom, zoom_level - 0.03)


                if event.button == 1: # Clic izquierdo
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    # IMPORTANTE: Convertir la posición del ratón (pantalla) 
                    # a la posición real del mundo (deshaciendo zoom y cámara)
                    world_mouse_x = (mouse_x - cam_x) / zoom_level
                    world_mouse_y = (mouse_y - cam_y) / zoom_level
                    

                    x_0, y_0 = jugador.posicion[0], jugador.posicion[1]
                    x_obj, y_obj = world_mouse_x, world_mouse_y
                    theta = atan2(y_obj - y_0, x_obj - x_0) # Ángulo al objetivo
                    # x -> Cos; y-> Sen
                    spawn_x = x_0 + radio_disparo * cos(theta)
                    spawn_y = y_0 + radio_disparo * sin(theta)
                    nueva_bala = src.declarations.Bala(
                        posicion_inicial=[spawn_x, spawn_y], 
                        objetivo_pos=(x_obj, y_obj),
                        sprite_path="sprite/bala.png"
                    )
                    balas_group.add(nueva_bala)

        if pygame.sprite.spritecollide(enemigo1, balas_group, False):
            print("colided")



        # Movimiento 
        # Con ratón

        # Con teclad
        keys = pygame.key.get_pressed()


        if keys[pygame.K_o]:
            zoom_level = max(min_zoom, zoom_level - 0.02)
        if keys[pygame.K_p]:
            zoom_level = min(max_zoom, zoom_level + 0.02)


        dx, dy = 0, 0
        a=1
        if keys[pygame.K_LSHIFT] : a = 2
        if keys[pygame.K_UP] or keys[pygame.K_w]:    dy = -1*a ; a=1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:  dy = 1 *a ; a=1
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  dx = -1 *a ; a=1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1 *a ; a=1

        # Mantenida igual
        if dx != 0 or dy != 0:
            norm_dx, norm_dy = dx, dy
            if dx != 0 and dy != 0:
                norm_dx /= sqrt(2)*proporcion; norm_dy /= sqrt(2)*proporcion
                
            desired_px = norm_dx * velocity
            desired_py = norm_dy * velocity
            
            hw, hh = tile_w / 2, tile_h / 2
            iso_u = (desired_px / hw + desired_py / hh) / 2
            iso_v = (desired_py / hh - desired_px / hw) / 2
            u_px, u_py = iso_u * hw, iso_u * hh
            v_px, v_py = -iso_v * hw, iso_v * hh
            
            foot_x, foot_y = jugador.posicion[0], jugador.posicion[1] + (jugador.rect.height // 2)
            tx, ty = mapa.pixel_to_tile(foot_x + desired_px, foot_y + desired_py)
            
            if mapa.es_caminable(tx, ty):
                jugador.movimiento(norm_dx, norm_dy)
            else:
                jugador.movimiento(0, 0)
        else:
            jugador.movimiento(0, 0)

        # Actualiza las balas
        balas_group.update()

        # Elimina balas lejanas para no saturar la memoria
        for bala in balas_group:
            dist = sqrt((bala.posicion[0]-jugador.posicion[0])**2 + (bala.posicion[1]-jugador.posicion[1])**2)
            if dist > 2000: # Si se aleja más de 2000 píxeles del jugador, se borra
                bala.kill()

        # -----------------------------
        # 4. DIBUJO
        # -----------------------------
        screen.fill(bg_color)

        # Dibujar Mapa
        for y, fila in enumerate(mapa.mapa):
            for x, tile in enumerate(fila):
                iso_x, iso_y = mapa.cart_to_iso(x, y)
                draw_x = (iso_x * zoom_level) + cam_x
                draw_y = (iso_y * zoom_level) + cam_y
                if -tile_w*zoom_level < draw_x < width + tile_w*zoom_level:
                    color = mapa.colores.get(tile, (255, 255, 255))
                    mapa.draw_tile(screen, color, draw_x, draw_y, zoom_level)

        # #### NUEVO: Dibujar Balas con Zoom y Cámara
        for bala in balas_group:
            b_orig_w, b_orig_h = bala.image.get_size()
            bala_scaled = pygame.transform.scale(bala.image, (int(b_orig_w * zoom_level), int(b_orig_h * zoom_level)))
            b_draw_x = (bala.posicion[0] * zoom_level) + cam_x
            b_draw_y = (bala.posicion[1] * zoom_level) + cam_y
            screen.blit(bala_scaled, bala_scaled.get_rect(center=(b_draw_x, b_draw_y)))

        # Dibujar Jugador
        orig_w, orig_h = jugador.image.get_size()
        player_scaled = pygame.transform.scale(jugador.image, (int(orig_w * zoom_level), int(orig_h * zoom_level)))
        p_draw_x = (jugador.posicion[0] * zoom_level) + cam_x
        p_draw_y = (jugador.posicion[1] * zoom_level) + cam_y
        screen.blit(player_scaled, player_scaled.get_rect(midbottom=(p_draw_x, p_draw_y)))

        # Dibujar enemigo 1

        enemigo1_w, enemigo1_h = enemigo1.image.get_size()
        enemigo1_scaled = pygame.transform.scale(enemigo1.image, (int(enemigo1_w * zoom_level), int(enemigo1_h * zoom_level)))
        enemigo1p_draw_x = (enemigo1.posicion[0] * zoom_level) + cam_x
        enemigo1p_draw_y = (enemigo1.posicion[1] * zoom_level) + cam_y
        screen.blit(enemigo1_scaled, enemigo1_scaled.get_rect(midbottom=(enemigo1p_draw_x, enemigo1p_draw_y)))

        # UI
        fps_text = font.render(f"FPS: {round(clock.get_fps())} | Zoom: {round(zoom_level, 2)}", True, fps_f_color)
        screen.blit(fps_text, fps_pos)

        pygame.display.flip()
        clock.tick(fps_cap)

    pygame.quit()

if __name__ == "__main__":
    main()