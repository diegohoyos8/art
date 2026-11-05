# 06 — Multicolor y circuitos

Haces de pistas paralelas que giran a 45°/90°, con pads, en varios colores (como Lostpixels).
Cada color es una **capa** del SVG y se plotea con una pluma distinta.

```bash
cd plotter/estilos
python circuito.py -o circuito.svg --papel A3 --pluma 0.4 --colores 4 --semilla 5
plotter/preparar.sh circuito.svg a3 0.4
```

## Cómo plotear varios colores

1. Fija muy bien el papel (no puede moverse **nada** entre colores).
2. En la app NextDraw elige plotear **por capas**: primero la capa 1, cambia la pluma, después la 2, etc.
   (los nombres de capa empiezan por número: `1-negro`, `2-rojo`…).
3. Orden: colores claros primero, negro al final (tapa pequeños desajustes).
4. Haz un "registro" de prueba: una cruz pequeña en una esquina en todas las capas para comprobar que coinciden.

| Parámetro | Efecto |
|---|---|
| `--pluma 0.4` | grosor de pluma: separación entre pistas = 4× y los haces no se pisan |
| `--pistas` | intentos de haz (solo se colocan los que caben sin chocar) |
| `--colores` | número de plumas (hasta 6) |
| `--paso` | separación entre pistas de un haz (mm, por defecto 4× pluma) |

Plumas: estilográfica o gel de colores (Uni-ball Signo, Sakura Gelly Roll) dan esos colores vivos.
