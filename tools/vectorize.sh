#!/usr/bin/env bash
# Uso: tools/vectorize.sh <imagen> [carpeta_salida] [PFM] [formatos]
#   PFM: "Sketch Lines PFM" (defecto) | "Sketch Squares PFM" | "Spiral PFM"
#   formatos: svg,gcode,pdf,png (defecto svg,gcode,png)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
JAR=$(ls "$ROOT"/DrawingBotV3/build/libs/*-all.jar 2>/dev/null | head -1 || true)
[ -z "$JAR" ] && { echo "Ejecuta primero tools/setup.sh"; exit 1; }
IMG="$1"; OUT="${2:-output}"; PFM="${3:-Sketch Lines PFM}"; FMT="${4:-svg,gcode,png}"
RUN=(java -cp "$JAR:$ROOT/build" drawingbot.HeadlessRunner "$IMG" "$OUT" "$PFM" "$FMT")
if [ -z "${DISPLAY:-}" ]; then xvfb-run -a "${RUN[@]}"; else "${RUN[@]}"; fi 2>&1 | grep --line-buffered "\[runner\]"
