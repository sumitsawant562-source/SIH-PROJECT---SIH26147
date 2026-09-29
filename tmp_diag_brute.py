import sys, time
sys.path.insert(0, "/home/user")
import numpy as np
from dsp import synth, demod, interleave as il

spec = dict(synth.DEFAULT_SPEC)
spec.update({"modulation": "QPSK", "fs": 200000.0, "symbol_rate": 25000.0, "n_symbols": 1500,
             "snr_db": 30.0, "fec": "conv_K7_r1_2", "interleaver": "diagonal", "interleaver_rows": 16,
             "seed": 11, "carrier_offset_hz": 2000.0, "payload": "text", "text": "INTERLEAVE TRUTH TEST "})
sig = synth.generate_signal(spec)
dm = demod.demodulate(np.asarray(sig.samples), 200000.0, "QPSK", 25000.0, rolloff=0.35)
bits = np.asarray(dm["bits"]).astype(np.int8)
gt = sig.ground_truth
print("recovered bits:", bits.size, "generated interleaved len:", gt.get("n_coded_bits"))
geoms = {g["label"]: g for g in il.candidate_geometries()}
g = geoms["diagonal rows=16"]
codes = list(il.STANDARD_CONV_CODES)[:3]
t0 = time.time()
best = []
for off in range(0, 1200):
    padded = np.concatenate([np.zeros(off, np.int8), bits[:3000]]) if off else bits[:3000]
    d = padded[il._perm_for(padded.size, g)]
    ev = il._best_decode_evidence(d, None, codes)
    best.append((round(ev.get("distance_per_bit", 1.0), 5), off))
best.sort()
print("brute-force best offsets:", best[:6], f"{time.time()-t0:.1f} s")
for dpb, off in best[:3]:
    padded = np.concatenate([np.zeros(off, np.int8), bits[:3000]]) if off else bits[:3000]
    d = padded[il._perm_for(padded.size, g)]
    print("   off", off, "d", dpb)
# also: what does the *generated* interleaved bit stream decode to after de-interleaving?
coded = np.array([int(c) for c in np.unpackbits(np.frombuffer(bytes.fromhex(gt["payload_bytes_hex"]), np.uint8))][:200], np.int8) if gt.get("payload_bytes_hex") else None
print("GT keys:", [k for k in gt.keys() if "bit" in k or "interleav" in k or "fec" in k])
