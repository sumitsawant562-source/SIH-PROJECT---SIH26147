import sys, json, time
sys.path.insert(0, "/home/user")
import numpy as np
from dsp import synth, modulation as md, spectrum as sp, params as pr, waterfall as wf, detect as det

spec = dict(synth.DEFAULT_SPEC)
spec.update({"modulation": "8PSK", "fs": 200000.0, "symbol_rate": 25000.0, "n_symbols": 3000,
             "snr_db": 24.0, "fec": "none", "carrier_offset_hz": 3000.0, "seed": 7})
sig = synth.generate_signal(spec)
x = np.asarray(sig.samples)
print("samples", x.size, "truth sps", 200000/25000)
d = det.detect_signals(x, 200000.0, snr_threshold_db=6.0)
chosen = det.rank_signals(d["signals"])[0]
print("chosen emission:", {k: chosen[k] for k in ("f_lo_hz","f_hi_hz","t0_s","t1_s","snr_db","bandwidth_hz","center_frequency_hz")})
pad = 0.60 * max(chosen["f_hi_hz"] - chosen["f_lo_hz"], 1.0)
seg = wf.extract_band(x, 200000.0, chosen["f_lo_hz"] - pad, chosen["f_hi_hz"] + pad, t0_s=chosen["t0_s"], t1_s=chosen["t1_s"])
print("segment:", seg.get("ok"), seg["samples"].size, "fs", seg["fs"], "bw", seg.get("bw_hz"), "note", str(seg.get("message"))[:80])
y, fs = seg["samples"], seg["fs"]
rec = sp.analyse_spectrum(x, 200000.0)
s2 = sp.analyse_spectrum(y, fs, noise_density_hint=rec.get("noise_density"))
print("segment spectrum:", {k: s2.get(k) for k in ("snr_db","obw_99_hz","noise_floor_db","center_frequency_hz")})
obw = s2.get("obw_99_hz"); snr = s2.get("snr_db")
print("envelope stats on segment:", json.dumps(pr.amplitude_statistics(y))[:200])
t0 = time.time()
amc = md.classify(y, fs, rs=25000.0, obw_hz=obw, snr_db=snr)
print(f"\nclassify WITH rs (25000, true): {amc['primary']} {amc['confidence']:.3f} [{time.time()-t0:.1f}s]")
print("candidates:", [(c["modulation"], round(c["probability"],2)) for c in amc["candidates"][:5]])
for f in (amc.get("rules_fired") or [])[:14]:
    print(f'   w={f.get("weight"):+.2f} {str(f.get("modulation")):6s} {str(f.get("rule"))[:110]}')
