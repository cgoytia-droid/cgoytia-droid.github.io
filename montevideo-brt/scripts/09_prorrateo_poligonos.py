"""Prorrateo exacto por superficie con los polígonos reales de los segmentos.

Uso: python3 09_prorrateo_poligonos.py <poligonos (shp/gpkg/geojson)> <insumos> <tablas>
Los polígonos deben traer CODSEG y DEPTO (capa Ocupacion_de_la_Vivienda de DINOT, o su
exportación desde QGIS). Entorno de estación: buffer de 800 m recortado por la celda de
Voronoi de la estación. Supuesto: viviendas uniformes dentro de cada segmento.
"""
import sys, pandas as pd, geopandas as gpd
from shapely.ops import voronoi_diagram
from shapely.geometry import MultiPoint
POL, D, T = sys.argv[1], sys.argv[2], sys.argv[3]
VALS = ['TotViv', 'Viv_Desoc', 'V_Desoc_4', 'V_Desoc_5', 'V_Desoc_7', 'Viv_Degrad', 'V_Desoc_8', 'Viv_Temp', 'estructural']
NOMBRES = {'TotViv': 'Viviendas', 'Viv_Desoc': 'Desoc. no temporada', 'V_Desoc_4': 'Alquiler o venta', 'V_Desoc_5': 'Construcción o reparación',
           'V_Desoc_7': 'Vacante', 'Viv_Degrad': 'Degradada', 'V_Desoc_8': 'Ignorado', 'Viv_Temp': 'Temporada', 'estructural': 'Estructural (vac.+degr.)'}

def entornos(est):
    e = est.to_crs(32721).sort_values('linea').drop_duplicates('nombre').reset_index(drop=True)
    env = e.buffer(5000).union_all().envelope
    vor = gpd.GeoDataFrame(geometry=list(voronoi_diagram(MultiPoint(list(e.geometry)), envelope=env).geoms), crs=32721)
    cell = gpd.sjoin(vor, e[['id_estacion', 'geometry']], predicate='contains')
    e = e.merge(cell[['id_estacion', 'geometry']].rename(columns={'geometry': 'celda'}), on='id_estacion')
    e['geometry'] = [p.buffer(800).intersection(c) for p, c in zip(e.geometry, e.celda)]
    return gpd.GeoDataFrame(e.drop(columns='celda'), geometry='geometry', crs=32721)

def prorratear(seg, ent):
    seg = seg.to_crs(32721).copy(); seg['A_seg'] = seg.area
    x = gpd.overlay(seg[['segkey', 'A_seg', 'geometry'] + VALS], ent[['id_estacion', 'linea', 'orden', 'nombre', 'eje_asignado_2025', 'geometry']], how='intersection')
    x['w'] = x.area / x.A_seg
    for v in VALS: x[v] = x[v] * x.w
    k = ['id_estacion', 'linea', 'orden', 'nombre', 'eje_asignado_2025']
    t = x.groupby(k)[VALS].sum().round(0).astype(int).rename(columns=NOMBRES)
    t.insert(0, 'Segmentos que aportan', x.groupby(k).size())
    t['% no temporada'] = (100 * t['Desoc. no temporada'] / t.Viviendas).round(1)
    t['% estructural'] = (100 * t['Estructural (vac.+degr.)'] / t.Viviendas).round(1)
    return t.reset_index().sort_values(['linea', 'orden'])

if __name__ == '__main__':
    pol = gpd.read_file(POL)
    pol['segkey'] = pol.DEPTO.astype(str).str.zfill(2) + '-' + pol.CODSEG.astype(str).str.zfill(7)
    attrs = pd.read_csv(f'{D}/segmentos_brt_2023.csv', dtype={'CODSEG': str})
    seg = pol[['segkey', 'geometry']].merge(attrs[['seg'] + VALS].rename(columns={'seg': 'segkey'}), on='segkey')
    print('polígonos con atributos:', len(seg), 'de', len(pol))
    t = prorratear(seg, entornos(gpd.read_file(f'{D}/estaciones.geojson')))
    t.to_csv(f'{T}/t11_prorrateo_poligonos.csv', index=False)
    with pd.ExcelWriter(f'{T}/Vacancia_por_estacion_BRT_2023.xlsx', mode='a', if_sheet_exists='replace') as w:
        t.to_excel(w, sheet_name='Prorrateo polígonos reales', index=False)
    print(t[['nombre', 'Viviendas', 'Desoc. no temporada', 'Estructural (vac.+degr.)']].to_string(index=False))
