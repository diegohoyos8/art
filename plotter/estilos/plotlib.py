"""Utilidades comunes: escribir polilíneas (en mm) como SVG con capas tipo Inkscape.

Cada capa = una pluma. NextDraw / Inkscape reconocen las capas por su nombre ("1", "2"...).
"""
from __future__ import annotations
import numpy as np

PAPELES = {  # ancho x alto en mm (vertical)
    "A6": (105, 148), "A5": (148, 210), "A4": (210, 297), "A3": (297, 420), "A2": (420, 594), "A1": (594, 841),
    "letter": (215.9, 279.4), "tabloid": (279.4, 431.8),
    # áreas útiles aproximadas de los NextDraw
    "nextdraw8511": (215.9, 279.4), "nextdraw1117": (279.4, 431.8), "nextdraw2234": (558.8, 863.6),
}


def paper(name: str, landscape: bool = False):
    w, h = PAPELES[name] if name in PAPELES else PAPELES[name.upper()]
    return (h, w) if landscape else (w, h)


def write_svg(path, layers, size_mm, colors=None, stroke_mm=0.3, widths=None):
    """layers: dict nombre -> lista de polilíneas (arrays Nx2 en mm)."""
    w, h = size_mm
    colors = colors or {}
    widths = widths or {}
    default = ["#111111", "#d62828", "#1d70b8", "#2a9d8f", "#e9a400", "#7b2cbf"]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" '
           f'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
           f'width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">']
    for i, (name, lines) in enumerate(layers.items()):
        col = colors.get(name, default[i % len(default)])
        out.append(f'<g inkscape:groupmode="layer" inkscape:label="{i+1}-{name}" id="layer{i+1}" '
                   f'fill="none" stroke="{col}" stroke-width="{widths.get(name, stroke_mm)}" stroke-linecap="round" stroke-linejoin="round">')
        for pl in lines:
            pl = np.asarray(pl)
            if len(pl) < 2:
                continue
            pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in pl)
            out.append(f'<polyline points="{pts}"/>')
        out.append("</g>")
    out.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(out))
    n = sum(len(v) for v in layers.values())
    print(f"SVG: {path}  ({n} trazos, {len(layers)} capa(s), {w}x{h} mm)")


def fit(lines_by_layer, size_mm, margin_mm=15, flip_y=False):
    """Escala y centra todas las capas dentro del papel con margen."""
    allpts = np.vstack([np.asarray(p) for ls in lines_by_layer.values() for p in ls if len(p)])
    mn, mx = allpts.min(0), allpts.max(0)
    w, h = size_mm
    s = min((w - 2 * margin_mm) / max(mx[0] - mn[0], 1e-9), (h - 2 * margin_mm) / max(mx[1] - mn[1], 1e-9))
    off = np.array([(w - (mx[0] - mn[0]) * s) / 2, (h - (mx[1] - mn[1]) * s) / 2])
    res = {}
    for k, ls in lines_by_layer.items():
        out = []
        for p in ls:
            q = (np.asarray(p, float) - mn) * s
            if flip_y:
                q[:, 1] = (mx[1] - mn[1]) * s - q[:, 1]
            out.append(q + off)
        res[k] = out
    return res


def value_noise(shape, scale, seed=0, octaves=3):
    """Ruido suave 2D (para flow fields) sin dependencias extra."""
    import cv2
    rng = np.random.default_rng(seed)
    h, w = shape
    acc = np.zeros(shape, np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        cells = max(2, int(max(h, w) / (scale / 2 ** o)))
        g = rng.random((cells, cells)).astype(np.float32)
        acc += amp * cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC)
        tot += amp
        amp *= 0.5
    acc /= tot
    return (acc - acc.min()) / (acc.max() - acc.min() + 1e-9)
