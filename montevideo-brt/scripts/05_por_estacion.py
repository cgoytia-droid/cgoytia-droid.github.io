"""Viviendas desocupadas por entorno de estación (segmento asignado a la estación más cercana, <= 800 m)."""
import sys, pandas as pd, geopandas as gpd
D, OUT = sys.argv[1], sys.argv[2]
g = gpd.read_file(f'{D}/segmentos_brt_2023.gpkg')
e = gpd.read_file(f'{D}/estaciones.geojson').to_crs(32721)[['id_estacion', 'linea', 'orden', 'nombre', 'tipo', 'departamento', 'eje_asignado_2025', 'geometry']]
# troncal compartido: se conserva una sola copia de cada estación (la de la línea A)
e = e.sort_values('linea').drop_duplicates('nombre')
j = gpd.sjoin_nearest(g, e, how='left', distance_col='dist_est', max_distance=800)
j = j[j.id_estacion.notna()].drop_duplicates('segkey')  # empates: una sola estación
j['anillo'] = (j.dist_est <= 400).map({True: '0-400', False: '400-800'})
cols = {'TotViv': 'Viviendas', 'Viv_Desoc': 'Desoc. no temporada', 'V_Desoc_4': 'Alquiler o venta', 'V_Desoc_5': 'Construcción o reparación',
        'V_Desoc_7': 'Vacante', 'Viv_Degrad': 'Degradada', 'V_Desoc_8': 'Ignorado', 'Viv_Temp': 'Temporada', 'estructural': 'Estructural (vac.+degr.)'}
k = ['id_estacion', 'linea', 'orden', 'nombre', 'eje_asignado_2025', 'departamento']
t = j.groupby(k)[list(cols)].sum().rename(columns=cols)
t.insert(0, 'Segmentos', j.groupby(k).size())
t['% no temporada'] = (100 * t['Desoc. no temporada'] / t.Viviendas).round(1)
t['% estructural'] = (100 * t['Estructural (vac.+degr.)'] / t.Viviendas).round(1)
t = t.reset_index().sort_values(['linea', 'orden'])
# troncal compartido: las 7 estaciones aparecen en ambas líneas; se reporta una vez
a = j.groupby(['id_estacion', 'anillo']).estructural.sum().unstack(fill_value=0).add_prefix('Estructural ')
t = t.merge(a, left_on='id_estacion', right_index=True, how='left')
sin = sorted(set(e.nombre) - set(t.nombre))
print('estaciones sin segmentos asignados:', len(sin), sin)
t.to_csv(f'{OUT}/t8_por_estacion.csv', index=False)
with pd.ExcelWriter(f'{OUT}/Vacancia_por_estacion_BRT_2023.xlsx') as w:
    t.to_excel(w, sheet_name='Por estación', index=False)
    j.drop(columns='geometry')[['segkey', 'NOMDEPTO', 'NOMLOC', 'id_estacion', 'nombre', 'dist_est', 'anillo'] + list(cols)].rename(columns=cols).to_excel(w, sheet_name='Segmentos asignados', index=False)
print(t[['linea', 'nombre', 'Segmentos', 'Viviendas', 'Desoc. no temporada', 'Estructural (vac.+degr.)', '% no temporada', '% estructural']].to_string(index=False))
print('totales', t[['Viviendas', 'Desoc. no temporada', 'Estructural (vac.+degr.)']].sum().to_dict())
