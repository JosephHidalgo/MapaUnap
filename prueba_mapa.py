import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json


coords_imagen = [
    [-15.825354, -70.011445], [-15.823873, -70.012067],
    [-15.82398, -70.013258], [-15.822161, -70.015832],
    [-15.82057, -70.01677], [-15.821731, -70.018739],
    [-15.82144, -70.019364], [-15.823072, -70.019974],
    [-15.823251, -70.019886], [-15.824381, -70.019013],
    [-15.825473, -70.017894], [-15.826369, -70.017414],
    [-15.828208, -70.016875]
]

# Extraer latitudes y longitudes
lats_img = [p[0] for p in coords_imagen]
lons_img = [p[1] for p in coords_imagen]

# Calcular mínimos y máximos
min_lat, max_lat = min(lats_img), max(lats_img)
min_lon, max_lon = min(lons_img), max(lons_img)

print(f"Bounding Box de la imagen: Latitud [{min_lat}, {max_lat}], Longitud [{min_lon}, {max_lon}]")



# Cargar datos
with open('graph_information.json', 'r') as file:
    data = json.load(file)
nodes = data['nodes']
edges = data['edges']

# Bounding Box de la imagen (calculado arriba)
img_extent = [min_lon - 0.002, max_lon + 0.001, min_lat - 0.002, max_lat + 0.001]  # Ejemplo con margen
# Crear figura
fig, ax = plt.subplots(figsize=(15, 15))

# 1. Cargar imagen con extent ajustado
img = mpimg.imread('resources/mapa.png')
ax.imshow(img, extent=img_extent, aspect='auto')  # aspect='auto' evita distorsión

# 2. Graficar nodos y aristas (ajusta colores para contraste)
for node in nodes:
    lon, lat = node['longitude'], node['latitude']
    if node['is_school']:
        ax.plot(lon, lat, 'ys', markersize=10, markeredgecolor='red', alpha=1)  # Amarillo sólido
        ax.text(lon, lat, node['school_name'], fontsize=8, color='black', ha='center', va='bottom')
    else:
        ax.plot(lon, lat, 'bo', markersize=5, alpha=0.5)  # Azul transparente

for edge in edges:
    source = nodes[edge['source']]
    target = nodes[edge['target']]
    ax.plot(
        [source['longitude'], target['longitude']],
        [source['latitude'], target['latitude']],
        'w-', linewidth=1, alpha=0.7  # Líneas blancas semitransparentes
    )

ax.plot([p[1] for p in coords_imagen], [p[0] for p in coords_imagen], 'r-', lw=2, alpha=0.5)

# 3. Ajustar límites del gráfico
ax.set_xlim(min_lon, max_lon)
ax.set_ylim(min_lat, max_lat)
ax.axis('off')  # Ocultar ejes
plt.tight_layout()
plt.show()