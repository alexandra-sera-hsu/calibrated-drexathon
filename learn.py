"""Step 4: the learning moment.

A human corrects the outcomes of the first N failures (the `feedback_set` in
labels.csv, "day 1"). We search for the (lo, hi) thresholds that minimise total
expected cost on those corrected outcomes (cost table in data/cost_table.csv),
preferring the smallest move from the current thresholds on ties. Then we replay the
LOGGED Drex probabilities for every case (no new API calls) under old vs new
thresholds and report cost on the held-out cases the feedback never saw.

    python learn.py [--mock]
"""
from __future__ import annotations

import argparse

from drexflaky.common import DEFAULT_HI, DEFAULT_LO, load_costs, load_labels, load_env, resolve_mode, read_json, result_path, write_json
from policy import decide, cost_of


def cost_derived_thresholds(costs):
    """If p were perfectly calibrated, the expected-cost-optimal cut points."""
    def ec(p, a):
        return p * costs[("flaky", a)] + (1 - p) * costs[("real", a)]
    grid = [i / 1000 for i in range(1001)]
    lo = next(p for p in grid if ec(p, "RETRY") <= ec(p, "BLOCK"))
    hi = next(p for p in grid if ec(p, "QUARANTINE") <= ec(p, "RETRY"))
    return lo, hi


def fit_thresholds(probs, truths, costs, lo0=DEFAULT_LO, hi0=DEFAULT_HI):
    grid = [i / 100 for i in range(1, 100)]
    best = None
    for lo in grid:
        for hi in grid:
            if hi < lo:
                continue
            c = cost_of([decide(p, lo, hi) for p in probs], truths, costs)
            key = (c, abs(lo - lo0) + abs(hi - hi0))
            if best is None or key < best[0]:
                best = (key, lo, hi)
    return best[1], best[2], best[0][0]


def run(mode: str, lo0=DEFAULT_LO, hi0=DEFAULT_HI) -> dict:
    labels = load_labels()
    costs = load_costs()
    drex = {c["case_id"]: c for c in read_json(result_path("drex", mode))["cases"]}
    fb = [r for r in labels if r["feedback_set"] and drex[r["case_id"]].get("p_flaky") is not None]
    lo1, hi1, fb_cost_after = fit_thresholds([drex[r["case_id"]]["p_flaky"] for r in fb], [r["truth"] for r in fb], costs, lo0, hi0)
    corrections = []
    for r in fb:
        p = drex[r["case_id"]]["p_flaky"]
        d0 = decide(p, lo0, hi0)
        ideal = min(("QUARANTINE", "RETRY", "BLOCK"), key=lambda a: costs[(r["truth"], a)])
        if d0 != ideal:
            corrections.append({"case_id": r["case_id"], "p_flaky": p, "decision_before": d0, "human_says": r["truth"],
                                "cost_before": costs[(r["truth"], d0)], "decision_after": decide(p, lo1, hi1),
                                "cost_after": costs[(r["truth"], decide(p, lo1, hi1))]})
    replay = []
    for r in labels:
        p = drex[r["case_id"]].get("p_flaky")
        b, a = decide(p, lo0, hi0), decide(p, lo1, hi1)
        replay.append({"case_id": r["case_id"], "truth": r["truth"], "ambiguous": r["ambiguous"], "feedback_set": r["feedback_set"],
                       "p_flaky": p, "before": b, "after": a, "cost_before": costs[(r["truth"], b)], "cost_after": costs[(r["truth"], a)]})
    held = [x for x in replay if not x["feedback_set"]]
    out = {"mode": mode, "thresholds_before": {"lo": lo0, "hi": hi0}, "thresholds_after": {"lo": lo1, "hi": hi1},
           "cost_derived_if_calibrated": dict(zip(("lo", "hi"), cost_derived_thresholds(costs))),
           "feedback_n": len(fb), "corrections": corrections,
           "heldout_n": len(held),
           "heldout_cost_before": sum(x["cost_before"] for x in held), "heldout_cost_after": sum(x["cost_after"] for x in held),
           "all_cost_before": sum(x["cost_before"] for x in replay), "all_cost_after": sum(x["cost_after"] for x in replay),
           "replay": replay}
    write_json(result_path("learn", mode), out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    load_env()
    mode = resolve_mode(a.mock, "NACE_API_KEY")
    o = run(mode)
    print(f"[learn] mode={mode} thresholds {o['thresholds_before']} -> {o['thresholds_after']} "
          f"(cost-optimal if calibrated: {o['cost_derived_if_calibrated']})")
    print(f"  {len(o['corrections'])} human corrections in feedback set of {o['feedback_n']}")
    print(f"  held-out cost (eng-minutes, n={o['heldout_n']}): {o['heldout_cost_before']:.0f} -> {o['heldout_cost_after']:.0f}")


if __name__ == "__main__":
    main()
