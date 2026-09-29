import sys, time
sys.path.insert(0, "/home/user")
import numpy as np
from dsp import synth, demod, interleave as il

CASES = [("none", {}), ("diagonal", {"interleaver_rows": 16}),
         ("convolutional", {"interleaver_rows": 16, "interleaver_depth": 4}),
         ("block", {"interleaver_rows": 16}), ("pseudo-random", {"interleaver_seed": 12345})]

for kind, extra in CASES:
    spec = dict(synth.DEFAULT_SPEC)
    spec.update({"modulation": "QPSK", "fs": 200000.0, "symbol_rate": 25000.0, "n_symbols": 1500,
                 "snr_db": 30.0, "fec": "conv_K7_r1_2", "interleaver": kind, "seed": 11,
                 "carrier_offset_hz": 2000.0, "payload": "text",
                 "text": "INTERLEAVE TRUTH TEST "})
    spec.update(extra)
    sig = synth.generate_signal(spec)
    x = np.asarray(sig.samples)
    dm = demod.demodulate(x, 200000.0, "QPSK", 25000.0, rolloff=0.35)
    bits = np.asarray(dm["bits"]).astype(np.int8)
    _l = dm.get("llrs")
    soft = np.asarray(_l if _l is not None else bits * 2.0 - 1.0, dtype=np.float64)
    for probe in (128, 256):
        t0 = time.time()
        r = il.test_deinterleaving(soft, bits, max_bits=3000, stage_bits=2200, n_probe_bits=probe,
                                   time_budget_s=120.0)
        dt = r.get("decode_test") if "decode_test" in r else (r or {})
        d = r
        best = d.get("best") or {}
        base = (d.get("baseline") or {}).get("distance_per_bit")
        print(f'{kind:14s} probe={probe:4d} base={base} best={best.get("geometry")} '
              f'rel={best.get("relative_improvement")} beats={best.get("beats_control_max")} '
              f'{time.time()-t0:5.1f} s')
    # full analysis verdict
    t0 = time.time()
    full = il.analyse_interleaving(soft, bits, max_bits=3000, time_budget_s=120.0)
    claimed = [h for h in full["hypotheses"] if not h.get("rank_excluded")]
    print(f'    -> analyse_interleaving: best={full.get("best") and full["best"].get("geometry")} '
          f'claims={[(h["kind"], round(h["confidence"], 2)) for h in claimed]} {time.time()-t0:.1f} s')
