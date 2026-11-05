# 04 — Flow fields (trazos orgánicos generativos)

Miles de curvas que siguen un campo de dirección suave: parecen pelo, hierba, viento o pinceladas (como el lienzo de florianmarkus).

```bash
cd plotter/estilos
python flowfield.py -o flow.svg --papel A3 --pluma 0.5 --lineas 1500 --semilla 7
```

| Parámetro | Efecto |
|---|---|
| `--pluma 0.5` | grosor de tu pluma: las curvas nunca se acercan a menos de 3× ese grosor |
| `--separacion` | fuerza otra separación mínima (mm) |
| `--lineas` | intentos de curva (se dibujan solo las que caben) |
| `--largo 60` | largo medio en mm |
| `--escala 180` | tamaño de los remolinos (más alto = más suave) |
| `--direccion -60` | ángulo dominante en grados |
| `--caos 1.2` | 0 = todas paralelas, 3 = remolinos |
| `--imagen foto.jpg` | la densidad sigue lo oscuro de una imagen: retrato o paisaje hecho de flujo |
| `--semilla` | cada número es una obra distinta: **anótalo** si te gusta |

**Pasos:** genera 10 semillas en A6, elige 1–2, súbelas a tamaño final, `preparar.sh flow.svg a3 0.5`, plotea.
**Material:** sobre lienzo o papel texturado usa rotuladores de punta de pincel o plumas de tinta pigmentada gruesas (0.8+).
