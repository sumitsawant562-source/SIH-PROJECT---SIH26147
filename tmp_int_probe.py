import sys, time
sys.path.insert(0, "/home/user")
import numpy as np
from dsp import interleave as il

bits = np.random.randint(0, 2, 6000).astype(np.int8)
soft = (bits * 2.0 - 1.0) + np.random.randn(6000) * 0.5
geoms = il.candidate_geometries()
t0 = time.time()
for g in geoms[:2]:
    for off in list(range(0, 64)) + [64, 96, 128, 192, 256]:
        p = il._perm_for(4096 + off, g)
    print(f"  {g['label']}: perms cached, {time.time()-t0:.2f} s")
t0 = time.time()
p = il._perm_for(4096 + 63, geoms[0])
print(f"  fresh perm 4160: {time.time()-t0:.3f} s")
t0 = time.time()
ev = il._best_decode_evidence(bits[:4096], None, list(il.STANDARD_CONV_CODES)[:1])
print(f"  probe decode 4096 bits: {time.time()-t0:.3f} s  ok={ev.get('ok')}")
t0 = time.time()
ev = il._best_decode_evidence(bits[:2200], None, list(il.STANDARD_CONV_CODES)[:3])
print(f"  stage2 decode 2200 bits x3 codes: {time.time()-t0:.3f} s")
t0 = time.time()
ev = il._best_decode_evidence(bits[:3000], None, list(il.STANDARD_CONV_CODES)[:3])
print(f"  full decode 3000 bits x3 codes: {time.time()-t0:.3f} s")
print("n geoms:", len(geoms), [g["label"] for g in geoms])
