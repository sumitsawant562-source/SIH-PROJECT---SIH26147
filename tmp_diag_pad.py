import sys
sys.path.insert(0, "/home/user")
import numpy as np
from dsp import synth, interleave as il

spec = dict(synth.DEFAULT_SPEC)
spec.update({"modulation": "QPSK", "fs": 200000.0, "symbol_rate": 25000.0, "n_symbols": 1500,
             "snr_db": 30.0, "fec": "conv_K7_r1_2", "interleaver": "diagonal", "interleaver_rows": 16,
             "seed": 11, "carrier_offset_hz": 2000.0, "payload": "text", "text": "INTERLEAVE TRUTH TEST "})
sig = synth.generate_signal(spec)
gt = sig.ground_truth
n_coded = gt["n_coded_bits"]
payload = np.array([int(c) for c in gt["payload_bitstring"]], np.uint8)
code = synth.ConvCode.preset(gt.get("fec_code") or "conv_K7_r1_2") if hasattr(synth.ConvCode, "preset") else None
coded = synth.conv_encode(payload, code) if code is not None else None
if coded is None or coded.size != n_coded:
    print("coded reconstruction unavailable", None if coded is None else coded.size, n_coded)
else:
    ilv = synth.interleave(coded.astype(np.uint8), "diagonal", rows=16)
    print("generated ilv len", ilv.size)
    g = {"kind": "diagonal", "params": {"rows": 16}, "label": "diagonal rows=16"}
    for drop in (0, 18, 36):
        recv = ilv[drop:]
        pad = np.concatenate([np.zeros(drop, np.uint8), recv]) if drop else recv
        de = pad[il._perm_for(pad.size, g)]
        n = min(de.size, coded.size)
        agree = float(np.mean(de[:n] == coded[:n].astype(np.uint8)))
        print(f"  drop={drop:3d} recv={recv.size} de-interleaved agreement={agree:.4f}")
