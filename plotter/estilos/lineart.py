"""Imagen -> dibujo de líneas (contornos), estilo plano/blueprint/ilustración.

Detecta bordes (Canny) y los convierte en trazos vectoriales. Ideal para logos, planos,
ilustraciones con contornos marcados y fotos con buen contraste.

  python lineart.py foto.jpg -o foto_lineas.svg --papel A4 --detalle 2
  --detalle 1..5 (más alto = más líneas), --min-largo en px para descartar ruido
"""
import argparse
import cv2
import numpy as np
import plotlib


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("imagen"); ap.add_argument("-o", "--salida", default="lineart.svg")
    ap.add_argument("--papel", default="A4"); ap.add_argument("--horizontal", action="store_true")
    ap.add_argument("--detalle", type=int, default=2)
    ap.add_argument("--min-largo", type=int, default=12)
    ap.add_argument("--suavizado", type=float, default=1.2, help="tolerancia de simplificación en px")
    a = ap.parse_args()

    img = cv2.imread(a.imagen, cv2.IMREAD_GRAYSCALE)
    scale = 1600 / max(img.shape)
    img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    img = cv2.bilateralFilter(img, 9, 60, 60)
    hi = {1: 200, 2: 150, 3: 110, 4: 80, 5: 55}[max(1, min(5, a.detalle))]
    edges = cv2.Canny(img, hi / 2.5, hi)
    edges = cv2.ximgproc.thinning(edges) if hasattr(cv2, "ximgproc") else edges
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    lines = []
    for c in contours:
        if cv2.arcLength(c, False) < a.min_largo:
            continue
        c = cv2.approxPolyDP(c, a.suavizado, False)[:, 0, :]
        lines.append(c.astype(float))
    size = plotlib.paper(a.papel, a.horizontal)
    plotlib.write_svg(a.salida, plotlib.fit({"lineas": lines}, size), size)


if __name__ == "__main__":
    main()
