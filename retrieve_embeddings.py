import argparse
import platform
from importlib.metadata import version
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from retrieve import load_chunks

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def print_vector(label, vector):
    coordinates = ", ".join(f"{value:.4f}" for value in vector[:12])
    print(f"{label}: shape={vector.shape}, length={np.linalg.norm(vector):.10f}")
    print(f"  First 12 coordinates: [{coordinates}]")


def inspect_question(model, question, chunks, document_vectors, document_lengths, k):
    query_vector = model.encode_query(
        question,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    ).astype(np.float64)
    print_vector("Question vector", query_vector)
    query_length = np.linalg.norm(query_vector)
    np.testing.assert_allclose(query_length, 1.0, rtol=0, atol=1e-6)
    print("Question length approximately 1: verified (absolute tolerance 1e-6)")

    scores = document_vectors @ query_vector
    cosines = scores / (document_lengths * query_length)
    np.testing.assert_allclose(scores, cosines, rtol=1e-6, atol=1e-7)
    ranked = sorted(range(len(chunks)), key=lambda index: (-scores[index], chunks[index].id))

    print("All passage scores (descending; ties by ascending ID):")
    for index in ranked:
        chunk = chunks[index]
        print(f"{chunk.id} | {chunk.filename} | dot={scores[index]:.10f} | cosine={cosines[index]:.10f}")
    difference = np.max(np.abs(scores - cosines))
    print(f"Dot/cosine agreement: verified (rtol=1e-6, atol=1e-7; max difference={difference:.12e})")

    top_index = ranked[0]
    products = query_vector * document_vectors[top_index]
    first_subtotal = np.sum(products[:12])
    remaining_subtotal = np.sum(products[12:])
    np.testing.assert_allclose(first_subtotal + remaining_subtotal, scores[top_index], rtol=1e-12, atol=1e-12)
    print(f"\nSimilarity inspection for top passage {chunks[top_index].id}:")
    print("First 12 coordinate products: [" + ", ".join(f"{value:.10f}" for value in products[:12]) + "]")
    print(f"First 12 subtotal: {first_subtotal:.10f}")
    print(f"Remaining {len(products) - 12} coordinates subtotal: {remaining_subtotal:.10f}")
    print(f"Full similarity (all {len(products)} coordinates): {scores[top_index]:.10f}")
    print(f"Direct cosine = dot / (question length * passage length): {cosines[top_index]:.10f}")
    print("Subtotal sum agrees with full similarity: verified (rtol=1e-12, atol=1e-12)")

    print(f"\nSelected passages (k={k}; no relevance threshold):")
    for index in ranked[:k]:
        chunk = chunks[index]
        print(f"\n[{chunk.id}] {chunk.filename}")
        print(chunk.text)


def main():
    parser = argparse.ArgumentParser(description="Inspect real Cedar Lab embeddings and retrieve passages.")
    parser.add_argument("questions", nargs="+", help="One or more questions, each wrapped in quotes.")
    parser.add_argument("--k", type=int, default=2, help="Maximum passages to select (default: 2).")
    args = parser.parse_args()
    if args.k < 1:
        parser.error("--k must be at least 1")

    model = SentenceTransformer(
        MODEL_NAME, device="cpu", cache_folder="_local/models", local_files_only=True,
    )
    chunks = load_chunks(Path(__file__).resolve().parent / "docs")
    document_vectors = model.encode_document(
        [chunk.text for chunk in chunks],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    ).astype(np.float64)
    document_lengths = np.linalg.norm(document_vectors, axis=1)
    np.testing.assert_allclose(document_lengths, 1.0, rtol=0, atol=1e-6)

    print(f"Python: {platform.python_version()}")
    for package in ("sentence-transformers", "torch", "transformers", "numpy"):
        print(f"{package}: {version(package)}")
    print(f"Model: {MODEL_NAME}")
    print(f"Device: {model.device}")
    print("Cache: _local/models (local files only)")
    print(f"Document matrix shape: {document_vectors.shape}")
    print("Document embeddings computed once and reused for every question in this run.")
    print("Model outputs are retained without rounding and converted to float64 for similarity arithmetic.")
    print(f"All {document_vectors.shape[1]} coordinates, not just the displayed 12, are used in retrieval.")
    print("Individual coordinates are not assigned semantic names.")
    for chunk, vector in zip(chunks, document_vectors):
        print_vector(f"Document {chunk.id} ({chunk.filename})", vector)
    print("All document lengths approximately 1: verified (absolute tolerance 1e-6)")

    for number, question in enumerate(args.questions, start=1):
        print(f"\nQ{number}: {question}")
        inspect_question(model, question, chunks, document_vectors, document_lengths, args.k)


if __name__ == "__main__":
    main()
