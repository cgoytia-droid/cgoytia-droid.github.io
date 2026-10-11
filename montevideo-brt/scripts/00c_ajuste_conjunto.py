"""Ajuste conjunto de vértices ambiguos compartidos.

Cada vértice físico (mismos bytes, misma zona) es una sola incógnita aunque aparezca en
varios polígonos. Se elige su valor, entre los candidatos posibles, para que todos los
polígonos que lo usan reproduzcan su área del DBF; descenso por coordenadas.
"""
import sys, pickle, json, numpy as np, pandas as pd, struct, itertools
from shapely.geometry import Polygon, MultiPolygon, mapping
from shapely.validation import make_valid
base = sys.argv[1]; T = pd.read_csv(sys.argv[2]).AREA.values; out = sys.argv[3]
recs, CANDS = pickle.load(open(base + '.pkl', 'rb'))
B = np.load(base + '.B.npy'); P0 = pickle.load(open(base + '.p0.pkl', 'rb'))
# grupos de vértices: clave = bytes crudos + ubicación aproximada (celda de 2 km)
gid, G = {}, []          # G[g] = array de candidatos (k,2)
poly_v = []              # por polígono: lista de ids de grupo por vértice (sin el de cierre)
for r, ((rn, parts, xs, ys, _), C, (p0, npts)) in enumerate(zip(recs, CANDS, P0)):
    ids = []
    for k in range(npts):
        raw = tuple(B[p0 + 16 * k: p0 + 16 * k + 16].tolist())
        key = (raw, int(xs[k] // 2000), int(ys[k] // 2000))
        if key not in gid:
            gid[key] = len(G); G.append(C[k])
        ids.append(gid[key])
    poly_v.append(ids)
G = [np.asarray(c, float) for c in G]
choice = np.zeros(len(G), int)
# inicializar con la solución de Viterbi (la más cercana a la secuencia decodificada)
for r, (rn, parts, xs, ys, _) in enumerate(recs):
    for k, g in enumerate(poly_v[r]):
        if len(G[g]) > 1: choice[g] = int(np.argmin(np.hypot(G[g][:, 0] - xs[k], G[g][:, 1] - ys[k])))
def ring_idx(r):
    parts = recs[r][1] + [len(poly_v[r])]
    return [list(range(a, z - 1)) for a, z in zip(parts[:-1], parts[1:]) if z - a >= 4]  # sin vértice de cierre
RINGS = [ring_idx(r) for r in range(len(recs))]
def signed_area(r):
    tot = 0.0
    for ring in RINGS[r]:
        P = np.array([G[poly_v[r][k]][choice[poly_v[r][k]]] for k in ring])
        x, y = P[:, 0], P[:, 1]
        tot += 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) * (1 if ring is RINGS[r][0] else -1)
    return tot
inc = {}
for r, ids in enumerate(poly_v):
    for g in set(ids):
        if len(G[g]) > 1: inc.setdefault(g, []).append(r)
A = np.array([signed_area(r) for r in range(len(recs))])
def obj(rs): return sum(((A_[r] - T[r]) / T[r]) ** 2 for r in rs)
print('grupos ambiguos:', len(inc), 'error área mediano inicial %.3f %%' % (100 * np.median(np.abs(A / T - 1))))
for sweep in range(6):
    moved = 0
    for g, rs in inc.items():
        best_c, best_o = choice[g], None
        old = choice[g]
        for c in range(len(G[g])):
            choice[g] = c
            A_ = {r: signed_area(r) for r in rs}
            o = sum(((A_[r] - T[r]) / T[r]) ** 2 for r in rs)
            # penalización suave a saltos (longitud de aristas incidentes)
            if best_o is None or o < best_o - 1e-12: best_o, best_c, bestA = o, c, A_
        choice[g] = best_c
        for r, a in bestA.items(): A[r] = a
        moved += best_c != old
    print('pasada', sweep, 'vértices cambiados', moved, 'error mediano %.4f %%' % (100 * np.median(np.abs(A / T - 1))), '>1%%: %d' % (np.abs(A / T - 1) > .01).sum())
    if not moved: break
feats = []
for r, (rn, parts, xs, ys, npd) in enumerate(recs):
    polys = []
    for i, ring in enumerate(RINGS[r]):
        P = [tuple(G[poly_v[r][k]][choice[poly_v[r][k]]]) for k in ring]
        polys.append(Polygon(P))
    shell = polys[0]
    holes = [p for p in polys[1:] if shell.contains(p.representative_point())]
    extra = [p for p in polys[1:] if not shell.contains(p.representative_point())]
    geom = make_valid(Polygon(shell.exterior.coords, [h.exterior.coords for h in holes]))
    if extra: geom = make_valid(MultiPolygon([geom] + extra) if geom.geom_type == 'Polygon' else geom.union(MultiPolygon(extra)))
    feats.append({'type': 'Feature', 'properties': {'rec': rn, 'err_area_pct': round(100 * (A[r] / T[r] - 1), 3)}, 'geometry': mapping(geom)})
json.dump({'type': 'FeatureCollection', 'features': feats}, open(out, 'w'))
