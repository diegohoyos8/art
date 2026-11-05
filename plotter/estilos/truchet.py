"""Patrón Truchet de arcos concéntricos (líneas paralelas que serpentean, ideal con pluma gruesa).

  python truchet.py -o truchet.svg --papel A4 --celda 20 --lineas 4 --semilla 3
"""
import argparse
import numpy as np
import plotlib


def arc(cx, cy, r, a0, a1, n=24):
    t = np.linspace(a0, a1, n)
    return np.c_[cx + r * np.cos(t), cy + r * np.sin(t)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--salida", default="truchet.svg")
    ap.add_argument("--papel", default="A4"); ap.add_argument("--horizontal", action="store_true")
    ap.add_argument("--celda", type=float, default=18, help="tamaño de la baldosa en mm")
    ap.add_argument("--lineas", type=int, default=4, help="líneas paralelas por arco")
    ap.add_argument("--vacio", type=float, default=0.0, help="probabilidad de baldosa vacía")
    ap.add_argument("--semilla", type=int, default=1)
    a = ap.parse_args()
    rng = np.random.default_rng(a.semilla)
    W, H = plotlib.paper(a.papel, a.horizontal)
    c = a.celda
    nx, ny = int((W - 30) // c), int((H - 30) // c)
    ox, oy = (W - nx * c) / 2, (H - ny * c) / 2
    # radios centrados en c/2 para que los arcos conecten con las baldosas vecinas
    radii = c / 2 + (np.arange(a.lineas) - (a.lineas - 1) / 2) * (c / (a.lineas + 1))
    lines = []
    for j in range(ny):
        for i in range(nx):
            x0, y0 = ox + i * c, oy + j * c
            r = rng.random()
            if r < a.vacio:
                continue
            if r < a.vacio + (1 - a.vacio) / 2:   # esquinas sup-izq e inf-der
                corners = [(x0, y0, 0, np.pi / 2), (x0 + c, y0 + c, np.pi, 1.5 * np.pi)]
            else:                                   # esquinas sup-der e inf-izq
                corners = [(x0 + c, y0, np.pi / 2, np.pi), (x0, y0 + c, 1.5 * np.pi, 2 * np.pi)]
            for cx, cy, a0, a1 in corners:
                for rr in radii:
                    lines.append(arc(cx, cy, rr, a0, a1))
    plotlib.write_svg(a.salida, {"truchet": lines}, (W, H), stroke_mm=0.8)


if __name__ == "__main__":
    main()
