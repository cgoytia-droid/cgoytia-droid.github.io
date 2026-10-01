"""Une ocupación de vivienda 2023 (DINOT, segmentos) con centroides y estaciones BRT."""
import sys, pandas as pd, geopandas as gpd
D = sys.argv[1]  # carpeta con insumos
OUT = sys.argv[2]
v = pd.read_csv(f'{D}/ocupacion_segmentos_2023.csv', dtype={'CODSEG': str, 'DEPTO': str, 'CODLOC': str})
c = pd.read_csv(f'{D}/cma_v2_segmentos.csv', dtype={'seg': str})
v['seg'] = v.DEPTO + '-' + v.CODSEG
g = v.merge(c[['seg', 'x', 'y']], on='seg', how='left')
print('sin centroide por depto:\n', g[g.x.isna()].NOMDEPTO.value_counts())
g = g[g.x.notna()]
g = gpd.GeoDataFrame(g, geometry=gpd.points_from_xy(g.x, g.y), crs=32721)
e = gpd.read_file(f'{D}/estaciones.geojson').to_crs(32721)
# distancia al centroide de la estación más cercana, por línea
for lin in ['A', 'B']:
    s = e[e.linea == lin]
    g[f'd_{lin}'] = g.geometry.apply(lambda p: s.distance(p).min())
g['d_min'] = g[['d_A', 'd_B']].min(axis=1)
g['linea_cercana'] = (g.d_A <= g.d_B).map({True: 'A', False: 'B'})
tr = e[e.eje_asignado_2025 == 'Troncal']
g['d_troncal'] = g.geometry.apply(lambda p: tr.distance(p).min())
g['tramo'] = 'Fuera'
g.loc[g.d_min <= 800, 'tramo'] = 'Línea ' + g.linea_cercana
g.loc[(g.d_troncal <= 800) & (g.d_troncal <= g.d_min + 1), 'tramo'] = 'Troncal'
g['banda'] = pd.cut(g.d_min, [0, 400, 800, 1e9], labels=['0-400 m', '400-800 m', '>800 m'], include_lowest=True)
g['estructural'] = g.V_Desoc_7 + g.Viv_Degrad  # vacante + degradada
g['desoc_total'] = g.Viv_Desoc + g.Viv_Temp
g.drop(columns='geometry').to_csv(f'{OUT}/segmentos_brt_2023.csv', index=False)
g.rename(columns={'seg':'segkey'}).to_file(f'{OUT}/segmentos_brt_2023.gpkg', driver='GPKG')
print(g.groupby(['NOMDEPTO', 'banda'], observed=True).size())
