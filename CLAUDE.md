# Reglas del proyecto (arte con plotter NextDraw)

- Toda obra se define SIEMPRE con **lienzo (papel) y grosor de pluma por capa** antes de generarla.
  Si el usuario no los da, pregúntalos o usa los de la obra anterior y dilo.
- Los generadores que aceptan `--pluma` deben recibir el grosor real.
- Ninguna obra se entrega sin pasar `plotter/preparar.sh obra.svg PAPEL PLUMAS`, que ejecuta
  `plotter/estilos/densidad.py`. Si falla (tinta excesiva), ajusta parámetros (separación,
  densidad, pluma más fina) y regenera hasta que pase. Informa al usuario del resultado.
- Al cambiar de tamaño de papel o de pluma, vuelve a preparar y comprobar: reducir el tamaño junta las líneas.
- El NextDraw usa SVG (no G-code). Capas = plumas, nombres que empiezan por número.
- Catálogo de plumas: `plotter/plumas.json`. Cuando el usuario diga que tiene o compra una pluma,
  márcala con `"tengo": true` (añádela si no existe). Para obras de color usa `--solo-mias` si tiene
  suficientes plumas; si no, recomienda qué comprar comparando ambos informes.
- Responde en español.
