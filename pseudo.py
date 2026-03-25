from math import cos, sin, radians
import cv2
import numpy as np
import matplotlib.pyplot as plt



"""


Los límites de las rectas de cada plano son la distancia en px de la proy correspondiente
Alzado: b1, r || x
Planta: b2, r || z
Perfil: b3, r || y
Donde r empieza en un punto (píxel en negro (0, 0, 0) ) de las proyecciones transformadas (isométricas) de b1, b2, b3 respectivamente.


"""


class GeneradorProyecciones:
    def __init__(self, ruta, tam_celda=16, escala=1.0):
        # Cargar imagen y verificar
        self.img = cv2.imread(ruta, cv2.IMREAD_GRAYSCALE)
        if self.img is None:
            raise FileNotFoundError(f"No se encuentra la imagen en: {ruta}")
            
        self.celda = tam_celda
        self.escala = escala
        self.k_iso = np.sqrt(2/3) # Coeficiente de reducción isométrico
        
        # Invertir: Fondo blanco (0), Dibujo negro (255)
        _, self.binaria = cv2.threshold(self.img, 200, 255, cv2.THRESH_BINARY_INV)

    def analizar_vista(self, region):
        """Detecta si hay dibujo en cada celda de la región."""
        h, w = region.shape
        filas, cols = h // self.celda, w // self.celda
        grid = np.zeros((filas, cols), dtype=bool)
        
        for f in range(filas):
            for c in range(cols):
                sub_img = region[f*self.celda:(f+1)*self.celda, c*self.celda:(c+1)*self.celda]
                # Umbral de detección: si más del 5% de la celda es negra
                if np.sum(sub_img > 0) > (self.celda * self.celda * 0.05):
                    grid[f, c] = True
        return grid

    def construir(self):
        h, w = self.binaria.shape
        mh, mw = h // 2, w // 2
        
        # Extracción de vistas según disposición estándar:
        # Alzado (Z, X) | Perfil (Z, Y)
        # -----------------------------
        # Planta (Y, X) | (Vacío/Inglete)
        
        m_alzado = self.analizar_vista(self.binaria[0:mh, 0:mw])
        m_perfil = self.analizar_vista(self.binaria[0:mh, mw:])
        m_planta = self.analizar_vista(self.binaria[mh:, 0:mw])

        # Dimensiones lógicas
        nz, nx = m_alzado.shape      # Alzado da Alto(Z) y Ancho(X)
        _, ny = m_perfil.shape       # Perfil da Alto(Z) y Profundidad(Y)
        
        voxels = np.zeros((nx, ny, nz), dtype=bool)

        for x in range(nx):
            for y in range(ny):
                for z in range(nz):
                    # Invertimos Z para que el índice 0 de la imagen sea la base del objeto
                    idx_z = (nz - 1) - z
                    
                    # CORRECCIÓN DE MAPEO:
                    # Alzado usa [Z, X]
                    # Perfil usa [Z, Y]
                    # Planta usa [Y, X]
                    if m_alzado[idx_z, x] and m_perfil[idx_z, y] and m_planta[y, x]:
                        voxels[x, y, z] = True

        if not np.any(voxels):
            print("Advertencia: No se generó ningún voxel. Revisa el tamaño de celda o la alineación.")
            
        self.render(voxels)

    def render(self, voxels):
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        tam_real = self.celda * self.escala * self.k_iso

        # Crear malla de coordenadas
        x, y, z = np.indices(np.array(voxels.shape) + 1).astype(float)
        x *= tam_real
        y *= tam_real
        z *= tam_real

        # Dibujar voxels
        ax.voxels(x, y, z, voxels, edgecolor='black', facecolors='#1f77b4', alpha=0.8)

        ax.set_title(f"Reconstrucción 3D (Escala: {self.escala})")
        ax.set_xlabel('Ancho (X)')
        ax.set_ylabel('Profundidad (Y)')
        ax.set_zlabel('Alto (Z)')
        
        # Forzar aspecto cúbico para no deformar la pieza
        max_dim = max(voxels.shape) * tam_real
        ax.set_xlim(0, max_dim)
        ax.set_ylim(0, max_dim)
        ax.set_zlim(0, max_dim)
        
        ax.view_init(elev=30, azim=135) # Ángulo mejorado para ver la escalera
        plt.show()

# Ejecución
# Nota: Asegúrate de que "imagen_aa4ca1.png" esté en el mismo directorio o ajusta la ruta.
gen = GeneradorProyecciones("assets/bloques/prueba3.png", tam_celda=1, escala=1.0)
gen.construir()