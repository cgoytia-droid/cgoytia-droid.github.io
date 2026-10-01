# Pipeline vacancia y vivienda promovida, BRT AMM

Insumos (no versionados, en la carpeta del proyecto en Dropbox):
`ocupacion_segmentos_2023.csv` (atributos de Ocupacion_de_la_Vivienda.dbf, DINOT),
`cma_v2_segmentos.csv` (centroides de segmento), `estaciones.geojson`
(estaciones_brt_corregidas_sobre_eje_2025), `deptos.geojson`,
`anv_vivienda_promovida.csv` (atributos de Vivienda_promovida_ANV_20260831.dbf).

    python3 01_base.py   <insumos> <insumos>
    python3 02_tablas.py <insumos> ../tablas
    python3 03_mapas.py  <insumos> ../figuras   # requiere t1 y anv_con_distancia en <insumos>
    python3 04_memo.py   ..

Clave de unión: `DEPTO + "-" + CODSEG` = campo `seg` de cma_v2_segmentos.
Los mapas usan centroides; con los polígonos del shapefile la unión es por CODSEG.
