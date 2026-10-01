"""Condición y motivo de desocupación por entorno de estación: conteos y composición."""
import sys, pandas as pd, numpy as np, matplotlib, matplotlib.ticker
matplotlib.use('Agg'); import matplotlib.pyplot as plt
T, OUT = sys.argv[1], sys.argv[2]
t = pd.read_csv(f'{T}/t8_por_estacion.csv')
CATS = [('Alquiler o venta', '#000000'), ('Construcción o reparación', '#4D4D4D'), ('Ignorado', '#9A9A9A'),
        ('Vacante', '#8DB600'), ('Degradada', '#5C7A00'), ('Temporada', '#D6D6D6')]
LEY = {'Degradada': 'Degradada (ruinosa o tapiada)', 'Ignorado': 'Motivo ignorado', 'Temporada': 'Temporada (uso estacional)'}
t['Desocupadas'] = t[[c for c, _ in CATS]].sum(axis=1)
t['etiqueta'] = t.nombre + np.where(t.eje_asignado_2025 == 'Troncal', '  [troncal]', '')

def figura(modo, nombre, titulo, xlab, nota):
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 10.5))
    for ax, lin, tit in [(axs[0], 'A', 'Troncal y línea A'), (axs[1], 'B', 'Línea B')]:
        d = t[t.linea == lin].sort_values('orden').reset_index(drop=True)
        base = d.Desocupadas if modo == 'comp' else (d.Viviendas if modo == 'tasa' else 1)
        left = np.zeros(len(d))
        for c, col in CATS:
            v = (100 * d[c] / base) if modo in ('comp', 'tasa') else d[c]
            ax.barh(d.index, v, left=left, color=col, height=.72, edgecolor='white', lw=.8, label=LEY.get(c, c)); left += v
        for i, r in d.iterrows():
            flag = ' *' if r.Segmentos <= 2 else ''
            lab = {'conteo': f"{int(r.Desocupadas)}", 'tasa': f"{100*r.Desocupadas/r.Viviendas:.1f} %".replace('.', ','),
                   'comp': f"n = {int(r.Desocupadas)}"}[modo] + flag
            ax.text(left[i] + (1 if modo == 'comp' else left.max() * .01), i, lab, va='center', fontsize=6.5)
        ax.set_yticks(d.index); ax.set_yticklabels(d.etiqueta, fontsize=7); ax.invert_yaxis()
        ax.set_title(tit, fontsize=9, loc='left', fontweight='bold'); ax.spines[['top', 'right']].set_visible(False)
        ax.set_xlabel(xlab, fontsize=7.5)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:g}'.replace('.', ',')))
        if modo == 'comp': ax.set_xlim(0, 118); ax.set_xticks(range(0, 101, 25))
    mx = max(a.get_xlim()[1] for a in axs)
    if modo != 'comp':
        for a in axs: a.set_xlim(0, mx)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=3, fontsize=7.5, frameon=False, loc='lower center', bbox_to_anchor=(.5, .035))
    fig.suptitle(titulo, x=.02, ha='left', fontsize=11, fontweight='bold')
    fig.text(.02, .005, 'Fuente: elaboración propia con DINOT-MVOT, ocupación de la vivienda por segmento censal (Censo 2023). Cada segmento se asigna a la estación más cercana\n'
             'si su centroide está a 800 m o menos; el troncal compartido se muestra con la línea A. ' + nota + ' * Entorno con 1 o 2 segmentos.', fontsize=6.3, color='#555555')
    plt.tight_layout(rect=(0, .08, 1, .97)); fig.savefig(f'{OUT}/{nombre}.png', dpi=220, facecolor='white'); plt.close(fig)

figura('conteo', 'G3_motivo_conteo_por_estacion', 'Gráfico 3. Viviendas desocupadas por condición y motivo, por entorno de estación BRT, 2023',
       'Viviendas desocupadas (número)', 'Etiqueta: total de desocupadas.')
figura('tasa', 'G4_motivo_tasa_por_estacion', 'Gráfico 4. Desocupación por condición y motivo, % del stock del entorno de cada estación, 2023',
       '% de las viviendas del entorno', 'Etiqueta: % de desocupadas sobre el total de viviendas.')
figura('comp', 'G5_motivo_composicion_por_estacion', 'Gráfico 5. Composición de las viviendas desocupadas por motivo, por entorno de estación, 2023',
       '% de las viviendas desocupadas del entorno', 'Etiqueta: número de desocupadas (base del 100 %).')
# tabla de composición para la planilla
comp = t[['linea', 'orden', 'nombre', 'eje_asignado_2025', 'Viviendas', 'Desocupadas'] + [c for c, _ in CATS]].copy()
for c, _ in CATS: comp[f'% {c} (sobre desocupadas)'] = (100 * comp[c] / comp.Desocupadas).round(1)
comp.sort_values(['linea', 'orden']).to_csv(f'{T}/t9_motivo_por_estacion.csv', index=False)
with pd.ExcelWriter(f'{T}/Vacancia_por_estacion_BRT_2023.xlsx', mode='a', if_sheet_exists='replace') as w:
    comp.sort_values(['linea', 'orden']).to_excel(w, sheet_name='Motivo por estación', index=False)
print('ok')
