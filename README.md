# drex-flaky: a flaky-test quarantine loop where Drex makes the call

**Nace AI Drexathon 2026, Apex Predator track.** *Take a frontier-LLM task, hand the decisions to Drex, and prove it faster, cheaper, or more accurate.*

When a CI test fails, someone has to decide whether to **quarantine** it (it's flaky), **retry** it, or **block** the merge (it's a real regression). Teams usually make that call with a yes/no rule or by pasting the log into an LLM. Both give a verdict with no notion of how sure they are, and the two kinds of mistake cost very different amounts:

| truth \ action | QUARANTINE | RETRY | BLOCK |
|---|---|---|---|
| real regression | **120** (bug ships) | 6 | 0 |
| flaky test | 2 | 4 | 25 (needless block) |

*(engineer-minutes, `data/cost_table.csv`)*

This project asks **Drex** one calibrated yes/no question per failure, keeps the raw probability, turns it into an action with two thresholds, and **learns those thresholds from a handful of human corrections** using the cost table. A frontier-class open LLM on **DeepInfra** handles the same task as the baseline.

## Architecture

```mermaid
flowchart LR
  A[CI failure log .log] -->|upload + /v1/documents/extract| B[Nace Document Intelligence]
  A -. fallback .-> B2[local regex extractor]
  B --> C[structured fields: error_type, test_name, duration, retry_passed, recent_fail_rate, changed_files]
  B2 --> C
  C -->|state + noul question, POST /v1/systemone| D[Drex: P(flaky)]
  D --> E{policy.py: p ≥ hi → QUARANTINE / lo ≤ p < hi → RETRY / p < lo → BLOCK}
  E --> F[human outcome / correction]
  F --> G[learn.py: refit lo, hi to minimise cost]
  G --> E
  A -->|same log + cost table| H[DeepInfra LLM baseline]
  E --> I[compare.py: metrics + charts]
  H --> I
```

## Quick start

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

# 1) No keys: full pipeline in MOCK mode (every output is labelled MOCK)
./run_all.sh --mock
python demo.py --offline --mock

# 2) Real: put keys in .env (gitignored), see .env.example
cp .env.example .env   # NACE_API_KEY=nace_sk_..., DEEPINFRA_API_KEY=...
./run_all.sh           # each stage runs for real when its key is present, otherwise falls back to mock
python demo.py --offline        # replays results/*_real.json, so it can't break on stage
python demo.py --live           # re-calls Drex live for the demo case
```

| file | what it does |
|---|---|
| `data/generate.py` | 60 seeded pytest/jest-style CI logs (36 flaky, 24 real, 16 deliberately ambiguous) plus `labels.csv` |
| `ndi_extract.py` | NDI extract with an inline JSON schema; regex fallback; records `path` = `ndi` or `local_regex` for each case |
| `drex_decide.py` | `GET /v1/models` checks the pinned model, then one `noul` question per case; logs raw `noul`, `request_id`, tokens, and latency |
| `policy.py` | two-threshold policy |
| `learn.py` | fits (lo, hi) on the 16 "day-1" human-labelled cases, then replays logged probabilities on the 44 held-out cases |
| `baseline_llm.py` | DeepInfra OpenAI-compatible endpoint, `meta-llama/Llama-3.3-70B-Instruct-Turbo` by default (`LLM_MODEL` overrides it), with the same cost table in the prompt |
| `compare.py` | `results/metrics_<mode>.{md,json}` and `results/charts/<mode>_*.png` |
| `demo.py` | scripted rich terminal demo for one ambiguous failure |

## Verified API shapes

**Drex** (`console.nace.ai/docs/drex/api-reference/systemone`, `/docs/drex/guides/reading-answers`):

```http
POST https://console.nace.ai/v1/systemone
Authorization: Bearer $NACE_API_KEY
X-Nace-Client: drex-flaky/0.1
Content-Type: application/json

{"model": "drex-max-v1.1",
 "state": {"context": "...", "structured_fields_from_ndi": {...}, "log_excerpt": "..."},
 "questions": {"is_flaky": {"type": "noul", "instructions": "Is this failure caused by test flakiness rather than a real code regression? ..."}}}
```

The response is `answers.is_flaky.noul` (P(yes), 0 to 1), along with `confidence` (= max(p, 1-p), which we do not threshold), `usage.input_tokens` (billed; output tokens are not), `evaluation_time_ms`, and `request_id`.

**NDI extract** (`/docs/perception/extract`): upload the `.log` (`client.documents.upload`), then call `POST /v1/documents/extract` with `{"source": {"type": "workspace_file", ...}, "schema": {...}, "instructions": "..."}` and `wait_seconds=60`, polling `GET /v1/documents/jobs/{id}`. The fields come back in `result.data`.

## Results

See `results/metrics_real.md` once the real pipeline has run. `results/metrics_mock.md` comes from the **MOCK** pipeline: those numbers are synthetic placeholders, not a claim about Drex or the LLM.

<!-- RESULTS_TABLE -->

What the cost table says before any data arrives: if P(flaky) were perfectly calibrated, the expected-cost-optimal cut points would be **lo ≈ 0.22, hi ≈ 0.98**. A wrong quarantine is so expensive that you should only auto-quarantine when Drex is very sure. A yes/no classifier cannot express that. A probability can.

## Intern

The public Nace docs index (`console.nace.ai/llms.txt`, `nace.ai/llms.txt`) doesn't mention "Intern" as of 2026-11-14. If it turns out to be Nace's agent wrapper, it would sit in front of `policy.py`: the agent reads a new CI failure, calls NDI and Drex as tools, and files the quarantine ticket or the block alert.

## License

MIT
