import numpy as np

"""
Dividir proyecciones
Transformar proyecciones a iso. por medio de Cr y escala : float
Cambiar la orientación de la proyección respecto al boceto (modo espejo para el alzado)
Detectar subregiones por el método del fill
PD: Se sup. qel dict. de ej. rep. todos los ptos. una vez aplic. todas las transfo. anteriormte. men.

"""

class BloqueProyeccion:
    def __init__(self, image_path, tam_celda):
        self.image_path = image_path
        self.tam = tam_celda
        self.proyecciones_raw = {"Alzado": set(), "Perfil": set(), "Planta": set()}
        self.max_z = 0
    
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
bloquecito = BloqueProyeccion("ola", 1)

# Datos coherentes para que la intersección no sea vacía:
diccionario_ejemplo = {
    "Alzado": [(10, 20), (5, 5)], # (x, z)
    "Perfil": [(30, 20), (5, 5)], # (y, z)
    "Planta": [(10, 30), (5, 5)]  # (x, y)
}

resultado = bloquecito.crear_V(diccionario_ejemplo)
print(f"Vértices 3D encontrados: {resultado}")