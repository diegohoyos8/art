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
   Si tienes un archivo `.osm` (exportado desde openstreetmap.org → Exportar): `python mapa.py --osm zona.osm -o zona.svg`
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

## Ideas

- **Mapa de maratón / ruta**: exporta tu ruta GPX (Strava, Garmin) y ábrela en Inkscape encima del mapa como capa extra en color.
- **Papel negro + gel blanco o metálico**: los mapas quedan espectaculares (como el vídeo del mapa morado).
- **Sin agua o sin calles pequeñas**: borra la capa en Inkscape para un mapa más limpio.
