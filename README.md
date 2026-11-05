# art — imagen → vectores para plotter

Usa [DrawingBotV3](https://github.com/SonarSonic/DrawingBotV3) (versión Free, open source) **sin interfaz gráfica**
para convertir una imagen en trazos lineales (SVG / G-code / PDF) listos para un pen plotter.

## Instalación

Requisitos: Java 21+, Gradle 8+, `xvfb` (solo en servidores sin pantalla).

```bash
tools/setup.sh      # clona DrawingBotV3 en tools/DrawingBotV3, lo compila y compila el runner
```

## Uso

```bash
tools/vectorize.sh input/foto.jpg output "Sketch Lines PFM" svg,gcode,png
```

| Argumento | Valores | Defecto |
|---|---|---|
| imagen | jpg, png, webp, tif… | — |
| carpeta de salida | | `output` |
| algoritmo (PFM) | `Sketch Lines PFM`, `Sketch Squares PFM`, `Spiral PFM` | `Sketch Lines PFM` |
| formatos | `svg`, `gcode`, `pdf`, `png` (vista previa) | `svg,gcode,png` |

- **Sketch Lines**: trazos tipo boceto, varios tonos de gris (un SVG con capas por pluma).
- **Sketch Squares**: igual pero con segmentos en ángulo recto.
- **Spiral**: una única línea continua en espiral — ideal para plotter (casi sin levantar la pluma).

El G-code sale en mm con la escala por defecto (1 px ≈ 1 mm). Para ajustar el tamaño al papel
lo más práctico es escalar el SVG en Inkscape / vpype (`vpype read out.svg scaleto 20cm 20cm write out2.svg`)
o redimensionar la imagen de entrada.

Archivos: `tools/src/drawingbot/HeadlessRunner.java` (runner), `tools/setup.sh`, `tools/vectorize.sh`.
