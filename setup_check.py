import platform
from importlib.metadata import version

from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME, device="cpu", cache_folder="_local/models")
vector = model.encode("This is a test sentence.")

print(f"Python: {platform.python_version()}")
for package in ("sentence-transformers", "torch", "transformers", "numpy"):
    print(f"{package}: {version(package)}")
print(f"Model: {MODEL_NAME}")
print(f"Device: {model.device}")
print(f"Vector shape: {vector.shape}")
