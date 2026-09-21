# ARSS — Complete Masterclass
## The Whole Project, Start to End, With Every Concept Taught Where It Actually Arose

**Purpose:** This is the single document to read to fully re-understand ARSS from zero — not just what it is today, but why every design choice exists, told as the project's actual chronological story, with every piece of RL/ML theory explained exactly at the point it became necessary. Read top to bottom once, and you should be able to open any cited paper's abstract afterward and know exactly what it's claiming and how it relates to ARSS.

**Audience:** Anyone on the team returning after a break with little technical recall — assumes nothing beyond "RL tries things and learns from outcomes."

---

# PART 0 — The Problem, Before Any of the Tech

Security Operations Centers (SOCs) run tools — firewalls, Intrusion Detection Systems (IDS), Security Information and Event Management platforms (SIEM) — that watch network traffic and flag anything suspicious as an **alert**. Modern detection tools are good at this: they generate a *lot* of alerts. The problem is that a human analyst has to look at each one and decide what to do about it, and there are far more alerts per day than any team of analysts can actually review. Most alerts are false alarms; a few are real threats; the analyst has to find the real ones in the pile, every day, without burning out. This is **alert fatigue**, and it's the actual problem ARSS exists to solve.

**The key reframe, stated on Day 0 of the project and re-confirmed a year later after a lot of technical detours:** the industry has gotten very good at *detecting* — flagging suspicious things. Nobody has solved *deciding* — what to actually do about each flagged thing, autonomously, in a way analysts can trust. That's the gap. ARSS is not a detector. It's a decision-maker that sits after detection.

```
Raw Traffic → Firewall → IDS/IPS → SIEM → [ARSS decides] → Human Analyst
```

Everything else in this document is the year-long journey of figuring out *how* to build that decision-maker properly.

---

# PART 1 — RL From Absolute Zero

Before any project history, the core idea, because everything below is a variation on this one loop.

## The loop
**An agent looks at a situation (a "state") → picks an action → receives a reward (or penalty) reflecting how good that was → adjusts its behavior so it picks better next time. Repeat forever.**

This loop has a formal name: a **Markov Decision Process (MDP)**. Every RL algorithm — tabular Q-learning, DQN, PPO, SAC, whatever — is just a different way of running this same loop and updating the agent's behavior from it. "Markov" just means: the current state contains everything relevant to decide the next action — you don't need the whole history, just where things stand right now.

**For ARSS, right now and always:** the "situation" is a network alert. The "action" is one of Ignore / Log / Block / Isolate. The "reward" is a score reflecting whether that was the right call, computed after the fact.

## The three design choices every RL system makes
Every paper you will ever read about RL is really just three decisions, dressed up in different notation:

1. **State space** — what information the agent is allowed to see before deciding.
2. **Action space** — the menu of things it's allowed to do.
3. **Reward function** — the scorecard that tells it, after acting, how good that action was.

Hold onto this. Nearly ARSS's entire research contribution is: *"every prior paper made these three choices worse than we do."* When you read any competitor paper's abstract, find these three things first — that's 80% of understanding the paper.

## How the agent actually learns: Q-values
The agent keeps a running number for every (state, action) pair: "if I take this action in this state, how good is that, accounting for everything that follows?" This number is the **Q-value**, `Q(s, a)`.

After acting, it nudges its estimate toward reality using the **Bellman update**:
```
Q(s,a) ← Q(s,a) + α · [R + γ · max(Q(s', a')) − Q(s,a)]
```
- `R` = the reward just received
- `s'` = the new state after acting
- `max(Q(s',a'))` = the agent's current best guess of how good the *next* state is, under its best available action
- `α` (learning rate) = how large a step to take toward this new evidence
- `γ` (discount factor) = how much to value future reward vs. immediate reward

You do not need to derive this. You need to recognize it as "the rule that lets the agent slowly correct itself from experience" whenever you see it in a paper.

**Exploration vs. exploitation:** should the agent keep doing what it currently believes is best ("exploit"), or occasionally try something else to check if it's actually better ("explore")? Every RL system has to balance this. "Epsilon-greedy" (act randomly some small % of the time) and "entropy bonus" (reward the agent for staying unpredictable — SAC does this) are two common answers you'll see named in papers.

---

# PART 2 — Progress Report I: The A* Agent (Pre-RL, Fall 2025)

The team's very first "decision-maker" wasn't RL at all — it was **A\* search**, a classical, non-learning algorithm. Worth understanding precisely why it was tried and precisely why it was abandoned, because that contrast is what taught the team why RL is the right family of tool at all.

**A\* mechanics, briefly:** A* picks the action that minimizes a cost function `f(n) = g(n) + h(n)`, where `g(n)` is the known cost so far and `h(n)` is an estimated cost to go. Applied here: `f = Business Cost + Security Risk`.

- **Business costs (hand-set):** Ignore = 0, Log = 2, Block = 20, Isolate = 80.
- **Security risk:** if Ignore, risk = danger score (a 95%-dangerous alert left alone = 95 risk); if Block, risk = chance of false positive × penalty; if Isolate, risk = 0 (fully contained).

Tested on three cases: a 1% "leaf" (false positive) → correctly chose Ignore. A 95% "robber" (real threat) → correctly chose Block. A 60% ambiguous case → chose Block (safety-first).

**Why it was abandoned:** A* recomputes the *same* answer every time it sees the *same* inputs. It has no memory of past outcomes and cannot improve. If it under- or over-reacted to a pattern yesterday, it will do the exact same thing today — there is no feedback loop. That absence of a feedback loop is precisely what RL adds. This is the first (of several) "static rule-based approach hits a ceiling, learning-based approach replaces it" pivots in this project's history — a pattern that repeats at least twice more below.

---

# PART 3 — Progress Report II: The Baseline ML Layer

Before RL can decide anything, something has to tell it *how dangerous* a given alert is. That's a separate, ordinary supervised-learning problem, not RL — worth being precise about the distinction, since these two layers get talked about together constantly.

**Supervised learning, in one paragraph:** you give a model many labeled examples (network flow → benign or attack) and it learns a function that maps new, unseen flows to a prediction. No "reward," no sequential decisions — just pattern-matching against a fixed dataset. This is a fundamentally different kind of learning from RL, even though both are called "AI." **Detection is supervised learning. Response is RL.** Keep this boundary sharp — it is the exact boundary the professor later used to say "you're just building a better IDS."

**The pipeline built:** dataset CICIDS2017 (2.83 million network flows, sampled to 100K for speed), 79 numeric features, binary labels (benign/attack). Pipeline: impute missing values → standardize features → Logistic Regression classifier, which outputs a *probability*, not just yes/no — this probability becomes the "danger score" the whole rest of the system is built around.

**Results:** 94% accuracy, 83% recall, 86% precision. The number that actually mattered: **788 false positives out of 30,000 samples** — this became the project's "before" baseline for the entire rest of its existence. The lesson: 94% accuracy sounds good, but 788 false alarms is still an analyst drowning. Accuracy alone hides the real problem.

---

# PART 4 — Progress Report III: The Q-Learning Revolution

Two upgrades happened together here: the detector got a deep learning upgrade, and the decision-maker was rebuilt from A* into actual RL — tabular Q-learning.

## The detection upgrade
Logistic Regression → a 3-layer Deep Neural Network (DNN). **Results: 98% accuracy, 96% recall, 412 false positives (down from 788, a 47% reduction), 227 false negatives (down from 992, a 77% reduction).** This is the moment the project proved that a more powerful model directly reduces analyst burden — not just a vanity metric improvement.

**SHAP, introduced here:** SHAP (SHapley Additive exPlanations) answers "why did the model flag this specific alert?" by attributing the prediction to individual input features. Global finding: Flow Duration and Backward Packet Length Max were the most influential features overall — proving the model was keying on real network patterns, not noise. Local finding: for any single alert, SHAP can say "flagged because FIN Flag Count was unusually low + timing was chaotic" — turning a black-box score into something an analyst can actually verify. This explainability layer becomes central to ARSS's whole later "we solve trust, not just detection" positioning.

## Tabular Q-Learning, in full mechanical detail
This is where the loop from Part 1 became real code. A Q-learning agent trained for 10,000 episodes in a simulated SOC environment, learning entries in a literal lookup table: rows = states (danger buckets), columns = actions (Ignore/Log/Block/Isolate), cells = Q-values, updated via the Bellman rule.

**The learned policy that emerged (unprompted, from training, not hand-coded):**

| Danger level | Learned action | Why |
|---|---|---|
| 0-30% | IGNORE | Avoid false-positive penalty, preserve analyst time |
| 30-70% | BLOCK | Risk of ignoring exceeds disruption of blocking |
| 70-90% | ISOLATE | Maximum threat → maximum containment |
| 90-100% | BLOCK | Isolate is too disruptive; Block is "good enough" here |

**The single most important insight from this whole phase:** the agent learned on its own that 90-100%-dangerous alerts should be *Blocked*, not *Isolated* — because Isolate carries high business disruption cost, and for a near-certain threat, Block already contains it well enough that the extra disruption of Isolate isn't worth it. **A* could never discover this.** A* would apply its fixed formula and get a fixed answer every time; this nuance only exists because the agent tried things, observed outcomes, and adjusted. This single result is the strongest concrete evidence, anywhere in the project's history, for *why RL over static rules* — hold onto it, it's a genuinely good talking point.

---

# PART 5 — v1 Complete: The Full First System

By the end of Fall 2025, the three layers were stacked into one pipeline:
```
Layer 1: Hybrid AI Detector (DNN + Random Forest)
       ↓
Layer 2: Q-Learning Response Agent
       ↓
Layer 3: SOC Dashboard (real-time visualization)
```
**Final v1 numbers:** 98.9% accuracy on CICIDS2017, 47% false-positive reduction vs. the original baseline, four autonomous actions available (Ignore/Log/Block/Isolate). Missing pieces, known at the time: no live traffic streaming (batch upload only), an aging 2017 dataset, room for deeper architectures.

---

# PART 6 — v2 Revolution: Modernizing Everything (Jan 2026)

Two intense days rebuilt the system's foundation.

**Day 1 — new data.** Switched to CIC-IIoT 2025 (685,000 samples, 71 features — down from 79, requiring a full pipeline rebuild). Fought serious Infinity/NaN data-cleanliness issues that CICIDS2017 hadn't presented.

**Day 2 — new intelligence.**
1. **Live traffic streaming** — `replay_traffic.py` sends packets to an API; `api.py` caches results; the dashboard polls for real-time updates.
2. **A real bug, fixed:** the dashboard kept re-counting the same 100 packets in a loop. Fixed with a unique `packet_id` per result and a `processedPacketIds` set tracked client-side. (Small, but a good example of "AI project" work being ordinary software engineering just as often as it's ML.)
3. **Deep ensemble architecture** — old: a simple 3-layer DNN. New: a 5-layer DNN (512→256→256→128→64 neurons) *plus* XGBoost, combined via **soft voting** (average both models' predicted probabilities, then take the highest). Applied at *two* stages now: Stage 1 (binary: attack or not) and Stage 2 (categorize confirmed attacks into 7 types).
4. **Class weights instead of SMOTE — an important, deliberate methodology choice.** Real network traffic is naturally imbalanced (~80% benign, ~20% malicious, some attack types under 1% of all traffic). SMOTE (Synthetic Minority Oversampling Technique) would *invent* synthetic examples of rare attack types to balance the training set — but that risks the model learning to recognize fabricated patterns that don't exist in real traffic, inflating accuracy in a way that fails in production. The alternative, chosen here: **class weights** — penalize the model more heavily for misclassifying a rare class, without ever fabricating data. The resulting accuracy number is lower but honest. Principle stated explicitly by the team: *"92% accuracy on real data beats 99% on synthetic data."*

**v2 final metrics:** Stage 1 (attack/benign detection) — 92.34% recall. Stage 2 (7-way attack categorization) — 92.83% accuracy. Lower than v1's 98.9% — and that's *expected and correct*, not a regression: different, harder, noisier dataset, and no SMOTE inflating the number. 92% honest beats 99% inflated.

---

# PART 7 — The Title Defense and the Reckoning (Jan 31 → Feb 4, 2026)

**Jan 31 — first title defense.** A professor challenged the project bluntly: *"You're doing just an AI-powered IDS/IPS that tells what attack it is."* The team successfully defended by pointing back to the original proposal's own language ("learns to respond dynamically"), the A²C (Automation-Augmentation-Collaboration) framework as theoretical grounding, DARPA's CASTLE program as a validating precedent, and the alert-fatigue crisis statistics. The defense worked — but it was a defense of the *idea*, not yet a defense of the *implementation*, and that gap surfaced four days later.

**Feb 4 — the real pivot.** Deeper professor feedback, delivered plainly:
- *"Q-Learning is VERY basic"* — tabular Q-learning is considered undergraduate-level RL.
- *"Everyone uses ML → Risk Score → RL pipeline"* — the team's core architecture wasn't distinctive.
- *"RL agents need a proper environment and continuous learning"* — the system had neither.
- *"This approach is not defensible on a panel."*

## Why tabular Q-learning actually is limited — the precise technical reason
This is worth understanding rigorously, not just accepting on authority, because it's the exact justification for everything that follows.

A Q-*table* needs one row for every possible state. With a state defined as a single "danger bucket" (say, 10 buckets: 0-9), a table needs only 10 × 4 actions = 40 cells — trivially small, fast, and fully interpretable (you can literally print the whole table and read every learned decision). But the moment the state becomes richer — say, `[danger_score (continuous, effectively infinite values), attack_category (7 options), confidence (continuous)]` — the number of distinct state combinations explodes toward infinity. You cannot build a table with infinite rows. This is the **state space explosion problem**, and it is the mechanical reason tabular Q-learning cannot survive contact with a genuinely informative state space. It's not that tabular Q-learning is "bad" in the abstract — it's that it structurally cannot support the richer state ARSS needed once the team decided the agent should see attack category and confidence, not just a bucketed score.

## The fix: Deep Q-Networks (DQN)
Replace the table with a **neural network** that takes the state as input and outputs a Q-value for each possible action. The network doesn't memorize — it *generalizes*, estimating a sensible Q-value even for a state combination it's never exactly encountered before, because it has learned underlying patterns rather than a lookup table. This is the single biggest technical decision to come out of this pivot, and it's what ARSS's redesign formally commits to.

Two pieces of jargon that travel with every DQN implementation:
- **Replay buffer** — a memory of past (state, action, reward, next-state) experiences; the network retrains on randomly sampled batches from this memory rather than only the most recent step, which stabilizes learning considerably.
- **Target network** — a second, slowly-updated copy of the Q-network used specifically to compute the "future reward" half of the Bellman update, so the training target isn't constantly shifting under the model's feet as it learns (a real stability problem if you use the same, rapidly-changing network for both roles).

**Team's stated response to the feedback:** *"Stop implementing. Start reading."* Literature review became the primary activity for the next several months — precisely because the team correctly recognized they couldn't claim novelty without first knowing, in detail, what had already been done. This is where Parts 9-10 below come from.

---

# PART 8 — The Redesign: What ARSS Actually Became (April 2026)

A full architecture review produced the reframe the project still runs on today.

## "ARSS is not an IDS. It never was."
```
Raw Traffic → Firewall → IDS/IPS → SIEM → [ARSS] → Human SOC Analyst
```
IDS/IPS/SIEM already do detection, aggregation, and correlation. ARSS receives alerts that have *already* passed every upstream filter. Its job is purely **triage**: auto-handle what's obviously routine, escalate only what genuinely needs a human. The earlier research energy spent on the detection layer had been mis-targeted — detection isn't the bottleneck; the decision layer is.

## The core flaw, precisely
The RL agent, as built through v2, was optimizing for: *"is this packet dangerous?"* — a question the ML detector had **already answered**. High score → Block. Low score → Ignore. That's a threshold rule wearing an RL costume, not a learned policy. What the RL agent *should* optimize for: *"what action minimizes analyst interruption while maximizing threat containment?"* — two competing objectives in genuine tension, which is exactly the kind of tradeoff RL exists to learn, and exactly what a pure danger-threshold can't express.

**Two specific problems this exposed:**
1. **State space too narrow** — the agent saw only `danger_bucket (0-9)`, discarding everything Stage 2 (attack categorization) had already computed. A MITM attack at 70% confidence and a Recon scan at 70% confidence looked *identical* to the agent — clearly wrong, since they warrant very different responses.
2. **Reward function invented, not grounded** — rewards were hand-crafted from danger level alone, with no connection to real threat intelligence. Missing a MITM should be far worse than missing a Recon scan; a danger-only reward can't express that distinction at all.

## The redesign itself
**New state space:** `State = [danger_score, attack_category (one-hot, 7 classes), category_confidence]`. The agent now sees attack *semantics*, not just a risk number.

**New reward, grounded in MITRE ATT&CK.** MITRE ATT&CK (covered properly in Part 9 below) assigns each attack category a tactic and, by extension, a severity weight:

| Attack type | MITRE tactic | Severity weight |
|---|---|---|
| MITM | Collection / Credential Access | 1.0 (critical) |
| Malware | Execution / Persistence | 1.0 (critical) |
| DDoS | Impact | 0.8 |
| DoS | Impact | 0.7 |
| Brute Force | Credential Access | 0.6 |
| Web Attacks | Initial Access | 0.5 |
| Recon | Discovery | 0.3 |

Missing a MITM now costs the agent roughly 3× what missing a Recon scan costs — a real, defensible, externally-sourced signal replacing an invented heuristic.

## New feature: the Cognitive Semantic Layer (Daud's contribution)
**Problem:** raw SHAP output ("FIN Flag = 0, +0.23") is too technical for a junior analyst to parse quickly. **Solution:** feed the SHAP values, the RL action, and the attack type into an LLM (Gemini), which generates a plain-English narrative — e.g., *"BLOCKED: Detected anomalous traffic on Port 445. Primary trigger: Flow Duration anomaly. Pattern consistent with SMB-based lateral movement."* This stays inside the triage scope — it's translation, not a new decision-making layer — and directly targets analyst *trust*, which is ARSS's stated differentiator against every commercial competitor.

**An idea evaluated and explicitly rejected:** a denoising autoencoder in front of the detector, to resist adversarial input perturbations. Real, well-supported idea — rejected for now because the professor's actual criticism was about the RL/decision layer, not detection robustness; pursuing it now would be scope creep away from the core contribution. Filed under Future Work instead. (Worth noting as a model of good scoping discipline: a good idea can still be the wrong idea *right now*.)

## Training vs. deployment — an important structural realization
Question raised directly: if modern IDS/IPS already detect, classify, and block, why does ARSS need Stage 1 and Stage 2 detectors at all? **Answer: they are training infrastructure, not the product.** In a real deployment, a SIEM already hands you a labeled, scored, typed alert — you'd skip straight to the RL agent. Stage 1/2 exist purely because the team is training on a raw public dataset (CIC-IIoT 2025) and needs *something* to generate the enriched state vector the RL agent learns from.
```
TRAINING:    Raw Dataset → Stage 1 → Stage 2 → RL trains on the enriched state
DEPLOYMENT:  SIEM Alert  → RL Agent → Action
```
**The actual deployable product, once built, is a small, fast, trained RL policy** — not a heavy detection pipeline. This reframing matters: it means ARSS's contribution is genuinely about the decision layer, and the detection stages are honestly scoped as scaffolding, not central claims. (One caveat added much later, in the paper draft: a real SIEM doesn't natively export CIC-IIoT 2025's specific 71-feature vector or a matching confidence score, so "just swap in the SIEM" is not fully solved — it's explicitly scoped as future work, not assumed away.)

---

# PART 9 — MITRE ATT&CK, Properly Explained

Referenced heavily above — worth its own section since it's load-bearing for the entire reward design.

MITRE ATT&CK is a public, continuously-maintained catalog, built by the security community, describing how real-world attackers actually operate. It has two layers:

- **Tactics** — the attacker's *goal* at a given stage of an intrusion (e.g., "Initial Access," "Credential Access," "Discovery," "Impact"). Think of these as chapter titles in "how an attack unfolds."
- **Techniques** — the *specific method* used to pursue a tactic, nested underneath it (e.g., a particular password-spraying method sits under the Credential Access tactic).

**ARSS operates at the tactic level** — each of its 7 attack categories maps to one MITRE tactic, and that tactic's associated severity becomes the reward weight (table in Part 8). This is a *broad* application of MITRE ATT&CK, not a fine-grained, technique-level one — a distinction worth being precise about, since a sharp panelist could reasonably ask "how granular is your MITRE grounding, really?" and "tactic-level, not technique-level" is the honest, correct answer.

**Why this matters for the whole research claim:** across the entire literature search (covered next), **zero peer-reviewed papers were found grounding an RL reward function in MITRE ATT&CK at all** — the closest adjacent work (MITREtrieval) extracts MITRE techniques from text using BERT, but never closes the loop back into a reward or policy. That absence is one of ARSS's three central novelty claims.

---

# PART 10 — The Competitive Landscape (What the Literature Review Actually Found)

By mid-2026, extensive literature verification (with real integrity lessons — see Part 11) established that RL for SOC alert response is a genuinely small field. This section introduces the remaining RL algorithm vocabulary — actor-critic, PPO, SAC, TD3 — exactly where it's needed: describing the papers that actually use it.

## Why these other algorithms exist at all
DQN (Part 7) works cleanly only with a **discrete** action space — a fixed menu, which is exactly ARSS's Ignore/Log/Block/Isolate setup. Most competitor papers instead output a **continuous priority score** (a ranking, not a discrete choice), and continuous outputs need different algorithm families:

- **Policy Gradient methods** — instead of learning Q-values first and picking the best one, the network directly learns a *policy* (the probability of taking each action) and nudges that policy toward whatever produced good outcomes.
- **Actor-Critic** — a two-network hybrid: the "actor" decides the action, the "critic" estimates how good that action turned out to be, and the critic's judgment trains the actor. Nearly every algorithm below is some actor-critic variant.
  - **SAC (Soft Actor-Critic)** — actor-critic plus an entropy bonus that rewards the agent for staying exploratory rather than collapsing onto one behavior too early.
  - **TD3 (Twin Delayed DDPG)** — actor-critic with specific tricks to avoid *overestimating* how good an action is (a known failure mode of naive actor-critic training).
  - **PPO (Proximal Policy Optimization)** — a widely-used, more stable policy-gradient method that caps how much the policy is allowed to shift in any single update, preventing the agent from overcorrecting itself into a worse policy.

**On/off-policy, in the same context:** DQN/SAC/TD3 are **off-policy** — they can learn from old experience gathered under an earlier version of the agent (this is why the replay buffer works at all). PPO is **on-policy** — it can only learn from data collected under its *current* policy, discarding old data after each update; more stable, but less sample-efficient. TD3-AP's own stated insight (below) is that off-policy methods suit alert environments better, precisely because alerts are sparse events and reusing old experience matters more than the extra stability on-policy training buys you.

## The actual papers, and exactly how each differs from ARSS

**SAC-AP** (Chavali et al., 2022) — the first in this lineage. Models alert prioritization as an adversarial Markov game between attacker and defender; uses SAC to minimize the defender's expected loss. ~30% better than a DDPG baseline. *Gap:* reward is an abstract "defender loss," invented for the game — no MITRE grounding; output is a ranking, not a response action.

**TD3-AP** (Chavali et al., 2024) — extends SAC-AP with TD3, validated on real IDS traffic (MQTT-IoT-IDS2020, DARPA 2000, CSE-CIC-IDS2018). Established that off-policy methods suit sparse-reward alert environments — a real, useful, borrowed insight. *Gap:* same abstract reward, no CTI grounding, no response actions.

**KNAP** (Chavali et al., 2024) — injects attack-graph "domain knowledge" into the RL training to improve sample efficiency. *Gap:* the "knowledge" is a custom attack-graph heuristic, not MITRE ATT&CK — still no standardized threat-intelligence grounding.

**Multi-Critic** (Chavali & Saxena, 2025) — a technical refinement (multiple critic networks, reducing Q-value overestimation). Same lineage, same abstract reward framing.

**AlertPro** (Wang et al., 2024) — **the closest prior art before Homayoun surfaced.** Two-module system: context inference extracts alert-sequence features, a self-evolution module uses RL with *real analyst feedback* to re-rank alerts, achieving sub-500ms latency. *Gap:* feedback is a simple binary correct/incorrect signal, with no severity weighting — a missed MITM and a missed Recon scan produce the identical training signal — and the output is still a ranked list, not a discrete response action.

**RADAMS** (Huang & Zhu, 2022) — RL-based alert *de-emphasis* against alert flooding, in an Industrial Control Systems setting specifically (not generic SOC). Uses **tabular** Q-learning (same limitation as ARSS's own pre-redesign approach) to decide how many alerts to visually de-emphasize, already differentiating cost by criticality and source layer via a 4-tier dollar-cost table. *Gap:* manages attention/visibility, never takes an actual response action (no Block/Isolate); cost table isn't MITRE-grounded.

**L2DHF** (Jalalvand et al., 2025) — a "Deep RL from Human Feedback" agent deciding, per alert, whether to accept an upstream AI's prioritization or defer to a human — structurally the same accept/defer tradeoff ARSS's LOG action encodes. Strong reported results (13-16%/60-67% accuracy gains, 98% fewer high-category misprioritizations). *Gap:* binary accept/defer only, not a multi-action response space; reward is accuracy-driven, not MITRE-grounded.

**AACT** (Turcotte, Labrèche, Paquette, 2025) — *not RL at all* — supervised imitation learning on real analyst decisions, with a genuine 6-month production SOC deployment: 61% alert reduction, 1.36% false-negative rate. Strong proof the triage problem is solvable, non-RL. *Gap (shared with Charlotte AI below):* imitation learning can only replicate the analysts it learned from — it cannot discover a *better* policy than its training data, only match it.

**CORTEX** (Wei et al., 2025) — multiple specialized LLM agents (behavior analysis, evidence-gathering, reasoning) coordinated into an auditable triage decision. *Gap:* not RL, not deterministic, carries real multi-agent-LLM latency cost; produces an audit trail, not a learned policy.

**CrowdStrike Charlotte AI** (commercial) — imitation learning on millions of real Falcon MDR analyst decisions. The single strongest *commercial* product in this space. *Gap:* same ceiling as AACT — replicates, cannot exceed, the analysts it was trained on. If those analysts systematically over-blocked Recon and under-responded to MITM, Charlotte AI learns and perpetuates exactly that bias. An RL agent optimizing against an external, principled severity signal (MITRE weights) is not bound by that same ceiling.

**Homayoun et al. 2026** ("Risk-Aware SOC Alert Handling in Adaptive Cyber Defense with Reinforcement Learning," ESORICS 2025 Workshops, Springer LNCS) — **the current closest competitor overall.** Uses plain PPO; its entire stated contribution is reward-shaping, not architecture. Its reward explicitly encodes threat criticality + detection confidence + isolation cost — confirmed, from the verified abstract, to be a **bespoke operational taxonomy, not MITRE ATT&CK-grounded.** State space and action space remain unverified — full text is paywalled (Springer/ACM DL), a genuine open item, not a resolved one.

## The three-way gap this establishes (ARSS's actual novelty claim)
Across the entire surveyed field, no single paper combines all three:
1. A **category-conditioned state space** (attack type + confidence, not a collapsed scalar score).
2. A reward **grounded in MITRE ATT&CK** tactic severity specifically (as opposed to an invented cost, or a different, bespoke operational taxonomy like Homayoun's).
3. A **discrete multi-action response space** (Ignore/Log/Block/Isolate) at the SIEM output layer, as opposed to a ranking or a binary accept/defer decision.

Also worth remembering from the commercial-landscape sweep: **as of the search, no commercial SOC/SOAR platform (Splunk SOAR, Palo Alto XSOAR, Microsoft Sentinel, IBM QRadar) publicly uses RL as its triage mechanism at all** — the market has converged on rules, supervised scoring, or LLM agents. RL-based autonomous triage is unclaimed commercially, not just academically.

## Full Literature Count, and a Plain-English Index of Every Paper (updated Sept 21, 2026)

**The numbers:** 29 papers are formally cited in `ARSS_Paper.tex` right now. A further 18 have been independently verified as real and ready to cite but aren't in the paper yet — pending a decision on which ones actually earn a spot. That's **47 total papers found and checked**, 29 currently in use.

The competitor papers already got the full plain-English treatment above (SAC-AP through Homayoun). Here's the rest — the supporting/theory papers from the formal 29 that weren't covered above, plus all 18 new candidates — in the same plain style.

### The remaining supporting papers already in the bibliography

- **SoK: The Pitfalls of Deep RL for Cybersecurity** (McFadden et al.) — reviewed 66 DRL-for-cybersecurity papers and catalogued 11 common mistakes researchers make (bad environment setup, unrealistic train/test splits, etc.). Used as a self-check checklist for ARSS's own evaluation plan, not a competitor.
- **Multi-Objective RL for Automated Resilient Cyber Defence** (O'Driscoll et al.) — a real, serious critique: argues that a single hand-set reward number locks an agent into one fixed tradeoff decided in advance, and proposes an approach that produces a whole *family* of adjustable policies instead. ARSS's honest response: yes, this phase's reward is a single scalarized number, deliberately, to match the simpler DQN approach — extending to the adjustable-family approach is named future work, not denied.
- **Dynamic Cyberattack Simulation... MITRE-ATT&CK** (Oh et al.) — uses MITRE ATT&CK to help an RL agent simulate realistic *attacker* behavior for red-team training — literally the opposite side of the problem from ARSS. Good proof MITRE+RL has been combined before, just never to ground a defensive reward.
- **AI-Driven Security Alert Screening... A Comprehensive Survey** (Ndichu et al., 2026) — a huge, recent review pulling together 119 records on alert fatigue since 2015. Confirms the problem is still active and unsolved, from a very wide-angle view.
- **Multi-Agent RL in Cybersecurity: From Fundamentals to Applications** (Landolt et al.) — broad survey of multi-agent RL applied to cybersecurity generally. Good background; not a rival since ARSS deliberately stays single-agent for now.
- **SoK: The MITRE ATT&CK Framework in Research and Practice** (Roy et al.) — systematically reviewed everywhere ATT&CK has been used in security research and found *no* prior work connecting it to reinforcement learning at all. An independent, second confirmation of ARSS's core novelty claim.
- **ARCS: Adaptive RL for Automated Cybersecurity Incident Response** (Ren et al.) — RL that picks a defense strategy once an incident is already confirmed — one layer downstream of the triage decision ARSS actually makes.
- **Safety-Contract Graph MARL** (de Jesus Silva) — shows RL trained to maximize pure security reward, with no explicit business-cost terms, blows through real operational limits (like acceptable downtime) in *100% of tested episodes*. Directly backs up why ARSS's reward includes analyst-workload and business-disruption terms, not just a "block everything" score.
- **Gartner 2026 Cybersecurity Trends report** — industry analyst report, not academic. Names AI-driven alert triage as a near-term SOC priority while stressing human oversight stays essential. Used for market-context only.

### The 18 new verified candidates (not yet added to the paper)

**#1 Okafor — offline-RL benchmark for SOC triage.** Head-to-head comparison of imitation learning and offline RL methods on triage data, with leakage-proofed evaluation. Solid, published, real. *ARSS angle: bridges the RL-vs-imitation-learning debate directly.*

**#2 Moran — fuzzy-logic alert prioritization.** Scores alerts by blending severity, detector confidence, and org risk-tolerance using fuzzy math. Sensible, not RL. *ARSS does better: only ranks — never decides or acts.*

**#3 Ndichu et al. — PACT, active learning for rare attacks.** Smarter trigger for "when do we actually need a human to double-check this," cutting false positives 21-43%. Solid, practical. *ARSS does better: improves detection, doesn't respond.*

**#4 Chowdhury/Tanvir — trust-calibration layer.** Adjusts for over-confident wrong answers slipping through a classifier. Useful, narrow. *ARSS does better: an add-on, not a decision-maker.*

**#5 Sahay et al. — LLM + RL threat hunting on Splunk.** Ambitious hybrid: anomaly detector + two-layer RL + LLM, closest of this batch to ARSS's territory. *ARSS does better: RL is a small buried piece here, not the main event; not MITRE-grounded.*

**#6 Mohsin et al. — 5-level human-AI trust framework.** Defines how much autonomy an AI should get in a SOC, tested with a simulated assistant. Credible framework. *ARSS does better: conceptual only, no trained policy behind it.*

**#7 AlertSAGE — smart alert grouping via graph transformer.** Clusters raw alerts into real incidents, 96% noise reduction. Strong technical result. *ARSS does better: groups alerts, never decides what to do about them.*

**#8 Javadpour et al. — broad RL-for-network-security survey+tutorial.** Textbook-style overview, not triage-specific. Good background citation only.

**#9 Liu et al. — DRL-MD, mitigation deployment planning.** Real MITRE+RL combination, but for *picking a fix* after an incident, not triaging the alert itself. *ARSS does better: operates upstream of this, at the response-decision stage.*

**#10 Huff et al. — governance-to-mitigation RL.** Maps org security maturity to ATT&CK fixes under a budget constraint. Same territory as #9. *ARSS does better: not a per-alert response decision.*

**#11 Bates, Hicks, Mavroudis — reward-shaping study.** Genuine counterargument: finds simple/sparse rewards often beat complicated/shaped ones. *ARSS's answer: its reward isn't hand-tuned shaping — it's anchored to an external, checkable standard (MITRE), a different category than what this paper critiques.*

**#12 Mukherjee et al. — LLM writes the reward function.** Clever, current idea for auto-generating cyber-defense rewards. *ARSS does better: an LLM-invented reward is still invented — not grounded in an external framework.*

**#13 Lazer et al. — broad agentic-AI-in-cybersecurity survey.** Wide-angle context piece across the whole security lifecycle. Too broad to be a rival.

**#14 Al-Sada et al. — MITRE ATT&CK survey, ACM Computing Surveys.** The strongest new find — same top-tier venue as your two best existing sources. Independently confirms nobody's connected ATT&CK to an RL reward.

**#15 Finistrella et al. — multi-agent RL survey.** Properly published, classifies MARL approaches in cybersecurity. Background only — ARSS is deliberately single-agent.

**#16 Vaarandi & Guerra-Manzanares — active learning for IDS alerts.** Real, published, cuts labeling burden. *ARSS does better: filters before triage, still leaves the decision to a human.*

**#17 Homayoun — the real competitor.** Already covered in full above. The one paper worth having a sharp, ready answer for.

**#18 Chhetri et al. — human-AI teaming, ACM TOIT.** Conceptual companion to the already-cited A2C paper, mostly the same author group. *ARSS does better: framework only, no trained policy — same gap as #6.*

---

# PART 11 — The Integrity Audits: A Real, Repeated Lesson

Two separate sessions (July 19-20 and Sept 19-20, 2026) independently found the same failure pattern in the project's own citation work, worth internalizing as a standing discipline, not a one-off cleanup.

**The pattern, every single time:** a citation's DOI and publisher link were correct — genuinely a real, existing paper — but the **title text or a headline result figure attached to it was wrong**: a paraphrase substituted for the actual title, or a number that doesn't appear anywhere in the source. Confirmed instances: a fabricated "alert volume" statistic repeated across four documents (including the signed scope document's own Abstract), a fabricated RADAMS recall/FPR figure, a misquoted SAC-AP percentage, an A2C citation pointing at a mismatched title/DOI pair, and a mistitled MITREtrieval citation.

**The actual lesson, stated precisely:** *a DOI resolving to a real paper is necessary but not sufficient verification.* The check that actually catches these errors is pulling the verbatim title from the real publisher page and diffing it character-by-character against what's recorded — not just confirming the paper exists.

**The standing rule adopted from this (borrowed structurally from a teammate's separate CY315 project, not its content):** a four-phase discipline — curate the bibliography by themed "job" buckets before reading anything; access only real PDFs/abstracts through legitimate channels, never trust a search-snippet summary; read fully and record with an honest confidence flag (full-text vs. abstract-only, always disclosed, never smoothed over); cross-reference each paper's own stated limitations for language that hands you your gap. The qualifying bar for any citation: real, verified, with a specific nameable job in the argument — never included just to pad toward a count.

**One document deliberately left uncorrected, on purpose:** the signed `ARSS_Scope_Document_v2.md` still carries four of these errors. This is a standing team decision, not an oversight — correcting an already-signed academic document is judged to be the supervisor's call to make, not something to quietly patch. It remains an open item to raise with Dr. Khan.

---

# PART 12 — Where ARSS Actually Stands Today

Being honest about this gap matters more than anything else in this document, because it's the question a defense panel will actually ask.

**What's genuinely strong:** the research idea has survived two separate rounds of pointed professor scrutiny. The literature grounding is, as of the latest audit, extensively verified — dozens of sources checked against real text, not summaries, with honest confidence-labeling throughout. A full IEEE-format paper draft exists (`ARSS_Paper.tex`) with a formally stated system model, related work, methodology, and evaluation *protocol*.

**What's genuinely missing:** **zero lines of the redesigned DQN agent exist in code.** `v2/server/decider.py` still runs the pre-February-pivot flat Q-learning, with `api.py` silently falling back to a hardcoded `Block if danger > 0.8 else Log` rule when no trained policy is available. The paper's Evaluation section is, honestly and explicitly, a protocol description only — no empirical results exist yet, by team decision, because the system isn't built. Reward function coefficients are still numeric placeholders, not a completed design pass.

**The honest framing for a defense, if asked "where are your results":** the research and design work is real and substantially de-risked; the implementation is the remaining, well-scoped engineering task, not an unsolved research problem. Those are different kinds of "not done," and it's worth being able to say precisely which one applies.

---

# PART 13 — Defense Readiness: Counter-Questions and How to Answer Them

Every question below is a real one a panel could reasonably ask. The answers are written to be *honest*, not just confident — several deliberately concede a real limitation before explaining why it doesn't sink the project. That's the stronger posture: a panel that catches you overselling a weak point loses trust fast; a panel that watches you name your own limitation first, and explain exactly what it does and doesn't affect, generally doesn't push further. Practice saying the honest half out loud, not just the reassuring half.

## On novelty and positioning

**"Isn't this just an IDS/IPS with extra steps?"**
No — and this is the single most important distinction to have automatic. An IDS/IPS *detects*. ARSS assumes detection is already done, correctly, by upstream tools, and receives an alert that has *already* passed the SIEM. Its only job is deciding what to do about that alert — a discrete response decision, not a classification task. If you're ever unsure how to answer a question in the room, ground it here: "we are downstream of detection, and our contribution is entirely in the decision layer" (Part 8).

**"RL for alert handling already exists — SAC-AP, TD3-AP, AlertPro, RADAMS. What's actually new?"**
Nothing about *using RL for alerts* is new — that's honestly stated, not hidden. What's new is a specific combination nothing in the surveyed field has together: a state space that preserves attack category and confidence instead of collapsing to a scalar risk score, a reward grounded in an external, industry-standard severity taxonomy (MITRE ATT&CK) instead of an invented game-theoretic cost, and a discrete multi-action response space instead of a ranking or a binary defer decision (Part 10). Name one prior paper by name when asked this — it shows you've actually read them, not just cited them.

**"Homayoun 2026 already does risk-aware reward shaping with criticality, confidence, and isolation cost — that sounds like exactly what you're doing."**
It's close, and worth naming as the closest prior work rather than downplaying it — but one difference is confirmed directly from its own abstract: Homayoun's reward taxonomy is a bespoke operational construct built for that paper's simulation, not MITRE ATT&CK-grounded. That's the real differentiator, and it's provable, not asserted. Be honest about the rest: Homayoun's state space and action space are currently unverified — full text is paywalled — so don't claim more distance from it than can actually be defended. Say plainly: "we know it differs on the reward taxonomy; we don't yet know how it compares on state/action design, and we're not going to claim otherwise."

**"If RL-based autonomous triage is such a good idea, why hasn't any commercial vendor shipped it?"**
Because the market solved a different, earlier problem — trust, not capability. Splunk SOAR, Palo Alto XSOAR, and Microsoft Sentinel all *can* automate responses; analysts routinely override them anyway because the systems can't explain their reasoning in terms the analyst already trusts. CrowdStrike Charlotte AI, the strongest commercial product in this space, uses imitation learning — it can replicate what analysts already do, but structurally cannot discover a policy *better* than its training data. ARSS's explainability layer (SHAP + LLM narrative, Part 8) and its externally-grounded reward exist specifically to address the trust gap that's kept the market from adopting RL here at all.

**"How does a GIKI undergrad team justify building something a billion-dollar security company, with vastly more resources, hasn't shipped? How can you claim RL for this isn't implemented, or is 'unsafe' — and how can you claim to make it safe?"**
This is the sharpest version of the "why hasn't industry done this" question, and it deserves a full answer, not a defensive one.

*Why the resource gap doesn't settle it:* what's stopping a company like CrowdStrike isn't technical capability — it's liability and sales economics, a different problem than the one ARSS is solving. If an autonomous RL agent Isolates a client's production server by mistake, that's a multi-million-dollar outage with the vendor's name attached, inside an enterprise contract with real legal exposure. Imitation learning — replicate what analysts already do — is a *safer commercial product* than RL, even at a lower performance ceiling, because it never does anything a human hasn't already approved of historically. That's a business decision, not proof the underlying idea is wrong. It's also directly evidenced in the literature already surveyed, not asserted: Charlotte AI's own documented limitation is that it can only replicate the analysts it trained on, never exceed them (Part 10) — a *named, acknowledged* tradeoff, not a mystery. There's real switching cost too: a vendor with thousands of enterprise SOAR customers can't casually re-architect the decision layer under all of them, regardless of whether RL would perform better.

*On the "isn't implemented" claim specifically — don't overstate it.* The defensible version is narrow and evidence-based: as of a literature and commercial-landscape sweep, no SOC/SOAR vendor publicly uses RL as its *triage decision mechanism*. That is not the same as claiming RL is broadly "unsafe" or unproven as a technique — RL is already used in recommendation systems, resource allocation, robotics, and guarded trading systems. Never let the claim drift from "no vendor does this specific thing, as far as this search found" into "RL is considered unsafe" as a blanket statement — the first is checkable and true; the second is an overclaim a panelist could reasonably puncture. And it isn't an undiscovered idea either: academics have explored exactly this since 2022 (the whole Chavali lineage, AlertPro, RADAMS, now Homayoun) — being first to combine three specific design choices *within an already-active research area* is the actual claim, not "nobody ever thought of this." Research exploring an idea years before industry adopts it is the normal order of things, not a red flag.

*On "how do you make it safe" — the honest answer is the strongest one.* ARSS does not claim to have solved AI safety for autonomous cyber response, and claiming otherwise in the room would be a real mistake. What it actually contributes is narrower: the LOG action is a built-in human-deferral valve, not a removal of humans from the loop; grounding the reward in MITRE ATT&CK makes the decision externally auditable rather than resting on an opaque self-invented reward; the explainability layer exists so a human can catch and override a bad call, not so the system can act unsupervised with impunity. That's a real, scoped contribution to *trust and interpretability* in the decision layer — not a formal safety proof, and the paper's own scope already states live deployment and full safety validation are future work, not solved now.

*On the "you're an undergrad" framing directly.* Research contributions are evaluated on whether the gap is real, the design is sound, and the evaluation is honest — not on the seniority of who's making the claim; a reviewer checks methodology, not a degree. The honest, correct posture is not "we know better than a billion-dollar company" — it's "we found a specific, verifiable gap this industry hasn't had commercial reason to close yet, and we're proposing a well-scoped way to close part of it." That is a modest claim, it is the one the paper actually makes, and it's a stronger position in the room than either false modesty or overclaiming would be.

## On technical choices

**"Why DQN when SAC/TD3/PPO are what the field actually uses?"**
Because the action space is different in kind, not just degree. SAC/TD3/PPO exist to handle *continuous* outputs — a priority score. ARSS's output is a fixed menu of four discrete actions. DQN is the correct, standard tool for a discrete action space; reaching for an actor-critic method here would be solving a problem ARSS doesn't have (Part 10). If pushed further: "we evaluated this explicitly — it's not that we didn't know about SAC/PPO, it's that they're the wrong tool for a discrete action space."

**"A discrete 4-action space seems like a step backward from a continuous priority ranking — isn't more granularity better?"**
A ranking still leaves the actual decision to a human — every prior ranking-based system requires an analyst to decide what a top-ranked alert should *trigger*. ARSS's contribution is precisely that it removes that remaining step: the output is an executable action, not one more thing to interpret. Granularity in ranking and autonomy in response are different axes, and this project is explicitly optimizing the second one.

**"Your MITRE severity weights (1.0, 0.8, 0.7...) look just as hand-set as the 'invented' rewards you criticize other papers for. What's actually different?"**
Fair challenge, and worth conceding the mechanism is similar — a human still assigns a number. What's different is the *source* of that number: it's derived from an external, community-maintained taxonomy that the security industry already uses to reason about severity, not invented for this training environment alone. It's independently checkable — anyone can look up whether MITM really maps to Credential Access/Collection and whether that's considered higher-severity than Discovery. An invented game-theoretic cost has no such external reference point to audit against.

**"Why tactic-level MITRE grounding and not technique-level — isn't that coarse?"**
Correctly identified as coarse, and that's a deliberate, stated scope choice, not an oversight — technique-level grounding would require mapping each of the 7 dataset attack categories to specific MITRE techniques rather than tactics, a meaningfully larger and more detail-sensitive undertaking. Tactic-level is the right first-phase granularity: broad enough to be tractable with 7 categories, specific enough to differentiate MITM from Recon meaningfully. Technique-level refinement is legitimate future work, not a hidden flaw.

**"How does the agent handle a state combination it's never seen during training?"**
This is exactly why the redesign moved from a Q-*table* to a Q-*network* (Part 7) — a table can only answer questions about states it has explicitly seen; a neural network generalizes across similar states by learning patterns rather than memorizing exact combinations. This isn't a hand-wave — it's the specific, named reason DQN was chosen over tabular Q-learning.

**"If Stage 1/2 detection confidence is wrong, doesn't the RL agent just inherit that error?"**
Yes, honestly — this is a real dependency, not one to paper over. The RL agent's decision quality is bounded by the detector's accuracy; garbage in the state vector produces a worse-informed decision. This is true of every layered system, not unique to ARSS, and it's exactly why confidence is included as its own state dimension rather than assumed reliable — a low-confidence classification and a high-confidence one should (once trained) produce different response behavior even at the same danger score. Whether the agent actually learns to use confidence this way is an empirical question for evaluation, not yet demonstrated.

## On results and evaluation

**"You have no implementation results. How can you claim a research contribution?"**
The honest answer is the strongest one here: the contribution being defended right now is the *system design* — the state space, the reward formulation, the formal MDP model, and the evaluation protocol (Part 12) — not an empirical result. That's a legitimate, common category of contribution at this stage of a project, provided it's stated as such rather than implied to be more. What would *not* be defensible is claiming performance numbers that don't exist. Never do that.

**"What will you actually compare against, once you do have results?"**
A rule-based/threshold baseline (the pre-redesign approach) at minimum, to isolate what the learned policy adds over a static rule — plus, ideally, a tabular Q-learning baseline using the old narrow state, to directly demonstrate the value of the richer state space (Part 7-8's whole argument, made empirical rather than just architectural).

**"Your detection numbers (92.34%/92.83%) are lower than v1's 98.9% — did the system get worse?"**
No — different, harder, more modern dataset, and deliberately no SMOTE inflating the number (Part 6). This is worth having ready as a crisp one-liner: "92% honest beats 99% inflated" — and be ready to explain *why* SMOTE would have inflated it (synthetic minority samples the model would learn to recognize that don't reflect real traffic).

## On deployment realism

**"You say the deployable product is just the trained policy — but a real SIEM doesn't emit your exact 71-feature vector or a matching confidence score. Doesn't that break the whole deployment story?"**
Correctly caught, and already conceded in the paper draft rather than glossed over: Stages 1-2 move from a public-dataset feature space to a deployment-specific one, and live-SIEM schema adaptation is explicitly scoped as future work, not assumed solved. The original framing overclaimed this once; it's been corrected. Say exactly that if asked — it demonstrates the team catches and fixes its own overclaims, which reads better than a panel catching it first.

**"How would an analyst ever trust an autonomous Isolate action if it's wrong?"**
This is the exact problem the Cognitive Semantic Layer exists to address (Part 8) — every autonomous action ships with a plain-English explanation of what triggered it and why, generated from real SHAP attributions and the actual RL decision, not a generic message. Trust isn't assumed; it's the explicit design target of a specific component, not an afterthought bolted on for the defense.

## On process

**"This took over a year and multiple pivots — didn't you waste a lot of time?"**
Reframe this one directly: every pivot was driven by a specific, named technical limitation being discovered and fixed — A* couldn't learn from outcomes, so it was replaced; tabular Q-learning couldn't scale its state space, so DQN replaced it; the reward was ungrounded, so MITRE ATT&CK replaced it. That's not wasted time, that's the project correctly responding to real feedback rather than defending a first draft. The alternative — shipping the January version unchanged — would have been indefensible in exactly the way the professor said it was.

---

# PART 14 — Full Glossary (Everything From Above, One Place)

- **MDP (Markov Decision Process)** — the formal state/action/reward/transition loop underlying all of RL.
- **State space / Action space / Reward function** — the three design choices that define any RL problem; ARSS's specific choices are `[danger, category, confidence]` / `{Ignore, Log, Block, Isolate}` / MITRE-weighted.
- **Policy (π)** — the agent's strategy: a mapping from state to action (or to action-probabilities).
- **Q-value, `Q(s,a)`** — the agent's running estimate of how good an action is in a given state, long-term.
- **Bellman update** — the rule for nudging Q-value estimates toward observed reality after each action.
- **α (learning rate)** — how large a correction each update makes.
- **γ (discount factor)** — how much future reward is valued relative to immediate reward.
- **Exploration vs. exploitation** — trying something new to learn more, vs. doing what's currently believed best.
- **Episode** — one full run of the agent from start to some end condition.
- **Convergence** — the point where training stabilizes and the policy stops meaningfully changing.
- **Tabular Q-learning** — a literal lookup table of Q-values; breaks down as the state space grows (the "state space explosion" problem).
- **DQN (Deep Q-Network)** — a neural network standing in for the Q-table, able to generalize to unseen states.
- **Replay buffer** — stored past experience, sampled randomly during training for stability.
- **Target network** — a slow-updating copy of the Q-network used to stabilize the Bellman update's "future reward" term.
- **Policy gradient** — directly learning a policy, rather than learning Q-values and picking the best.
- **Actor-Critic** — two networks: one decides (actor), one judges (critic).
- **SAC, TD3, PPO** — specific actor-critic/policy-gradient algorithms used when the action space is continuous (SAC-AP, TD3-AP, and Homayoun 2026 respectively).
- **On-policy vs. off-policy** — whether an algorithm can learn from old experience (off-policy: DQN/SAC/TD3/ARSS) or only from current-policy data (on-policy: PPO).
- **Sparse vs. dense reward** — feedback only at the end of an episode, vs. feedback after every action (ARSS is dense, MITRE-anchored).
- **Baseline** — the simpler comparison method a paper (or ARSS itself) is measured against to prove the RL adds value.
- **MITRE ATT&CK — Tactic** — the attacker's goal at a stage (e.g., Credential Access). **Technique** — the specific method used to pursue that tactic. ARSS grounds its reward at the tactic level.
- **SHAP** — feature-attribution explainability method; answers "which input features drove this specific prediction."
- **Soft voting (ensemble)** — averaging two models' predicted probabilities and taking the highest, rather than trusting either model alone.
- **Class weights vs. SMOTE** — two answers to imbalanced training data; ARSS uses class weights (penalize errors on rare classes) specifically to avoid SMOTE's risk of inflating accuracy with synthetic, non-real examples.
- **A²C (Automate-Augment-Collaborate)** — the theoretical framework ARSS operationalizes: routine cases get full automation, novel/uncertain cases get human collaboration (ARSS's LOG action = Collaborate mode).

---

*Compiled: September 19-20, 2026. This document supersedes the earlier, shorter "checkpoint" version of the RL primer — same core vocabulary, now told as one connected narrative with the project's actual history. Companion documents: `ARSS_Literature_Review.md` (polished, citation-ready) and `ARSS_Literature_Session_Notes.md` (raw working notes, verification status, open items).*
