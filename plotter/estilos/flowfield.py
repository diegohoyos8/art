"""Flow field generativo: curvas que siguen un campo de ruido (estilo trazos de pincel/pelo).

Las curvas NUNCA se acercan entre sí más que --separacion (por defecto 3x el grosor de la
pluma), así la tinta no se acumula ni empapa el papel.

  python flowfield.py -o flow.svg --papel A3 --pluma 0.5 --lineas 1500 --semilla 7
  --imagen foto.jpg  -> más juntas en lo oscuro, más separadas en lo claro
"""
import argparse
import numpy as np
import plotlib


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--salida", default="flowfield.svg")
    ap.add_argument("--papel", default="A3"); ap.add_argument("--horizontal", action="store_true")
    ap.add_argument("--pluma", type=float, default=0.5, help="grosor de la pluma en mm")
    ap.add_argument("--separacion", type=float, help="mm mínimos entre curvas (defecto 3x pluma)")
    ap.add_argument("--lineas", type=int, default=1500, help="intentos de curva (máximo)")
    ap.add_argument("--largo", type=float, default=60, help="largo medio de cada curva (mm)")
    ap.add_argument("--escala", type=float, default=180, help="tamaño de los remolinos (mm)")
    ap.add_argument("--direccion", type=float, default=-60, help="ángulo dominante en grados")
    ap.add_argument("--caos", type=float, default=1.2, help="cuánto se desvía del ángulo dominante (radianes)")
    ap.add_argument("--imagen", help="usar imagen como mapa de densidad")
    ap.add_argument("--umbral", type=float, default=0.15, help="con --imagen: las curvas no entran donde la oscuridad es menor")
    ap.add_argument("--semilla", type=int, default=1)
    ap.add_argument("--margen", type=float, default=15)
    a = ap.parse_args()

    rng = np.random.default_rng(a.semilla)
    W, H = plotlib.paper(a.papel, a.horizontal)
    sep_min = a.separacion or 3 * a.pluma
    res = 2
    gh, gw = int(H * res), int(W * res)
    field = plotlib.value_noise((gh, gw), a.escala * res, a.semilla)
    ang = np.deg2rad(a.direccion) + (field - 0.5) * 2 * a.caos

    dens = None
    if a.imagen:
        import cv2
        im = cv2.imread(a.imagen, cv2.IMREAD_GRAYSCALE)
        dens = 1 - cv2.GaussianBlur(cv2.resize(im, (gw, gh)).astype(float) / 255, (0, 0), 2)
        lo, hi = np.percentile(dens, [5, 98])              # estira el contraste a 0..1
        dens = np.clip((dens - lo) / (hi - lo + 1e-9), 0, 1)

    # rejilla de ocupación: celda = sep_min/2; guarda la separación exigida en ese punto
    cell = sep_min / 2
    oh, ow = int(H / cell) + 2, int(W / cell) + 2
    occ = np.zeros((oh, ow), bool)

    def sep_at(x, y):
        if dens is None:
            return sep_min
        d = dens[min(int(y * res), gh - 1), min(int(x * res), gw - 1)]
        return sep_min * (1 + 5 * (1 - d) ** 1.5)   # claro -> hasta 6x más separado

    def free(x, y, sep, own):
        cx, cy = int(x / cell), int(y / cell)
        rr = int(np.ceil(sep / cell))
        y0, y1, x0, x1 = max(cy - rr, 0), cy + rr + 1, max(cx - rr, 0), cx + rr + 1
        blk = occ[y0:y1, x0:x1]
        if not blk.any():
            return True
        ys, xs = np.nonzero(blk)
        for yy, xx in zip(ys + y0, xs + x0):
            if (yy, xx) in own:
                continue
            if np.hypot((xx + 0.5) * cell - x, (yy + 0.5) * cell - y) < sep:
                return False
        return True

    lines, step, m = [], 0.5, a.margen
    for _ in range(a.lineas):
        x, y = rng.uniform(m, W - m), rng.uniform(m, H - m)
        if dens is not None and rng.random() > dens[int(y * res) % gh, int(x * res) % gw] ** 1.5:
            continue
        if not free(x, y, sep_at(x, y), set()):
            continue
        L = rng.gamma(2.0, a.largo / 2)
        pts, own = [(x, y)], {(int(y / cell), int(x / cell))}
        for _ in range(int(L / step)):
            t = ang[min(int(y * res), gh - 1), min(int(x * res), gw - 1)]
            nx, ny = x + np.cos(t) * step, y + np.sin(t) * step
            if not (m <= nx <= W - m and m <= ny <= H - m) or not free(nx, ny, sep_at(nx, ny), own):
                break
            if dens is not None and dens[min(int(ny * res), gh - 1), min(int(nx * res), gw - 1)] < a.umbral:
                break                                    # no invade zonas claras: mantiene la forma
            x, y = nx, ny
            pts.append((x, y)); own.add((int(y / cell), int(x / cell)))
        if len(pts) > 6:
            for cy_, cx_ in own:
                occ[cy_, cx_] = True
            lines.append(np.array(pts)[::2])
    print(f"Separación mínima entre curvas: {sep_min:.2f} mm (pluma {a.pluma} mm)")
    plotlib.write_svg(a.salida, {"flujo": lines}, (W, H), stroke_mm=a.pluma)


if __name__ == "__main__":
    main()
