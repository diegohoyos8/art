#!/usr/bin/env bash
# Clona y compila DrawingBotV3 (versión Free) y el runner sin interfaz.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
DBV3="$ROOT/DrawingBotV3"
if [ ! -d "$DBV3" ]; then
  git clone --depth 1 https://github.com/SonarSonic/DrawingBotV3 "$DBV3"
fi
# build.gradle trae clases Test no abstractas que rompen en Gradle 8+
sed -i 's/^class \(\w*\) extends Test/abstract class \1 extends Test/' "$DBV3/build.gradle"
(cd "$DBV3" && gradle shadowJar --no-daemon -q)
JAR=$(ls "$DBV3"/build/libs/*-all.jar | head -1)
rm -rf "$ROOT/build" && javac -cp "$JAR" -d "$ROOT/build" "$ROOT/src/drawingbot/HeadlessRunner.java"
echo "OK: $JAR"
