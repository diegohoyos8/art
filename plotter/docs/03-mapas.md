# 03 — Mapas geográficos

Calles, ríos y costa desde OpenStreetMap, separados por importancia en capas (= plumas).

## Pasos

1. **Elige el lugar** y el radio en metros (2–3 km para un centro urbano en A3, 10+ km para una ciudad entera).
2. **Genera** (necesita internet):
   ```bash
   cd plotter/estilos
   python mapa.py --lugar "Madrid, Spain" --radio 2500 --papel A3 -o madrid.svg
   python mapa.py --punto 40.4168,-3.7038 --radio 1500 --circulo -o sol.svg     # recorte circular
   ```
   Sin internet: región entera `.osm.pbf` de Geofabrik (ver abajo):
   `python mapa.py --pbf madrid-latest.osm.pbf --punto 40.4168,-3.7038 --radio 2500 --papel A3 -o madrid.svg`
3. **Capas que salen**:
   | Capa | Contenido | Pluma sugerida |
   |---|---|---|
   | `1-principales` | autopistas, avenidas | 0.8 |
   | `2-secundarias` | calles medianas | 0.5 |
   | `3-pequenas` | calles residenciales, caminos | 0.2–0.3 |
   | `4-agua` | ríos, lagos, costa | azul |
   | `marco` | borde del recorte | la más gruesa |
4. **Prepara**: `plotter/preparar.sh madrid.svg a3 20mm`
5. **Texto** (nombre de la ciudad, coordenadas): añádelo en Inkscape con *Hershey Text* en una capa nueva.

## Dónde descargar mapas con más detalle

| Fuente | Qué da | Uso |
|---|---|---|
| **download.geofabrik.de** | Regiones completas de OpenStreetMap (`.osm.pbf`), al día | `mapa.py --pbf archivo --punto lat,lon` |
| **extract.bbbike.org** | Recorte a medida de cualquier ciudad (elige formato PBF) | igual que Geofabrik |
| **overpass-turbo.eu** | Capas concretas (edificios, ríos, metro…) en GeoJSON | ábrelas en Inkscape como capa extra |
| **centrodedescargas.cnig.es** | IGN España: curvas de nivel, modelos de terreno, CartoCiudad | mapas topográficos de líneas |
| **datos.madrid.es** | Callejero oficial de Madrid | `mapa_madrid_callejero.py` |

## Ideas

- **Mapa de maratón / ruta**: exporta tu ruta GPX (Strava, Garmin) y ábrela en Inkscape encima del mapa como capa extra en color.
- **Papel negro + gel blanco o metálico**: los mapas quedan espectaculares (como el vídeo del mapa morado).
- **Sin agua o sin calles pequeñas**: borra la capa en Inkscape para un mapa más limpio.

## Madrid sin OpenStreetMap: Callejero oficial del Ayuntamiento

`estilos/mapa_madrid_callejero.py` dibuja Madrid con los datos oficiales del Ayuntamiento
(cruces + direcciones con coordenadas). Así se hizo `ejemplos/madrid_A3.svg`.

1. Descarga de **datos.madrid.es** el "Callejero oficial del Ayuntamiento de Madrid": los CSV de **cruces** y de **direcciones**.
   (Copia de 2024 en el repo GitHub `iqueipopg/MadridGPS` → `data.zip`.)
2. Genera:
   ```bash
   cd plotter/estilos
   python mapa_madrid_callejero.py cruces.csv --direcciones direcciones.csv -o madrid.svg --papel A3
   # otro centro / zoom:  --centro 40.4153,-3.6845 --radio 1500   (Retiro, más cerca)
   # sin título:          --titulo ""
   ```
3. `plotter/preparar.sh madrid.svg a3 10mm`

Capas: `1-principales` (avenidas, paseos, autovías → pluma 0.7–0.8), `2-calles` (0.3), `3-pequenas` (0.1–0.2),
`4-marco`, `5` = título MADRID + coordenadas en fuente Hershey (un solo trazo).
Para el A3 de ejemplo: ~29 m con tinta (casi todo en la capa 2, ten una pluma 0.3 de repuesto).
