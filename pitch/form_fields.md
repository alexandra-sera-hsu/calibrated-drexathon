# Drexathon submission form fields (Team Calibrated)

All numbers come from `results/metrics_real.md`, `results/intern_excerpt.md`, and `results/*_real.json` (real API runs, 2026-11-14).

## Project name
Calibrated: Flaky or Real? (Drex triages your red CI builds)

## Track
Apex Predator

## Team
Calibrated (Alexandra, solo)

## Brief explanation
(1,060 characters without the Adobe line. Replace `[ADOBE LINE]` with one sentence, e.g. "Pitch visuals made with Adobe Express.", or delete it.)

Drex beats frontier LLMs at CI triage: 96.7% accuracy, 0 real bugs quarantined, ~48% lower expected cost (118 vs 228 eng-min) and 8x faster (292 vs 2,456 ms p50) than Llama-3.3-70B on 60 labeled CI failures; held-out 44: 98 vs 176. Problem: every red build forces a quarantine/retry/block call, and wrongly quarantining a real bug ships it. How: NDI extracted structured fields from all 60 raw logs; Drex (drex-max-v1.1) returns one calibrated P(flaky); two thresholds fit to an explicit cost table pick the action. DeepInfra ran the baselines (Llama-3.3-70B 85.0%, DeepSeek-V3.2 88.3%) and Intern's agent. Intern ran the loop headless: Qwen3.8-27B on DeepInfra triaged 3 cases via our tools while Drex supervised as System 1 (16 checks, 6 turns, 39 s) and flagged the Drex-vs-human disagreement. Insight: all 24 real regressions scored P(flaky) <= 0.35, 34/36 flaky >= 0.93, none in the 0.40-0.80 retry band; the LLMs hedged with RETRY on 41/60. [ADOBE LINE] Evidence: results/metrics_real.md, drex_real.json, ndi_real.json, llm_real.json, intern_excerpt.md.

## Presentation comment
Live demo: `python demo.py --live` (NDI → Drex → policy → feedback on case_007). Offline replay of the logged real results: `python demo.py --offline`. The deck is pitch/index.html, with a PDF at pitch/Calibrated_Drexathon.pdf.
