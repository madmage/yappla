"""Verify monkey-patching"""

from abduction03 import EntailmentEngine

engine = EntailmentEngine()
print(f"prove method: {engine.prove}")
print(f"method code: {engine.prove.__code__.co_filename}")

# Check if it's the original or patched
import inspect
source = inspect.getsource(engine.prove)
print(f"\nFirst 200 chars of prove method source:")
print(source[:200])
