# test_distilbert.py
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from ml_pipeline.distilbert import classify_threat
print(classify_threat("Multiple failed login attempts from 192.168.1.10"))

