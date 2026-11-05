"""Retrato con trazos que siguen la forma (estilo grabado / huella dactilar).

Calcula la orientación de la imagen (tensor de estructura) y dibuja guiones/curvas
que fluyen a lo largo de los contornos. Lo oscuro = trazos más largos y apretados.

  python retrato_flujo.py cara.jpg -o cara.svg --papel A4 --espaciado 1.2
"""
import argparse
import cv2
import numpy as np
import plotlib


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("imagen"); ap.add_argument("-o", "--salida", default="retrato_flujo.svg")
    ap.add_argument("--papel", default="A4"); ap.add_argument("--horizontal", action="store_true")
    ap.add_argument("--espaciado", type=float, default=0.5, help="mm mínimos entre trazos en zonas oscuras")
    ap.add_argument("--claro", type=float, default=4.5, help="espaciado en zonas claras (mm)")
    ap.add_argument("--largo-max", type=float, default=14, help="mm")
    ap.add_argument("--umbral", type=float, default=0.2, help="0-1: por debajo de esta oscuridad no se dibuja")
    ap.add_argument("--gamma", type=float, default=0.8, help="<1 oscurece, >1 aclara")
    ap.add_argument("--semilla", type=int, default=1)
    a = ap.parse_args()
    rng = np.random.default_rng(a.semilla)

    W, H = plotlib.paper(a.papel, a.horizontal)
    m = 12
    img = cv2.imread(a.imagen, cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
    ih, iw = img.shape
    s = min((W - 2 * m) / iw, (H - 2 * m) / ih)           # mm por px
    res = 4                                                # px de trabajo por mm
    gw, gh = int(iw * s * res), int(ih * s * res)
    img = cv2.resize(img, (gw, gh), interpolation=cv2.INTER_AREA)
    img = cv2.createCLAHE(2.0, (8, 8)).apply((img * 255).astype(np.uint8)).astype(np.float32) / 255
    dark = 1 - cv2.GaussianBlur(img, (0, 0), 1.5)
    lo, hi = np.percentile(dark, [3, 97])                 # estira el contraste a 0..1
    dark = np.clip((dark - lo) / (hi - lo + 1e-9), 0, 1) ** a.gamma

    # orientación: tangente a los contornos (perpendicular al gradiente)
    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=5); gy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=5)
    sig = 6 * res
    jxx = cv2.GaussianBlur(gx * gx, (0, 0), sig); jyy = cv2.GaussianBlur(gy * gy, (0, 0), sig)
    jxy = cv2.GaussianBlur(gx * gy, (0, 0), sig)
    theta = 0.5 * np.arctan2(2 * jxy, jxx - jyy) + np.pi / 2

    cell = a.espaciado * res / 2
    occ = np.zeros((int(gh / cell) + 1, int(gw / cell) + 1), np.float32)  # guarda espaciado ocupado

    def free(x, y, sp):
        cx, cy = int(x / cell), int(y / cell)
        r = int(np.ceil(sp / cell))
        return not occ[max(0, cy - r):cy + r + 1, max(0, cx - r):cx + r + 1].any()

    def mark(x, y):
        occ[min(int(y / cell), occ.shape[0] - 1), min(int(x / cell), occ.shape[1] - 1)] = 1

    seeds = np.stack(np.meshgrid(np.arange(0, gw, cell), np.arange(0, gh, cell)), -1).reshape(-1, 2)
    seeds = seeds + rng.uniform(0, cell, seeds.shape)
    rng.shuffle(seeds)
    seeds = sorted(seeds, key=lambda p: -dark[min(int(p[1]), gh - 1), min(int(p[0]), gw - 1)])  # oscuro primero

    lines = []
    for sx, sy in seeds:
        sx, sy = min(sx, gw - 2), min(sy, gh - 2)
        d = dark[int(min(sy, gh - 1)), int(min(sx, gw - 1))]
        if d < a.umbral:
            continue
        sp = (a.claro + (a.espaciado - a.claro) * d) * res
        if not free(sx, sy, sp * 0.9):
            continue
        L = (2 + a.largo_max * d ** 1.3) * res
        path = []
        for sign in (1, -1):
            x, y, pts, prev = sx, sy, [], None
            for _ in range(int(L / 2)):
                t = theta[int(y), int(x)]
                v = np.array([np.cos(t), np.sin(t)])
                if prev is not None and v @ prev < 0:
                    v = -v
                v = v * sign if prev is None else v
                prev = v
                x, y = x + v[0], y + v[1]
                if not (0 <= x < gw - 1 and 0 <= y < gh - 1) or not free(x, y, sp * 0.45):
                    break
                pts.append((x, y))
            path = pts[::-1] + [(sx, sy)] if sign == 1 else path + pts
        if len(path) < 3:
            continue
        for x, y in path:
            mark(x, y)
        mark(sx, sy)
        lines.append(np.array(path)[::2] / res + [m + (W - 2 * m - iw * s) / 2, m + (H - 2 * m - ih * s) / 2])
    plotlib.write_svg(a.salida, {"trazos": lines}, (W, H), stroke_mm=0.4)


if __name__ == "__main__":
    main()
