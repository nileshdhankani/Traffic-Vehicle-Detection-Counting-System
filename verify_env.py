#!/usr/bin/env python3
"""
Verify that all dependencies are correctly installed.
Run this after pip install to confirm the environment is ready.
"""

import sys

print("=" * 60)
print("ENVIRONMENT VERIFICATION")
print("=" * 60)

# Check Python version
print(f"\n[1/5] Python Version: {sys.version}")
if sys.version_info < (3, 10):
    print("⚠️  WARNING: Python 3.10+ is recommended")
else:
    print("✓ Python version OK")

# Check OpenCV
try:
    import cv2
    print(f"\n[2/5] OpenCV: {cv2.__version__}")
    print("✓ OpenCV imported successfully")
except ImportError as e:
    print(f"\n[2/5] OpenCV: FAILED - {e}")
    sys.exit(1)

# Check Ultralytics YOLO
try:
    from ultralytics import YOLO
    print(f"\n[3/5] Ultralytics YOLO: Available")
    print("✓ YOLO imported successfully")
except ImportError as e:
    print(f"\n[3/5] Ultralytics YOLO: FAILED - {e}")
    sys.exit(1)

# Check Streamlit
try:
    import streamlit
    print(f"\n[4/5] Streamlit: {streamlit.__version__}")
    print("✓ Streamlit imported successfully")
except ImportError as e:
    print(f"\n[4/5] Streamlit: FAILED - {e}")
    sys.exit(1)

# Check NumPy & Pandas
try:
    import numpy as np
    import pandas as pd
    print(f"\n[5/5] NumPy: {np.__version__}, Pandas: {pd.__version__}")
    print("✓ NumPy and Pandas imported successfully")
except ImportError as e:
    print(f"\n[5/5] NumPy/Pandas: FAILED - {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL DEPENDENCIES VERIFIED")
print("=" * 60)
print("\nYou are ready to proceed to Phase 2.")
print("\nNext step: Run 'python verify_env.py' to confirm this output,")
print("then let me know it worked.")
