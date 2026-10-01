"""Mapas de vacancia 2023 en el entorno BRT. Paleta: grises secuenciales, verde #8DB600 solo para el BRT."""
import sys, pandas as pd, geopandas as gpd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from shapely.geometry import LineString
D, OUT = sys.argv[1], sys.argv[2]
plt.rcParams.update({'font.family': 'Carlito', 'font.size': 9, 'axes.edgecolor': '#BBBBBB'})
VERDE = '#8DB600'; GRISES = ['#E3E3E3', '#B5B5B5', '#858585', '#4D4D4D', '#000000']
g = gpd.read_file(f'{D}/segmentos_brt_2023.gpkg')
g = g[g.TotViv >= 30]  # segmentos con stock mínimo para tasas estables
e = gpd.read_file(f'{D}/estaciones.geojson').to_crs(32721)
dep = gpd.read_file(f'{D}/deptos.geojson').to_crs(32721)
lineas = gpd.GeoDataFrame({'linea': ['A', 'B']}, geometry=[LineString(e[e.linea == l].sort_values('orden').geometry.tolist()) for l in ['A', 'B']], crs=32721)
buf = gpd.GeoDataFrame(geometry=[e.buffer(800).union_all()], crs=32721)
a = pd.read_csv(f'{D}/anv_con_distancia.csv')
a = gpd.GeoDataFrame(a, geometry=gpd.points_from_xy(a.coorX, a.CoorY), crs=4326).to_crs(32721)

def base(ax, ext):
    dep.boundary.plot(ax=ax, color='#CCCCCC', lw=.5)
    buf.boundary.plot(ax=ax, color=VERDE, lw=.8, ls='--')
    lineas.plot(ax=ax, color=VERDE, lw=1.6)
    e.plot(ax=ax, color='white', edgecolor=VERDE, markersize=10, lw=1, zorder=5)
    ax.set_xlim(ext[0], ext[2]); ax.set_ylim(ext[1], ext[3]); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(''); ax.set_ylabel('')
    for l, frac in [('A', .999), ('B', .999)]:
        ln = lineas[lineas.linea == l].geometry.iloc[0]
        for f in (.5, .85):
            pt = ln.interpolate(f, normalized=True)
            if ext[0] < pt.x < ext[2] and ext[1] < pt.y < ext[3]:
                ax.annotate(f'Línea {l}', (pt.x, pt.y), xytext=(8, -12), textcoords='offset points', fontsize=8, color='#5C7A00', fontweight='bold', zorder=6); break
    x0, y0 = ext[0] + (ext[2]-ext[0])*.04, ext[1] + (ext[3]-ext[1])*.04
    ax.plot([x0, x0+2000], [y0, y0], color='black', lw=1.5); ax.text(x0+1000, y0+250, '2 km', ha='center', fontsize=7)

def clases(ax, col, bins, labels, titulo, sizecol='TotViv', loc='lower right'):
    k = pd.cut(g[col], bins, labels=False, include_lowest=True)
    s = 4 + 40 * np.sqrt(g[sizecol] / g[sizecol].max())
    for i in range(len(labels)):
        m = k == i
        ax.scatter(g.geometry.x[m], g.geometry.y[m], s=s[m], c=GRISES[i], edgecolors='white', linewidths=.3, zorder=3)
    h = [Line2D([], [], marker='o', ls='', mfc=GRISES[i], mec='#999', ms=6, label=labels[i]) for i in range(len(labels))]
    h += [Line2D([], [], color=VERDE, lw=1.6, label='BRT y estaciones'), Line2D([], [], color=VERDE, lw=.8, ls='--', label='Entorno 800 m')]
    ax.legend(handles=h, title=titulo, loc=loc, fontsize=7, title_fontsize=7.5, frameon=False)

EXT_AMM = (562000, 6131500, 612000, 6153500)
EXT_COR = (569500, 6133500, 590500, 6146500)
FUENTE = 'Fuente: elaboración propia con DINOT-MVOT, ocupación de la vivienda por segmento censal (Censo 2023), y estaciones BRT corregidas 2025.\nCírculos: centroide de segmento, área proporcional a viviendas. Se excluyen segmentos con menos de 30 viviendas.'

def guardar(fig, nombre, titulo, fuente=FUENTE, yf=.01):
    fig.suptitle(titulo, x=.02, ha='left', fontsize=11, fontweight='bold')
    fig.text(.02, yf, fuente, fontsize=6.5, color='#555555', ha='left')
    fig.savefig(f'{OUT}/{nombre}.png', dpi=220, bbox_inches='tight', facecolor='white'); plt.close(fig)

g['pct_nt'] = 100 * g.Viv_Desoc / g.TotViv
g['pct_av'] = 100 * g.V_Desoc_4 / g.TotViv
g['pct_est'] = 100 * g.estructural / g.TotViv
g['pct_temp'] = 100 * g.Viv_Temp / g.TotViv
B5 = [0, 5, 8, 11, 15, 100]; L5 = ['< 5 %', '5-8 %', '8-11 %', '11-15 %', '≥ 15 %']

# M1: panorama AMM, desocupación no temporada
fig, ax = plt.subplots(figsize=(9, 5.2)); base(ax, EXT_AMM)
clases(ax, 'pct_nt', B5, L5, 'Viviendas desocupadas\n(no temporada), % del stock')
guardar(fig, 'M1_desocupacion_no_temporada_AMM', 'Mapa 1. Desocupación no estacional por segmento censal, Montevideo y Canelones, 2023')

# M2: corredor, vacancia estructural (vacante + degradada), en conteo
fig, ax = plt.subplots(figsize=(9, 5.8)); base(ax, EXT_COR)
k = pd.cut(g.estructural, [-1, 0, 10, 20, 40, 1e6], labels=False)
for i in range(5):
    m = k == i
    ax.scatter(g.geometry.x[m], g.geometry.y[m], s=[3, 10, 25, 50, 90][i], c=GRISES[i], edgecolors='white', linewidths=.3, zorder=3)
h = [Line2D([], [], marker='o', ls='', mfc=GRISES[i], mec='#999', ms=[2, 3.5, 5, 7, 9][i], label=l) for i, l in enumerate(['0', '1-10', '11-20', '21-40', '> 40'])]
h += [Line2D([], [], color=VERDE, lw=1.6, label='BRT y estaciones'), Line2D([], [], color=VERDE, lw=.8, ls='--', label='Entorno 800 m')]
ax.legend(handles=h, title='Viviendas vacantes o degradadas\n(conteo por segmento)', loc='lower right', fontsize=7, title_fontsize=7.5, frameon=False)
guardar(fig, 'M2_vacancia_estructural_corredor', 'Mapa 2. Stock de vacancia estructural (vacante + ruinosa o tapiada) en el corredor, 2023',
        FUENTE.split('\n')[0] + '\nCírculos: centroide de segmento, tamaño según número de viviendas vacantes o degradadas. Se excluyen segmentos con menos de 30 viviendas.')

# M3: corredor, alquiler o venta (vacancia friccional)
fig, ax = plt.subplots(figsize=(9, 5.8)); base(ax, EXT_COR)
clases(ax, 'pct_av', [0, 2, 3.5, 5, 7, 100], ['< 2 %', '2-3,5 %', '3,5-5 %', '5-7 %', '≥ 7 %'], 'Desocupadas para alquiler\no venta, % del stock', loc='lower right')
guardar(fig, 'M3_vacancia_friccional_corredor', 'Mapa 3. Desocupación por alquiler o venta (componente friccional) en el corredor, 2023')

# M4: vivienda promovida ANV sobre vacancia estructural %
fig, ax = plt.subplots(figsize=(9, 5.8)); base(ax, EXT_COR)
ax.scatter(g.geometry.x, g.geometry.y, s=4, c='#D0D0D0', zorder=2)
for per, col in [('2011-2020', '#858585'), ('2021-2026', '#000000')]:
    m = a.periodo == per
    ax.scatter(a.geometry.x[m], a.geometry.y[m], s=3 + 2.5 * np.sqrt(a.TOTAL_VP[m]) * 3, facecolors='none', edgecolors=col, linewidths=.6, zorder=4, label=f'Proyectos promovidos {per}')
h = [Line2D([], [], marker='o', ls='', mfc='none', mec='#858585', ms=6, label='Proyectos 2011-2020'), Line2D([], [], marker='o', ls='', mfc='none', mec='black', ms=6, label='Proyectos 2021-2026'),
     Line2D([], [], marker='o', ls='', mfc='#D0D0D0', mec='none', ms=3, label='Segmentos censales'),
     Line2D([], [], color=VERDE, lw=1.6, label='BRT y estaciones'), Line2D([], [], color=VERDE, lw=.8, ls='--', label='Entorno 800 m')]
ax.legend(handles=h, title='Vivienda promovida ANV\n(área ∝ unidades)', loc='lower right', fontsize=7, title_fontsize=7.5, frameon=False)
guardar(fig, 'M4_vivienda_promovida_ANV', 'Mapa 4. Proyectos de vivienda promovida (ANV) por período de promoción y corredor BRT',
        'Fuente: elaboración propia con ANV, vivienda promovida, corte 31/08/2026 (capa entregada por DINOT), y estaciones BRT corregidas 2025.')

# M5: Canelones, temporada
fig, ax = plt.subplots(figsize=(9, 5.2)); base(ax, (586000, 6136000, 626000, 6158000))
clases(ax, 'pct_temp', [0, 2, 5, 10, 25, 100], ['< 2 %', '2-5 %', '5-10 %', '10-25 %', '≥ 25 %'], 'Viviendas de temporada,\n% del stock')
guardar(fig, 'M5_temporada_costa', 'Mapa 5. Vivienda de temporada en el borde costero metropolitano, 2023')

# G1: composición por banda, Montevideo (barras apiladas horizontales)
t = pd.read_csv(f'{D}/t1_depto_banda.csv'); t = t[t.NOMDEPTO == 'MONTEVIDEO'].set_index('banda')
comp = ['% Alquiler o venta', '% Construcción o reparación', '% Motivo ignorado', '% Vacante', '% Degradada (ruinosa o tapiada)', '% Temporada']
cols = ['#000000', '#4D4D4D', '#858585', VERDE, '#5C7A00', '#CFCFCF']
fig, ax = plt.subplots(figsize=(8, 2.6)); left = np.zeros(len(t))
for c, col in zip(comp, cols):
    ax.barh(t.index, t[c], left=left, color=col, edgecolor='white', lw=2, height=.6, label=c[2:]); left += t[c].values
for i, v in enumerate(left): ax.text(v + .15, i, f'{v:.1f} %'.replace('.', ','), va='center', fontsize=8)
ax.invert_yaxis(); ax.spines[['top', 'right']].set_visible(False); ax.set_xlabel('% del stock de viviendas'); ax.set_xlim(0, 13.5)
ax.legend(ncol=3, fontsize=7, frameon=False, loc='upper center', bbox_to_anchor=(.5, -.35))
guardar(fig, 'G1_composicion_banda_MVD', 'Gráfico 1. Composición de la desocupación por distancia a estaciones BRT, Montevideo, 2023',
        'Fuente: elaboración propia con DINOT-MVOT (Censo 2023). Distancia del centroide de segmento a la estación más cercana.', yf=-.34)
print('ok')
