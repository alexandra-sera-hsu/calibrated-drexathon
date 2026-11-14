# Speaker script: "Flaky or real? Let Drex decide." (5:00)

Pace: about 130 words per minute. Spoken text is about 650 words. Lines in **[brackets]** are stage directions; don't say them.
Before you start, fill every `[RESULT: …]` and `[INSIGHT: …]` with the real numbers from `../results/`. If a number isn't ready, drop the sentence. Don't guess.

---

## 0:00–0:20 · Slide 1: Title  (~45 words)

Hi, I'm Alexandra. Every time a CI build goes red, someone is making a bet. Is this test flaky, or did we just break something? Today I'll show you what happened when we stopped guessing, asked Drex how sure it was, and put a price on being wrong.

**[→ next slide]**

## 0:20–0:55 · Slide 2: The problem  (~80 words)

Flaky tests are expensive in two ways. They burn reruns: CI minutes and engineer attention spent on failures that aren't real. Worse, they erode trust. Once red stops meaning "broken," people stop looking.

The mistakes don't cost the same, either. A wasted rerun costs minutes. Quarantining a real bug ships it.

So we asked a frontier LLM, and it gives you a verdict: "this test is flaky." It sounds confident, but there's no uncertainty attached and nothing for you to tune. Drex gives you a probability instead.

**[→ next slide]**

## 0:55–1:35 · Slide 3: The learning  (~85 words)

Here's what we learned before we wrote much software. **[point at histogram]** This is Drex's probability of flaky across every failure we scored, split by what was actually true.

[INSIGHT: say the headline in one sentence.]

[RESULT: share] of failures sit at the confident ends, and those can be handled automatically. The middle band is where the trouble is. That's where a verdict model is confidently wrong: [RESULT: LLM error rate in middle band]. And when it's wrong in the expensive direction, it costs [RESULT: cost ratio] times a wasted rerun. That's why we wanted a probability and not a verdict.

**[→ next slide]**

## 1:35–2:00 · Slide 4: How it works  (~60 words)

The loop has four steps. NDI, Nace Document Intelligence, turns a raw CI log into structured fields. Drex takes that state and a typed question and returns P(flaky). A two-threshold policy turns that number into an action: quarantine, retry, or block and alert. Then human corrections recalibrate the thresholds against our cost table.

**[→ next slide]**

## 2:00–3:30 · Slide 5: LIVE DEMO  (~170 words)

**[SWITCH TO LIVE TERMINAL NOW. Run: `[DEMO: command]`]**

This is a fresh CI failure the system hasn't seen. **[run it]**

First, NDI extracts the fields: the error type, the test name, timing, and the retry history. Next is the Drex call. Notice that what comes back is a number, P(flaky) equals **[read it]**, not a paragraph. Then the policy applies. It's above or below our thresholds, so the action is **[read action]**.

Now the important part. **[run a failure where the decision was wrong, or enter a human correction]** Say an engineer marks this one: "no, that was a real bug." That correction goes into the feedback step. We recompute expected cost against the cost table, and you can see the thresholds move from **[read old]** to **[read new]**. The model didn't change. Our policy got smarter about what a mistake costs.

The whole thing took **[read latency]**. That's fast enough to sit inside CI as a check.

**[SWITCH BACK TO SLIDES → slide 6]**

> **Fallback if the demo fails (say this, then move on to slide 6 right away):**
> "The live environment isn't cooperating, so here's the same run we recorded this morning. The numbers on the next slide come from exactly this loop."
> **[If there's a screenshot or recording in `../results/`, show it for no more than 15 seconds.]**

## 3:30–4:20 · Slide 6: Results  (~105 words)

Here are the head-to-head results. We used the same labeled failures and the same cost table, with Drex plus our policy on one side and [MODEL] on DeepInfra on the other.

Accuracy is [RESULT: Drex accuracy] versus [RESULT: LLM accuracy]. Look at the row that matters most, though: real bugs wrongly quarantined, [RESULT: Drex count] versus [RESULT: LLM count]. Expected cost is [RESULT: Drex cost] versus [RESULT: LLM cost].

It's also faster, [RESULT: Drex latency] versus [RESULT: LLM latency], and cheaper, at [RESULT: Drex $/1k] versus [RESULT: LLM $/1k] per thousand decisions.

**[point at lower chart]** And this is the learning loop. After human corrections, expected cost went from [RESULT: before] to [RESULT: after].

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
