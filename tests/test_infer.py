import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml_pipeline.infer import infer_log
print(infer_log({"raw": "Too many connections from 10.0.0.1"}))  # should be 'dos_attack'


