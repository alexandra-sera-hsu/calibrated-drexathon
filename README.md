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
| `triage.py`, `AGENTS.md`, `run_intern.sh` | the same loop as tools for an Intern session |

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

These are **real** Drex (`drex-max-v1.1`) and NDI results, from 60 real `POST /v1/systemone` calls and 60 of 60 NDI extract jobs, run 2026-11-14. The **LLM baseline is pending** until there's a DeepInfra key, and no LLM numbers are shown until it actually runs. The rule baseline is a deterministic local heuristic (retry passed ⇒ quarantine, else block). Mock-mode outputs (`results/*_mock.*`) are synthetic and watermarked.

**REAL API RESULTS** (Drex + NDI real; LLM baseline pending: no DEEPINFRA_API_KEY yet)  
Drex model: `drex-max-v1.1` · LLM: `pending (no DEEPINFRA_API_KEY)` · thresholds {'lo': 0.4, 'hi': 0.8} → {'lo': 0.4, 'hi': 0.8}

### Held-out cases (n=44)

| System | Accuracy (flaky vs real) | Real bugs quarantined | Needless blocks | Retries | Expected cost (eng-min) | p50 latency (ms) | $ / 1k decisions |
|---|---|---|---|---|---|---|---|
| Drex (before learning) | 95.5% | 0 | 2 | 0 | 98 | 277 | $0.0724 |
| Drex (after learning) | 95.5% | 0 | 2 | 0 | 98 | 277 | $0.0724 |
| Rule baseline (retry passed => quarantine, else block) | 93.2% | 1 | 2 | 0 | 218 | 0 | $0.0000 |
| LLM baseline (DeepInfra) - PENDING | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |

### All cases (n=60)

| System | Accuracy (flaky vs real) | Real bugs quarantined | Needless blocks | Retries | Expected cost (eng-min) | p50 latency (ms) | $ / 1k decisions |
|---|---|---|---|---|---|---|---|
| Drex (before learning) | 96.7% | 0 | 2 | 0 | 118 | 292 | $0.0724 |
| Drex (after learning) | 96.7% | 0 | 2 | 0 | 118 | 292 | $0.0724 |
| Rule baseline (retry passed => quarantine, else block) | 93.3% | 2 | 2 | 0 | 358 | 0 | $0.0000 |
| LLM baseline (DeepInfra) - PENDING | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |

![P(flaky) by truth](results/prob_histogram.png)
![learning step](results/cost_before_after.png)
![Drex vs baselines](results/drex_vs_llm.png)

### What we learned

- **Drex separates the two classes cleanly.** All 24 real regressions scored P(flaky) ≤ 0.35, 34 of 36 flaky failures scored ≥ 0.93, and **no failure fell in the 0.40–0.80 retry band**. That includes the two real race-condition bugs whose retry *passed* (P = 0.07 and 0.09). A "retry passed ⇒ flaky" rule quarantines both, at 120 eng-min each.
- **The learning step is honest about what it can and can't fix.** The 16 day-1 human labels changed **0** decisions. The cost-minimising refit keeps lo = 0.40 and hi = 0.80, and the band of equally good thresholds is wide: any lo from 0.08 to 0.80, or any hi from 0.40 to 0.93. Held-out cost is 98 → 98.
- **The one confident disagreement doesn't move the thresholds.** That's case_049 or case_058: a flaky order-dependence failure where both retries failed and the PR touched `settings.py`, and Drex gave P ≈ 0.001. The cheapest threshold change that "fixes" it raises total cost on all 60 cases from **118 to 484** eng-min, so the loop keeps the thresholds and sends the pattern to the evidence backlog instead. A useful next fix is to add a "passes in isolation" signal to the state.
- **The cost table alone isn't enough.** If P were perfectly calibrated, the cost table would pick lo = 0.22, hi = 0.98. On these probabilities that costs 110 vs 98 on held-out, because Drex's 0.93–0.98 flaky cases would be retried instead of quarantined. Fitting on labels beats trusting the cost table alone.
- **Cost:** NDI cost $0.228 for all 60 logs, as reported by the SDK job cost; some pages were cache hits. Drex used 36,224 input tokens, about $0.004 at an assumed $0.12/M for Drex Max. Drex Max probabilities are not bit-identical between calls (case_007: 0.074 cached vs 0.107 live), so the stage demo replays the logged values.

What the cost table says before any data arrives: if P(flaky) were perfectly calibrated, the expected-cost-optimal cut points would be **lo ≈ 0.22, hi ≈ 0.98**. A wrong quarantine is so expensive that you should only auto-quarantine when Drex is very sure. A yes/no classifier cannot express that. A probability can.

## Running it as an Intern agent

[Intern](https://github.com/nace-ai/intern) is the Nace agent harness. Its **System 2** model does the work by calling tools, and its **System 1**, a decision model, watches every turn and guards tool calls. Here System 1 is **Drex** (`drex:drex-max-v1.1`, from the Nace console) and System 2 is a **DeepInfra** model (default `deepseek-ai/DeepSeek-V3.2`).

```bash
uv tool install "intern-agent @ git+https://github.com/nace-ai/intern"
./run_intern.sh case_007 case_041 case_049      # needs NACE_API_KEY + DEEPINFRA_API_KEY
```

`AGENTS.md` tells the agent to work only through `triage.py`:
- `extract`: NDI
- `decide`: Drex `noul`
- `act`: the policy
- `truth`, then `feedback`: the human label, then the threshold refit

Every tool call is journaled to `results/intern_actions.jsonl`, and the Intern event stream goes to `results/intern_run.jsonl`. The agent never chooses the action itself. The policy does.

## License

MIT
