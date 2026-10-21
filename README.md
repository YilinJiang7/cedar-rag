# CEDAR-RAG

A small teaching project for the retrieval step of RAG (retrieval-augmented generation). It prints matching source passages and does not generate an answer.

## Run

Use the existing virtual environment. The keyword retriever itself uses only Python's standard library; it does not load the embedding model or need a model download.

```sh
cd /Users/yilinjiang/Projects/cedar-rag
.venv/bin/python retrieve.py "May a trained graduate student operate the laser alone at 19:00?"
.venv/bin/python retrieve.py "May a trained graduate student operate the laser alone at 19:00?" --k 1
```

`question` is a required quoted argument. `--k` is a positive integer, defaults to 2, and limits the number of selected passages.

## How retrieval works

- `docs/access.txt`, `docs/training.txt`, and `docs/booking.txt` contain the six supplied paragraphs verbatim. Each labeled paragraph is one chunk.
- The loader stores each chunk's ID, filename, and complete paragraph text separately. Only the paragraph text is searched.
- Both the question and paragraph text are lowercased and split into alphanumeric words. Punctuation and underscores separate words; for example, `19:00` becomes `19` and `00`.
- Exactly these stopwords are removed from both: `a, an, the, is, are, to, of, in, at, for, and, or, may, can, i, it, be`.
- A score is the number of distinct remaining question words also found in the paragraph. Repeated words count once. There is no stemming, synonym expansion, or semantic search.
- All six scores and matched words are printed in descending score order, with ties broken by ascending chunk ID. Up to `k` positive scoring chunks are selected and printed with their IDs, filenames, and complete text.
- If every score is zero, the program prints `No matching passages.`

`retrieve.py` contains loading, tokenization, scoring, ranking, and command line output. The existing `setup_check.py` and `evidence/setup-check.txt` remain unchanged.
