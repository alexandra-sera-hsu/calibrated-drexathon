"""Step 6: metrics table + slide charts for Drex (before/after learning) vs the LLM baseline.

Metrics are on the HELD-OUT cases (not in the human feedback set) so the learned
thresholds are not graded on the data they were fit to. All-60 numbers are in the JSON.

    python compare.py [--mock]      # writes results/metrics_<mode>.{json,md} + results/charts/<mode>_*.png
"""
from __future__ import annotations

import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from drexflaky.common import CHARTS, RESULTS, banner, load_costs, load_env, load_labels, p50, read_json, resolve_mode, result_path, write_json  # noqa: E402


def metrics(rows, decisions, labels_pred, costs, latencies, usd_per_1k):
    n = len(rows)
    truths = [r["truth"] for r in rows]
    acc = sum(lp == t for lp, t in zip(labels_pred, truths)) / n
    wq = sum(d == "QUARANTINE" and t == "real" for d, t in zip(decisions, truths))
    nb = sum(d == "BLOCK" and t == "flaky" for d, t in zip(decisions, truths))
    rt = sum(d == "RETRY" for d in decisions)
    cost = sum(costs[(t, d)] for d, t in zip(decisions, truths))
    return {"n": n, "accuracy": round(acc, 3), "wrong_quarantines_of_real_bugs": wq, "needless_blocks": nb,
            "retries": rt, "expected_cost_eng_min": cost, "cost_per_failure": round(cost / n, 2),
            "p50_latency_ms": p50(latencies), "usd_per_1k_decisions": usd_per_1k}


def watermark(fig, mode):
    if mode != "real":
        fig.text(0.5, 0.5, "MOCK DATA", fontsize=60, color="red", alpha=0.18, ha="center", va="center", rotation=25)
    fig.text(0.99, 0.01, banner(mode), fontsize=8, ha="right", color="red" if mode != "real" else "gray")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    load_env()
    dmode = resolve_mode(a.mock, "NACE_API_KEY")
    lmode = resolve_mode(a.mock, "DEEPINFRA_API_KEY")
    mode = "real" if (dmode == "real" and lmode == "real") else ("mock" if dmode == lmode == "mock" else "mixed")
    costs = load_costs()
    labels = {r["case_id"]: r for r in load_labels()}
    drex_all = read_json(result_path("drex", dmode)); drex = {c["case_id"]: c for c in drex_all["cases"]}
    llm_all = read_json(result_path("llm", lmode)); llm = {c["case_id"]: c for c in llm_all["cases"]}
    learn = read_json(result_path("learn", dmode)); rep = {x["case_id"]: x for x in learn["replay"]}

    out = {"mode": {"drex": dmode, "llm": lmode}, "drex_model": drex_all.get("model_requested"), "llm_model": llm_all.get("model"),
           "thresholds_before": learn["thresholds_before"], "thresholds_after": learn["thresholds_after"], "tables": {}}
    for split, keep in (("heldout", lambda r: not r["feedback_set"]), ("all", lambda r: True)):
        rows = [r for r in labels.values() if keep(r)]
        ids = [r["case_id"] for r in rows]
        dl = ["flaky" if (drex[i]["p_flaky"] or 0) >= 0.5 else "real" for i in ids]
        lat = [drex[i].get("latency_ms") for i in ids]
        out["tables"][split] = {
            "Drex (before learning)": metrics(rows, [rep[i]["before"] for i in ids], dl, costs, lat, drex_all.get("usd_per_1k")),
            "Drex (after learning)": metrics(rows, [rep[i]["after"] for i in ids], dl, costs, lat, drex_all.get("usd_per_1k")),
            "LLM baseline": metrics(rows, [llm[i]["action"] for i in ids], [llm[i]["label"] for i in ids], costs,
                                    [llm[i].get("latency_ms") for i in ids], llm_all.get("usd_per_1k")),
        }
    write_json(RESULTS / f"metrics_{mode}.json", out)

    # markdown table
    lines = [f"**{banner(mode) if mode != 'mixed' else 'MIXED: Drex=' + dmode + ', LLM=' + lmode}**  ",
             f"Drex model: `{out['drex_model']}` · LLM: `{out['llm_model']}` · thresholds {learn['thresholds_before']} → {learn['thresholds_after']}", ""]
    for split in ("heldout", "all"):
        t = out["tables"][split]
        n = next(iter(t.values()))["n"]
        lines += [f"### {'Held-out cases' if split == 'heldout' else 'All cases'} (n={n})", "",
                  "| System | Accuracy (flaky vs real) | Real bugs quarantined | Needless blocks | Retries | Expected cost (eng-min) | p50 latency (ms) | $ / 1k decisions |",
                  "|---|---|---|---|---|---|---|---|"]
        for k, m in t.items():
            usd = f"${m['usd_per_1k_decisions']:.4f}" if m["usd_per_1k_decisions"] is not None else "n/a"
            lat = f"{m['p50_latency_ms']:.0f}" if m["p50_latency_ms"] is not None else "n/a"
            lines.append(f"| {k} | {m['accuracy']:.1%} | {m['wrong_quarantines_of_real_bugs']} | {m['needless_blocks']} | {m['retries']} | "
                         f"{m['expected_cost_eng_min']:.0f} | {lat} | {usd} |")
        lines.append("")
    (RESULTS / f"metrics_{mode}.md").write_text("\n".join(lines))
    print("\n".join(lines))

    CHARTS.mkdir(parents=True, exist_ok=True)
    lo0, hi0 = learn["thresholds_before"]["lo"], learn["thresholds_before"]["hi"]
    lo1, hi1 = learn["thresholds_after"]["lo"], learn["thresholds_after"]["hi"]
    # 1. histogram
    fig, ax = plt.subplots(figsize=(9, 4.8))
    pf = [drex[i]["p_flaky"] for i, r in labels.items() if r["truth"] == "flaky" and drex[i]["p_flaky"] is not None]
    pr = [drex[i]["p_flaky"] for i, r in labels.items() if r["truth"] == "real" and drex[i]["p_flaky"] is not None]
    bins = [i / 20 for i in range(21)]
    ax.hist([pr, pf], bins=bins, stacked=True, color=["#d62728", "#2ca02c"], label=["truly real regression", "truly flaky"])
    for x, s, c in ((lo0, "--", "gray"), (hi0, "--", "gray"), (lo1, "-", "black"), (hi1, "-", "black")):
        ax.axvline(x, ls=s, color=c, lw=1.5)
    ax.text(lo1, ax.get_ylim()[1] * 0.75, f" lo={lo1:.2f}", fontsize=9); ax.text(hi1, ax.get_ylim()[1] * 0.75, f" hi={hi1:.2f}", fontsize=9)
    ax.set_xlabel("Drex P(flaky)  (noul)"); ax.set_ylabel("# failures")
    ax.set_title("Drex probability by ground truth  (dashed = before learning, solid = after)")
    ax.text(0.02, 0.6, "BLOCK", transform=ax.transAxes); ax.text(0.55, 0.6, "RETRY", transform=ax.transAxes); ax.text(0.9, 0.6, "QUAR.", transform=ax.transAxes)
    ax.legend(loc="upper left", bbox_to_anchor=(0.1, 0.99)); watermark(fig, dmode); fig.tight_layout(); fig.savefig(CHARTS / f"{mode}_prob_histogram.png", dpi=160); plt.close(fig)
    # 2. cost before/after (feedback set, held-out, all)
    rp = learn["replay"]
    groups = {"feedback set\n(human-corrected)": [x for x in rp if x["feedback_set"]],
              "held-out\n(never seen)": [x for x in rp if not x["feedback_set"]], "all": rp}
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    xs = range(len(groups)); w = 0.38
    bb = ax.bar([x - w / 2 for x in xs], [sum(r["cost_before"] for r in g) for g in groups.values()], w, color="#9e9e9e", label=f"before (lo={lo0:.2f}, hi={hi0:.2f})")
    ba = ax.bar([x + w / 2 for x in xs], [sum(r["cost_after"] for r in g) for g in groups.values()], w, color="#1f77b4", label=f"after (lo={lo1:.2f}, hi={hi1:.2f})")
    ax.bar_label(bb, fmt="%.0f"); ax.bar_label(ba, fmt="%.0f")
    ax.set_xticks(list(xs)); ax.set_xticklabels(list(groups)); ax.set_ylabel("expected cost (eng-minutes)")
    ax.set_title(f"Learning from {len(learn['corrections'])} human corrections"); ax.legend()
    watermark(fig, dmode); fig.tight_layout(); fig.savefig(CHARTS / f"{mode}_cost_before_after.png", dpi=160); plt.close(fig)
    # 3. Drex vs LLM
    fig, axes = plt.subplots(1, 4, figsize=(13, 4))
    names = ["Drex (after learning)", "LLM baseline"]; cols = ["#1f77b4", "#ff7f0e"]
    for ax, key, title in zip(axes, ["expected_cost_eng_min", "wrong_quarantines_of_real_bugs", "p50_latency_ms", "usd_per_1k_decisions"],
                              ["expected cost (eng-min) ↓", "real bugs quarantined ↓", "p50 latency ms ↓", "$ per 1k decisions ↓"]):
        v = [t[n][key] or 0 for n in names]
        b = ax.bar(["Drex", "LLM"], v, color=cols); ax.bar_label(b, fmt="%.3g"); ax.set_title(title, fontsize=10)
    fig.suptitle(f"Drex ({out['drex_model']}) vs {out['llm_model']}  — held-out n={t[names[0]]['n']}")
    watermark(fig, mode); fig.tight_layout(); fig.savefig(CHARTS / f"{mode}_drex_vs_llm.png", dpi=160); plt.close(fig)
    print(f"charts -> {CHARTS}/{mode}_*.png")


if __name__ == "__main__":
    main()
