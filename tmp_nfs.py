import sys, time
sys.path.insert(0, "/home/user")
import numpy as np
from dsp import params as pr, modulation as md, synth

# clean 8PSK, known rate; compare classification/rate with a *known* fs vs normalised fs = 1.0
spec = dict(synth.DEFAULT_SPEC)
spec.update({"modulation": "8PSK", "fs": 200000.0, "symbol_rate": 125000.0, "n_symbols": 3000,
             "snr_db": 24.0, "fec": "none", "carrier_offset_hz": 3000.0, "seed": 7})
sig = synth.generate_signal(spec)
x = np.asarray(sig.samples)
print("samples:", x.size)
for fs, label in ((200000.0, "fs known"), (1.0, "fs normalised (unknown rate)")):
    t0 = time.time()
    rpr = pr.full_parameter_report(x, fs)
    rs = (rpr.get("symbol_rate") or rpr.get("primary") or {})
    print(f'\n{label}: symbol_rate record keys={list(rpr.keys())[:6]}')
    t1 = time.time()
    amc = md.classify(x, fs, rs=None, obw_hz=None)
    print(f'  classify (no rs hint): {amc["primary"]} conf {amc["confidence"]:.3f} '
          f'[{time.time()-t1:.1f} s]  candidates: {[(c["modulation"], round(c["probability"],2)) for c in amc["candidates"][:4]]}')
