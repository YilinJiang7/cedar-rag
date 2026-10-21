import argparse
import re
from dataclasses import dataclass
from pathlib import Path

STOPWORDS = {
    "a", "an", "the", "is", "are", "to", "of", "in", "at", "for",
    "and", "or", "may", "can", "i", "it", "be",
}


@dataclass
class Chunk:
    id: str
    filename: str
    text: str


def tokenize(text):
    return set(re.findall(r"[^\W_]+", text.lower())) - STOPWORDS


def load_chunks(docs_dir):
    chunks = []
    for filename in ("access.txt", "training.txt", "booking.txt"):
        contents = (docs_dir / filename).read_text(encoding="utf-8")
        for paragraph in contents.strip().split("\n\n"):
            label, text = paragraph.split("] ", 1)
            chunks.append(Chunk(label[1:], filename, text))
    return chunks


def score_chunks(question, chunks):
    query_words = tokenize(question)
    scored = []
    for chunk in chunks:
        matched_words = query_words & tokenize(chunk.text)
        scored.append((len(matched_words), chunk, matched_words))
    return scored


def main():
    parser = argparse.ArgumentParser(description="Retrieve Cedar Lab passages by keyword overlap.")
    parser.add_argument("question", help="Question to search for; wrap it in quotes.")
    parser.add_argument("--k", type=int, default=2, help="Maximum passages to select (default: 2).")
    args = parser.parse_args()
    if args.k < 1:
        parser.error("--k must be at least 1")

    chunks = load_chunks(Path(__file__).resolve().parent / "docs")
    scored = score_chunks(args.question, chunks)
    ranked = sorted(scored, key=lambda item: (-item[0], item[1].id))

    print(f"Query words: {', '.join(sorted(tokenize(args.question)))}")
    print("All chunk scores (highest first):")
    for score, chunk, matched_words in ranked:
        matches = ", ".join(sorted(matched_words)) or "(none)"
        print(f"{chunk.id} | {chunk.filename} | score={score} | matched={matches}")

    selected = [item for item in ranked if item[0] > 0][:args.k]
    if not selected:
        print("No matching passages.")
        return

    print(f"\nSelected passages (k={args.k}):")
    for score, chunk, matched_words in selected:
        print(f"\n[{chunk.id}] {chunk.filename}")
        print(chunk.text)


if __name__ == "__main__":
    main()
