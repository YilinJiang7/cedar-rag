# CEDAR-RAG

Author: Yilin Jiang (worked solo, no partner).

A small teaching project for the retrieval step of RAG (retrieval-augmented generation). It prints matching source passages and does not generate an answer.

## Environment

Versions recorded by the actual run in `evidence/setup-check.txt`:

| Component | Version |
|---|---|
| Python | 3.11.14 |
| sentence-transformers | 6.1.0 |
| torch | 2.14.1 |
| transformers | 5.20.2 |
| numpy | 2.4.6 |

Model: `sentence-transformers/all-MiniLM-L6-v2`. Model loading and inference use CPU only.

One-time setup commands (run only when creating the environment):

```sh
cd /Users/yilinjiang/Projects/cedar-rag
/Users/yilinjiang/.local/share/uv/python/cpython-3.11.14-macos-aarch64-none/bin/python3.11 -m venv .venv
.venv/bin/python -m pip install sentence-transformers numpy
.venv/bin/python setup_check.py
```

The Python command above uses the resolved Python 3.11 executable installed on this machine. On another machine, use the path to its installed Python 3.11 executable. The versions above record this project's setup run; the unpinned install command may install different package versions when run later.

The model downloads once into `_local/models` during the first setup check and is reused from that cache. `_local/` (including `_local/models`) and `.venv/` are git-ignored. The embedding retriever loads only the already-downloaded local model files.

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

## Files

The submission tracks the following files:

| File | Contents |
|---|---|
| `.gitignore` | Ignore rules for `.venv/`, `__pycache__/`, `*.pyc`, `.DS_Store`, and `_local/`. |
| `README.md` | Author, environment, setup and run commands, retrieval explanations, file inventory, and submission notes. |
| `docs/access.txt` | Verbatim Cedar Lab passages A1 and A2: access hours and the laser two-person rule. |
| `docs/training.txt` | Verbatim Cedar Lab passages T1 and T2: laser training and accompanied visitors. |
| `docs/booking.txt` | Verbatim Cedar Lab passages B1 and B2: room bookings and cancellation. |
| `retrieve.py` | Standard-library keyword retrieval with exact stopwords, distinct-word overlap scores, and ranked source passages. |
| `retrieve_embeddings.py` | Cached CPU embedding retrieval, vector inspection, dot-product and cosine checks, and ranked source passages. |
| `setup_check.py` | Environment check that loads the model on the CPU, encodes a test sentence, and prints versions and vector shape. |
| `results.csv` | Q1-Q4 selected IDs and scores, evidence targets, and human review. The `keyword_evidence_complete`, `embedding_evidence_complete`, and `observation` columns are our human judgments. |
| `evidence/setup-check.txt` | Actual setup-check output, including package versions, model name, CPU device, and vector shape. |
| `evidence/embedding-inspection.txt` | Actual Q1 embedding run, including coordinates, lengths, all scores, similarity calculations, and selected passages. |
| `evidence/retrieval-runs.txt` | Actual keyword and embedding output for Q1-Q4 at `k=2`, with commands and execution environment. |
| `evidence/k-experiment.txt` | Q1 embedding selections for `k=1`, `k=2`, and `k=3`; actual reruns for `k=1` and `k=3`; and a separately labeled human judgment section. |
| `evidence/answer-audit-q1.md` | Q1's original generated answer, human audit, one prompt revision, revised answer, and follow-up audit using the same passages. |
| `evidence/answer-audit-q4.md` | Q4's original generated answer and human audit for a question whose answer is absent from the sources. |

## Answer generation (Task 4)

Answers were generated manually in fresh Codex conversations with no file access, pasting only the question, the `k=2` embedding passages, and the prompt. See `evidence/answer-audit-q1.md` and `evidence/answer-audit-q4.md` for the answers, audits, and Q1 prompt revision. The retrieval scripts themselves print passages and do not generate answers.

All run output in evidence/ is our own; no borrowed output.

## Individual reflection — Yilin Jiang

(to be added)
