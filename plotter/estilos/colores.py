"""Imagen -> dibujo multicolor con las plumas de TU catálogo que mejor la reproducen.

1. Simula cómo se mezclan en el papel los tramados de cada pluma (las tintas se superponen
   y filtran la luz: modelo multiplicativo con la cobertura de cada tramado).
2. Prueba combinaciones de plumas del catálogo (plotter/plumas.json) y elige la que da
   menor error de color (ΔE, diferencia perceptual: <5 muy fiel, 5-10 bien, >15 lejos).
3. Genera una capa por pluma: líneas paralelas, cada color con su ángulo, que se dibujan
   o no según cuánta tinta de ese color necesita cada zona. La cobertura máxima por capa
   está limitada para que el papel no se empape (y luego preparar.sh lo verifica).

  python colores.py foto.jpg -o foto_color.svg --papel A3 --plumas 3
  python colores.py foto.jpg --plumas 3 --usar "Micron negro"      # obliga a incluir una
  python colores.py foto.jpg --solo-elegir --max 5                 # solo informe de fidelidad
"""
import argparse
import itertools
import json
import os
import cv2
import numpy as np
from skimage.color import rgb2lab
import plotlib

CAT = os.path.join(os.path.dirname(__file__), "..", "plumas.json")
BAYER8 = np.array([0, 4, 2, 6, 1, 5, 3, 7])


def hex2rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255


def to_lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)


def simulate(c, A, paper):
    """c: (P,N) coberturas; A: (N,3) absorción por canal; paper (3,) lineal -> (P,3) lineal."""
    g = 1 - c[:, :, None] * A[None, :, :]          # (P,N,3)
    return paper[None, :] * np.prod(g, axis=1)


def solve(target_lin, A, paper, cmax, ucap, iters=250):
    """Coberturas por píxel que mejor reproducen target (pérdida en espacio gamma ~ perceptual)."""
    P, N = len(target_lin), len(A)
    c = np.full((P, N), 0.1)
    tgt = target_lin ** (1 / 2.2)
    m = np.zeros_like(c); v = np.zeros_like(c)
    lr, b1, b2 = 0.03, 0.9, 0.999
    for t in range(1, iters + 1):
        g = 1 - c[:, :, None] * A[None, :, :]
        f = paper[None, :] * np.prod(g, axis=1)                       # (P,3)
        fe = np.maximum(f, 1e-6) ** (1 / 2.2)
        dL_df = 2 * (fe - tgt) * fe / (2.2 * np.maximum(f, 1e-6))     # (P,3)
        df_dc = -A[None, :, :] * f[:, None, :] / np.maximum(g, 1e-6)  # (P,N,3)
        grad = np.einsum("pc,pnc->pn", dL_df, df_dc)
        m = b1 * m + (1 - b1) * grad; v = b2 * v + (1 - b2) * grad ** 2
        c -= lr * (m / (1 - b1 ** t)) / (np.sqrt(v / (1 - b2 ** t)) + 1e-8)
        c = np.clip(c, 0, cmax)
        union = 1 - np.prod(1 - c, axis=1)                             # tinta total
        over = union > ucap
        if over.any():
            c[over] *= (ucap / union[over])[:, None]
    return c


def tone_map(img_srgb, A, paper, cmax, ucap):
    """Comprime la luminosidad de la imagen al rango que las plumas pueden dar sin saturar."""
    from skimage.color import lab2rgb
    darkest = paper.copy()
    k = int(np.argmax(A.mean(1)))                       # la pluma más oscura, a tope
    darkest = simulate(np.array([[0.0] * len(A)]) + np.eye(len(A))[k] * min(cmax, ucap), A, paper)[0]
    Lmin = rgb2lab(to_srgb(darkest).reshape(1, 1, 3))[0, 0, 0]
    Lpap = rgb2lab(to_srgb(paper).reshape(1, 1, 3))[0, 0, 0]
    lab = rgb2lab(img_srgb)
    lo, hi = np.percentile(lab[..., 0], [1, 99])
    lab[..., 0] = Lmin + (np.clip(lab[..., 0], lo, hi) - lo) / max(hi - lo, 1e-6) * (Lpap - Lmin)
    return np.clip(lab2rgb(lab), 0, 1)


def delta_e(a_lin, b_lin):
    la, lb = rgb2lab(to_srgb(a_lin).reshape(-1, 1, 3)), rgb2lab(to_srgb(b_lin).reshape(-1, 1, 3))
    return float(np.linalg.norm(la - lb, axis=-1).mean())


def evaluate(idx, pens, target, paper, cmax, ucap):
    A = np.array([1 - np.clip(to_lin(hex2rgb(pens[i]["color"])) / paper, 0, 1) for i in idx])
    c = solve(target, A, paper, cmax, ucap, iters=150)
    return delta_e(simulate(c, A, paper), target), c, A


def choose(pens, target, paper, k, forced, cmax, ucap):
    """Búsqueda voraz + intercambios: rápida y casi óptima."""
    sel = list(forced)
    cache = {}

    def score(s):
        key = tuple(sorted(s))
        if key not in cache:
            cache[key] = evaluate(list(key), pens, target, paper, cmax, ucap)[0]
        return cache[key]

    while len(sel) < k:
        best = min((i for i in range(len(pens)) if i not in sel), key=lambda i: score(sel + [i]))
        sel.append(best)
    improved = True
    while improved:
        improved = False
        for pos in range(len(forced), len(sel)):
            for i in range(len(pens)):
                if i in sel:
                    continue
                trial = sel.copy(); trial[pos] = i
                if score(trial) < score(sel) - 1e-3:
                    sel, improved = trial, True
    return sel, score(sel)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("imagen"); ap.add_argument("-o", "--salida", default="color.svg")
    ap.add_argument("--catalogo", default=CAT)
    ap.add_argument("--papel", default="A3"); ap.add_argument("--horizontal", action="store_true")
    ap.add_argument("--plumas", type=int, default=3, help="número de plumas a usar")
    ap.add_argument("--max", type=int, default=5, help="hasta cuántas plumas incluir en el informe")
    ap.add_argument("--usar", action="append", default=[], help="pluma obligatoria (nombre del catálogo)")
    ap.add_argument("--cobertura-max", type=float, default=0.45, help="tinta máxima por capa (0-1)")
    ap.add_argument("--tinta-total", type=float, default=0.55, help="tinta máxima sumando capas (0-1)")
    ap.add_argument("--color-papel", help="color del papel, p.ej. #ece3d0 (crema). Por defecto el del catálogo")
    ap.add_argument("--sin-compresion", action="store_true", help="no comprimir tonos (oscuros se aplanan)")
    ap.add_argument("--contornos", type=int, default=0, help="añade contornos (line art) con la pluma más oscura; 1-5 = detalle")
    ap.add_argument("--solo-elegir", action="store_true")
    ap.add_argument("--margen", type=float, default=15)
    a = ap.parse_args()

    cat = json.load(open(a.catalogo))
    pens, paper = cat["plumas"], to_lin(hex2rgb(a.color_papel or cat.get("papel", "#ffffff")))
    names = [p["nombre"] for p in pens]
    forced = [names.index(n) for n in a.usar]

    img = cv2.cvtColor(cv2.imread(a.imagen), cv2.COLOR_BGR2RGB).astype(float) / 255
    small = cv2.resize(img, (48, int(48 * img.shape[0] / img.shape[1])), interpolation=cv2.INTER_AREA)
    target = to_lin(small.reshape(-1, 3))

    print(f"Fidelidad (ΔE medio: <5 muy fiel · 5-10 bien · >15 lejos) — cobertura máx. {a.cobertura_max:.0%}/capa")
    results = {}
    for k in range(max(1, len(forced)), max(a.max, a.plumas) + 1):
        sel, de = choose(pens, target, paper, k, forced, a.cobertura_max, a.tinta_total)
        results[k] = sel
        mark = "  ← elegido" if k == a.plumas else ""
        print(f"  {k} plumas: ΔE {de:5.1f}  {' + '.join(names[i] for i in sel)}{mark}")
    if a.solo_elegir:
        return

    sel = results[a.plumas]
    sel.sort(key=lambda i: -hex2rgb(pens[i]["color"]).mean())     # claros primero
    # coberturas a resolución de trabajo
    W, H = plotlib.paper(a.papel, a.horizontal)
    m = a.margen
    s = min((W - 2 * m) / img.shape[1], (H - 2 * m) / img.shape[0])
    dw, dh = img.shape[1] * s, img.shape[0] * s
    ox, oy = (W - dw) / 2, (H - dh) / 2
    work = cv2.resize(img, (int(dw), int(dh)), interpolation=cv2.INTER_AREA)   # 1 px = 1 mm
    work = cv2.GaussianBlur(work, (0, 0), 0.7)
    A = np.array([1 - np.clip(to_lin(hex2rgb(pens[i]["color"])) / paper, 0, 1) for i in sel])
    if not a.sin_compresion:
        work = tone_map(work, A, paper, a.cobertura_max, a.tinta_total)
    tgt = to_lin(work.reshape(-1, 3))
    c = solve(tgt, A, paper, a.cobertura_max, a.tinta_total).reshape(work.shape[0], work.shape[1], -1)
    sim = to_srgb(simulate(c.reshape(-1, len(sel)), A, paper)).reshape(work.shape)
    base = os.path.splitext(a.salida)[0]
    cv2.imwrite(base + "_simulacion.png", cv2.cvtColor((np.hstack([work, sim]) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))

    layers, colors, widths = {}, {}, {}
    for li, pi in enumerate(sel):
        pen = pens[pi]; w = pen["grosor"]
        spacing = w / a.cobertura_max                       # todas las líneas = cobertura máxima
        th = np.deg2rad(15 + li * 180 / len(sel))
        d, n = np.array([np.cos(th), np.sin(th)]), np.array([-np.sin(th), np.cos(th)])
        corners = np.array([[0, 0], [dw, 0], [0, dh], [dw, dh]])
        pn, pd = corners @ n, corners @ d
        cov = c[:, :, li] / a.cobertura_max
        lines = []
        step = 0.4
        ts = np.arange(pd.min(), pd.max(), step)
        for k, off in enumerate(np.arange(pn.min(), pn.max(), spacing)):
            pts = off * n + ts[:, None] * d
            inside = (pts[:, 0] >= 0) & (pts[:, 0] < dw - 1) & (pts[:, 1] >= 0) & (pts[:, 1] < dh - 1)
            if not inside.any():
                continue
            val = np.zeros(len(pts))
            val[inside] = cov[pts[inside, 1].astype(int), pts[inside, 0].astype(int)]
            thr = (BAYER8[k % 8] + 0.5) / 8
            on = inside & (val > thr)
            edges = np.flatnonzero(np.diff(np.r_[0, on.astype(int), 0]))
            for s0, s1 in zip(edges[::2], edges[1::2]):
                if (s1 - s0) * step >= 1.0:                 # descarta puntitos
                    lines.append(np.array([pts[s0], pts[s1 - 1]]) + [ox, oy])
        name = pen["nombre"].replace(" ", "_")
        layers[name] = lines; colors[name] = pen["color"]; widths[name] = w
    if a.contornos:
        gray = cv2.cvtColor((cv2.resize(img, (int(dw * 4), int(dh * 4))) * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        gray = cv2.bilateralFilter(gray, 9, 60, 60)
        hi = {1: 200, 2: 150, 3: 110, 4: 80, 5: 55}[max(1, min(5, a.contornos))]
        edges = cv2.Canny(gray, hi / 2.5, hi)
        cnts, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        dark = max(range(len(sel)), key=lambda li: A[li].mean())
        name = pens[sel[dark]]["nombre"].replace(" ", "_")
        n0 = len(layers[name])
        for cc in cnts:
            if cv2.arcLength(cc, False) < 40:
                continue
            cc = cv2.approxPolyDP(cc, 1.5, False)[:, 0, :].astype(float) / 4 + [ox, oy]
            layers[name].append(cc)
        print(f"Contornos añadidos a la capa de {pens[sel[dark]]['nombre']}: {len(layers[name]) - n0} trazos")
    plotlib.write_svg(a.salida, layers, (W, H), colors=colors, widths=widths)
    print("Plumas por capa (en este orden): " + ", ".join(f"{li + 1}={pens[i]['nombre']} {pens[i]['grosor']}" for li, i in enumerate(sel)))
    print("Para preparar: preparar.sh " + a.salida + f" {a.papel.lower()} " + ",".join(str(pens[i]["grosor"]) for i in sel))
    print("Simulación del color: " + base + "_simulacion.png")


if __name__ == "__main__":
    main()
