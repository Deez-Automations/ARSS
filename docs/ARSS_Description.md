# ARSS — Project Description

**Purpose of this document:** a single reference for the team covering where the project stands after the September 2026 redesign — the verdict on whether it's sufficient as an FYP, how to pitch it, and every feature, novelty claim, and research gap found, each explained in plain language so it doesn't require re-reading the full research trail to understand.

---

## Verdict: Is This Enough for an FYP?

**Yes.** But it's worth being precise about what "enough" means, because chasing "impressive" instead of "sound" is what caused problems earlier in this project's history.

- **It clears the real bar, not a guessed one.** Checked directly against the NCEAC accreditation manual: the project maps onto 8 of the 9 official characteristics of a "Complex Computing Problem" — the actual formal standard an FYP is required to meet.
- **It has genuinely separable work for three people over a year** — the simulation environment, the five compared decision methods, and the safety/evaluation layer are each real, distinct pieces of work, not one task split arbitrarily three ways.
- **A working piece already exists and is already evaluated** — the two-stage alert detector (92.34% / 92.83%), not a promise.
- **The research question survived deliberate attempts to disprove it**, across multiple independent passes, rather than just never having been challenged.
- **"Enough" means defensible and sound — not guaranteed to dazzle.** The honest open risk (a simple hand-written rule might perform just as well as the learned methods) is not a flaw in the project. It's what makes it real research instead of a predetermined result, and it should be stated in the room as a strength, not hidden.

---

## How to Pitch It

- **Lead with the human problem, not the technical machinery.** Open with the real statistic (SOC teams overwhelmed, alerts going unresolved) before anything about algorithms or architecture — it establishes why anyone should care before asking them to follow technical detail.
- **State the one-sentence thesis early and plainly.** "ARSS is the layer that decides what happens to an alert while accounting for how busy the team currently is." Say it directly — hedging reads as doubt even when the underlying claim is solid.
- **Use specific numbers instead of vague claims everywhere possible.** "13+ platforms checked," "92.34% / 92.83%" — specificity is what separates a checked claim from an asserted one, and it's easy for a panel to tell the difference.
- **State the falsifiable hypothesis as a strength, out loud, before being asked.** Say plainly that if a simple threshold rule performs just as well as the learned methods, that is still a valid, useful result. This defuses the sharpest possible objection before anyone raises it, and it signals scientific maturity rather than salesmanship.
- **Be ready for "why not just configure a rule in existing tools" — it's the single most likely hard question.** The answer: concede it's technically possible today, point out that's exactly why a plain threshold is baseline #1 in the comparison rather than an oversight, and explain briefly why hand-written rules don't scale (they don't adapt over time, and they can't jointly weigh many signals at once without becoming unmanageable).

---

## Features — What the System Actually Does

Each of these is a real component of the design, not a wishlist item.

1. **Alert Understanding** — *What it means:* before anything else happens, the system reads an incoming alert and extracts the basics about it — how dangerous it looks, what kind of attack it resembles, and how confident the detector is in that judgment. This part is already built and already tested (92.34% / 92.83% accuracy on two separate tasks).

2. **SOC-State Awareness** — *What it means:* the system also keeps track of how busy the security team currently is — how many alerts are waiting, how long the oldest one has been sitting there, and how many cases each analyst currently has open. This is the genuinely new input nobody else uses in a live decision.

3. **Adaptive Disposition Policy** — *What it means:* given both the alert's danger and the team's current situation together, the system decides one of three things: close the alert automatically because it's not worth a human's time, put it in a queue for later, or flag it for a human to look at right now.

4. **Severity Floor** — *What it means:* a hard, unbreakable rule sitting underneath everything else — if an alert is genuinely severe, it can never be automatically closed or buried, no matter how backed up the team is. This is what keeps the system safe even while it's being efficient.

5. **Feedback Loop** — *What it means:* over time, the system adjusts its behavior based on whether its past decisions turned out to be correct, instead of running on a fixed set of rules that never improve.

*Optional, secondary additions if time allows (not required for the core thesis):* enriching alerts with extra context before deciding, routing escalated alerts to the right specific analyst, and generating shift-handoff summaries. These widen what the system covers but sit outside the safety boundary — the system never takes an enforcement action (blocking, isolating) regardless of how far this widens.

---

## Novelties — What's Actually Claimed as New

Each of these was checked, not assumed.

1. **The policy acts on its own — it doesn't just advise a human.** Most comparable systems (existing and academic) produce a recommendation for a person to act on. This one makes the call directly, within the safety floor.

2. **It reacts to the team's workload in real time, not a snapshot.** The decision changes as the queue changes, rather than being fixed at one point in time and never revisited.

3. **It's designed to be tested against something more than a replay of old data.** Many comparable studies evaluate their method by replaying historical logs; this is built to be tested in a live, running simulation instead.

4. **No commercial platform does this today — confirmed, not guessed.** Over 13 major SOC platforms (Splunk, Microsoft Sentinel, CrowdStrike, and others) were checked directly against their own technical documentation. None of them let current team workload change what happens to an alert.

5. **Nobody has tried a "bandit"-style learning method for this exact problem.** This is a specific, narrow, unclaimed piece of technical territory found during the research process.

6. **The way results get measured is built to avoid a known trap.** Recent 2026 research pointed out that many studies in this space accidentally let future information leak into their tests, making results look better than they really are. This project's evaluation is deliberately built to avoid that mistake.

---

## Research Gaps — What's Genuinely Open, Stated Honestly

Precision matters here — overclaiming any of these is exactly the mistake this project already corrected once.

1. **The broad idea of "consider workload when triaging" is not new — real prior work exists.** Two papers (Shah 2019, Ghadermazi 2024) already touch this idea, using traditional optimization methods rather than machine learning, and without the system acting on its own. This needs to be cited honestly in the paper, not skipped over.

2. **The closest real competitor is a 2026 paper (Lázaro et al.), and the difference from it is specific, not vague.** Their system uses real operational data, which is genuinely impressive — but it's a tool that advises a human rather than deciding on its own, and it was tested by replaying old records rather than running live. Three precise differences, not a claim of being completely unprecedented.

3. **The original idea (an AI that blocks or isolates threats on its own) is frozen, not being pursued.** Research found this problem already solved at a very advanced level by academic work published since 2021 — pursuing it further would mean re-doing work that's already been done, not contributing something new.

4. **No commercial company having built this yet is not, by itself, a research contribution.** It's tempting to say "nobody's shipped this, so we should," but that's a business/deployment gap, not a research gap — a panel would correctly reject that framing. The actual claim rests on the academic gap (point 1 and 2 above), not the commercial one.

5. **One source still needs to be double-checked before it's treated as fact.** A few specific claims about a 2026 paper (that certain learning methods perform poorly on this kind of problem, and that it also uses a safety-floor-style rule) were never confirmed against the paper's actual full text — every attempt to access it hit a paywall. These should not be cited in the final paper until verified directly.

---

## Slide Deck

The presentable version of this material (6 slides, built for the 10-minute Presentation 1 format) is published here:
**https://claude.ai/artifact/Cj17KL6giniiDqCKLQzgh5**

This is a private link — it needs to be shared with the team from the page's Share menu before anyone else can open it. A plain-text version of the same slide content also lives in this repository at `docs/ARSS_Title_Defense_Slides.md`.

---

*Compiled September 24, 2026, from the full research and reset process documented in `docs/DTRA_Development_Journal.md`.*
