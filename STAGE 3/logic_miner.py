import os
import glob
import json
import re
import ollama
import json_repair

# ==========================================
# CONFIGURATION
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE2_OUTPUT = os.path.join(PROJECT_ROOT, "STAGE 2", "output")
STAGE3_OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
MODEL = "qwen2.5:32b"

# ==========================================
# EXTRACTION PROMPT v2
# ==========================================
SYSTEM_PROMPT = """
You are a deterministic logic extraction engine.

Your job is to convert source text into compact, reusable reasoning primitives for downstream LLM reasoning.

CRITICAL RULES:
1. Output EXACTLY one valid JSON object. No markdown. No commentary. No explanations.
2. Do not reproduce extended source passages. Preserve any source metadata supplied by the pipeline and do not invent citation data.
3. Extract transferable logic, not summaries.
4. Prefer compact operational rules over descriptive sentences.
5. Convert implied causal logic into heuristics even when the text does not explicitly say "if/then."
6. Return empty arrays ONLY if the chunk is clearly boilerplate, a table of contents, acknowledgements, bibliography, an index, or has no transferable logic.
7. Use the CONTEXT header only to understand domain and scope. Do not turn source titles into heuristic content.

HEURISTIC EXTRACTION STANDARD:
A heuristic must describe a reusable operational rule:
- trigger = condition, situation, signal, pattern, or decision context
- action = recommended interpretation, decision, response, or expected consequence
- context = domain/situation where the rule applies

Good heuristic style:
- "If facing certain losses, risk tolerance tends to increase to avoid realizing the loss."
- "If an environment changes faster than agents can adapt, previously rational behavior can become maladaptive."
- "If outcomes are independent, do not infer future probabilities from recent event frequency."

Bad heuristic style:
- "The text discusses market efficiency."
- "People are irrational sometimes."
- "This chapter explains behavior."

CLASSIFICATION STANDARD:
Use classifications for taxonomies, named concepts, behavioral types, decision categories, risk categories, system types, or strategic frameworks.

CONTEXTUAL ANCHOR STANDARD:
Use contextual_anchors for exceptions, nuances, boundary conditions, environmental dependencies, historical constraints, or situations that modify the application of a rule.

OUTPUT FORMAT:
{
  "heuristics": [
    {"trigger": "...", "action": "...", "context": "..."}
  ],
  "classifications": [
    {"category": "...", "definition": "...", "parameters": []}
  ],
  "contextual_anchors": [
    {"scenario": "...", "nuance_adjustment": "..."}
  ]
}
"""

def extract_json(text):
    """Isolates the JSON payload safely."""
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    match = re.search(r'(\{.*\})', text, re.DOTALL)
    return match.group(1) if match else text

def normalize_output(data):
    """Guarantees the expected top-level schema without masking failed parsing."""
    if not isinstance(data, dict):
        raise ValueError("Model output is not a JSON object.")

    clean = {
        "heuristics": data.get("heuristics", []),
        "classifications": data.get("classifications", []),
        "contextual_anchors": data.get("contextual_anchors", [])
    }

    for key in clean:
        if not isinstance(clean[key], list):
            clean[key] = []

    return clean

def mine_logic():
    if not os.path.exists(STAGE3_OUTPUT):
        os.makedirs(STAGE3_OUTPUT)

    chunk_files = glob.glob(os.path.join(STAGE2_OUTPUT, "**", "chunks", "*.md"), recursive=True)
    print(f"Found {len(chunk_files)} chunks to mine.")
    print(f"Model: {MODEL}")
    print("Prompt: HEE extraction prompt v2")
    print("Context window: 8192")

    for chunk_path in chunk_files:
        book_name = os.path.basename(os.path.dirname(os.path.dirname(chunk_path)))
        chunk_name = os.path.basename(chunk_path)

        book_fragment_dir = os.path.join(STAGE3_OUTPUT, book_name, "fragments")
        if not os.path.exists(book_fragment_dir):
            os.makedirs(book_fragment_dir)

        fragment_path = os.path.join(book_fragment_dir, chunk_name.replace(".md", ".json"))

        if os.path.exists(fragment_path):
            continue

        with open(chunk_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"Mining Logic: {book_name} -> {chunk_name}", flush=True)

        try:
            response = ollama.generate(
                model=MODEL,
                system=SYSTEM_PROMPT,
                prompt=f"Extract compact operational reasoning primitives from this chunk:\n\n{content}",
                format='json',
                stream=False,
                options={
                    "temperature": 0.0,
                    "num_ctx": 8192
                }
            )

            raw_output = response['response']
            cleaned_text = extract_json(raw_output)

            try:
                parsed = json.loads(cleaned_text)
            except Exception:
                parsed = json_repair.loads(cleaned_text)

            clean_json = normalize_output(parsed)

            with open(fragment_path, 'w', encoding='utf-8') as f:
                json.dump(clean_json, f, indent=2, ensure_ascii=False)

            print(
                f"   [+] Saved {chunk_name}: "
                f"H={len(clean_json['heuristics'])}, "
                f"C={len(clean_json['classifications'])}, "
                f"A={len(clean_json['contextual_anchors'])}",
                flush=True
            )

        except Exception as e:
            print(f"   [!] Failed to mine {chunk_name}: {e}", flush=True)

    print("\nSTAGE 3 COMPLETE: Logic Fragments generated.")

if __name__ == "__main__":
    mine_logic()
