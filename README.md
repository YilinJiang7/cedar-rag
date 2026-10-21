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

## Embedding retrieval and inspection

Run from the project folder using the prepared environment and existing local model cache:

```sh
.venv/bin/python retrieve_embeddings.py "May a trained graduate student operate the laser alone at 19:00?"
.venv/bin/python retrieve_embeddings.py "May a trained graduate student operate the laser alone at 19:00?" "How do I cancel a booking?" --k 2
```

The separate embedding retriever loads `sentence-transformers/all-MiniLM-L6-v2` on the CPU with `cache_folder="_local/models"` and `local_files_only=True`. It encodes only passage texts with `encode_document()` once per run and reuses them for every question, encoded with `encode_query()` by the same model. Both calls request normalized NumPy embeddings. IDs and filenames remain metadata.

The model turns each text into a vector of 384 numbers. Normalization makes each vector's length approximately 1. Retrieval multiplies corresponding question and passage coordinates and adds all 384 products: this is the dot product. The script also divides the dot product by the two vector lengths to calculate cosine similarity directly and verifies numerical agreement.

The program prints package versions, actual shapes, lengths, the first 12 coordinates of every vector, all six scores, and the selected source passages. Coordinates are shown to four decimal places but have no individual semantic labels. Computation retains the model's unrounded values, converted to float64 for arithmetic. For each question's top passage it shows the first 12 products, their subtotal, the remaining 372 coordinates' subtotal, and the full similarity. All 384 coordinates determine retrieval. Scores sort descending, with ties by ascending ID; `--k` defaults to 2 and selects the top `k` available passages without a relevance threshold.

The actual Q1 run is saved in `evidence/embedding-inspection.txt`. No answer is generated, and `retrieve.py` is unchanged.
