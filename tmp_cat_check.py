import sys
sys.path.insert(0, "/home/user")
import numpy as np
from dsp import synth, interleave as il

rng = np.random.default_rng(0)
bits = rng.integers(0, 2, 4000).astype(np.uint8)
cases = [("block", {"rows": 8}), ("block", {"rows": 16}), ("block", {"rows": 32}),
         ("convolutional", {"rows": 8, "depth": 2}), ("convolutional", {"rows": 16, "depth": 4}),
         ("diagonal", {"rows": 8}), ("diagonal", {"rows": 16}), ("diagonal", {"rows": 32}),
         ("pseudo-random", {"seed": 12345}), ("pseudo-random", {"seed": 999})]
for kind, params in cases:
    kw = dict(rows=params.get("rows", 16), depth=params.get("depth", 4), seed=params.get("seed", 12345))
    ilv = synth.interleave(bits, kind, **kw)
    de = il.deinterleave(ilv, kind, **params)
    n = min(de.size, bits.size)
    exact = float(np.mean(de[:n] == bits[:n]))
    # also test the "padded" alignment trick
    pad = np.concatenate([np.zeros(0, dtype=np.uint8), ilv])
    print(f'  {kind:14s} {str(params):34s} round-trip agreement {exact:.4f}')
