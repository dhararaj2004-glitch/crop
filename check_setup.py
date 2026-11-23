"""Quick health check. Run:  python check_setup.py"""
import os
import sys

ok = True
print(f"Python {sys.version.split()[0]}")
if not ((3, 10) <= sys.version_info[:2] <= (3, 13)):
    print("  ! TensorFlow 2.20 needs Python 3.10 - 3.13 (you have a different version).")
    ok = False

for mod in ["streamlit", "cv2", "numpy", "PIL"]:
    try:
        __import__(mod)
        print(f"  ok  {mod}")
    except Exception:
        print(f"  MISSING  {mod}  -> pip install -r requirements.txt")
        ok = False

# Check for ML runtime (ai-edge-litert, tflite-runtime, or tensorflow)
has_runtime = False
for mod in ["ai_edge_litert", "tflite_runtime", "tensorflow"]:
    try:
        __import__(mod)
        print(f"  ok  {mod} (ML runtime)")
        has_runtime = True
        break
    except Exception:
        pass
if not has_runtime:
    print("  MISSING  ML runtime (ai_edge_litert or tensorflow) -> pip install ai-edge-litert")
    ok = False

here = os.path.dirname(os.path.abspath(__file__))
m = os.path.join(here, "model")
has_model = any(os.path.exists(os.path.join(m, f)) for f in ("leaf_model.keras", "leaf_model.tflite"))
has_classes = os.path.exists(os.path.join(m, "class_names.json"))
print(f"  {'ok ' if has_model else 'MISSING'}  model/leaf_model.keras (or .tflite)")
print(f"  {'ok ' if has_classes else 'MISSING'}  model/class_names.json")
if not (has_model and has_classes):
    print("\nThe app will still start (severity grader works), but disease prediction needs the two model files.")
    print("Train them with notebooks/kaggle_train.ipynb on Kaggle - see README.md, Step 1.")
print("\nAll good." if ok else "\nFix the items above, then run again.")
