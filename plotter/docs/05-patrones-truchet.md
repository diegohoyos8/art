# 05 — Patrones de líneas paralelas (Truchet)

Baldosas con arcos concéntricos que, al girarse al azar, forman caminos que serpentean
(como las líneas paralelas con pluma gruesa de Václav Zahrádka).

```bash
cd plotter/estilos
python truchet.py -o truchet.svg --papel A3 --celda 20 --lineas 4 --semilla 3
```

| Parámetro | Efecto |
|---|---|
| `--celda` | tamaño de la baldosa (mm) |
| `--lineas` | líneas paralelas por camino |
| `--vacio 0.1` | huecos aleatorios: deja respirar el patrón |
| `--semilla` | variación |

**Regla de oro**: la separación entre líneas es `celda / (lineas+1)`. Debe ser ≥ 2× el grosor de la pluma.
Con pluma 0.8 → `--celda 20 --lineas 4` (4 mm entre líneas).

**Variantes para explorar** (editando el script): baldosas de 3 tipos (rectas + arcos), celdas de distintos tamaños,
recortar el patrón dentro de una silueta (exporta la silueta como SVG y combínala en Inkscape con *Path → Intersection*).
