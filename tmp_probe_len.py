import sys, time
sys.path.insert(0, "/home/user")
import numpy as np
from dsp import synth, demod, interleave as il

spec = dict(synth.DEFAULT_SPEC)
spec.update({"modulation": "QPSK", "fs": 200000.0, "symbol_rate": 25000.0, "n_symbols": 1500,
             "snr_db": 30.0, "fec": "conv_K7_r1_2", "interleaver": "block", "interleaver_rows": 16,
             "seed": 11, "carrier_offset_hz": 2000.0, "payload": "text",
             "text": "INTERLEAVE TRUTH TEST "})
sig = synth.generate_signal(spec)
x = np.asarray(sig.samples)
dm = demod.demodulate(x, 200000.0, "QPSK", 25000.0, rolloff=0.35)
bits = np.asarray(dm["bits"]).astype(np.int8)
_l = dm.get("llrs"); soft = np.asarray(_l if _l is not None else bits * 2.0 - 1.0, dtype=np.float64)
for probe in (256, 512, 768, 1024):
    t0 = time.time()
    r = il.test_deinterleaving(soft, bits, max_bits=3000, stage_bits=2200, n_probe_bits=probe,
                              time_budget_s=120.0)
    cands = r["candidates"][:3]
    print(f'block-16 probe={probe:4d} {time.time()-t0:5.1f}s base={r["baseline"]["distance_per_bit"]:.4f} '
          f'-> ' + " | ".join(f'{c["geometry"]} rel={c["relative_improvement"]:.3f}' for c in cands))
