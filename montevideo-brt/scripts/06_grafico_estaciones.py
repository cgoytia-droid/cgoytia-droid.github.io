"""Gráfico: vacancia estructural por entorno de estación, en el orden de cada línea."""
import sys, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
T, OUT = sys.argv[1], sys.argv[2]
VERDE, OSC = '#8DB600', '#5C7A00'
t = pd.read_csv(f'{T}/t8_por_estacion.csv')
fig, axs = plt.subplots(1, 2, figsize=(11, 10), sharex=True)
for ax, lin, tit in [(axs[0], 'A', 'Troncal y línea A: 18 de Julio, 8 de Octubre, Cno. Maldonado, Ruta 8'), (axs[1], 'B', 'Línea B: Av. Italia, Giannattasio')]:
    d = t[t.linea == lin].sort_values('orden')
    y = range(len(d))
    ax.barh(y, d.Vacante, color=VERDE, height=.7, edgecolor='white', lw=1, label='Vacante')
    ax.barh(y, d.Degradada, left=d.Vacante, color=OSC, height=.7, edgecolor='white', lw=1, label='Degradada (ruinosa o tapiada)')
    for i, (_, r) in enumerate(d.iterrows()):
        flag = ' *' if r.Segmentos <= 2 else ''
        ax.text(r['Estructural (vac.+degr.)'] + 4, i, f"{int(r['Estructural (vac.+degr.)'])} ({r['% estructural']:.1f} %){flag}".replace('.', ','), va='center', fontsize=7)
    ax.set_yticks(list(y)); ax.set_yticklabels([n + ('  [troncal]' if eje == 'Troncal' else '') for n, eje in zip(d.nombre, d.eje_asignado_2025)], fontsize=7); ax.invert_yaxis()
    ax.set_title(tit, fontsize=9, loc='left', fontweight='bold'); ax.spines[['top', 'right']].set_visible(False)
    ax.set_xlabel('Viviendas vacantes o degradadas\n(entre paréntesis, % del stock del entorno)', fontsize=7.5)
axs[0].legend(fontsize=7.5, frameon=False, loc='lower right'); axs[0].set_xlim(0, 380)
fig.suptitle('Gráfico 2. Vacancia estructural por entorno de estación BRT (800 m), 2023', x=.02, ha='left', fontsize=11, fontweight='bold')
fig.text(.02, .005, 'Fuente: elaboración propia con DINOT-MVOT (Censo 2023). Cada segmento se asigna a la estación más cercana si su centroide está a 800 m o menos; el troncal compartido se muestra con la línea A.\n'
         '* Entorno con 1 o 2 segmentos: tasa poco estable. Seis estaciones (Ruta 8 oriental y Giannattasio / Guenoas) no reciben segmentos.', fontsize=6.5, color='#555555')
plt.tight_layout(rect=(0, .03, 1, .97)); fig.savefig(f'{OUT}/G2_vacancia_por_estacion.png', dpi=220, facecolor='white')
