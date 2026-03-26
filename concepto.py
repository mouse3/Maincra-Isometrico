import numpy as np

"""
Dividir proyecciones
Transformar proyecciones a iso. por medio de Cr y escala : float
Cambiar la orientación de la proyección respecto al boceto (modo espejo para el alzado)
Detectar subregiones
    1. Método flood fill de 4 dirr. Complejidad del tipo O(N) {N: nº pixeles}
    
PD: Se sup. qel dict. de ej. rep. todos los ptos. una vez aplic.as todas las transfo. anteriormte. men.

Se guarda el hash de la figura a subir en un .txt, tras esto se ejecuta toda la función para sacar el diccionario final;
una vez con el diccionario final, se guarda en un json donde al hash se le asigna el mismo diccionario.
Cuando el juego vuelve a ejecutarse, primero verifica si todas las imágenes de las texturas están incluidas en el
.txt con los hashes, la imagen q no esté se procesa y blablabla y luego se añade nuevamente al .txt.


"""

class BloqueProyeccion:
    def __init__(self, image_path, tam_celda):
        self.image_path = image_path
        self.tam = tam_celda
        self.proyecciones_raw = {"Alzado": set(), "Perfil": set(), "Planta": set()}
        self.max_z = 0
    
    def detector_vacio(self):
        from PIL import Image
        imagen = Image.open(self.image_path)
        pixeles = imagen.load()
        ancho, alto = imagen.size
        for y in range(alto):
            for x in range(ancho):
                print(f"Pixel en ({x}, {y}): {pixeles[x, y]}")

    """
    Teniendo el mapa de colores, 
    Sabiendo q el sistema no ignora las diagonales, hay q definir q:
    BUCLE PRINCIPAL:
    BUCLE:
    A un pto. negro se le asigna un pto. A(color random != (0, 0, 0)) y otro pto. B(color random != (0, 0, 0)) 
    solo si se cumple q{ 
        1. Hay min. un px. negro en los 3 px izq.
        2. Hay min. un px. negro en los 3 px drch.
        3. Hay min. un px. negro en los 3 px inf.
        4. Hay min. un px. negro en los 3 px sup.
        5. Hay min. 2 px. color (random != (0, 0, 0)) en los px circundantes
    }
    SI se cumple que cantidad [px (random != (0, 0, 0)) en los 8 puntos circundantes) = 2. Ergo A y B corresponden a ellos 2.
    Aplicamos flood fill entre A y B. 
    {
                def flood_fill_conecta(ruta_imagen : PIL.load(), inicio, fin):
                    # ruta_imagen es una de las proyecciones
                    ancho, alto = img.size
                    visitado = set()
                    cola = deque([inicio])
                    while cola:
                        x, y = cola.popleft()
                        if (x, y) == fin:
                            return True
                        if (x, y) in visitado:
                            continue
                        
                        visitado.add((x, y))
                        if pixels[x, y][:3] == (0, 0, 0):
                            continue  # pared
                        
                        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < ancho and 0 <= ny < alto:
                                cola.append((nx, ny))
    }
    return False
    Si no hay path:
        -Entonces agregamos A a una lista tipo "Subreg_1".
    Si hay path:
        - Avanzamos al siguiente px negro y ejecutamos otra vez el bucle
    
    CUANDO un px negro tenga tres circundantes tal que los tres no estén en el mismo sector (px inf. o sup. o dch. o izq.), 
    puede implicar una bifurcación, por tanto (nada, no se q implica esto pero algo útil será). 
    
    TERMINAMOS EL BUCLE.
    Comenzamos nuevo bucle
    # hay q mejorar el pseudocódigo de aquí hasta nuevo comentario.
    Una vez tenemos las listas, recorremos todos los puntos con el mismo método fill para así contar cuantas subregiones hay,
    cuando tengamos las subregiones separadas
    ¿"Rellenamos/incluimos"? todos los ptos. dentro del {contorno q describa la lista).
    # Hasta aquí la mejora del pseudocódigo. 
    PASAMOS A OTRA PROYECCIÓN
    TERMINAMOS EL BUCLE PRINCIPAL
    Creamos un diccionario 
    diccionario_final{
        "Alzado": {
            "subreg1":[(x, y, z), (x, y, z), (x, y, z)]
            "subreg2":[(x, y, z), (x, y, z), (x, y, z)]
            "subreg3":[(x, y, z), (x, y, z), (x, y, z)]
        }
        "Perfil": (...)
        "Planta": (...)
    }
    De tal manera que diccionario_final : dict. de dict. de list. de tupl. 
    y, por último, 
    return diccionario_final
    
    """

    def crear_V(self, dictionary : dict):
        V = []
        """
        f(y, z) Perfil
        g(x, z) Alzado
        h(x, y) Planta
        V=\{ (x, y, z)\in\mathbb{R}^3 | f(y, z) = g(x, z) = h(x, y)\}. 
        """
        # Extraemos las listas para iterar
        alzado = dictionary.get("Alzado", [])
        perfil = dictionary.get("Perfil", [])
        planta = dictionary.get("Planta", [])

        for Punto_Alzado in alzado:
            # Se ha de cumplir que f(y, z) = g(x, z) = h(x, y)
            for Punto_Perfil in perfil:
                # g(z) == f(z)
                if Punto_Alzado[1] == Punto_Perfil[1]:
                    for Punto_Planta in planta:
                        # g(x) == h(x) and f(y) == h(y)
                        if (Punto_Alzado[0] == Punto_Planta[0]) and (Punto_Perfil[0] == Punto_Planta[1]):
                            # Añadimos el pto. V(x, y, z)
                            nuevo_punto = (Punto_Alzado[0], Punto_Perfil[0], Punto_Alzado[1])
                            if nuevo_punto not in V:
                                V.append(nuevo_punto)
        return V # V : list of tuples

# --- Ejemplo de ejecución ---
bloquecito = BloqueProyeccion("assets/bloques/prueba1.png", 1)

# Datos coherentes para que la intersección no sea vacía:
diccionario_ejemplo = {
    "Alzado": [(10, 20), (5, 5)], # (x, z)
    "Perfil": [(30, 20), (5, 5)], # (y, z)
    "Planta": [(10, 30), (5, 5)]  # (x, y)
}

resultado = bloquecito.crear_V(diccionario_ejemplo)
print(f"Vértices 3D encontrados: {resultado}")
bloquecito.detector_vacio()