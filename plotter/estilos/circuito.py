"""Circuitos multicolor: haces de pistas paralelas que giran a 45/90°, con pads y vías.
Cada color es una capa = una pluma distinta.

  python circuito.py -o circuito.svg --papel A3 --pistas 60 --colores 4 --semilla 5
"""
import argparse
import numpy as np
import plotlib

DIRS = np.array([(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)], float)


def circle(cx, cy, r, n=20):
    t = np.linspace(0, 2 * np.pi, n)
    return np.c_[cx + r * np.cos(t), cy + r * np.sin(t)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--salida", default="circuito.svg")
    ap.add_argument("--papel", default="A3"); ap.add_argument("--horizontal", action="store_true")
    ap.add_argument("--pistas", type=int, default=50, help="número de haces")
    ap.add_argument("--colores", type=int, default=4)
    ap.add_argument("--paso", type=float, default=1.6, help="separación entre pistas de un haz (mm)")
    ap.add_argument("--semilla", type=int, default=1)
    a = ap.parse_args()
    rng = np.random.default_rng(a.semilla)
    W, H = plotlib.paper(a.papel, a.horizontal)
    m, g = 15, 4.0  # margen, rejilla (mm)
    names = ["negro", "rojo", "azul", "verde", "ocre", "violeta"][:a.colores]
    layers = {n: [] for n in names}
    occ = set()
    for _ in range(a.pistas):
        col = names[rng.integers(len(names))]
        k = int(rng.integers(1, 7))                   # pistas en el haz
        p = np.array([rng.uniform(m, W - m), rng.uniform(m, H - m)])
        p = np.round(p / g) * g
        d = int(rng.integers(0, 8, ) // 2 * 2)        # empieza en horizontal/vertical
        path = [p.copy()]
        for _ in range(int(rng.integers(4, 14))):
            seg = int(rng.integers(2, 10)) * g
            v = DIRS[d] / np.linalg.norm(DIRS[d])
            q = p + v * seg * (np.sqrt(2) if d % 2 else 1)
            if not (m < q[0] < W - m and m < q[1] < H - m):
                break
            key = tuple(np.round(q / g).astype(int))
            if key in occ:
                break
            occ.add(key)
            p = q; path.append(p.copy())
            d = (d + rng.choice([-1, 0, 1])) % 8       # gira 45° o sigue recto
        if len(path) < 2:
            continue
        path = np.array(path)
        for i in range(k):                            # desplaza cada pista del haz
            off = (i - (k - 1) / 2) * a.paso
            seg = np.diff(path, axis=0); nrm = np.c_[-seg[:, 1], seg[:, 0]]
            nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
            nv = np.vstack([nrm[0], (nrm[:-1] + nrm[1:]) / 2, nrm[-1]])
            nv /= np.linalg.norm(nv, axis=1, keepdims=True) + 1e-9
            pl = path + nv * off
            layers[col].append(pl)
            for end in (pl[0], pl[-1]):                # pads en los extremos
                if rng.random() < 0.6:
                    layers[col].append(circle(*end, 0.6))
        if rng.random() < 0.3:                         # chip / vía grande
            layers["negro"].append(circle(*path[-1], rng.uniform(1.5, 3.5)))
    plotlib.write_svg(a.salida, layers, (W, H), stroke_mm=0.4,
                      colors={"negro": "#111", "rojo": "#d62828", "azul": "#1d70b8", "verde": "#2a9d8f", "ocre": "#e9a400", "violeta": "#7b2cbf"})


if __name__ == "__main__":
    main()
