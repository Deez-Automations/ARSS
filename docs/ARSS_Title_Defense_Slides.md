---

# ARSS
### Category-Conditioned Deep Reinforcement Learning for MITRE ATT&CK-Grounded Autonomous SOC Alert Triage

Muhammad Daniyal (2023406) · Haider Iqbal (2023416) · Syed Daud (2023677)
Supervisor: Dr. Muhammad Fawad Khan · Co-Supervisor: Miss Hadia Abbas
BS Cybersecurity, Faculty of Computer Science and Engineering, GIKI
Title Defense — September 2026

---

# Agenda

1. The problem
2. Why it's still unsolved
3. What we reviewed, and the gap we found
4. Our proposed system
5. The formal design
6. Dataset
7. Future scope

---

# The Problem: Alert Fatigue

A 2025 systematic review in *ACM Computing Surveys* (Tariq et al.) found:

- **51%** of SOC teams report feeling overwhelmed by alert volume
- Analysts resolve only **49%** of alerts assigned to them within a workday

This is not a detection failure. The alerts are being generated correctly — the failure is downstream, at the decision layer.

*Source: Tariq et al., ACM Computing Surveys, DOI 10.1145/3723158*

---

# What Already Exists, and Where It Stops

| Tool | What it does | What it doesn't do |
|---|---|---|
| IDS / IPS | Detects and flags suspicious traffic | Takes no response decision |
| SIEM | Aggregates and correlates alerts | Still requires human triage |
| SOAR | Automates responses via playbooks | Playbooks are static — don't learn from outcomes |
| ML risk-scoring | Ranks alerts by threat probability | Doesn't take an action, still leaves the decision to a human |

These tools are good at what they do. None of them decide, and none of them learn from what happened after a decision was made. That is the specific gap this project addresses.

---

# Where ARSS Sits

```
Raw Traffic → Firewall → IDS/IPS → SIEM → [ARSS] → Human Analyst
```

ARSS is not a detection system.

It receives alerts that have already passed every upstream filter. Its only job is deciding what happens next.

**ARSS is not a better IDS — it is the decision layer that comes after detection.**

---

# What We Reviewed

Literature review: **29 sources** formally cited, verified against primary text and publisher records — not just search summaries. Errors found in the team's own earlier bibliography were corrected, not hidden.

The RL-for-alert-response lineage:

SAC-AP (2022) → TD3-AP (2024) → KNAP (2024) → Multi-Critic (2025) → AlertPro (2024) → RADAMS (2022) → L2DHF (2025) → **Homayoun (2026)**

---

# The Consistent Limitation Across Prior Work

Every prior RL-for-alert system shares two limitations:

1. **Reward is invented** — an abstract "defender loss" or game-theoretic cost, not tied to how security teams actually judge severity.
2. **Output is a ranking**, not an action — the analyst still decides what a top-ranked alert should trigger.

**Concrete example:** AlertPro (Wang et al., 2024) — has a real analyst-feedback loop, achieves sub-500ms latency — and still only re-ranks alerts. The analyst still decides what to do with the top result.

---

# The Confirmed Gap

No surveyed paper combines all three of these:

1. A state space that preserves **attack category and confidence**, not a collapsed risk score.
2. A reward grounded in **MITRE ATT&CK tactic severity**, not an invented cost.
3. A **discrete four-action response** (Ignore / Log / Block / Isolate), not a ranking.

**This is ARSS's novelty claim.**

---

# The Closest Prior Work: Homayoun 2026

Homayoun (ESORICS 2025 Workshops) — the closest related work found.

- Confirmed from the paper's own abstract: reward built from **threat criticality, confidence, and isolation cost**
- Confirmed: **not** MITRE ATT&CK-grounded
- **Not yet known** (full text paywalled): its state space and action space

We are stating plainly what is known and what remains unverified about the closest comparable work, rather than overclaiming distance from it.

---

# Objectives

- Train a two-stage ML ensemble (XGBoost + DNN) for binary detection and 7-way attack categorization with confidence scoring
- Design a category-conditioned RL state space encoding danger score, attack category, and confidence
- Train a DQN agent with a MITRE ATT&CK severity-weighted reward, balancing analyst workload against threat containment
- Implement a Cognitive Semantic Layer translating SHAP + RL output into plain-English narratives
- Demonstrate, via baseline comparison, that the category-conditioned agent outperforms a rule-based threshold system
- Evaluate the full pipeline on CIC-IIoT 2025 and report autonomous-handling rate, false negative rate by category, and false positive escalation rate

---

# System Architecture

```
Stage 1: Binary Detection (XGBoost + DNN, soft voting)
   ↓ if attack
Stage 2: Attack Categorization — 7 classes (XGBoost + DNN, soft voting)
   ↓
RL Response Agent (DQN)
   ↓
{ Ignore, Log, Block, Isolate }
```

---

# The Formal Design

**State:** `[danger_score, attack_category (7-way one-hot), confidence]`
**Action:** `{Ignore, Log, Block, Isolate}`
**Reward:** dense, tactic-severity-weighted, dual-objective (containment vs. analyst workload)

**Algorithm: DQN**

DQN is chosen because the action space is discrete, not continuous. Competitor systems (SAC-AP, TD3-AP) use actor-critic methods because their output is a continuous priority score — a different problem shape than a fixed four-action menu.

---

# MITRE ATT&CK Severity Weighting

| Attack Category | MITRE Tactic | Severity Weight |
|---|---|---|
| MITM | Collection / Credential Access | 1.0 |
| Malware | Execution / Persistence | 1.0 |
| DDoS | Impact | 0.8 |
| DoS | Impact | 0.7 |
| Brute Force | Credential Access | 0.6 |
| Web Attacks | Initial Access | 0.5 |
| Recon | Discovery | 0.3 |

This grounding operates at the **tactic level**, not the individual-technique level — a deliberate scope choice for this phase of the work, not an oversight.

---

# Dataset

**CIC-IIoT 2025** — Canadian Institute for Cybersecurity, University of New Brunswick

- 685,000 samples, 71 features, 7 attack categories
- A controlled-lab testbed dataset — real attack tools run against real infrastructure, not synthetic company data and not real production traffic either
- Real production network data is confidential by nature, which is exactly why the field builds controlled testbed datasets instead of using company data
- Same family of dataset used across the surveyed literature (TD3-AP evaluates on MQTT-IoT-IDS2020, DARPA 2000, CSE-CIC-IDS2018) — this is standard practice in the field, not a workaround unique to this project

---

# Future Scope

- Richer per-alert information: multi-part alert labels, alert age, analyst workload signal, network context, short-term memory of attacker behavior, worst-case risk tracking
- Finer-grained MITRE grounding: individual attacker techniques instead of 7 broad categories — literature review confirms no prior work combines ATT&CK with RL at *any* level of detail, so this would extend an already-uncommon idea rather than catch up to one
- Hard operational limits instead of soft reward penalties
- A trainable range of tradeoffs (aggressive vs. cautious) instead of one fixed, locked-in blend
- Multiple judges during training, easy-to-hard training progression, auto-tuned severity weights, drift detection for staleness

These are literature-backed directions, not commitments — presented for the supervisor's guidance on which are worth prioritizing given the remaining timeline.

---

*Draft 1 — September 21, 2026. Covers the material presented through Dataset and Future Scope. Results, current build status, evaluation plan, work plan, and conclusion slides to follow in a subsequent draft.*
