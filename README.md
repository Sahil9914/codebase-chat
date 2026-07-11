# Codebase Chat — RAG for Code

Chat with any GitHub repository in plain English. Paste a repo URL, and ask questions like "how does backpropagation work?" or "what does the Neuron class do?" — get accurate, plain-English answers grounded in the actual source code, not hallucinated.

## How it works

1. **Clone** — downloads the target GitHub repo locally
2. **Parse** — uses Python's native `ast` library to split code into structural chunks at the function/method level (not naive character-based splitting), preserving file, class, and line-number metadata
3. **Embed** — converts each code chunk into a vector using `BAAI/bge-small-en-v1.5`, a free, locally-run embedding model
4. **Store** — saves chunks + embeddings in Qdrant, a vector database optimized for semantic search
5. **Retrieve** — converts the user's question into the same vector space and finds the closest matching code chunks
6. **Answer** — passes the retrieved chunks + question to Gemini, which writes a grounded, accurate answer citing the real code

## Why structural (AST-based) chunking instead of naive text splitting

Splitting code every N characters or lines risks cutting a function mid-logic — for example, separating an `if` condition from its `return` statement, which can flip the actual meaning of the code. Using `ast`, every chunk is guaranteed to be a complete, semantically meaningful unit (one full function or method), which produces sharper, more accurate embeddings and more reliable search results.

## Tech stack

| Component | Tool |
|---|---|
| Code parsing | Python `ast` (built-in) |
| Repo cloning | GitPython |
| Embeddings | `BAAI/bge-small-en-v1.5` (Sentence Transformers) |
| Vector database | Qdrant (local, via Docker) |
| LLM | Google Gemini (`gemini-2.0-flash`) |
| UI | Streamlit |

## Setup

```bash
git clone https://github.com/Sahil9914/codebase-chat.git
cd codebase-chat

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

docker run -p 6333:6333 qdrant/qdrant

echo "GEMINI_API_KEY=your_key_here" > .env

streamlit run app.py
```

## Usage

1. Paste a GitHub URL in the sidebar (e.g. `https://github.com/karpathy/micrograd`)
2. Click **Load Repo** — the app clones, parses, and indexes the repo
3. Ask questions in the chat box — answers are grounded in the actual indexed code, with a "View source code used" panel showing similarity scores and exact source references

## Design decisions

- **Function-level chunking, not class-level**: a whole-class chunk blurs the meaning of multiple unrelated methods together, weakening search precision. Each function gets its own embedding; the parent class is attached as metadata instead.
- **Local embeddings over an embedding API**: keeps the pipeline free and fast for development; no external dependency for the retrieval step.
- **Gemini for generation only**: the LLM's job is limited to reading retrieved context and writing an answer — it never sees the whole repo, which keeps answers grounded and avoids context-window limits on large codebases.

## Author

Sahil Chalotra — [GitHub](https://github.com/Sahil9914) · [LinkedIn](https://linkedin.com/in/sahilchalotraa)
