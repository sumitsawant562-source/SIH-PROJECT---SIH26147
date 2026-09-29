import sys
sys.path.insert(0, "/home/user")
import numpy as np
from dsp import synth, demod, interleave as il

def record(kind, n_symbols=1500):
    spec = dict(synth.DEFAULT_SPEC)
    spec.update({"modulation": "QPSK", "fs": 200000.0, "symbol_rate": 25000.0, "n_symbols": n_symbols,
                 "snr_db": 30.0, "fec": "conv_K7_r1_2", "interleaver": kind, "interleaver_rows": 16,
                 "seed": 11, "carrier_offset_hz": 2000.0, "payload": "text",
                 "text": "INTERLEAVE TRUTH TEST "})
    sig = synth.generate_signal(spec)
    dm = demod.demodulate(np.asarray(sig.samples), 200000.0, "QPSK", 25000.0, rolloff=0.35)
    return np.asarray(dm["bits"]).astype(np.int8)

geoms = {g["label"]: g for g in il.candidate_geometries()}

def _aligned(bits_arr, g, off):
    if off <= 0:
        return bits_arr[il._perm_for(bits_arr.size, g)]
    padded = np.concatenate([np.zeros(off, dtype=np.int8), bits_arr])
    return padded[il._perm_for(bits_arr.size + off, g)]

codes = list(il.STANDARD_CONV_CODES)[:3]
for kind, glabel in (("diagonal", "diagonal rows=16"), ("pseudo-random", "pseudo-random seed=12345"),
                     ("block", "block rows=16")):
    bits = record(kind)
    g = geoms[glabel]
    print(f"\n{kind} -> geometry '{glabel}' (bits {bits.size})")
    # baseline (identity)
    ev0 = il._best_decode_evidence(bits[:2200], None, codes)
    print(f"  identity             d={ev0['distance_per_bit']:.5f}")
    for off in (0, 1, 2, 4, 8, 16, 32, 48, 53, 64, 128, 256):
        d_bits = _aligned(bits[:3000], g, off)
        ev = il._best_decode_evidence(d_bits, None, codes)
        dpb = ev.get("distance_per_bit")
        star = " <== correct geometry" if dpb is not None and dpb < 0.02 else ""
        print(f"  correct geom off={off:4d}   d={dpb:.5f}{star}")
    # probe ranking (what the probe sees), probe_len 2048
    probe = bits[:2048]
    scored = []
    for off in sorted(set(range(0, 64)) | {64, 96, 128, 192, 256}):
        db = _aligned(probe, g, off)
        ev = il._best_decode_evidence(db[:2048 - off], None, codes[:1])
        if ev.get("ok"):
            scored.append((round(ev["distance_per_bit"], 5), off))
    scored.sort()
    print("  probe top-6:", scored[:6])
