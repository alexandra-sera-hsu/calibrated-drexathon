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
