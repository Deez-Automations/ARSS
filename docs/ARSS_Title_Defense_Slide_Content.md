# ARSS — Title Defense Slide Content (Draft 1)
**Purpose:** Full slide-by-slide content for the Sept 28, 2026 title defense — on-slide text plus presenter talking points for each slide, and marked spots for graphs to be built later. Every number in this document is either independently verified against a primary source, or is the team's own internal, reproducible result. Nothing here is carried over unverified from the pre-audit January 2026 masterclass materials.

**A note on what was deliberately left out, and why:** the earlier (January 2026) slide materials contained statistics — 71% SOC burnout, 73% false-positive rate, $4.44M breach cost, 80% workload-reduction math, DARPA CASTLE and AIxCC references — that were never subjected to the citation-verification process this project has run since July 2026, a process that has already caught a fabricated statistic and a wrong DOI elsewhere in this project's own bibliography. Rather than risk repeating that mistake in front of a panel, none of those figures are used here. Only Tariq et al. 2025's statistics survive, because they were the ones explicitly re-verified, word for word, against the actual paper. If the team wants to reinstate any of the excluded numbers, they need to go through the same verification process first — not be added back because they sound good.

---

## SLIDE 1 — Title

**On slide:**
> **ARSS**
> Category-Conditioned Deep Reinforcement Learning for MITRE ATT&CK-Grounded Autonomous SOC Alert Triage
>
> Muhammad Daniyal (2023406) · Haider Iqbal (2023416) · Syed Daud (2023677)
> Supervisor: Dr. Muhammad Fawad Khan · Co-Supervisor: Miss Hadia Abbas
> BS Cybersecurity, Faculty of Computer Science and Engineering, GIKI
> Title Defense — September 2026

**Say:** Introduce yourselves by name and role, state the project name once clearly, and move on. Don't over-explain the title yet — that's the next few slides' job.

---

## SLIDE 2 — Agenda

**On slide:**
1. The problem
2. Why it's still unsolved
3. What we reviewed, and the gap we found
4. Our proposed system
5. The formal design
6. Dataset and current results
7. What's built, what isn't
8. How we'll evaluate it
9. Work plan
10. Conclusion

**Say:** One line — "We'll walk through the problem, what's already been tried, our specific contribution, and exactly where the project stands today, including what's not finished yet." Set the expectation of honesty early; it pays off later.

---

## SLIDE 3 — The Problem: Alert Fatigue

**On slide:**
> A 2025 systematic review in *ACM Computing Surveys* (Tariq et al.) found:
> - **51%** of SOC teams report feeling overwhelmed by alert volume
> - Analysts resolve only **49%** of alerts assigned to them within a workday
>
> This is not a detection failure. The alerts are being generated correctly — the failure is downstream, at the decision layer.

**[GRAPH: simple two-bar chart, "51% overwhelmed" vs "49% resolved in a workday" — source: Tariq et al. 2025, ACM Computing Surveys, DOI 10.1145/3723158]**

**Say:** These two numbers are doing real work in the argument — don't rush past them. If asked for the source, you have the DOI ready. Do not use any other statistic here that isn't from this same paper.

---

## SLIDE 4 — What Already Exists, and Where It Stops

**On slide:**

| Tool | What it does | What it doesn't do |
|---|---|---|
| IDS / IPS | Detects and flags suspicious traffic | Takes no response decision |
| SIEM | Aggregates and correlates alerts | Still requires human triage |
| SOAR | Automates responses via playbooks | Playbooks are static — don't learn from outcomes |
| ML risk-scoring | Ranks alerts by threat probability | Doesn't take an action, still leaves the decision to a human |

**Say:** The point of this slide isn't "these tools are bad" — they're good at what they do. The point is that none of them decide, and none of them learn from what happened after a decision was made. That's the specific, narrow gap the rest of the talk is about.

---

## SLIDE 5 — Where ARSS Sits

**On slide:**
```
Raw Traffic → Firewall → IDS/IPS → SIEM → [ARSS] → Human Analyst
```
> ARSS is not a detection system. It receives alerts that have already passed every upstream filter. Its only job is deciding what happens next.

**Say:** State this plainly and let it land — "ARSS is not a better IDS" is the single most important sentence in the whole defense, because it's the exact distinction a panel is most likely to probe. Have it ready word for word.

---

## SLIDE 6 — What We Reviewed

**On slide:**
> Literature review: **29 sources** formally cited, verified against primary text and publisher records, not just search summaries.
>
> The RL-for-alert-response lineage:
> SAC-AP (2022) → TD3-AP (2024) → KNAP (2024) → Multi-Critic (2025) → AlertPro (2024) → RADAMS (2022) → L2DHF (2025) → **Homayoun (2026)**

**Say:** If asked how thorough the review was, this is where you say it plainly: sources were checked against actual publisher pages and DOIs, not summarized secondhand — and where errors were found in the team's own earlier work, they were corrected, not hidden. That's a stronger answer than claiming a flawless process.

---

## SLIDE 7 — The Consistent Limitation Across All of Them

**On slide:**
> Every prior RL-for-alert system shares two limitations:
> 1. **Reward is invented** — an abstract "defender loss" or game-theoretic cost, not tied to how security teams actually judge severity.
> 2. **Output is a ranking**, not an action — the analyst still decides what a top-ranked alert should trigger.

**Say:** Name at least one paper specifically when you say this (AlertPro is the strongest example — real analyst feedback loop, still only re-ranks). Generic claims invite generic pushback; specific claims invite specific, answerable questions.

---

## SLIDE 8 — The Confirmed Gap

**On slide:**
> No surveyed paper combines all three:
> 1. A state space that preserves **attack category and confidence**, not a collapsed risk score.
> 2. A reward grounded in **MITRE ATT&CK tactic severity**, not an invented cost.
> 3. A **discrete four-action response** (Ignore / Log / Block / Isolate), not a ranking.

**Say:** This is your novelty claim. Say it exactly this way, three numbered points, every time — don't paraphrase it differently across the talk and the Q&A. Consistency here matters more than eloquence.

---

## SLIDE 9 — The Closest Prior Work: Homayoun 2026

**On slide:**
> Homayoun (ESORICS 2025 Workshops) — the closest related work.
> - Confirmed from the paper's own abstract: reward built from **threat criticality, confidence, and isolation cost**
> - Confirmed: **not** MITRE ATT&CK-grounded
> - **Not yet known** (full text paywalled): its state space and action space

**Say:** Say the "not yet known" part out loud, unprompted, before anyone asks. Volunteering the limit of what you know is a stronger position than waiting to be caught not knowing it.

---

## SLIDE 10 — Objectives

**On slide:**
- Train a two-stage ML ensemble (XGBoost + DNN) for binary detection and 7-way attack categorization with confidence scoring
- Design a category-conditioned RL state space encoding danger score, attack category, and confidence
- Train a DQN agent with a MITRE ATT&CK severity-weighted reward, balancing analyst workload against threat containment
- Implement a Cognitive Semantic Layer translating SHAP + RL output into plain-English narratives
- Demonstrate, via baseline comparison, that the category-conditioned agent outperforms a rule-based threshold system
- Evaluate the full pipeline on CIC-IIoT 2025 and report autonomous-handling rate, false negative rate by category, and false positive escalation rate

**Say:** These are word-for-word from the scope document (`ARSS_Scope_Document_v2.md`, Objectives 1.2.1) — keep them that way rather than re-wording on the fly, since consistency with the submitted document matters if a panelist has it open.

---

## SLIDE 11 — System Architecture

**On slide:**
```
Stage 1: Binary Detection (XGBoost + DNN, soft voting)
   ↓ if attack
Stage 2: Attack Categorization — 7 classes (XGBoost + DNN, soft voting)
   ↓
RL Response Agent (DQN)
   ↓
{ Ignore, Log, Block, Isolate }
```

**[GRAPH/DIAGRAM: the three-stage pipeline as a flowchart — reuse the Mermaid diagram already in the project README as the visual base]**

**Say:** Walk left to right once, plainly. Save the "why DQN" justification for the next slide rather than front-loading it here.

---

## SLIDE 12 — The Formal Design

**On slide:**
> **State:** `[danger_score, attack_category (7-way one-hot), confidence]`
> **Action:** `{Ignore, Log, Block, Isolate}`
> **Algorithm:** DQN — chosen because the action space is discrete, not continuous (unlike SAC-AP/TD3-AP's ranking output)
> **Reward:** dense, tactic-severity-weighted, dual-objective (containment vs. analyst workload)

**Say:** If asked "why DQN and not PPO/SAC like the competitor papers," the answer is on this slide already — different action-space shape, not an oversight. Say that directly rather than looking for the answer live.

---

## SLIDE 13 — MITRE ATT&CK Severity Weighting

**On slide:**

| Attack Category | MITRE Tactic | Severity Weight |
|---|---|---|
| MITM | Collection / Credential Access | 1.0 |
| Malware | Execution / Persistence | 1.0 |
| DDoS | Impact | 0.8 |
| DoS | Impact | 0.7 |
| Brute Force | Credential Access | 0.6 |
| Web Attacks | Initial Access | 0.5 |
| Recon | Discovery | 0.3 |

**Say:** State plainly that this is **tactic-level** grounding, not technique-level — say it before being asked. It's a deliberate scope choice, not an oversight, and saying so first removes the question before it's raised.

---

## SLIDE 14 — Dataset

**On slide:**
> **Why a lab-built benchmark, not real company traffic:** controlled testbed datasets are the established methodology across this research area — real attack tools run deliberately against real lab infrastructure, producing broader, more reproducible attack coverage than any single real-world network could safely provide. Standard practice across the literature already cited (TD3-AP: MQTT-IoT-IDS2020, DARPA 2000, CSE-CIC-IDS2018), not a workaround unique to this project.
>
> **CIC-IIoT 2025** — Canadian Institute for Cybersecurity, University of New Brunswick
> - 685,000 samples, 71 features, 7 attack categories
> - Sensor and network traffic captured together, synchronized in real time — not network packets alone, unlike most prior benchmarks (including CICIDS2017)
> - The 71 features were derived through deliberate multi-objective feature selection, not exported raw and unfiltered
> - From the same research group behind CICIDS2017, CIC-IDS2018, and CIC-IoT2023 — an established, independently scrutinized testbed methodology
> - Peer-reviewed (*Electronics*, 2025) prior to publication
> - 7 clearly separated attack categories, each mappable to a MITRE ATT&CK tactic — a direct structural fit for this project's category-conditioned design

**Say:** Lead with the substance (sensor+network fusion, curated feature selection, established lab lineage), not "confidentiality made us do it" — that's true but sounds like an excuse if it's the *first* thing said. If pushed on why not real company data specifically, then explain: real network data is confidential by nature, which is exactly why the field builds controlled testbed datasets instead — but that's the second sentence, not the opening one. Be honest if asked about maturity: this dataset is newer than CICIDS2017, so it has fewer independent papers that have stress-tested it — a real, fair tradeoff for being more realistic and better-matched to the project, not something to hide.

---

## SLIDE 15 — Future Scope

**On slide:**
> **Future Scope**
> - Richer per-alert information: multi-part alert labels, alert age, analyst workload signal, network context, short-term memory of attacker behavior, worst-case risk tracking
> - Finer-grained MITRE grounding: individual attacker techniques instead of 7 broad categories — confirmed via literature review that no prior work combines ATT&CK with RL at *any* level of detail, so this extends an already-uncommon idea rather than catching up to one
> - Hard operational limits instead of soft reward penalties (one paper's own test: soft penalties alone led to budget violations in every run; a hard limit cut that to almost none)
> - A trainable range of tradeoffs (aggressive vs. cautious) instead of one fixed, locked-in blend
> - Multiple judges instead of one during training, easy-to-hard training progression, auto-tuned severity weights, and a signal for noticing when attack patterns have shifted enough to need retraining

**Say:** Frame this as a menu, not a commitment — say so explicitly. "These are literature-backed directions we could pursue with more time; we'd want your guidance on which are worth prioritizing given what's left in the timeline." Let the supervisor pick priorities rather than presenting this as things the team has already decided to build. The full plain-language breakdown of every item here, plus the honest limitations that push back against some of ARSS's own current design choices, is in `docs/ARSS_Future_Scope_and_Limitations.md` — read that before this slide, since a couple of items here (the reward-design ones especially) are genuine open questions the team should have an answer ready for, not just a bullet point.

---

## Appendix note for the team

This is Draft 1, intentionally stopped after Slide 15 (Future Scope) — this is the portion being taken to the professor first. Slides covering current results, what's built vs. not, the evaluation plan, work plan, and conclusion will be added back once this first portion is reviewed.

This deck assumes the panel will ask hard questions, not soft ones — every "Say" note above exists because that specific question is plausible, not hypothetical. The full anticipated-question bank with worked answers already exists in `docs/ARSS_RL_Concepts_Primer.md`, Part 13 ("Defense Readiness"). Read that alongside this deck, not instead of it — this document is the sequence and the facts; that one is the rehearsal for what happens when someone interrupts the sequence.

Graphs are marked with `[GRAPH: ...]` placeholders throughout and still need to be built — this is the first draft of content, not the final visual deck.

---

*Draft 1 compiled: September 21, 2026. Covers Slides 1-15 per team direction — results, built-vs-not, evaluation plan, work plan, and conclusion slides held for a subsequent draft.*
