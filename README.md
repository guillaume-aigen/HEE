# Heuristic Extraction Engine (HEE)

HEE is a local, five-stage Python pipeline that turns long-form documents you are authorized to process into structured Markdown and JSON reasoning artifacts for downstream LLM use. It can also package aggregated JSON modules as a Claude skill folder.

The project is designed for local processing with Marker, Ollama, and a local model. No cloud API key is required.

## Important use and rights notice

Use HEE only with documents you own, are licensed to process, or otherwise have permission to use. Keep copyright notices, attribution, citations, and publication information intact. Do not commit or redistribute source books, private documents, or generated output that you do not have the right to share.

The included `.gitignore` deliberately excludes source inputs, generated outputs, and the private working manual.

<img width="1870" height="941" alt="Artboard 62" src="https://github.com/user-attachments/assets/36bfbb0f-5958-425e-8b35-d7af430cb3db" />

## Pipeline

1. **Stage 1 — Ingest and normalize**: Converts EPUB and PDF inputs to Markdown with Marker, preserves metadata and rights notices, and normalizes conversion artifacts.
2. **Stage 2 — Slice**: Splits Markdown into header-aware chunks with overlap for local-model processing.
3. **Stage 3 — Mine logic**: Uses Ollama to extract a consistent JSON schema of heuristics, classifications, and contextual anchors.
4. **Stage 4 — Aggregate**: Combines fragments per source domain and removes exact duplicate records.
5. **Stage 5 — Package**: Copies master JSON modules into a Claude-compatible skill folder and generates `SKILL.md` instructions.

## Prerequisites

- Python 3.10 or later
- [Ollama](https://ollama.com/) running locally
- A local Ollama model compatible with the Stage 3 configuration (default: `qwen2.5:32b`)
- Marker and the Python packages in `requirements.txt`

Install the Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Pull the default local model if needed:

```powershell
ollama pull qwen2.5:32b
```

## Run the pipeline

Place only authorized EPUB or PDF files in `STAGE 1/input/`, then run each stage from the project root:

```powershell
python "STAGE 1/ebook2MD.py"
python "STAGE 2/batch_slice.py"
python "STAGE 3/logic_miner.py"
python "STAGE 4/logic_aggregator.py"
python "STAGE 5/claude_skill_packager.py"
```

Stage 5 asks for an agent name and writes a new `<Agent_Name>_Heuristics_Skill/` folder in `STAGE 5/`.

## Configuration

The scripts derive their directories from their own location, so the project can be cloned anywhere. Stage 1 also honors optional environment variables when needed by a particular machine:

- `TORCH_DEVICE` (for example, `cuda`)
- `INFERENCE_RAM`
- `OMP_NUM_THREADS`

Update `MODEL` in `STAGE 3/logic_miner.py` if you use a different locally installed Ollama model.

## Current limitations

- Stage 3 processes chunks serially and relies on the local Ollama service.
- Stage 4 removes exact duplicates only; it does not yet perform semantic deduplication.
- The generated skill is intended as a folder-format starting point. Verify the current import requirements of the Claude environment you use before distribution.

## Contributing

Issues and pull requests are welcome. Please do not include copyrighted source documents, credentials, or private generated outputs in contributions.
