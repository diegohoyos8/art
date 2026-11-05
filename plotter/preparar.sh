#!/usr/bin/env bash
# Prepara cualquier SVG para el NextDraw: escala al papel, une y ordena trazos (menos
# levantadas de pluma = plot más rápido) y deja capas numeradas 1,2,3... (una por pluma).
#
# Uso: plotter/preparar.sh entrada.svg [papel] [margen] [salida.svg]
#   papel: a4 | a3 | letter | tabloid | 279.4x431.8mm ...   (defecto a4)
#   margen: 15mm (defecto)
set -euo pipefail
IN="$1"; PAPER="${2:-a4}"; MARGIN="${3:-15mm}"; OUT="${4:-${IN%.svg}_plot.svg}"
VPYPE="$(dirname "$0")/../.venv/bin/vpype"; [ -x "$VPYPE" ] || VPYPE=vpype
"$VPYPE" read "$IN" \
  linemerge --tolerance 0.3mm \
  linesimplify --tolerance 0.05mm \
  reloop linesort \
  layout --fit-to-margins "$MARGIN" "$PAPER" \
  write "$OUT" \
  stat | awk '/^Layer|^Totals/{l=$0} /^  Length:/{printf "%-9s con tinta: %6.1f m\n", l, $2*0.0254/96}
             /^  Pen-up length:/{printf "%-9s en el aire: %5.1f m\n", l, $3*0.0254/96}'
echo "Listo para plotear: $OUT"
