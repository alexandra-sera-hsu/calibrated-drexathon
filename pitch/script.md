# Speaker script: "Flaky or real? Let Drex decide." (5:00)

Pace: about 130 words per minute. Spoken text is about 650 words. Lines in **[brackets]** are stage directions; don't say them.
All numbers below come from the real runs in `../results/metrics_real.md` (2026-11-14). Don't change them without re-running.

---

## 0:00–0:10 · Adobe opener (only if `../adobe/opener.mp4` is in the deck)

**[Let the 10-second Adobe opener play. Don't talk over it. Advance when the tagline lands: "Flaky or real? Drex knows."]**

## 0:10–0:30 · Slide 1: Title  (~45 words)

**[If the opener was missing, start immediately.]** Hi, I'm Alexandra. Every time a CI build goes red, someone is making a bet. Is this test flaky, or did we just break something? Today I'll show you what happened when we stopped guessing, asked Drex how sure it was, and put a price on being wrong.

**[→ next slide]**

## 0:20–0:55 · Slide 2: The problem  (~80 words)

Flaky tests are expensive in two ways. They burn reruns: CI minutes and engineer attention spent on failures that aren't real. Worse, they erode trust. Once red stops meaning "broken," people stop looking.

The mistakes don't cost the same, either. A wasted rerun costs minutes. Quarantining a real bug ships it.

So we asked a frontier LLM, and it gives you a verdict: "this test is flaky." It sounds confident, but there's no uncertainty attached and nothing for you to tune. Drex gives you a probability instead.

**[→ next slide]**

## 0:55–1:35 · Slide 3: The learning  (~85 words)

Here's what we learned before we wrote much software. **[point at histogram]** This is Drex's probability of flaky across every failure we scored, split by what was actually true.

Drex split the failures into two clean clusters: all 24 real regressions scored P(flaky) ≤ 0.35, 34 of 36 flaky failures scored ≥ 0.93, and none landed in the 0.40–0.80 retry band. That includes two real race-condition bugs whose retry passed, which a “retry passed ⇒ flaky” rule would have quarantined.

58 of 60 failures sit at the confident ends, and those can be handled automatically. Look at the two real race-condition bugs: their retry passed, so a simple 'retry passed means flaky' rule quarantines them. Drex put them at 7 and 9 percent. That mistake costs 20 times a wasted rerun. That's why we wanted a probability and not a verdict.

**[→ next slide]**

## 1:35–2:00 · Slide 4: How it works  (~60 words)

We ran the loop as an Intern session, Nace's agent harness. Qwen on DeepInfra does the work, and Drex is System 1, checking every turn and guarding every tool call. It has four steps. NDI, Nace Document Intelligence, turns a raw CI log into structured fields. Drex takes that state and a typed question and returns P(flaky). A two-threshold policy turns that number into an action: quarantine, retry, or block and alert. Then human corrections recalibrate the thresholds against our cost table.

**[→ next slide]**

## 2:00–3:30 · Slide 5: LIVE DEMO  (~170 words)

**[SWITCH TO LIVE TERMINAL NOW. Run: `python demo.py --live --step`. If the network fails, run `python demo.py --offline --step`.]**

This is case 7, a real bug that looks flaky: the PR removed a lock, and the retry passed. **[run it]**

First, NDI extracts the fields: the error type, the test name, timing, and the retry history. Next is the Drex call. Notice that what comes back is a number, P(flaky) equals **[read it]**, not a paragraph. Then the policy applies. It's above or below our thresholds, so the action is **[read action]**.

Now the feedback step. Sixteen human labels went in, and they changed zero decisions. The thresholds held at 0.40 and 0.80, and anywhere from 0.08 to 0.80 for the low threshold gives the same cost. Then an engineer overrides Drex on case 49: "that one was flaky." Should the thresholds move? The loop checks against the cost table. Fixing that one case would push total cost from 118 to 484 engineer-minutes, so the thresholds stay put and the case goes to the evidence backlog. The loop learns not to overreact.

The whole thing took **[read latency]**. That's fast enough to sit inside CI as a check.

**[SWITCH BACK TO SLIDES → slide 6]**

> **Fallback if the demo fails (say this, then move on to slide 6 right away):**
> "The live environment isn't cooperating, so here's the same run we recorded this morning. The numbers on the next slide come from exactly this loop."
> **[If there's a screenshot or recording in `../results/`, show it for no more than 15 seconds.]**

## 3:30–4:20 · Slide 6: Results  (~105 words)

Here are the head-to-head results. We used the same 60 labeled failures and the same cost table, with Drex plus our policy on one side and Llama 3.3 70B on DeepInfra on the other. We also ran DeepSeek V3.2.

Accuracy is 96.7 percent versus 85. Look at the row that matters most, though: real bugs wrongly quarantined, zero versus zero. The LLM is careful, but it pays for that with hedging: it said RETRY on 41 of 60 failures, and Drex retried none. So expected cost is 118 engineer-minutes versus 228, about half. DeepSeek came in at 210.

It's also faster, 292 milliseconds versus about 2.5 seconds, more than 8 times faster. Per thousand decisions it costs about seven cents, the same ballpark as Llama at six cents and half of DeepSeek's fifteen.

**[point at lower chart]** And this is the learning loop. The thresholds we learned held cost at 118. Trusting the cost table alone would have cost 132, and forcing a fix for the one disagreement would have cost 484.

**[→ next slide]**

## 4:20–5:00 · Slide 7: Why, what's next, the ask  (~75 words)

So here's the takeaway: a verdict can't learn your costs, but a probability can. Where you set the thresholds is a business decision, not something you fix in a prompt. Uncertainty sends the hard cases to a human, and each correction moves a number.

Next, we'd run this as a CI check with per-repo cost tables, then apply the same loop to alerts and paging.

Our ask is to pilot it on one team's CI. Send us your flakiest repo. Thank you!

**[STOP. 5:00]**

---

### Timing checkpoints
| Time | You should be on |
|---|---|
| 0:55 | Slide 3 (learning) |
| 2:00 | Terminal, demo running |
| 3:30 | Back on slide 6, even if the demo isn't finished |
| 4:20 | Slide 7 |

If you're running long, cut the latency line in the demo and the "what's next" sentence on slide 7.
