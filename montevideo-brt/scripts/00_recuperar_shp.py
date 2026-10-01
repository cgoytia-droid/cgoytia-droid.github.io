"""Reconstruye polígonos de un .shp leído como texto cp1252 con bytes ambiguos (U+FFFD).

U+FFFD representa uno de: 0x00-0x08, 0x0B-0x1F, 0x81, 0x8D, 0x8F, 0x90, 0x9D.
Se resuelve con las restricciones del formato: longitudes de registro, números de
partes y puntos coherentes, y continuidad entre vértices consecutivos.
"""
import sys, struct, itertools, numpy as np
src, out = sys.argv[1], sys.argv[2]
t = open(src, encoding='utf-8').read()
AMB = [b for b in range(32) if b not in (9, 10)] + [0x81, 0x8D, 0x8F, 0x90, 0x9D]
rev = {}
for b in range(256):
    ch = bytes([b]).decode('cp1252', errors='replace')
    if ch != '�': rev[ch] = b
B = np.array([-2 if c == '\n' else rev.get(c, -1) for c in t], dtype=np.int16)  # -1: ambiguo; -2: 0x0A o 0x0D
OPT = {-1: AMB, -2: [0x0A, 0x0D]}
AMB = AMB  # (0x0D aparece como salto de línea)
N = len(B)

def ints_le(pos, n=4, maxval=None, nb=4):
    """Candidatos de un int32 little-endian; los bytes de orden >= nb se asumen 0."""
    opts = [([B[pos + i]] if B[pos + i] >= 0 else OPT[int(B[pos + i])]) if i < nb else [0] for i in range(n)]
    if any(B[pos + i] != -1 for i in range(nb, n)): return
    for combo in itertools.product(*opts):
        v = int.from_bytes(bytes(combo), 'little')
        if maxval is None or v <= maxval: yield v

def dbl(pos, prev=None):
    """Double little-endian. Bytes 0-3 ambiguos -> 0 (error < 2 cm). Bytes 4-7 ambiguos:
    se resuelven de mayor a menor peso eligiendo el valor más cercano a prev."""
    bs = [int(x) for x in B[pos:pos + 8]]
    hi = [i for i in range(4, 8) if bs[i] < 0]
    kind = list(bs)
    for i in range(8):
        if bs[i] < 0: bs[i] = 0x0A if bs[i] == -2 else 0
    for i in sorted(hi, reverse=True):
        best = None
        for v in OPT[kind[i]]:
            bs[i] = v
            x = struct.unpack('<d', bytes(bs))[0]
            if not (4e5 < x < 7e6): continue
            sc = abs(x - prev) if prev is not None else abs(x - 3e6)
            if best is None or sc < best[0]: best = (sc, v)
        bs[i] = best[1] if best else 0
    return struct.unpack('<d', bytes(bs))[0], len(hi)

def plausible_rec(pos, recnum):
    """¿Hay un encabezado de registro de polígono válido en pos?"""
    if pos + 52 > N: return False
    z = lambda i: B[pos + i] == -1  # byte cero (o ambiguo)
    if not all(z(i) for i in (0, 1, 2, 4, 5, 8, 9, 10, 11)): return False
    lo = int(B[pos + 3])
    if (recnum & 0xFF) not in ([lo] if lo >= 0 else OPT[lo]): return False
    return all(B[pos + 12 + 8 * k + 7] == 0x41 for k in range(4))

def decode_fast(p0, npts):
    xs, ys, px, py = [], [], 5.8e5, 6.14e6
    for k in range(npts):
        x, _ = dbl(p0 + 16 * k, px); y, _ = dbl(p0 + 16 * k + 8, py)
        xs.append(x); ys.append(y); px, py = x, y
    return xs, ys, 0

RANGO = {0: (4.5e5, 6.7e5), 1: (6.0e6, 6.3e6)}

def cands(pos, eje):
    """Todos los valores posibles de una coordenada dentro del rango del AMM."""
    bs = [int(x) for x in B[pos:pos + 8]]
    hi = [i for i in range(4, 8) if bs[i] < 0]
    kinds = [bs[i] for i in hi]
    for i in range(8):
        if bs[i] < 0: bs[i] = 0x0A if bs[i] == -2 else 0
    out = []
    for combo in itertools.product(*[OPT[k] for k in kinds]):
        for i, v in zip(hi, combo): bs[i] = v
        x = struct.unpack('<d', bytes(bs))[0]
        if RANGO[eje][0] < x < RANGO[eje][1]: out.append(x)
    return out or [1e9], len(hi)  # fuera de rango: valor absurdo, lo descarta la validación

def decode_pts(p0, npts):
    """Viterbi: elige, entre los candidatos de cada vértice, la secuencia de menor longitud total."""
    C, nh = [], 0
    for k in range(npts):
        cx, h1 = cands(p0 + 16 * k, 0); cy, h2 = cands(p0 + 16 * k + 8, 1); nh += h1 + h2
        cx, cy = cx[:40], cy[:40]
        C.append(np.array([(x, y) for x in cx for y in cy]))
    cost = np.zeros(len(C[0])); back = []
    for k in range(1, npts):
        dmat = np.hypot(C[k][:, None, 0] - C[k - 1][None, :, 0], C[k][:, None, 1] - C[k - 1][None, :, 1]) + cost[None, :]
        j = np.argmin(dmat, axis=1); back.append(j); cost = dmat[np.arange(len(j)), j]
    i = int(np.argmin(cost)); seq = [i]
    for j in reversed(back): i = int(j[i]); seq.append(i)
    seq.reverse()
    pts = [C[k][seq[k]] for k in range(npts)]
    global LASTC
    LASTC = C
    return [p[0] for p in pts], [p[1] for p in pts], nh

def len_ok(pos, clen):
    w = (clen // 2).to_bytes(4, 'big')
    return all((w[i] in OPT[int(B[pos + 4 + i])]) if B[pos + 4 + i] < 0 else B[pos + 4 + i] == w[i] for i in range(4))

recs, pos, rn, nhi, N_EXP, repaired = [], 100, 1, 0, 1734, False
CANDS, P0 = [], []
while len(recs) < N_EXP:
    c = pos + 8
    found, fallback = None, None
    for nparts in ints_le(c + 36, maxval=200, nb=1):
        if nparts < 1: continue
        for npts in ints_le(c + 40, maxval=65535, nb=2):
            if npts < 4: continue
            clen = 44 + 4 * nparts + 16 * npts
            end = c + clen
            if not len_ok(pos, clen): continue
            last = len(recs) == N_EXP - 1
            if not ((last and end >= N - 2) or plausible_rec(end, rn + 1)): continue
            xs, ys, nh = decode_fast(c + 44 + 4 * nparts, npts)
            ref = (min(xs), min(ys), max(xs), max(ys))
            err = max(abs(dbl(c + 4 + 8 * k, ref[k])[0] - ref[k]) for k in range(4))
            cand = (nparts, npts, end, xs, ys, nh)
            if err < 1.0:
                found = cand; break
            if fallback is None: fallback = cand
        if found: break
    if not found and not fallback:
        # un par CR+LF colapsado en LF dentro del registro: reinsertar 0x0D donde cierre el bbox
        best = None
        for i in [k for k in range(c + 44, min(N, c + 44 + 16 * 65535)) if B[k] == -2][:400]:
            B2 = np.insert(B, i, 0x0D); B2[i + 1] = 0x0A
            Bs, B = B, B2; N += 1
            for nparts in ints_le(c + 36, maxval=200, nb=1):
                for npts in ints_le(c + 40, maxval=65535, nb=2):
                    clen = 44 + 4 * max(nparts, 1) + 16 * npts
                    if npts < 4 or i >= c + clen or not len_ok(pos, clen) or not plausible_rec(c + clen, rn + 1): continue
                    xs, ys, nh = decode_fast(c + 44 + 4 * nparts, npts)
                    ref = (min(xs), min(ys), max(xs), max(ys))
                    err = max(abs(dbl(c + 4 + 8 * k, ref[k])[0] - ref[k]) for k in range(4))
                    if best is None or err < best[0]: best = (err, i, B2, (nparts, npts, c + clen, xs, ys, nh))
            B = Bs; N -= 1
        if best:
            B, N, found, repaired = best[2], N + 1, best[3], True
            print('CR reinsertado en', best[1], 'registro', rn, 'error bbox', round(best[0], 3))
    found = found or fallback
    assert found, ('sin solución', rn, pos)
    nparts, npts, end, _, _, _ = found
    xs, ys, nh = decode_pts(c + 44 + 4 * nparts, npts); nhi += nh
    # anillos por cierre: cada anillo termina al volver a su primer vértice
    parts, k0 = [0], 0
    for k in range(1, npts):
        if k > k0 + 2 and abs(xs[k] - xs[k0]) < 0.05 and abs(ys[k] - ys[k0]) < 0.05 and k + 1 < npts:
            parts.append(k + 1); k0 = k + 1
    recs.append((rn, parts, xs, ys, nparts)); CANDS.append(LASTC); P0.append((c + 44 + 4 * nparts, npts)); pos = end; rn += 1
    if rn % 200 == 0: print(rn, pos, flush=True)
import pickle; pickle.dump((recs, CANDS), open(out + '.pkl', 'wb')); np.save(out + '.B.npy', B); pickle.dump(P0, open(out + '.p0.pkl', 'wb'))
print('registros', len(recs), 'bytes altos ambiguos resueltos', nhi)
# a GeoJSON en EPSG:5382 (SIRGAS-ROU98 UTM 21S)
import json
from shapely.geometry import Polygon, MultiPolygon, mapping
from shapely.validation import make_valid
feats = []
for rn, parts, xs, ys, npdecl in recs:
    bounds = parts + [len(xs)]
    rings = [list(zip(xs[a:b], ys[a:b])) for a, b in zip(bounds[:-1], bounds[1:])]
    polys = [Polygon(r) for r in rings if len(r) >= 4]
    g = make_valid(MultiPolygon(polys) if len(polys) > 1 else polys[0])
    feats.append({'type': 'Feature', 'properties': {'rec': rn, 'partes_decl': npdecl, 'partes_rec': len(parts)}, 'geometry': mapping(g)})
json.dump({'type': 'FeatureCollection', 'features': feats}, open(out, 'w'))
