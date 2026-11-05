"""Flow field generativo: muchas curvas que siguen un campo de ruido (estilo trazos de pincel/pelo).

  python flowfield.py -o flow.svg --papel A3 --lineas 1500 --semilla 7
  --imagen foto.jpg  -> la densidad de líneas sigue lo oscuro de la imagen
"""
import argparse
import numpy as np
import plotlib


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--salida", default="flowfield.svg")
    ap.add_argument("--papel", default="A3"); ap.add_argument("--horizontal", action="store_true")
    ap.add_argument("--lineas", type=int, default=1200)
    ap.add_argument("--largo", type=float, default=60, help="largo medio de cada curva (mm)")
    ap.add_argument("--escala", type=float, default=180, help="tamaño de los remolinos (mm)")
    ap.add_argument("--direccion", type=float, default=-60, help="ángulo dominante en grados")
    ap.add_argument("--caos", type=float, default=1.2, help="cuánto se desvía del ángulo dominante (radianes)")
    ap.add_argument("--imagen", help="usar imagen como mapa de densidad")
    ap.add_argument("--semilla", type=int, default=1)
    ap.add_argument("--margen", type=float, default=15)
    a = ap.parse_args()

    rng = np.random.default_rng(a.semilla)
    W, H = plotlib.paper(a.papel, a.horizontal)
    res = 2  # celdas por mm
    gh, gw = int(H * res), int(W * res)
    field = plotlib.value_noise((gh, gw), a.escala * res, a.semilla)
    ang = np.deg2rad(a.direccion) + (field - 0.5) * 2 * a.caos

    dens = None
    if a.imagen:
        import cv2
        im = cv2.imread(a.imagen, cv2.IMREAD_GRAYSCALE)
        dens = 1 - cv2.resize(im, (gw, gh)).astype(float) / 255

    lines, step = [], 0.5
    m = a.margen
    while len(lines) < a.lineas:
        x, y = rng.uniform(m, W - m), rng.uniform(m, H - m)
        if dens is not None and rng.random() > dens[int(y * res) % gh, int(x * res) % gw] ** 1.5:
            continue
        L = rng.gamma(2.0, a.largo / 2)
        pts = [(x, y)]
        for _ in range(int(L / step)):
            gy, gx = int(y * res), int(x * res)
            if not (m <= x <= W - m and m <= y <= H - m):
                break
            t = ang[min(gy, gh - 1), min(gx, gw - 1)]
            x += np.cos(t) * step; y += np.sin(t) * step
            pts.append((x, y))
        if len(pts) > 4:
            lines.append(np.array(pts)[::2])
    plotlib.write_svg(a.salida, {"flujo": lines}, (W, H), stroke_mm=0.5)


if __name__ == "__main__":
    main()
