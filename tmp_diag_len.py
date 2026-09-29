import sys
sys.path.insert(0, "/home/user")
import numpy as np
from dsp import synth, interleave as il, demod

rng = np.random.default_rng(1)
src = rng.integers(0, 2, 3000).astype(np.uint8)
for kind, kw in (("diagonal", {"rows": 16}), ("block", {"rows": 16})):
    ilv = synth.interleave(src, kind, **kw)
    print(f"{kind}: generated len={ilv.size}")
    for recv_len in (3514, 3000, 3504, 3488):
        crop = ilv[:recv_len] if recv_len <= ilv.size else np.concatenate([ilv, np.zeros(recv_len - ilv.size, np.uint8)])
        de = il.deinterleave(crop, kind, **kw)
        n = min(de.size, src.size)
        print(f"   recv_len={recv_len:5d} agreement={float(np.mean(de[:n] == src[:n])):.4f}")
    # with a padding trick: pad the front with zeros and de-interleave a longer array
    for off in (0, 16, 32):
        padded = np.concatenate([np.zeros(off, np.uint8), ilv]) if off else ilv
        de = il.deinterleave(padded, kind, **kw)
        n = min(de.size - off, src.size)
        print(f"   pregap={off:3d} agreement(start of recovered)={float(np.mean(de[off:off+n] == src[:n])):.4f}")
