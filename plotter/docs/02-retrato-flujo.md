# 02 — Retrato de flujo (guiones que siguen la forma)

Estilo de las caras hechas con miles de guiones curvos que rodean nariz, ojos y arrugas (como el trabajo de Václav Zahrádka).
El script calcula hacia dónde "fluye" la imagen y dibuja trazos a lo largo de los contornos:
zonas oscuras = trazos largos y juntos, zonas claras = cortos y separados.

## Pasos

1. **Foto**: retrato con **luz lateral fuerte** (sombras marcadas), fondo liso, la cara llenando el encuadre. Blanco y negro con contraste alto.
2. **Genera**:
   ```bash
   cd plotter/estilos
   python retrato_flujo.py ../../input/cara.jpg -o cara.svg --papel A3
   ```
3. **Ajusta** (cambia una cosa cada vez):
   | Parámetro | Efecto |
   |---|---|
   | `--espaciado 0.5` | separación mínima (mm) en zonas oscuras. Debe ser ≥ grosor de la pluma |
   | `--claro 4.5` | separación en zonas claras (más alto = más blanco) |
   | `--largo-max 14` | largo de los trazos en lo oscuro |
   | `--umbral 0.2` | por debajo de esta oscuridad no se dibuja (fondo limpio) |
   | `--gamma 0.8` | <1 oscurece la imagen, >1 la aclara |
   | `--semilla N` | otra variación con los mismos parámetros |
4. **Prepara**: `plotter/preparar.sh cara.svg a3 0.4` y prueba en A5 primero (con pluma más fina).
5. **Pluma**: fineliner 0.3–0.5 negro. Velocidad media: son miles de trazos cortos, cada uno sube y baja la pluma.
