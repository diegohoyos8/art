# 07 — Planos técnicos / blueprint y SVG existentes

Para dibujos que **ya son vectoriales**: planos (como el A380 de Orowan Studio), diagramas, logos, SVG de internet o de CAD.

## Pasos

1. **Consigue el vector**: SVG, PDF vectorial o DXF (CAD). Si solo tienes una imagen, conviértela con la guía 01-B (line art).
   - DXF/PDF → ábrelo en Inkscape → *Guardar como* SVG.
2. **Limpia en Inkscape**:
   - Quita rellenos (el plotter solo hace contornos): *Objeto → Relleno y borde → sin relleno, con borde*.
   - Si quieres zonas rellenas, rellénalas con líneas de sombreado (en Inkscape: extensión *Hatch fill* de la NextDraw/AxiDraw, o a mano).
   - Texto → fuentes Hershey (de un solo trazo).
3. **Prepara**: `plotter/preparar.sh plano.svg a3 20mm`
4. **Look blueprint**: papel azul marino o negro de ≥ 200 g + **gel blanco** (Uni-ball Signo UM-153, Sakura Gelly Roll 08 blanco).
   Plotea **lento** (el gel blanco necesita tiempo para cargar tinta) y deja secar antes de tocar.
