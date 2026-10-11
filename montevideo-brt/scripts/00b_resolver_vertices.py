"""Resuelve vértices ambiguos usando vértices compartidos con segmentos vecinos y el área del DBF.

1) Pool de vértices no ambiguos; un vértice ambiguo toma el candidato que coincide (< 5 cm)
   con un vértice del pool. Iterativo: lo resuelto entra al pool.
2) Lo que queda: Viterbi de menor longitud de anillo con los candidatos restantes.
3) Polígonos con área distinta de la del DBF (> 0,5 %): búsqueda local sobre los vértices
   no anclados para acercar el área, sin crear autointersecciones.
"""
import sys, pickle, json, numpy as np, pandas as pd
from shapely.geometry import Polygon, mapping
from shapely.validation import make_valid
recs, CANDS = pickle.load(open(sys.argv[1], 'rb'))
areas = pd.read_csv(sys.argv[2]).AREA.values
out = sys.argv[3]
key = lambda x, y: (int(round(x * 10)), int(round(y * 10)))
pool = {}
def add(x, y):
    pool.setdefault(key(x, y), []).append((x, y))
def match(x, y):
    kx, ky = key(x, y)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for (px, py) in pool.get((kx + dx, ky + dy), []):
                if abs(px - x) < .05 and abs(py - y) < .05: return True
    return False
S = [[c.copy() for c in C] for C in CANDS]  # candidatos vigentes
for C in S:
    for c in C:
        if len(c) == 1: add(*c[0])
amb0 = sum(len(c) > 1 for C in S for c in C); fijo = [[len(c) == 1 for c in C] for C in S]
for it in range(10):
    cambios = 0
    for r, C in enumerate(S):
        for k, c in enumerate(C):
            if len(c) == 1: continue
            m = np.array([match(x, y) for x, y in c])
            if m.sum() >= 1:
                C[k] = c[m][:1] if m.sum() == 1 else c[m]
                if len(C[k]) == 1: add(*C[k][0]); fijo[r][k] = True; cambios += 1
    print('iteración', it, 'resueltos por vecindad', cambios)
    if not cambios: break
amb1 = sum(len(c) > 1 for C in S for c in C)
print(f'vértices ambiguos: {amb0} -> {amb1} tras vecindad')

def viterbi(C):
    cost = np.zeros(len(C[0])); back = []
    for k in range(1, len(C)):
        d = np.hypot(C[k][:, None, 0] - C[k - 1][None, :, 0], C[k][:, None, 1] - C[k - 1][None, :, 1]) + cost[None, :]
        j = np.argmin(d, axis=1); back.append(j); cost = d[np.arange(len(j)), j]
    i = int(np.argmin(cost)); seq = [i]
    for j in reversed(back): i = int(j[i]); seq.append(i)
    seq.reverse(); return [C[k][seq[k]].copy() for k in range(len(C))]

def rings(pts, parts):
    b = parts + [len(pts)]
    return [pts[a:z] for a, z in zip(b[:-1], b[1:]) if z - a >= 4]
def area(pts, parts):
    try: return sum(Polygon(r).area * (1 if i == 0 else 1) for i, r in enumerate(rings(pts, parts)))
    except Exception: return 0
def valid(pts, parts):
    try: return all(Polygon(r).is_valid for r in rings(pts, parts))
    except Exception: return False

feats, stats = [], {'ajustados': 0, 'mejoran': 0}
for r, ((rn, parts, _, _, npdecl), C) in enumerate(zip(recs, S)):
    pts = viterbi(C)
    target = areas[r]
    a0 = area(pts, parts)
    if abs(a0 / target - 1) > .005:
        stats['ajustados'] += 1
        libres = [k for k, c in enumerate(C) if len(c) > 1 and not fijo[r][k]]
        best = abs(a0 - target)
        for _ in range(3):
            mejor_paso = False
            for k in libres:
                for cand in C[k]:
                    old = pts[k].copy(); pts[k] = cand.copy()
                    a = area(pts, parts)
                    if abs(a - target) < best - 1e-6 and valid(pts, parts):
                        best = abs(a - target); old = pts[k].copy(); mejor_paso = True
                    pts[k] = old
            if not mejor_paso: break
        if best < abs(a0 - target): stats['mejoran'] += 1
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    polys = [Polygon(rg) for rg in rings(list(zip(xs, ys)), parts)]
    g = make_valid(polys[0] if len(polys) == 1 else polys[0].union(polys[1]) if False else __import__('shapely').geometry.MultiPolygon(polys))
    feats.append({'type': 'Feature', 'properties': {'rec': rn}, 'geometry': mapping(g)})
print(stats)
json.dump({'type': 'FeatureCollection', 'features': feats}, open(out, 'w'))
