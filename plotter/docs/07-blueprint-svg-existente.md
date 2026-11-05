# 07 — Planos técnicos / blueprint y SVG existentes

Para dibujos que **ya son vectoriales**: planos (como el A380 de Orowan Studio), diagramas, logos, SVG de internet o de CAD.

## Pasos

1. **Consigue el vector**: SVG, PDF vectorial o DXF (CAD). Si solo tienes una imagen, conviértela con la guía 01-B (line art).
   - DXF/PDF → ábrelo en Inkscape → *Guardar como* SVG.
2. **Limpia en Inkscape**:
   - Quita rellenos (el plotter solo hace contornos): *Objeto → Relleno y borde → sin relleno, con borde*.
   - Si quieres zonas rellenas, rellénalas con líneas de sombreado (en Inkscape: extensión *Hatch fill* de la NextDraw/AxiDraw, o a mano).
   - Texto → fuentes Hershey (de un solo trazo).
3. **Prepara**: `plotter/preparar.sh plano.svg a3 0.5 20mm`
   El control de densidad marcó que el guerrero en line art con gel blanco 0.8 empapa el papel (incluso en A3);
   con **gel 0.5** pasa. Usa 0.8 solo para dibujos con pocas líneas.
4. **Look blueprint**: papel azul marino o negro de ≥ 200 g + **gel blanco 0.5** (Sakura Gelly Roll 05 blanco, Uni-ball Signo 0.5); el 0.8 (Signo UM-153, Gelly Roll 08) solo para diseños con pocas líneas.
   Plotea **lento** (el gel blanco necesita tiempo para cargar tinta) y deja secar antes de tocar.
