"""Tasas de desocupación por tramo BRT y banda de distancia; vivienda promovida ANV en entornos."""
import sys, numpy as pd_np, pandas as pd, geopandas as gpd, numpy as np
D, OUT = sys.argv[1], sys.argv[2]
g = pd.read_csv(f'{D}/segmentos_brt_2023.csv', dtype={'CODSEG': str})
cats = {'Temporada': 'Viv_Temp', 'Alquiler o venta': 'V_Desoc_4', 'Construcción o reparación': 'V_Desoc_5',
        'Degradada (ruinosa o tapiada)': 'Viv_Degrad', 'Vacante': 'V_Desoc_7', 'Motivo ignorado': 'V_Desoc_8'}
def tasas(df, by):
    a = df.groupby(by, observed=True)[['TotViv', 'desoc_total', 'Viv_Desoc', 'estructural'] + list(cats.values())].sum()
    r = pd.DataFrame({'Segmentos': df.groupby(by, observed=True).size(), 'Viviendas': a.TotViv,
                      'Desocupadas (todas)': a.desoc_total, '% desocupadas': 100 * a.desoc_total / a.TotViv,
                      '% no temporada': 100 * a.Viv_Desoc / a.TotViv,
                      'Estructural (vacante+degradada)': a.estructural, '% estructural': 100 * a.estructural / a.TotViv})
    for k, v in cats.items(): r[f'% {k}'] = 100 * a[v] / a.TotViv
    return r.round(2)
mvd = g[g.NOMDEPTO == 'MONTEVIDEO']
t1 = tasas(g, ['NOMDEPTO', 'banda']); t1.to_csv(f'{OUT}/t1_depto_banda.csv')
t2 = tasas(g, ['tramo']); t2.to_csv(f'{OUT}/t2_tramo.csv')
t3 = tasas(g, 'NOMDEPTO'); t3.to_csv(f'{OUT}/t3_depto.csv')
# dispersión entre segmentos (no ponderada) para dimensionar heterogeneidad
g['pct_nt'] = 100 * g.Viv_Desoc / g.TotViv
g['pct_est'] = 100 * g.estructural / g.TotViv
q = g[g.TotViv >= 50].groupby(['NOMDEPTO', 'banda'], observed=True)[['pct_nt', 'pct_est']].quantile([.25, .5, .75]).unstack().round(1)
q.to_csv(f'{OUT}/t4_dispersion.csv')
# bootstrap por segmentos: diferencia % no temporada 0-800 vs >800, Montevideo
rng = np.random.default_rng(1)
def rate(df): return 100 * df.Viv_Desoc.sum() / df.TotViv.sum()
ins, out = mvd[mvd.d_min <= 800], mvd[mvd.d_min > 800]
bs = [rate(ins.sample(len(ins), replace=True, random_state=rng.integers(1e9))) - rate(out.sample(len(out), replace=True, random_state=rng.integers(1e9))) for _ in range(2000)]
print('MVD dif no temporada (<=800 - >800): %.2f pp, IC95 bootstrap [%.2f, %.2f]' % (rate(ins) - rate(out), *np.percentile(bs, [2.5, 97.5])))
def rate_e(df): return 100 * df.estructural.sum() / df.TotViv.sum()
bs = [rate_e(ins.sample(len(ins), replace=True, random_state=rng.integers(1e9))) - rate_e(out.sample(len(out), replace=True, random_state=rng.integers(1e9))) for _ in range(2000)]
print('MVD dif estructural: %.2f pp, IC95 [%.2f, %.2f]' % (rate_e(ins) - rate_e(out), *np.percentile(bs, [2.5, 97.5])))
# ANV
a = pd.read_csv(f'{D}/anv_vivienda_promovida.csv')
a = gpd.GeoDataFrame(a, geometry=gpd.points_from_xy(a.coorX, a.CoorY), crs=4326).to_crs(32721)
e = gpd.read_file(f'{D}/estaciones.geojson').to_crs(32721)
a['d_min'] = a.geometry.apply(lambda p: e.distance(p).min())
a['banda'] = pd.cut(a.d_min, [0, 400, 800, 1e9], labels=['0-400 m', '400-800 m', '>800 m'], include_lowest=True)
a['periodo'] = np.where(pd.to_datetime(a.FECHA_PROM).dt.year <= 2020, '2011-2020', '2021-2026')
ta = a.groupby(['NOMDEPTO', 'banda'], observed=True).agg(proyectos=('IDEN', 'size'), viviendas=('TOTAL_VP', 'sum')).reset_index()
ta.to_csv(f'{OUT}/t5_anv_banda.csv', index=False)
tp = a.groupby(['periodo', 'banda'], observed=True).TOTAL_VP.sum().unstack(); tp['% en 0-800 m'] = 100 * (tp['0-400 m'] + tp['400-800 m']) / tp.sum(axis=1)
tp.round(1).to_csv(f'{OUT}/t6_anv_periodo.csv')
a.drop(columns='geometry').to_csv(f'{OUT}/anv_con_distancia.csv', index=False)
# comparación: participación en stock vs en vivienda promovida, Montevideo
st = mvd.groupby('banda', observed=True).TotViv.sum(); st = 100 * st / st.sum()
vp = a[a.NOMDEPTO == 'MONTEVIDEO'].groupby('banda', observed=True).TOTAL_VP.sum(); vp = 100 * vp / vp.sum()
ds = mvd.groupby('banda', observed=True).estructural.sum(); ds = 100 * ds / ds.sum()
cmp_ = pd.DataFrame({'% stock viviendas 2023': st, '% vacancia estructural': ds, '% vivienda promovida ANV': vp}).round(1)
cmp_.to_csv(f'{OUT}/t7_participaciones_mvd.csv')
for n, t in [('t1', t1), ('t2', t2), ('t3', t3), ('t5', ta), ('t6', tp.round(1)), ('t7', cmp_)]: print('\n', n); print(t.to_string())
print('\n t4'); print(q.to_string())
