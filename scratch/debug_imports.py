import time
import sys
import os

# Ensure the root directory is in sys.path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.insert(0, root)

def time_import(module_name):
    print(f"Starting import of {module_name}...", flush=True)
    start = time.time()
    try:
        if module_name in sys.modules:
            del sys.modules[module_name] # Force re-import
        __import__(module_name)
        print(f"Import {module_name} took {time.time() - start:.2f}s", flush=True)
    except Exception as e:
        print(f"Import {module_name} failed: {e}", flush=True)

modules = [
    "streamlit",
    "dotenv",
    "langchain_groq",
    "agents",
    "rag",
    "backend",
    "app"
]

for m in modules:
    time_import(m)
