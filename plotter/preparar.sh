#!/usr/bin/env bash
# Prepara cualquier SVG para el NextDraw y COMPRUEBA QUE NO EMPAPE EL PAPEL.
#
#   1. Escala el dibujo al papel (lienzo) con margen.
#   2. Une y ordena los trazos (menos levantadas de pluma = plot más rápido).
#   3. Asigna a cada capa el grosor real de su pluma.
#   4. Simula la tinta con esos grosores y bloquea si hay zonas saturadas.
#
# Uso: plotter/preparar.sh entrada.svg PAPEL PLUMAS [MARGEN] [SALIDA]
#   PAPEL : a4 | a3 | a5 | a6 | letter | tabloid | 279.4x431.8mm ...
#   PLUMAS: grosor en mm. Uno para todo ("0.5") o uno por capa en orden ("0.7,0.3,0.2,0.8,0.5")
#   MARGEN: 15mm por defecto
# Ejemplo: plotter/preparar.sh madrid.svg a3 0.7,0.3,0.2,0.8,0.5 10mm
set -euo pipefail
if [ $# -lt 3 ] || [[ "$3" == *mm ]]; then
  echo "Uso: $0 entrada.svg PAPEL PLUMAS [MARGEN] [SALIDA]   (p.ej. $0 obra.svg a3 0.5 15mm)"
  echo "PLUMAS es obligatorio: el grosor de la pluma decide si la tinta empapa el papel."
  exit 1
fi
IN="$1"; PAPER="$2"; PENS="$3"; MARGIN="${4:-15mm}"; OUT="${5:-${IN%.svg}_plot.svg}"
HERE="$(cd "$(dirname "$0")" && pwd)"
VPYPE="$HERE/../.venv/bin/vpype"; [ -x "$VPYPE" ] || VPYPE=vpype
PY="$HERE/../.venv/bin/python"; [ -x "$PY" ] || PY=python3

# grosor de pluma por capa
IFS=',' read -ra P <<< "$PENS"
PENARGS=()
if [ ${#P[@]} -eq 1 ]; then
  PENARGS=(penwidth -l all "${P[0]}mm")
else
  for i in "${!P[@]}"; do PENARGS+=(penwidth -l "$((i + 1))" "${P[$i]}mm"); done
fi

"$VPYPE" read "$IN" \
  linemerge --tolerance 0.3mm \
  linesimplify --tolerance 0.05mm \
  reloop linesort \
  layout --fit-to-margins "$MARGIN" "$PAPER" \
  "${PENARGS[@]}" \
  write "$OUT" \
  stat | awk '/^Layer|^Totals/{l=$0} /^  Length:/{printf "%-9s con tinta: %6.1f m\n", l, $2*0.0254/96}
             /^  Pen-up length:/{printf "%-9s en el aire: %5.1f m\n", l, $3*0.0254/96}'

echo "--- Control de densidad de tinta ---"
if "$PY" "$HERE/estilos/densidad.py" "$OUT" --plumas "$PENS"; then
  echo "Listo para plotear: $OUT"
else
  echo "NO PLOTEAR TODAVÍA: $OUT tiene zonas con demasiada tinta (mira el *_densidad.png)."
  exit 2
fi
