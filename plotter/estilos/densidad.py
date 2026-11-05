"""Control de densidad de tinta: ¿este SVG empapará o emborronará el papel con estas plumas?

Dibuja virtualmente cada trazo con el grosor REAL de su pluma y mide:
  1. Cobertura local: % de papel cubierto de tinta en cada ventana de 3x3 mm.
     Por encima de ~85 % las líneas se funden en una mancha y el papel se empapa.
  2. Pasadas: cuántas veces pasa la pluma por el mismo punto. 3+ pasadas = riesgo de
     papel mojado, bolitas o rotura.

  python densidad.py obra_plot.svg --plumas 0.5            (una pluma para todas las capas)
  python densidad.py madrid_plot.svg --plumas 0.7,0.3,0.2,0.8,0.5   (una por capa, en orden)

Sale con código 0 si es seguro plotear, 2 si no. Genera obra_densidad.png (mapa de calor).
"""
import argparse
import sys
import cv2
import numpy as np
import vpype

PX2MM = 25.4 / 96


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("svg")
    ap.add_argument("--plumas", required=True, help="grosor en mm: '0.5' o '0.7,0.3,...' (una por capa)")
    ap.add_argument("--max-cobertura", type=float, default=0.85, help="cobertura local máxima (0-1)")
    ap.add_argument("--ventana", type=float, default=3.0, help="mm de la ventana de medida")
    ap.add_argument("--max-pasadas", type=int, default=3, help="pasadas en un mismo punto que se consideran riesgo")
    ap.add_argument("--tolerancia", type=float, default=0.5, help="%% del área dibujada que puede superar los límites")
    ap.add_argument("--res", type=float, default=10, help="px por mm de la simulación")
    a = ap.parse_args()

    doc = vpype.read_multilayer_svg(a.svg, quantization=0.1, crop=False)
    pens = [float(x) for x in a.plumas.split(",")]
    lids = sorted(doc.layers)
    if len(pens) == 1:
        pens = pens * len(lids)
    if len(pens) != len(lids):
        sys.exit(f"Hay {len(lids)} capas pero diste {len(pens)} grosores de pluma")

    W, H = (np.array(doc.page_size) * PX2MM) if doc.page_size else (420, 594)
    r = a.res
    gw, gh = int(W * r) + 1, int(H * r) + 1
    total = np.zeros((gh, gw), np.uint16)
    per_layer = {}
    for lid, pen in zip(lids, pens):
        t = max(1, int(round(pen * r)))
        lay = np.zeros((gh, gw), np.uint16)
        for line in doc.layers[lid]:
            pts = np.c_[line.real, line.imag] * PX2MM * r
            x0, y0 = np.floor(pts.min(0)).astype(int) - t
            x1, y1 = np.ceil(pts.max(0)).astype(int) + t
            x0, y0 = max(x0, 0), max(y0, 0)
            x1, y1 = min(x1, gw - 1), min(y1, gh - 1)
            if x1 <= x0 or y1 <= y0:
                continue
            m = np.zeros((y1 - y0 + 1, x1 - x0 + 1), np.uint8)
            cv2.polylines(m, [np.round(pts - [x0, y0]).astype(np.int32)], False, 1, t, cv2.LINE_8)
            lay[y0:y1 + 1, x0:x1 + 1] += m
        per_layer[lid] = lay
        total += lay

    ink = (total > 0).astype(np.float32)
    k = max(3, int(a.ventana * r) | 1)
    cov = cv2.blur(ink, (k, k))
    drawn = cv2.dilate(ink, np.ones((k, k), np.uint8)) > 0      # zona con dibujo
    area_drawn = max(drawn.sum(), 1)
    hot_cov = (cov > a.max_cobertura) & drawn
    hot_pass = total >= a.max_pasadas
    pct_cov = 100 * hot_cov.sum() / area_drawn
    pct_pass = 100 * hot_pass.sum() / area_drawn

    print(f"Lienzo {W:.0f}x{H:.0f} mm · plumas {', '.join(f'capa {l}: {p} mm' for l, p in zip(lids, pens))}")
    print(f"Cobertura media en zona dibujada: {100 * ink[drawn].mean():.0f} %   (máx. local {100 * cov.max():.0f} %)")
    print(f"Zonas saturadas (> {a.max_cobertura:.0%} de tinta en {a.ventana:g} mm): {pct_cov:.2f} % del dibujo")
    print(f"Zonas con {a.max_pasadas}+ pasadas de pluma: {pct_pass:.2f} % del dibujo")

    bad = hot_cov | hot_pass
    if bad.any():
        blame = {lid: int((per_layer[lid][bad] > 0).sum()) for lid in lids}
        worst = max(blame, key=blame.get)
        print(f"Capa que más contribuye a las zonas problemáticas: {worst} (pluma {pens[lids.index(worst)]} mm)")

    # mapa de calor: gris = tinta, naranja = cerca del límite, rojo = problema
    vis = np.full((gh, gw, 3), 255, np.uint8)
    vis[ink > 0] = (90, 90, 90)
    vis[(cov > a.max_cobertura * 0.85) & drawn & (ink > 0)] = (0, 150, 255)
    vis[bad] = (0, 0, 230)
    out = a.svg.rsplit(".", 1)[0] + "_densidad.png"
    scale = 1600 / max(gw, gh)
    cv2.imwrite(out, cv2.resize(vis, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA))
    print(f"Mapa de calor: {out}")

    ok = pct_cov <= a.tolerancia and pct_pass <= a.tolerancia
    print("✅ DENSIDAD OK: seguro para plotear" if ok else
          "❌ DEMASIADA TINTA: no plotear así. Separa más las líneas, reduce la densidad o usa una pluma más fina")
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
