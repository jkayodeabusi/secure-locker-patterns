import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.pop("BREAK_PATTERNS", None)
os.environ.pop("DEMO_MODE", None)
