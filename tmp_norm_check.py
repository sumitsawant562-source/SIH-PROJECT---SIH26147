import sys, time
sys.path.insert(0, "/home/user")
import numpy as np
from dsp import synth, modulation as md, params as pr, pipeline as pipe

for mod in ("8PSK", "QPSK", "16QAM"):
    spec = dict(synth.DEFAULT_SPEC)
    spec.update({"modulation": mod, "fs": 1.0, "symbol_rate": 0.125, "n_symbols": 3000,
                 "snr_db": 24.0, "fec": "none", "carrier_offset_hz": 0.015, "seed": 5,
                 "payload": "random"})
    sig = synth.generate_signal(spec)
    x = np.asarray(sig.samples)
    r = pr.estimate_symbol_rate(x, 1.0)
    rs = (r.get("primary") or {}).get("symbol_rate_hz")
    amc = md.classify(x, 1.0, rs=rs)
    print(f'{mod:6s} n={x.size:6d}  rs={rs if rs is None else round(rs, 6)} (truth 0.125)  '
          f'classify={amc["primary"]} {amc["confidence"]:.2f}  '
          f'cands={[(c["modulation"], round(c["probability"],2)) for c in amc["candidates"][:3]]}')
