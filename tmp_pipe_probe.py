import sys, time, json
sys.path.insert(0, "/home/user")
import sqlalchemy as sa
from backend.app.db import SessionLocal
from backend.app.models import UploadedFile
from backend.app.storage import load_samples, effective_fs
from dsp import pipeline as pipe

db = SessionLocal()
f = db.scalars(sa.select(UploadedFile).where(UploadedFile.filename == "sample_qpsk.wav")).first()
loaded = load_samples(f)
fs, known, src = effective_fs(f, loaded)
x = loaded["samples"]
print("samples:", x.size, "fs:", fs, "known:", known, src)
t0 = time.time()
res = pipe.analyse_record(x, fs, {"run_hypotheses": True, "run_interleaving": False})
print(f"TOTAL {time.time()-t0:.1f} s")
for s in res["stages"]["stages"]:
    print(f'  {s["duration_ms"]:9.1f} ms  {s["status"]:6s} {s["name"][:60]:62s} {s["note"][:70]}')
json.dump(res, open("/tmp/pipe_res.json", "w"), default=str)
print("saved /tmp/pipe_res.json")
