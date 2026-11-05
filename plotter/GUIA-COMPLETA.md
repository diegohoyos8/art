# Guía completa: arte con plotter (NextDraw), de cero a la primera obra

> Resumen del proyecto y todo lo que necesitas entender para que salga bien.
> Los datos de la máquina son orientativos: confírmalos en la web y la documentación de Bantam Tools antes de comprar.

---

## 1. Cómo funciona un plotter de plumas

Un plotter como el NextDraw es, básicamente, **una mano robótica que sostiene una pluma**:

```
   ordenador ──USB──► placa de control ──► 2 motores paso a paso (mueven X e Y con correas)
   (envía el SVG                         └► 1 motor/servo pequeño (sube y baja la pluma)
    en tiempo real)
```

- **No "imprime"**: dibuja línea a línea, como tú a mano. Cada línea del archivo es un recorrido de la pluma.
- **Solo entiende líneas** (vectores). Una foto (píxeles) hay que convertirla antes en líneas → eso hacen los scripts de este repo.
- **La pluma baja por gravedad / con poca fuerza**. Por eso funcionan bien las plumas que pintan sin apretar.
- **El ordenador debe estar conectado todo el plot**: la máquina no guarda el dibujo, el software se lo va enviando. Un plot puede durar de 10 minutos a varias horas.
- **El papel no se mueve**: se fija a la mesa (cinta de pintor / tapete) y la pluma recorre el área de dibujo.
- **Varios colores = varias pasadas**: se dibuja la capa 1 con una pluma, se pausa, cambias la pluma, capa 2… sin tocar el papel.

## 2. Qué modelo elegir

| Modelo | Área (aprox.) | Papel | Comentario |
|---|---|---|---|
| NextDraw 8511 | 8.5 × 11 in | A4 / carta | Para aprender. Se te quedará pequeño pronto |
| **NextDraw 1117** | 11 × 17 in | **A3** / tabloide | **Recomendado**: A4 y A3, el tamaño ideal para láminas y mapas |
| NextDraw 2234 | 22 × 34 in | ~A1 | Piezas grandes; requiere mesa amplia y plots muy largos |

## 3. ¿iPad o PC?

| Tarea | iPad | Ordenador (Mac / Windows / Linux) |
|---|---|---|
| Diseñar / pedirme variaciones a mí (Claude) | ✅ | ✅ |
| Ver y descargar los SVG (GitHub, Drive) | ✅ | ✅ |
| Editar SVG a mano | ✅ con Affinity Designer o Linearity Curve | ✅ Inkscape (gratis) |
| **Controlar el plotter** | ❌ | ✅ **necesario** |

**El NextDraw necesita un ordenador** conectado por USB con el software de Bantam Tools. El iPad no puede controlarlo.
- Sirve cualquier portátil sencillo (no hace falta potencia): un Mac o PC antiguo, o un mini PC.
- Opción avanzada: un Raspberry Pi pegado al plotter ejecutando el control por línea de comandos (`nextdraw` en Python), y tú lo manejas desde el iPad por SSH (app Termius). Funciona, pero es más técnico; empieza con un portátil.

## 4. Software que necesitas

| Programa | Para qué | Dónde |
|---|---|---|
| **Software NextDraw de Bantam Tools** (extensión de Inkscape + herramientas/API) | Configurar la máquina, ajustar la altura de la pluma, plotear, plotear por capas, pausar | Web de Bantam Tools → Support / Software |
| **Inkscape** (gratis) | Abrir el SVG, revisar capas, añadir texto (Hershey), enviarlo al plotter con la extensión | inkscape.org |
| **Este repo** (`diegohoyos8/art`) | Generar el arte: mapas, retratos, patrones… | GitHub |
| **vpype** (opcional en tu PC) | Optimizar el SVG (ya te los entrego optimizados) | `pip install vpype` |

**Flujo real día a día:**
```
iPad: me pides una obra ─► yo genero el SVG en el repo ─► lo descargas en el ordenador
Ordenador: Inkscape abre el SVG ─► Extensiones → NextDraw ─► Plot (capa por capa)
```

## 5. Plumas, bolígrafos y pinceles: qué funciona

| Tipo | ¿Funciona? | Notas |
|---|---|---|
| **Fineliners de tinta pigmentada** (Sakura Pigma Micron, Staedtler, Uni Pin) | ✅✅ El mejor punto de partida | Línea constante, no se corre. 0.1–0.8 mm |
| **Gel** (Uni-ball Signo, Pilot G2, Gelly Roll) | ✅ | Colores vivos, blanco/metálicos para papel negro. Plotear más lento |
| **Estilográficas** | ✅ | Preciosas (como el vídeo de Lostpixels). Velocidad lenta y constante, tinta de calidad |
| **Rotuladores / Sharpie / Posca** | ✅ | Trazos gruesos; ideales para patrones tipo truchet. Ojo: traspasan papel fino |
| **Bolígrafo normal (BIC)** | ⚠️ | Necesita presión: la línea sale débil o se corta. Añadir peso al portaplumas ayuda |
| **Lápiz / grafito / color** | ⚠️ | Funciona con poca presión: tono suave. Mejor minas blandas |
| **Pinceles / rotuladores pincel** | ⚠️✅ | Posible, con trazo expresivo. Con pintura líquida hay que recargar: se pausa o se programan "visitas al tintero". Bantam tiene una sección "Paint" para esto |
| Plumas muy gruesas o pesadas | ❌/⚠️ | Si no caben en el portaplumas, hace falta un adaptador |

**Regla de oro**: si la pluma pinta sola, apoyada y sin apretar, funcionará en el plotter.

## 6. Papel y materiales iniciales (lista de compra)

- Papel liso de ≥ 200 g: Bristol (Canson / Strathmore), A4 y A3. Un bloc barato para pruebas.
- Papel negro o azul marino de ≥ 200 g para el gel blanco (mapas y blueprints).
- Fineliners Micron negro: 0.1, 0.3, 0.5, 0.8 (con repuestos de 0.3).
- Gel blanco Uni-ball Signo UM-153 o Gelly Roll 08.
- Cinta de pintor, regla, escuadra para alinear el papel.
- Presupuesto aproximado: plotter 1117 (~1.220 €) + materiales (~80–120 €) + ordenador si no tienes.

## 7. El proceso para cada obra (siempre igual)

1. **Idea y estilo** → elige uno de los 8 estilos (`plotter/README.md`).
2. **Fuente** → imagen, lugar del mapa o parámetros.
3. **Generar SVG** → script del estilo (o pídemelo a mí).
4. **Preparar** → `preparar.sh obra.svg a3 0.5`: escala, optimiza recorridos, te dice los metros de tinta y **comprueba que la tinta no empape el papel con esa pluma** (si no pasa, no se plotea).
5. **Revisar** en Inkscape: tamaño, márgenes, capas `1-…`, `2-…`.
6. **Configurar la máquina**: altura de la pluma (que toque el papel sin presionar), velocidad (empieza lento).
7. **Prueba** en A5/A6 papel barato. Ajusta.
8. **Plot final**: fija bien el papel, plotea capa por capa, colores claros primero.
9. **Archivar**: SVG + comando + semilla + foto en `proyectos/`.

## 8. Plan de aprendizaje recomendado (4 semanas)

| Semana | Objetivo | Proyectos |
|---|---|---|
| 1 | Conocer la máquina | Patrones de prueba (truchet, flow field) en A4 con Micron 0.5. Ajustar altura y velocidad |
| 2 | Imágenes | El guerrero (Sketch Lines y Espiral), line art de una ilustración, retrato de flujo de una foto propia |
| 3 | Mapas | Madrid A3 (OSM completo), tu barrio, una ciudad especial para regalar. Probar papel negro + gel blanco |
| 4 | Color | Circuito multicolor de 4 plumas, mapa con río en azul. Aprender registro entre capas |

## 9. Los 10 errores que arruinan un plot (y cómo evitarlos)

1. **Papel que se mueve** → fíjalo en las 4 esquinas, y más si plotea horas.
2. **Pluma demasiado baja** → arrastra o rompe el papel. Debe apenas tocar.
3. **Demasiada densidad** → la tinta empapa el papel. **Esto lo controla `preparar.sh` automáticamente** según el lienzo y la pluma.
4. **Diseñar en A4 y ampliar a A1** → diseña al tamaño final.
5. **Pluma que se seca** en plots largos → ten repuesto; mira los metros que da `preparar.sh`.
6. **Texto con fuentes normales** → sale hueco. Usa Hershey.
7. **Rellenos en el SVG** → el plotter solo hace contornos; convierte los rellenos en sombreado.
8. **Velocidad alta con gel o estilográfica** → líneas que se cortan. Más lento.
9. **No hacer prueba pequeña** → siempre A6 primero.
10. **No anotar la semilla y los parámetros** → nunca podrás repetir esa obra.

## 10. Qué tienes ya hecho en este repo

| Carpeta / archivo | Contenido |
|---|---|
| `plotter/README.md` | Índice de estilos y flujo |
| `plotter/docs/00…07` | Guía de cada estilo |
| `plotter/plumas.json` | Catálogo de tus plumas (color y grosor) para el estilo multicolor |
| `plotter/estilos/*.py` | Generadores: colores (imagen multicolor), mapa, mapa Madrid (callejero), line art, retrato de flujo, flow field, truchet, circuito |
| `plotter/preparar.sh` | Optimiza cualquier SVG para el NextDraw y bloquea si hay exceso de tinta |
| `plotter/estilos/densidad.py` | Simula la tinta con el grosor real de cada pluma |
| `tools/` | DrawingBotV3 sin interfaz (imagen → trazos tonales) |
| `plotter/ejemplos/` | Galería de muestra y el mapa de Madrid A3 listo |
