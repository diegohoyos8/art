# 00 — Equipo, materiales y flujo de trabajo

## Qué NextDraw elegir

| Modelo | Área aprox. | Papel | Para qué |
|---|---|---|---|
| **8511** | 8.5 × 11 in (~216 × 279 mm) | Carta / A4 | Aprender, postales, pruebas rápidas. Más barato. |
| **1117** | 11 × 17 in (~279 × 432 mm) | Tabloide / **A3** | **Recomendado**: A3 es el formato "de pared" más vendible y sigue siendo manejable. |
| **2234** | 22 × 34 in (~559 × 864 mm) | ~A1 | Piezas grandes para exposición; plots de muchas horas, más espacio y mesa. |

Comprueba las medidas exactas en la ficha de Bantam Tools antes de comprar.
Mi recomendación: **1117**. Te deja hacer A4 y A3, y el salto de A4 a A3 cambia mucho el impacto de un mapa o un retrato.

## Software

| Herramienta | Uso |
|---|---|
| **Bantam Tools NextDraw** (app / extensión Inkscape / CLI Python `nextdraw`) | Mandar el SVG al plotter, velocidad, altura de pluma, plotear por capas |
| **Inkscape** (gratis) | Ver/editar SVG, mover capas, añadir texto (usa fuentes de trazo simple "Hershey" para texto) |
| **vpype** (instalado aquí) | Optimizar: unir líneas, ordenar trazos, escalar al papel → `preparar.sh` |
| Scripts de `plotter/estilos/` | Generan el SVG de cada estilo |
| **DrawingBotV3** (`tools/`) | Imagen → trazos tonales |

## Materiales básicos

- **Plumas**: Sakura Pigma Micron (0.1–0.8), Staedtler pigment liner, Uni-ball Signo (gel, blancas para papel negro/azul), Pilot G2, plumas estilográficas (como el vídeo de Lostpixels). Empieza con un pack de Micron 0.3/0.5 negro.
- **Papel**: liso y con gramaje ≥ 200 g (Bristol, Canson Bristol, papel de acuarela satinado). Papel negro/azul marino para pluma blanca (estilo blueprint/mapa).
- **Cinta de pintor** o placa magnética para fijar el papel. Si el papel se mueve, el plot se arruina.

## Flujo detallado

1. **Elegir estilo** (ver tabla del README) y **tamaño final**.
2. **Preparar la fuente**: imagen recortada y con buen contraste; coordenadas del mapa; o parámetros.
3. **Generar** el SVG con el script del estilo (usa `--papel A3` etc.).
4. **Preparar para el plotter**:
   ```bash
   plotter/preparar.sh obra.svg a3 0.5 15mm      # papel, grosor de pluma, margen → obra_plot.svg
   ```
   Te dice los **metros con tinta** y **en el aire**, y **simula la tinta con el grosor real de la pluma**:
   si hay zonas que empaparían el papel, se para y genera `obra_plot_densidad.png` con las zonas en rojo.
   ⚠️ Si cambias el papel o la pluma, vuelve a preparar: la misma obra en A6 tiene las líneas 3× más juntas que en A3. Más metros = más tiempo y más desgaste de pluma.
   Regla práctica: si una pluma fina debe hacer > 150 m, ten una de repuesto.
5. **Revisar** `obra_plot.svg` en Inkscape: capas `1-…`, `2-…` = una pluma cada una.
6. **Prueba**: plotea una versión A5/A6 con una pluma más fina (`preparar.sh obra.svg a6 0.1`) en papel barato, ajusta altura de pluma y velocidad
   (más lento = línea más uniforme con plumas de gel/estilográficas).
7. **Plot final**: plotea capa por capa (en la app de NextDraw, modo *layers*), cambiando la pluma entre capas
   sin mover el papel. Empieza por los colores claros y termina con el negro.
8. **Archivar** en `proyectos/AAAA-MM-nombre/`: SVG, comando exacto usado (incluida la `--semilla`), foto final.

## Errores comunes

- **Demasiado detalle**: la pluma tiene grosor; líneas a < 0.5 mm con pluma 0.5 se convierten en una mancha. Ajusta densidad al grosor.
- **Tinta que empapa**: demasiadas pasadas en la misma zona rompen el papel → reduce densidad o usa papel más grueso.
- **Escala**: diseña al tamaño final (`--papel`), no escales al final un diseño A4 a A1: las líneas quedarán muy separadas.
- **Texto**: las fuentes normales salen como contornos huecos. Usa fuentes Hershey (Inkscape → Extensiones → Texto → Hershey Text).
