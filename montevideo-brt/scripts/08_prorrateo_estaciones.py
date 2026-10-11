"""Prorrateo por superficie de las viviendas de cada segmento entre entornos de estación.

Sin polígonos confiables, cada segmento se aproxima por un disco centrado en su centroide
(INE) con su área exacta del DBF de DINOT. Entorno de estación: buffer de 800 m recortado
por la celda de Voronoi de la estación (estación más cercana). Supuesto: viviendas
distribuidas uniformemente dentro del segmento.
"""
import sys, pandas as pd, geopandas as gpd, numpy as np
from shapely.ops import voronoi_diagram
from shapely.geometry import MultiPoint
D, T, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
g = gpd.read_file(f'{D}/segmentos_brt_2023.gpkg')
e = gpd.read_file(f'{D}/estaciones.geojson').to_crs(32721).sort_values('linea').drop_duplicates('nombre').reset_index(drop=True)
vor = gpd.GeoDataFrame(geometry=list(voronoi_diagram(MultiPoint(list(e.geometry)), envelope=e.buffer(5000).union_all().envelope).geoms), crs=32721)
cell = gpd.sjoin(vor, e[['id_estacion', 'geometry']], predicate='contains')
e = e.merge(cell[['id_estacion', 'geometry']].rename(columns={'geometry': 'celda'}), on='id_estacion')
e['entorno'] = [p.buffer(800).intersection(c) for p, c in zip(e.geometry, e.celda)]
ent = gpd.GeoDataFrame(e.drop(columns=['geometry', 'celda']), geometry='entorno', crs=32721)
g['radio'] = np.sqrt(g.AREA / np.pi)
disc = g.copy(); disc['geometry'] = g.geometry.buffer(g.radio, quad_segs=16)
x = gpd.overlay(disc[['segkey', 'TotViv', 'Viv_Desoc', 'V_Desoc_4', 'V_Desoc_5', 'V_Desoc_7', 'Viv_Degrad', 'V_Desoc_8', 'Viv_Temp', 'estructural', 'AREA', 'geometry']],
                ent[['id_estacion', 'linea', 'orden', 'nombre', 'eje_asignado_2025', 'entorno']].rename_geometry('geometry'), how='intersection')
x['w'] = x.area / x.AREA.clip(lower=1)
vals = ['TotViv', 'Viv_Desoc', 'V_Desoc_4', 'V_Desoc_5', 'V_Desoc_7', 'Viv_Degrad', 'V_Desoc_8', 'Viv_Temp', 'estructural']
for v in vals: x[v] = x[v] * x.w
k = ['id_estacion', 'linea', 'orden', 'nombre', 'eje_asignado_2025']
t = x.groupby(k)[vals].sum().round(0).astype(int)
t.insert(0, 'Segmentos que aportan', x.groupby(k).size())
t = t.rename(columns={'TotViv': 'Viviendas', 'Viv_Desoc': 'Desoc. no temporada', 'V_Desoc_4': 'Alquiler o venta', 'V_Desoc_5': 'Construcción o reparación',
                      'V_Desoc_7': 'Vacante', 'Viv_Degrad': 'Degradada', 'V_Desoc_8': 'Ignorado', 'Viv_Temp': 'Temporada', 'estructural': 'Estructural (vac.+degr.)'})
t['% no temporada'] = (100 * t['Desoc. no temporada'] / t.Viviendas).round(1)
t['% estructural'] = (100 * t['Estructural (vac.+degr.)'] / t.Viviendas).round(1)
t = t.reset_index().sort_values(['linea', 'orden'])
# comparación con la asignación por centroide
old = pd.read_csv(f'{T}/t8_por_estacion.csv')[['nombre', 'Viviendas', 'Estructural (vac.+degr.)']].rename(columns={'Viviendas': 'Viviendas (centroide)', 'Estructural (vac.+degr.)': 'Estructural (centroide)'})
t = t.merge(old, on='nombre', how='left')
t.to_csv(f'{T}/t10_prorrateo_por_estacion.csv', index=False)
with pd.ExcelWriter(f'{T}/Vacancia_por_estacion_BRT_2023.xlsx', mode='a', if_sheet_exists='replace') as w:
    t.to_excel(w, sheet_name='Prorrateo por superficie', index=False)
print('estaciones con datos:', len(t), 'de', len(e))
print(t[t['Viviendas (centroide)'].isna()][['nombre', 'Segmentos que aportan', 'Viviendas', 'Desoc. no temporada', 'Estructural (vac.+degr.)', '% no temporada', '% estructural']].to_string(index=False))
print('totales', t[['Viviendas', 'Desoc. no temporada', 'Estructural (vac.+degr.)']].sum().to_dict(), '| centroide', old[['Viviendas (centroide)', 'Estructural (centroide)']].sum().to_dict())
d = t.dropna(subset=['Viviendas (centroide)']); d = d.assign(dif=100 * (d.Viviendas / d['Viviendas (centroide)'] - 1))
print('cambio en viviendas por estación vs centroide: mediana %.0f %%, p10 %.0f %%, p90 %.0f %%' % (d.dif.median(), d.dif.quantile(.1), d.dif.quantile(.9)))
print(d.reindex(d.dif.abs().sort_values(ascending=False).index)[['nombre', 'Viviendas (centroide)', 'Viviendas', 'Estructural (centroide)', 'Estructural (vac.+degr.)']].head(8).to_string(index=False))
