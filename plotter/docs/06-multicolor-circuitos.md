# 06 — Multicolor y circuitos

Haces de pistas paralelas que giran a 45°/90°, con pads, en varios colores (como Lostpixels).
Cada color es una **capa** del SVG y se plotea con una pluma distinta.

```bash
cd plotter/estilos
python circuito.py -o circuito.svg --papel A3 --pistas 80 --colores 4 --semilla 5
plotter/preparar.sh circuito.svg a3
```

## Cómo plotear varios colores

1. Fija muy bien el papel (no puede moverse **nada** entre colores).
2. En la app NextDraw elige plotear **por capas**: primero la capa 1, cambia la pluma, después la 2, etc.
   (los nombres de capa empiezan por número: `1-negro`, `2-rojo`…).
3. Orden: colores claros primero, negro al final (tapa pequeños desajustes).
4. Haz un "registro" de prueba: una cruz pequeña en una esquina en todas las capas para comprobar que coinciden.

| Parámetro | Efecto |
|---|---|
| `--pistas` | número de haces |
| `--colores` | número de plumas (hasta 6) |
| `--paso 1.6` | separación entre pistas de un haz (mm) |

Plumas: estilográfica o gel de colores (Uni-ball Signo, Sakura Gelly Roll) dan esos colores vivos.
