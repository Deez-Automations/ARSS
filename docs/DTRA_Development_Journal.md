# 📔 DTRA Development Journal
## The Complete Journey: From Summer Concept to Research Contribution

> **Purpose:** This is our checkpoint log. Every conversation, decision, learning, and breakthrough documented so we never lose context. Conversational, connectable, like notes tying dots together.

---

## 🧬 GENESIS: The Original Proposal
**Date:** Pre-Semester (Summer 2025)
**Team:** Haider (2023416) + Daniyal (2023406)
**Course:** CS 351 - AI Lab

### The Problem We Identified
> "Modern Security Operations Centers (SOCs) are overwhelmed by alert fatigue, a condition where analysts face thousands of alerts daily from numerous security tools most of which are false positives."

**Key insight from Day 0:** We didn't want to build "another IDS." We wanted to solve the HUMAN problem - analysts burning out from alert overload.

### Our Original Vision
1. **Detect Threats Intelligently** - ML classifier with confidence outputs
2. **Quantify Alert Confidence** - Probabilities, not binary yes/no
3. **Explain Alerts** - SHAP/LIME for transparency
4. **Automate Response Decisions** - RL agent that learns Ignore/Log/Block/Isolate
5. **Optimize Response Strategy** - Balance security vs. business continuity

### What We Planned vs. What We Built

| Planned (Proposal) | Actually Built | Why Changed |
|-------------------|----------------|-------------|
| UNSW-NB15 dataset | CICIDS2017 → CIC-IIoT 2025 | Better labels, more attack types |
| A* search for responses | A* → then **Q-Learning** | RL adapts, A* is static |
| Q-Learning or DQN | Q-Learning only | Simpler, interpretable, worked well |
| Single ML model | Hybrid Ensemble (DNN+RF→DNN+XGB) | Ensemble beats single model |

---

## 📊 PROGRESS REPORT I: The A* Agent
**Milestone:** Agent/search algorithm implementation

### What We Built
The "Decider" brain using A* search:
```
f(n) = g(n) + h(n)
     = Business Cost + Security Risk
```

**Business Costs (our rules):**
- Ignore: 0 (free)
- Log: 2 (cheap)
- Block: 20 (medium disruption)
- Isolate: 80 (high disruption)

**Security Risk calculation:**
- If Ignore: Risk = Danger Score (ignoring 95% threat = 95 risk)
- If Block: Risk = False Positive chance × penalty
- If Isolate: Risk = 0 (threat contained)

### The "Working Example" (3 Test Cases)
1. **1% "Leaf" (false positive):** Agent chose IGNORE ✅ → Alert fatigue solved
2. **95% "Robber" (true threat):** Agent chose BLOCK ✅ → Autonomous response
3. **60% "Ambiguous":** Agent chose BLOCK ✅ → Safety-first policy

### What We Learned
- A* works for cost-minimization BUT it's static
- We need something that LEARNS from outcomes
- This led us to Q-Learning in Report III

---

## 📊 PROGRESS REPORT II: The ML Baseline
**Milestone:** Data preprocessing pipeline + baseline ML models

### The Data Journey
- **Dataset:** CICIDS2017 (2.83 million network flows)
- **Sampling:** Used 100K rows strategically (fast prototyping)
- **Features:** 79 numeric features (Flow Duration, Packet Lengths, etc.)
- **Labels:** Binary (0 = Benign, 1 = Attack)

### The Pipeline We Built
```python
Pipeline:
  1. SimpleImputer → Fill NaN with median
  2. StandardScaler → Normalize features
  3. LogisticRegression → Baseline classifier
```

### Baseline Results
- **Accuracy:** 94%
- **Recall:** 83% (catches 83% of real attacks)
- **Precision:** 86%

### The Key Metric: Alert Fatigue
> **788 False Positives out of 30,000 samples**

This became our "before" number. The whole project is about reducing this.

### What We Learned
- Logistic Regression outputs probabilities ✅ (Danger Scores work!)
- 94% sounds good but 788 false alarms = analyst burnout
- We need a more powerful model → Deep Learning

---

## 📊 PROGRESS REPORT III: The Intelligence Upgrade
**Milestone:** Advanced ML/DL + RL + Interpretability

### The DNN Upgrade
Replaced Logistic Regression with 3-layer Deep Neural Network.

| Metric | Baseline (LR) | Advanced (DNN) | Improvement |
|--------|---------------|----------------|-------------|
| Accuracy | 94% | 98% | +4% |
| Recall | 83% | 96% | +13% |
| False Positives | 788 | 412 | **-47%** |
| False Negatives | 992 | 227 | **-77%** |

**This was huge.** We cut alert fatigue nearly in half just by upgrading the model.

### SHAP Explainability
We implemented SHAP to answer "WHY did you flag this?"

**Global findings:**
- Flow Duration and Bwd Packet Length Max = most influential features
- Proves model uses logical network patterns, not random noise

**Local explanations:**
- For each alert, we can show: "Flagged because FIN Flag Count was high + timing was chaotic"
- This builds analyst TRUST in the AI

### The Q-Learning Revolution
**This is where A* died and RL was born.**

We trained a Q-Learning agent for 10,000 episodes in a simulated SOC environment.

**The Learned Policy:**
| Danger Level | Optimal Action | Why |
|--------------|----------------|-----|
| 0-30% | IGNORE | Avoid false positive penalty, save analyst time |
| 30-70% | BLOCK | Risk of ignoring > disruption of blocking |
| 80-90% | ISOLATE | Maximum containment for extreme threats |
| 90-100% | BLOCK | Isolate too costly, Block is sufficient |

**💡 Key Insight:** The agent figured out that 90-100% threats should be BLOCKED, not ISOLATED. 
Why? Because Isolate has high business disruption, and Block is "good enough" for near-certain threats. 
This is NUANCE that A* could never learn - it came from experience.

### What We Learned
- DNN + SHAP = powerful and transparent
- Q-Learning > A* because it adapts
- We have a complete v1 system now

---

## 🏗️ V1 COMPLETE: The Final System
**Timeline:** End of Fall 2025 Semester

### Architecture Delivered
```
Layer 1: Hybrid AI Detector (DNN + Random Forest)
    ↓
Layer 2: Q-Learning Response Agent
    ↓
Layer 3: SOC Dashboard (Real-time visualization)
```

### Final v1 Metrics
- **Accuracy:** 98.9% on CICIDS2017
- **False Positive Reduction:** 47% vs baseline
- **Autonomous Actions:** Ignore/Log/Block/Isolate

### What Was Still Missing
- Live traffic streaming (batch upload only)
- Modern attack types (CICIDS2017 is from 2017)
- Deeper model architectures
- XGBoost stacking

---

## 🚀 V2 REVOLUTION: January 2026
**Timeline:** January 20-21, 2026
**Trigger:** "v1 works, but we can do better"

### Day 1: Foundation Rebuild
**What We Did:**
- Created v1/ (legacy) and v2/ (next-gen) folder structure
- Switched to CIC-IIoT 2025 dataset (685K samples, 71 features)
- Built new preprocessing pipeline
- Fought the Infinity/NaN nightmare

**The 71-Feature Challenge:**
Old dataset had 79 features, new has 71. Complete pipeline rebuild.

### Day 2: Intelligence Upgrade
**What We Built:**
1. **Live Traffic Streaming**
   - `replay_traffic.py` → sends packets to API
   - `api.py` → caches results for dashboard
   - Dashboard polls `/api/recent` for real-time updates

2. **The Looping Bug Fix**
   - Dashboard kept re-counting same 100 packets
   - Added unique `packet_id` to each result
   - Implemented `processedPacketIds` Set in JavaScript

3. **Deep Ensemble Architecture**
   - Old: Simple 3-layer DNN
   - New: 5-layer DNN (512→256→256→128→64) + XGBoost stacking
   - Soft voting between DNN and XGBoost for both stages

4. **Class Weights Instead of SMOTE**
   - Decision: NO synthetic data
   - Real traffic isn't balanced; we should train on real distributions
   - Use class weights to penalize missing rare attacks

### v2 Final Metrics
- **Stage 1 (Detection):** 92.34% Recall (Ensemble)
- **Stage 2 (Categorization):** 92.83% Accuracy (7 attack types)

**Why lower than v1's 98.9%?**
- Different dataset (CIC-IIoT 2025 is harder/noisier than CICIDS2017)
- No SMOTE = honest accuracy, not inflated
- 92% on modern data > 99% on old data

---

## 🎓 THE TITLE DEFENSE: January 31, 2026
**Event:** Professor challenged our project's novelty

### The Challenge
> "You're doing just an AI-powered IDS/IPS that tells what attack it is"

### Our Defense
We realized we had all the ammunition from Day 0:

1. **Original Proposal says:** "a system that doesn't just detect threats but learns to respond dynamically"
2. **A²C Framework:** We implement Automation-Augmentation-Collaboration
3. **DARPA CASTLE:** Same RL approach funded by DOD
4. **Alert Fatigue Crisis:** 51% of SOC teams overwhelmed (ACM 2025)

### Documents Created
- `DTRA_Defense_Strategy.md` - Complete rebuttal with citations
- `DTRA_Research_Roadmap.md` - 25-paper reading plan for publication

---

## 🧠 KEY DECISIONS LOG

| Decision | Why | Date |
|----------|-----|------|
| Hybrid AI (DNN+RF→DNN+XGB) | Ensemble beats single model for tabular data | Summer → Jan 2026 |
| A* → Q-Learning | Static rules < Adaptive learning | Progress III |
| No SMOTE | Real traffic unbalanced; honest accuracy | Jan 21, 2026 |
| Class Weights | Penalize missing rare attacks without fake data | Jan 21, 2026 |
| 5-layer DNN | 7 categories need more capacity | Jan 21, 2026 |
| Unique Packet IDs | Fix dashboard looping bug | Jan 21, 2026 |
| CIC-IIoT 2025 | Modern IoT attacks, realistic noise | Jan 20, 2026 |

---

## 📚 LESSONS LEARNED

### Technical
1. **Data > Model** - 70% of ML success is preprocessing
2. **Ensemble always wins** - DNN+XGB > DNN alone
3. **A* is dead, RL is king** - Adaptive learning beats static rules
4. **Save EVERYTHING** - Scaler, imputer, encoder, config, models
5. **Flush your prints** - `flush=True` saves debugging hours
6. **Test with unique IDs** - Prevents re-counting bugs

### Research
1. **Frame the problem** - "Alert fatigue" > "better detection"
2. **Cite or die** - Academic projects need literature backing
3. **Know your layer** - Detection vs. Decision is THE distinction
4. **Find your framework** - A²C gave us theoretical grounding

### Process
1. **Document as you go** - This journal is evidence
2. **Version your work** - v1/ and v2/ saved sanity
3. **Defend proactively** - Don't wait for criticism

---

## 📈 METRICS EVOLUTION

| Stage | Model | Accuracy | False Positives | Key Win |
|-------|-------|----------|-----------------|---------|
| Report II | LogReg | 94% | 788 | Baseline |
| Report III | DNN | 98% | 412 | 47% FP reduction |
| v1 Final | DNN+RF | 98.9% | - | Hybrid works |
| v2 | DNN+XGB (stacked) | 92.34% recall | - | Modern data + live |

---

## 🔮 WHAT'S NEXT

### Immediate (February)
- [ ] Read 3 core papers (Alert Fatigue, A²C, DARPA CASTLE)
- [ ] Create 1-page defense cheat sheet
- [ ] Add 80% workload reduction math proof
- [ ] Practice elevator pitch

### Short-term (March)
- [ ] Add SHAP to v2 dashboard
- [ ] Design validation experiment
- [ ] Write Related Work section

### Medium-term (April-May)
- [ ] Complete paper draft
- [ ] Run experiments
- [ ] FYP defense preparation

### Long-term (June+)
- [ ] Submit to IEEE INMIC or IBCAST
- [ ] National competition
- [ ] Consider journal publication

---

---

## 🔄 CRITICAL PIVOT: February 4, 2026
**Event:** Professor feedback on RL approach
**Status:** MAJOR DIRECTION CHANGE

### The Feedback (Honest Truth)

Professor's key points:
1. **"Q-Learning is VERY basic"** - Tabular Q-Learning is undergraduate-level RL
2. **"Everyone uses ML→Risk Score→RL pipeline"** - Our core architecture is common
3. **"RL agents need proper environment and continuous learning"** - We lack both
4. **"This approach is not defensible on panel"** - Need unique contribution

### Why Professor Is RIGHT ✅

| What We Have | Why It's Weak |
|--------------|---------------|
| Tabular Q-Learning | Can't handle continuous state spaces |
| Fixed 4 states | No generalization to unseen situations |
| Offline training only | No continuous adaptation post-deployment |
| Single agent | Can't scale to distributed networks |
| Invented reward function | Not learned from real analyst behavior |

### What State-of-Art Is Doing (2024-2025)

| Approach | What Papers Are Using |
|----------|----------------------|
| Deep Q-Network (DQN) | Neural net approximates Q-function |
| PPO / SAC | Policy gradient methods for continuous spaces |
| Multi-Agent RL (MARL) | DARPA AIxCC winners use this |
| Inverse RL | Learn reward from expert analyst behavior |
| Safe RL | Guarantee safety constraints on actions |
| Human-in-the-Loop RL | Incorporate analyst feedback into learning |

### The New Direction

**STOP IMPLEMENTING. START READING.**

Next 2 weeks focus:
1. Read 15-20 papers on RL for cybersecurity
2. Identify what everyone is doing vs. what's actually novel
3. Find a specific GAP we can fill
4. Redesign RL component based on research

### Potential Gap Areas (To Verify)

| Gap | Why It Might Be Novel |
|-----|----------------------|
| Human-in-the-loop RL for SOC | Analysts correct RL decisions → agent learns |
| Inverse RL from analyst logs | Learn reward from what experts actually do |
| Safe RL with formal constraints | Guarantee never blocks legitimate traffic |
| Continuous online learning | Agent improves during deployment |
| Hierarchical RL | High-level policy + low-level actions |

### Decision Made

- **Created:** `DTRA_Research_Papers.md` (18 papers prioritized)
- **Action:** Pause implementation, start literature review
- **Goal:** Find defensible unique contribution for FYP panel

### Lesson Learned

> "Don't guess at novelty. Read the papers. Know what's actually been done before claiming contribution."

---

## 📝 UPDATED: What's Next

### Immediate (February 4-18)
- [ ] Read Priority 1 papers (4 papers)
- [ ] Document gaps in reading template
- [ ] Identify top 3 potential novel directions

### Short-term (February 18-28)
- [ ] Read Priority 2 papers (4 papers)
- [ ] Decide on specific gap to target
- [ ] Design new RL approach

### Medium-term (March)
- [ ] Implement improved RL component
- [ ] Compare with current Q-Learning baseline
- [ ] Write literature review section

---

*Journal updated: February 4, 2026*

---

## 📁 SESSION: February 18, 2026
**Focus:** Admin + Project Rebranding

### Folder Restructure
- DTRA folder moved to `d:\GIKI\Semester 5\CS 351\DTRA\`
- Old path: `d:\GIKI\CS 351\DTRA\` → New path confirmed and verified
- All files intact: Journal, Research Papers, Masterclass Slides, v1/, v2/

### Senior Design Project (SDP) Registration
- Filling out GIKI SDP registration form (6th → 8th semester project)
- **Project Title drafted:** `[NAME]: Autonomous SOC Alert Triage Using Hybrid Deep Learning and Reinforcement Learning`
- **Summary drafted:** ~100 words, handwritten-friendly
- **SDGs mapped:** 8 (Decent Work), 9 (Industry & Innovation), 16 (Peace & Institutions)
- **Work Plan:** Term I = Literature + Baseline, Term II = Novel RL + Environment, Term III = Integration + Paper

### Project Renaming Decision
- **"DTRA" name dropped** — doesn't sound good enough for SDP
- Brainstormed 15 name candidates:

| # | Name | Full Form |
|---|------|-----------|
| 1 | ARIA | Autonomous Response Intelligence Agent |
| 2 | AURA | Autonomous Unified Response Agent |
| 3 | CORTEX | Cyber Operations Response & Threat EXecution |
| 4 | AEGIS | Adaptive Engine for Guided Incident Suppression |
| 5 | SENTRY | Self-learning ENgine for Threat Response & Triage |
| 6 | WARDEN | Workload-Aware Reinforcement Decision ENgine |
| ... | + 9 more | See naming session |

- **Decision:** Pending — coming back to finalize name

### Status
- [ ] Finalize project name
- [ ] Complete SDP form with final name
- [ ] Submit SDP registration

---

*Journal updated: February 18, 2026*
*Covers: Summer 2025 → February 18, 2026*

> **The Bottom Line:** We started with "let's solve alert fatigue with AI that DECIDES, not just DETECTS." Every step - from A* to Q-Learning, from Logistic Regression to Deep Ensemble, from CICIDS2017 to CIC-IIoT 2025 - moved us closer to that goal. Now entering SDP phase — same mission, stronger foundation, better name.

---

## 📁 SESSION: April 8, 2026
**Focus:** Deep architecture audit + RL redesign direction + project rename
**Team:** Daniyal (2023406) + Haider (2023416) + Daud (2023677) ← Daud joins the team

---

### Project Officially Renamed
- **Old name:** DTRA (Dynamic Threat Response Agent) — dropped
- **New name:** ARSS — **Autonomous Response System for SOC**
- Cleaner, more professional, accurately describes what the system does

---

### The Big Realization: What ARSS Actually Is

Had a full architecture review today. The fundamental clarification that changed everything:

**ARSS is not an IDS.** It never was. It sits here:

```
Raw Traffic → Firewall → IDS/IPS → SIEM → [ARSS] → Human SOC Analyst
```

IDS already does sequence analysis, signature matching, pattern detection. ARSS receives alerts that have already passed all upstream filters. Its job is **alert triage** — auto-handle what's obvious, surface only what genuinely needs human judgment.

This reframing clarified why the professor called the approach baseline. We were building a system to reduce analyst burnout, then spending all our research energy on the detection layer (which isn't the bottleneck). The bottleneck is the **decision layer**.

---

### The Core Flaw Identified

**The RL agent is optimizing for the wrong thing.**

Current RL: optimizes for "is this packet dangerous?" — which the ML already answered.

What it should optimize for: **"what action minimizes analyst interruption while maximizing threat containment?"**

Those are two competing objectives. The RL should be learning to balance that tradeoff. Right now it's just echoing the detector output dressed up as a decision.

**Two specific problems:**

1. **State space is too narrow** — agent sees `danger_bucket (0-9)`. Throws away attack category, confidence, everything Stage 2 produced. A MITM at 70% and a Recon scan at 70% get the same state. That's wrong.

2. **Reward function is invented** — rewards are hand-crafted based on danger level alone. Doesn't know that missing a MITM is catastrophically worse than missing a Recon. No grounding in real threat intelligence.

---

### The Redesign Direction

**New state space:**
```
State = [danger_score, attack_category (one-hot), category_confidence]
```
Agent now sees attack semantics, not just a risk bucket.

**New reward function — grounded in MITRE ATT&CK:**

| Attack Type | MITRE Tactic | Severity Weight |
|-------------|--------------|-----------------|
| MITM | Collection / Credential Access | 1.0 |
| Malware | Execution / Persistence | 1.0 |
| DDoS | Impact | 0.8 |
| DoS | Impact | 0.7 |
| Brute Force | Credential Access | 0.6 |
| Web Attacks | Initial Access | 0.5 |
| Recon | Discovery | 0.3 |

Reward is now tied to industry threat intelligence, not invented heuristics. Missing a MITM hurts 3x more than missing a Recon. That's the right optimization signal.

---

### New Feature Added: Cognitive Semantic Layer (Daud's idea ✅)

**Problem:** SHAP output is too technical for junior SOC analysts.

**Solution:** LLM (Gemini) receives SHAP values + RL action + attack type → generates a plain-English Tactical Incident Narrative.

**Example output:**
> "BLOCKED: Detected anomalous traffic on Port 445. Primary trigger: Flow Duration anomaly (SHAP). Pattern consistent with SMB-based lateral movement."

This stays in scope — it's still in the triage layer, translating technical output for the human analyst. Direct contribution to cognitive load reduction.

---

### Idea Evaluated and Rejected: Adversarial Noise Suppression Filter (Daud's idea ❌)

Denoising autoencoder before the detector to resist adversarial perturbations. Real concept, strong research backing. Rejected for now because:
- Detection layer isn't the professor's criticism — RL/approach is
- Needs a full red team evaluation to be credible in a paper
- Scope creep away from the core contribution

Moved to **Future Work.**

---

### The Training vs Deployment Realization

A key question came up: modern IDS/IPS already detect, classify, and block — so why do we have Stage 1 and Stage 2?

Answer: **they are a training utility, not the product.**

In real deployment, the SIEM already provides labeled, scored, typed alerts. You skip detection entirely and feed straight into the RL agent. Stage 1 and 2 only exist because we're working with a raw dataset (CIC-IIoT 2025) and need them to generate the enriched state vector the RL trains on.

```
TRAINING:    Raw Dataset → Stage 1 → Stage 2 → RL trains on enriched state
DEPLOYMENT:  SIEM Alert  → RL Agent → Action
```

The deployable artifact is a **lightweight trained RL policy** that plugs into any SIEM via API. No heavy detection engine. No re-inference. Just fast, explainable triage decisions on top of the SOC's existing infrastructure. That's the real product.

---

### Documents Created / Updated This Session
- `docs/DTRA_RL_Redesign_Thinking.md` — full write-up of redesign rationale, state space, reward function, training vs deployment split, and contribution statement
- `README.md` — rebranded to ARSS, updated architecture with Mermaid UML diagram
- GitHub repo renamed to `ARSS`

---

### What's Next
- [ ] Finalize MITRE ATT&CK severity weights for all 7 attack categories
- [ ] Decide: DQN or expanded Q-table?
- [ ] Find research papers backing category-conditioned state space
- [ ] Find research papers backing MITRE-grounded reward shaping
- [ ] Design LLM narrative prompt template (Cognitive Semantic Layer)

---

## 📁 SESSION: April 14, 2026
**Focus:** Literature review — commercial landscape + academic research on RL for SOC alert triage

---

### Literature Review: Commercial Landscape

Conducted a full sweep of commercial SOC/SOAR platforms (2022-2026).

**Finding: Nobody uses RL for alert triage. Confirmed.**

| Platform | Triage Approach |
|----------|----------------|
| Splunk SOAR | Rule-based playbooks |
| Palo Alto XSOAR | Rules + ML scoring |
| Microsoft Sentinel | Graph-based ML (Fusion) |
| CrowdStrike Charlotte AI | Supervised imitation learning + LLM |
| IBM QRadar | Rules + NLP enrichment |
| Dropzone, Exaforce, Prophet | LLM agents |

The entire 2024-2026 "Agentic SOC" wave converged on LLM multi-agent systems trained via supervised imitation learning — not RL. CrowdStrike Charlotte AI is trained on millions of real analyst triage decisions but it replicates past decisions, it can't discover better policies. RL as a triage decision mechanism is completely unclaimed in commercial deployments.

Gartner's 2025 capability list for AI SOC Agents does not mention RL at all. That's a citation.

---

### Literature Review: Academic Research (2022-2026)

Found 16 papers in the RL-for-cyber space. Key findings:

**Papers closest to ARSS:**

| Paper | Year | What They Do | Gap vs ARSS |
|-------|------|-------------|-------------|
| RADAMS (Huang & Zhu) | 2022 | RL to de-emphasize noisy alerts, models analyst attention | Doesn't take response actions — just dims alerts |
| AlertPro | 2024 | RL for context-aware alert prioritization | Ranking only, no Ignore/Log/Block/Isolate action space |
| L2DHF (Jalalvand et al.) | 2025 | RL to decide defer vs auto-close | Binary only, not multi-action response |
| SAC-AP / TD3-AP / KNAP | 2022-2024 | Actor-critic RL for IDS alert ranking | Prioritization only, no autonomous response |
| AACT (Secureworks) | 2025 | Supervised ML triage — 61% alert reduction in real SOC | Not RL, proves the problem is solvable |
| CORTEX | 2025 | LLM multi-agent triage | Not RL, expensive, non-deterministic |

**Key reference found:**
Jalalvand et al. (2025) ACM Computing Surveys — "Alert Fatigue in SOCs: Research Challenges" explicitly flags RL at the triage layer as underexplored. This is the authoritative citation for our problem statement.

---

### The Two Confirmed Gaps

**Gap 1 — Action space at SIEM layer:**
Every RL paper either ranks alerts or makes a binary defer/auto decision. Nobody has built an RL agent with a discrete 4-action response space (Ignore/Log/Block/Isolate) operating at the SIEM layer. ARSS is first.

**Gap 2 — MITRE ATT&CK in reward function:**
Zero papers found encoding MITRE ATT&CK severity weights into an RL reward function. Not in academic literature, not in commercial implementations. Completely unclaimed.

---

### 5 Must-Read Papers (Priority Order)

1. **Jalalvand et al. (2025)** — ACM Computing Surveys — "Alert Fatigue in SOCs" — foundational problem statement citation
2. **RADAMS — Huang & Zhu (2022)** — Computers & Security — closest prior work, must position against it
3. **AACT — Secureworks (2025)** — proves triage layer problem is real and ML-solvable, argue why RL is better
4. **L2DHF — Jalalvand et al. (2025)** — arXiv — HITL deferral RL approach
5. **AlertPro (2024)** — Computers & Security — RL for prioritization, distinguish from response

---

### What's Next
- [ ] Find IEEE/ACM published papers (in progress — search running)
- [ ] Read the 5 priority papers above
- [ ] Write formal literature review section for proposal
- [ ] Finalize MITRE ATT&CK severity weights
- [ ] Decide DQN vs expanded Q-table

---

### The Market Gap Clarity

Key question raised: if this problem is real, why hasn't the market solved it?

Answer: **The market solved detection. Nobody solved trust.**

CrowdStrike, Palo Alto XSOAR, Splunk SOAR — they all automate responses. But analysts routinely override them because they can't see the reasoning. A system that says "Blocked" with no explanation doesn't reduce burnout, it creates a different kind of anxiety. Analysts don't adopt what they don't trust.

| What Market Solved | What Remains Unsolved |
|--------------------|-----------------------|
| Detecting threats | Explaining why something was flagged |
| Automating responses | Justifying why that response was chosen |
| Aggregating alerts | Plain-English briefings for analysts |
| Blocking at scale | Building analyst trust in autonomous decisions |

ARSS fills the trust gap — explainable, MITRE-grounded, plain-English triage. Added a **Why ARSS** section to the README capturing this positioning.

---

*Journal updated: April 8, 2026*
*Covers: Summer 2025 → April 8, 2026*

> **The Bottom Line:** ARSS is the right name for what this actually is. Stage 1 and 2 are scaffolding — they train the RL, then step aside. The real product is the decision agent. Lightweight, fast, SIEM-pluggable, and explainable. The market solved detection. We're solving trust. Next session: papers.

---

## 📁 SESSION: July 19-20, 2026
**Focus:** Session recovery, literature integrity audit, IEEE paper drafting, bibliography expansion toward genuine 35-source coverage

---

### Context: Session Recovery

Previous Claude Code session for this project was lost. Rebuilt full context from scratch by reading every doc, the git log, and the actual v2 code — not just the docs' claims about the code. That distinction mattered: the docs describe a category-conditioned, MITRE-grounded DQN agent. The actual code (`v2/server/decider.py`, `api.py`) still runs the pre-February-pivot flat Q-learning, no trained Q-table exists, and `api.py` silently falls back to `Block if danger > 0.8 else Log`. Three months of research/planning docs, zero lines of the redesigned RL agent. This gap between "what's written" and "what's built" is now tracked explicitly rather than assumed away.

### The Adopted Process: Four Phases, Ported from the CY315 Project

Daniyal's CY315 (UA-SAC) project had already worked out a rigorous literature process across ~35 verified sources. Explicitly **not** reusing CY315's content or paper — only its structure, since this is separate research work. Reconstructed and adopted the same four-phase discipline:

**Phase 1 — Curation (before touching a single PDF).** Audit what's already in the bibliography first: orphan citations (never cited in body text), stale recency, mislabeled entries. Then search in themed buckets, each with a distinct job in the argument — not one generic sweep. For ARSS, the buckets are: RL-theory grounding for the reward (why worst-case/scalarized reward design is principled, not invented), recent DRL applications in the exact subdomain (SOC/SIEM alert response, 2022-2026), non-RL competitors solving the same problem (supervised triage, LLM-agent triage), MITRE ATT&CK + ML/RL integration beyond MITREtrieval, category-conditioned state-space precedent, and recent surveys for context.

**Phase 2 — Access.** Real PDF or verified abstract before anything is trusted — never a search-snippet summary taken at face value. Legitimate channels only: arXiv, ResearchGate request-a-copy, institutional library, direct author email. Never Sci-Hub or mirrors.

**Phase 3 — Reading and notes.** One paper at a time, full read before writing the entry, same rigor for old citations as new ones. Fixed fields: citation, link, source-read status (full PDF vs. abstract-only, always flagged honestly), what it does, core mechanism, its stated limitations and future work pulled from its own text, direct comparison to ARSS, and its specific job in the argument.

**Phase 4 — Cross-referencing.** Hunt each paper's own limitations/future-work language for sentences that hand you your gap. Check for contradictions against ARSS's own claims rather than let them sit unnoticed. Flag when a paper doesn't do what its citation implies.

**The qualifying bar for any candidate, regardless of phase:**
- Real first, no exceptions — verified venue, DOI, actual abstract, not a plausible-sounding summary.
- A specific, nameable job in the argument (competitor, theory grounding, recency signal, gap-filler) — if the job can't be named, it doesn't make the cut.
- Quality over hitting a target count. 35 is the CY315 benchmark, not a quota to pad toward.
- No redundant duplicates — a new candidate doing the same job as an existing citation needs a genuinely different angle to also qualify.
- Recency weighted deliberately when fixing a stale bibliography, but never recency for its own sake — still has to clear the "real job" bar.
- Confidence tracked and disclosed per source — abstract-only vs. fully-verified-read is marked every time, never smoothed over.

### What the Audit Found

Applied to ARSS's existing 11-13 source bibliography (assembled before this session, most likely during an earlier AI-assisted research pass that never verified sources against primary text), the audit found a real integrity problem, not a stylistic one:

- **Tariq et al. 2025** — the "4,484 alerts/day, 67% uninvestigated" statistic, repeated across the Development Journal, Literature Review, Research Findings, **and the already-signed scope document's Abstract and Problem Statement**, does not appear anywhere in the actual 38-page paper. Full-text search confirmed zero matches. Real reported figures: 51% of SOC teams overwhelmed (Trend Micro), 49% of alerts resolved in a workday (IBM).
- **RADAMS (Huang & Zhu 2022)** — the "95.89% recall, 5.86% FPR on 500K+ alerts" figure does not exist in the paper. It doesn't even report classification metrics; its actual result is "up to 20% IDoS risk reduction," a dollar-cost metric, in an Industrial Control Systems context the existing docs had also mislabeled as generic SOC.
- **SAC-AP (Chavali et al. 2022)** — cited as "16% reduction vs. DDPG," actual abstract says "up to 30%." Misquoted, not fabricated.
- **A2C framework** — the title in the bibliography, "Human-AI Teaming for Alert Fatigue: An A2C Framework Approach," does not match any real paper under its cited DOI. Replaced with the verified paper that actually defines A2C by name (Tariq et al., arXiv:2401.14432).
- **AACT** — informally attributed to "Secureworks" in the April 14 entry above; verified authors are affiliated with Sophos and Flare.
- **Finding 7 misattribution** — the Tariq et al. alert-volume quote was headed "Jalalvand et al. 2025" in the Research Findings doc, crediting the wrong author for the wrong paper.

Every one of these has been corrected in `ARSS_Literature_Review.md`, `ARSS_Research_Findings.md`, and the new `ARSS_Paper.tex`. The signed scope document itself was left untouched per direction — that correction is a separate decision involving the supervisor, not something to silently patch.

### The Paper: `docs/ARSS_Paper.tex`

Drafted a full IEEEtran conference-format paper, structurally mirroring CY315's paper (System Model with formal MDP math → Related Work → Proposed Methodology as three numbered layers with an algorithm block → Evaluation Plan → Conclusion). Explicitly no fabricated results — the Evaluation Plan section describes the protocol only, since the RL agent hasn't been implemented yet.

Two design corrections made mid-session, both substantive, not cosmetic:
1. **The SIEM-deployment claim was overclaimed.** The original framing — "in deployment, the SIEM supplies equivalent data directly, Stages 1-2 are not required" — doesn't survive scrutiny. A real SIEM does not natively export CIC-IIoT 2025's 71 flow-level statistical features, nor a continuous multi-class confidence score. Corrected to the honest version: Stages 1-2 move from a public-dataset feature space to a deployment-specific one, and live-SIEM schema adaptation is explicitly scoped as future work, not assumed solved.
2. **The reward function's business-disruption and analyst-cost terms are now grounded, not just plausible.** A 2026 paper (Safety-Contract Graph MARL) shows reward-only RL for autonomous network security response violates SOC operational budgets in 100% of tested episodes without exactly these kinds of terms — cited directly in Section IV as validation for why the dual-objective reward isn't a stylistic addition.

### Bibliography Growth: 18 → 24 (toward a 35 target)

Six new sources added this session, each read in full before being cited, not snippet-trusted:
- **L2DHF (Jalalvand et al. 2025)** — a DRLHF accept/defer agent, arguably the closest prior art now, closer than AlertPro, since its whole mechanism is the same accept/defer tradeoff the Log action encodes. Real results: 13-16%/60-67% accuracy gains, 98% fewer high-category misprioritizations.
- **AACT (Turcotte, Labrèche, Paquette 2025)** — supervised imitation-learning triage, real 6-month SOC deployment, 61% alert reduction, 1.36% FN rate.
- **CORTEX (Wei et al. 2025)** — multi-agent LLM triage, non-RL competitor.
- **SoK: MITRE ATT&CK (Roy et al. 2023)** — systematization review confirming no ATT&CK-to-RL connection exists in the broader literature either.
- **ARCS (Ren et al. 2025)** — RL for incident-response strategy selection, one layer downstream of triage.
- **Safety-Contract Graph MARL (Silva 2026)** — the reward-only-RL-breaks-constraints finding above.

### Open Items

- **Homayoun 2026** ("Risk-Aware SOC Alert Handling... Reinforcement Learning," ESORICS workshops) — the single most contemporary and closest-sounding paper found. Reward encodes "threat criticality, confidence, and isolation cost" — structurally close to ARSS's own design. Abstract confirmed real; full technical content (state/action space, MITRE grounding or not) still unverified. ResearchGate request-a-copy sent, not yet accepted. This is the one open item that could require repositioning the paper's contribution claim, not just adding a citation.
- **TD3-AP, KNAP, Multi-Critic, AlertPro, Homayoun** — confirmed paywalled on both IEEE and the checked institutional library access; four of the five actually live on Elsevier ScienceDirect or SpringerLink, not IEEE, so IEEE-only access won't reach them. DOIs logged above for whoever has broader access to try.
- Reward function coefficients ($\lambda_{\text{miss}}$, $C_{\text{analyst}}$, $C_{\text{biz}}$) are still placeholders pending a real design pass.
- 11 more sources needed to reach the 35 benchmark, without padding — search continuing.

---

*Journal updated: July 20, 2026*
*Covers: Session recovery through ongoing literature verification pass*

> **The Bottom Line:** The idea survived two rounds of professor scrutiny and is genuinely sound. What hadn't survived scrutiny was the paperwork underneath it — several load-bearing citations were wrong, one was fabricated outright, and the actual RL agent the whole paper describes doesn't exist in code yet. This session's work isn't glamorous, but it's the actual floor a real submission stands on. Verify before you build on it.

---

## 📁 SESSION: September 19, 2026
**Focus:** Session recovery (again) + title defense date locked + full document audit

---

### Title Defense Date Set

Title defense presentation scheduled for **~September 28, 2026** (one week out from this session). Marking rubric incoming from the team, not yet reviewed.

### Full Context Re-Grounding

Prior Claude Code session was lost again. Rebuilt context by reading every doc in the repo end to end this time, not just `docs/` — root-level files too: `README.md`, `DTRA_Masterclass_Slides.md`, `DTRA_NotebookLLM_Prompt.md`, `DTRA_Research_Papers.md`, `DTRA Story.pdf`, `Scope Documents.pdf`, `SDP - Scope Document - Sample.pdf`, and the root export of the scope document. Confirms: last real research session was July 19-20, 2026 (literature verification). Nothing in the codebase or docs indicates any work happened between July 20 and this session.

### Finding: The Signed Scope Document Still Contains the Fabricated Citations

The July 19-20 session found and corrected a fabricated statistic and several wrong citations (Tariq et al. "4,484 alerts/day, 67% uninvestigated" — doesn't exist in the source paper; RADAMS "95.89% recall, 5.86% FPR" — doesn't exist in that paper either; the A2C bibitem pointing at a non-existent paper) — but explicitly left `docs/ARSS_Scope_Document_v2.md` untouched, on the reasoning that correcting an already-signed document is a supervisor-level decision, not something to silently patch.

Confirmed this session by re-reading `docs/ARSS_Scope_Document_v2.md` directly: it still contains, uncorrected —
- Table 1, row 6: "4,484 alerts/day, 67% uninvestigated" (the fabricated stat)
- Table 1, row for RADAMS: "95.89% recall on 500K+ alerts" (the fabricated stat)
- Reference [8]: the A2C bibitem with the wrong title/DOI pairing

This is the document that was actually signed (`Fawad Sign.pdf`, dated the same day as the docx/pdf export, Apr 20) and submitted to the department. It has not been corrected. This is a live risk for the title defense: if a panelist cross-checks any of these three numbers against the cited source, they won't find them. The team needs to decide — before Sept 28 — whether and how to address this with the supervisor (Dr. Muhammad Fawad Khan), since the corrected versions already exist in `ARSS_Literature_Review.md`, `ARSS_Research_Findings.md`, and `ARSS_Paper.tex`.

### Secondary Finding: Bibliography Further Along Than Journal Recorded

`ARSS_Paper.tex` was saved 6 minutes after the July 20 journal entry was finalized, and already has **29 verified bibitems** — more than the "18 → 24, toward 35" the journal entry describes. Six additional sources (SoK Pitfalls in DRL-for-Cybersecurity, Multi-Objective RL critique, MITRE+RL attack-sim paper, a 2026 alert-fatigue survey covering 119 records, MARL-in-cybersecurity survey, Gartner 2026 trends) are in the `.tex` bibliography but were never logged in the journal text. Journal text and actual file state had drifted apart — noted here per the standing instruction to reconcile rather than just append.

### Confirmed Still Open (carried over from July 20, unchanged)

- Homayoun 2026 — ResearchGate request still pending, not yet verified beyond abstract.
- TD3-AP, KNAP, Multi-Critic, AlertPro — still paywalled, DOIs logged for broader-access retrieval.
- Reward coefficients ($\lambda_{\text{miss}}$, $C_{\text{analyst}}$, $C_{\text{biz}}$) — still placeholders.
- Zero lines of the redesigned RL agent exist in code (`v2/server/decider.py` unchanged).
- `ARSS_Paper.tex` has never successfully compiled — `IEEEtran.cls` missing locally (per `ARSS_Paper.log`, July 10 attempt).

### Mid-Session Correction: MITREtrieval Title Was Wrong (Caught by Haider)

While verifying the Homayoun 2026 paper's venue, Haider flagged that the MITREtrieval citation looked off. Checked it directly: the DOI (`10.1109/TNSM.2024.3401200`), IEEE Xplore document ID (`10539631`), journal/volume/issue, and author list were all already correct everywhere it's cited — but the title text was a paraphrase, not the real published title.

- **Recorded (wrong):** "MITREtrieval: Fusing BERT with MITRE ATT&CK Ontology for TTP Extraction from Threat Reports"
- **Actual (verified against IEEE Xplore, ACM DL, ResearchGate, and two university research-portal listings for the authors):** "MITREtrieval: Retrieving MITRE Techniques From Unstructured Threat Reports by Fusion of Deep Learning and Ontology" — same DOI, same paper, just mistitled.

Fixed in `ARSS_Paper.tex`, `ARSS_Research_Findings.md`, and `ARSS_Literature_Review.md`. Left `ARSS_Scope_Document.md` (v1, historical) and `ARSS_Scope_Document_v2.md` (signed) untouched, same rule as the July 19-20 corrections — the signed document doesn't get silently patched. This is now a fourth item on the list to raise with Dr. Khan, alongside the fabricated alert-volume stat, the RADAMS figure, and the A2C mismatch.

**Pattern worth noting:** every citation-integrity error found across both sessions has been a paraphrased/fabricated *title or figure* sitting on top of an otherwise-correct DOI and link. Worth spot-checking the remaining ~25 bibliography entries' titles verbatim against their DOIs at some point, not just trusting that a correct DOI implies a correct title.

### What's Next

- [ ] Review the marking rubric once shared and align prep priorities to it
- [ ] Team decision: how/whether to flag the signed scope document's uncorrected citations to the supervisor before Sept 28 (now 4 items: alert-volume stat, RADAMS figure, A2C mismatch, MITREtrieval title)
- [ ] Decide defense talking points given the paper has no implementation results yet — evaluation plan only
- [ ] Continue toward 35-source literature benchmark if time allows before the defense
- [ ] Consider a verbatim title-vs-DOI spot check across the rest of the bibliography

---

*Journal updated: September 19, 2026*
*Covers: July 20, 2026 session recovery through title defense date confirmation*

> **The Bottom Line:** One week to title defense. The research case is strong and well-documented, but the signed scope document still carries the citation errors that were caught and fixed everywhere else. That gap needs a decision, not just a note — before the panel finds it first.

---

## 📁 SESSION: September 20, 2026 (continued)
**Focus:** Literature search expansion, RL refresher materials, GitHub sync

---

### Literature Search Agents

Ran two parallel background searches for 2024-2026 papers, quality-filtered against the standing bar (real, verified, specific job in the argument, no padding). One completed with 13 new candidates plus a full Homayoun 2026 deep-dive; a second, independent run was still pending as of this entry and should be reconciled against the first when it lands.

**Homayoun 2026 resolved.** Full abstract retrieved and cross-verified across 3 independent sources. Confirmed: algorithm is plain PPO, reward is explicitly "threat criticality + confidence + isolation cost" — **not MITRE ATT&CK-grounded**, straight from the authors' own abstract. State space and action space remain unrecoverable from any open source (Springer/ACM DL paywalled) — a hard blocker, not a search failure. ARSS's novelty gap on category-conditioned state space and the 4-action response space survives untouched against this paper; only the reward-taxonomy differentiator is currently provable.

**13 new candidates found**, not yet added to the bibliography — logged with full detail in the new `ARSS_Literature_Session_Notes.md` rather than repeated here. Notable: a "Beyond Rewards in RL for Cyber Defence" paper that argues *for* sparse rewards (a real counterpoint to engage with, not just cite favorably), and DRL-MD (RL + MITRE ATT&CK, but for mitigation-deployment planning, not per-alert triage — a "the combination exists, just not for our problem" citation).

### Two New Reference Documents Created

1. **`docs/ARSS_RL_Concepts_Primer.md`** — a from-zero RL vocabulary refresher (MDP, Q-values, tabular vs. deep Q-learning, actor-critic/PPO/SAC/TD3, on/off-policy, reward shaping, MITRE ATT&CK basics), written after the team realized they'd lost most technical RL recall after the months-long gap and needed to be able to read a paper abstract and actually understand it. Every concept is tied back to ARSS's own specific design choices, not left generic.
2. **`docs/ARSS_Literature_Session_Notes.md`** — the raw working notes behind the literature review: status snapshot, verification-depth breakdown, the Homayoun deep-dive, the MITREtrieval correction reasoning, and the new candidate list. Deliberately kept separate from the polished `ARSS_Literature_Review.md`/`ARSS_Research_Findings.md` — this is the "how we got there," not the citation-ready output.

### `brag` Skill Installed

Installed the `brag` Claude Code skill (github.com/latent-spaces/brag) into `.claude/skills/brag/` — generates short launch-style promo videos via Hyperframes, not slide decks (flagged this distinction before installing; team confirmed they wanted it anyway). Note: this machine has no Node.js, npx, or FFmpeg on PATH — the skill files are in place, but the actual render pipeline needs that toolchain set up before `/brag` can run.

### GitHub Sync

Found that **months of local documentation had never been pushed** — `ARSS_Paper.tex`, the signed `ARSS_Scope_Document_v2.md`, the Masterclass slides, the Research Papers list, the NotebookLLM prompt doc, the related-work table, both downloaded literature PDFs, and the defense/story PDFs were all sitting locally, untracked, alongside one already-committed-but-unpushed doc addition from April 15. Committed a curated set (listed in the commit itself) and pushed to `origin/main` so Haider and Daud can actually access current state.

**Deliberately excluded from this push, flagged rather than silently included:**
- `v2/models/*.h5`, `*.pkl` — showed real content changes (`dtra_categorizer.h5` grew from 789KB to 3.4MB) with no session context explaining why. Left as local uncommitted changes rather than guessing whether this was an intentional retrain.
- `Fawad Sign.pdf` — contains the supervisor's actual signature; sensitive, not pushed without explicit confirmation.
- `Scope Documents.pdf`, `SDP - Scope Document - Sample.docx/pdf` — reference/template material, not ARSS's own content (`Scope Documents.pdf` is literally a different team's SDP).
- `~$SS Scope Document .docx` — a Word lock/temp file, never worth tracking.
- `docs/ARSS_Paper.log` — a failed local LaTeX compile log, diagnostic noise, not source content.

### What's Next

- [ ] Reconcile the second (pending) literature-search agent run against the first once it completes
- [ ] Decide which 5-6 of the 13 new candidates actually get added to the formal bibliography
- [ ] Team decision on `Fawad Sign.pdf` and the model file changes — both left out of today's push pending input
- [ ] Everything carried over from the Sept 19 entry above (rubric review, signed-doc correction decision, defense talking points) still stands

---

*Journal updated: September 20, 2026*

---

## 📁 SESSION: September 21, 2026
**Focus:** Verifying the 13 candidate papers — real DOIs and arXiv links, no guessing

---

### All 13 Candidates Independently Re-Verified

The first agent's stopped/cancelled run from the previous session was confirmed dead (explicitly stopped, not resumable — the second parallel run from Sept 20 already covered the same ground, so nothing was actually lost). Ran a fresh, targeted verification pass on the 13 candidate papers found Sept 20: for each one, confirmed the verbatim title, full author list, real DOI (via Crossref API where applicable), and real arXiv link (via direct arXiv API queries, not web-search summaries) — or confirmed genuinely no arXiv preprint exists, checked by querying the arXiv API directly rather than assuming absence from a search result.

**Final tally:** 1 of 13 has both a DOI and an arXiv preprint (#6, the ACM TOIT paper). 4 have a DOI but no arXiv version exists at all (#1 Okafor 2026, #7 AlertSAGE, #8 the RL-for-network-security survey, #9 DRL-MD) — all four confirmed arXiv-absent by direct API query, not inferred from a missed search. 8 are arXiv preprints with no publisher DOI yet (expected — several are recent 2026 submissions still pending venue acceptance).

**Two discrepancies flagged, not silently fixed** (same discipline as every prior integrity pass):
- Paper 6's arXiv-listed title reads "Human AI Collaboration," no hyphen — task input had "Human-AI." Very likely a typographic variant of the ACM-published form (authors/DOI/abstract all match exactly), but left unresolved rather than assumed.
- Paper 8's title is stored in sentence case on Crossref/ScienceDirect ("network security," "comprehensive" lowercase) vs. title case as given — same likely-benign-formatting caveat, flagged rather than normalized.

**One unresolved gap:** AlertSAGE's (#7) authors are recorded as initials-only everywhere searched, including Springer's own chapter page — full given names could not be recovered from any source.

Full table with every link: given directly to the team in-session; not yet copied into `ARSS_Literature_Session_Notes.md` as a permanent record — worth doing before these details are needed again.

### What's Next

- [ ] Copy the verified 13-paper table (with DOIs/arXiv links) into `ARSS_Literature_Session_Notes.md` as the permanent record
- [ ] Decide which 5-6 of these actually earn a spot in the formal `ARSS_Paper.tex` bibliography
- [ ] Resolve the two flagged title discrepancies (#6, #8) before citing either formally — quick confirms, not blockers
- [ ] Everything else carried over from Sept 20 (rubric, signed-doc decision, `Fawad Sign.pdf`, model file changes) still stands

---

*Journal updated: September 21, 2026*
*Covers: literature search expansion, RL primer, GitHub sync*

> **The Bottom Line:** The team can now actually read a paper abstract and know what it's claiming — that was the missing piece, not more papers. Homayoun's reward-taxonomy gap is confirmed and citable; its state/action space stays an open question behind a paywall. Everything that existed only on one laptop for months now lives on GitHub too.

---

## 📁 SESSION: September 21, 2026 (continued)
**Focus:** Closing the "never independently re-verified" gap on the 4 legacy Chavali/Wang citations

---

### The Most Serious Citation Error Found on This Project So Far

Ran a dedicated deep-verification pass on SAC-AP, TD3-AP, KNAP, Multi-Critic, and AlertPro — the five papers that had been cited on trust from the original, since-proven-unreliable April 2026 compilation and never independently re-checked, despite two prior integrity audits fixing errors everywhere else.

**TD3-AP's DOI was simply wrong — not mistitled, wrong.** The DOI recorded everywhere in this project (`10.1016/j.cose.2024.103893`) resolves, per Crossref, to a completely unrelated paper by different authors on a different topic (an intrusion-classification methodology comparison by Bingu et al.). The correct DOI is `10.1016/j.cose.2024.103854` — almost certainly a single-digit transposition typo (893 vs. 854) made once, early, and copied forward into every document since without anyone clicking through. This is categorically worse than the prior title/figure errors: a title paraphrase is a paraphrase, but a wrong DOI sends a reader — including a panelist — to a stranger's paper entirely. Corrected in `ARSS_Paper.tex`, `ARSS_Literature_Review.md`, `ARSS_Research_Findings.md`.

**AlertPro was substantially mistitled**, not just paraphrased loosely. Real title (three-way confirmed via Crossref, Semantic Scholar, and dblp): "Combating alert fatigue with AlertPro: Context-aware alert prioritization using reinforcement learning for multi-step attack detection." What was recorded — "AlertPro: Context-Aware Reinforcement Learning for Alert Prioritization" — dropped both the paper's actual framing and its actual technical scope (multi-step attack detection specifically, not generic alert prioritization). Corrected everywhere, full author list corrected from "et al." too.

**KNAP and Multi-Critic both had real, if less severe, title errors** — both missing their real subtitles ("...to Prioritize Alerts Generated by Intrusion Detection Systems" / "...in Intrusion Detection Systems"). Corrected. **KNAP also has an open, unresolved concern**: this paper's own text describes it as improving "sample efficiency," but secondary sources (primary abstract still paywalled — Springer login wall) describe its actual headline contribution as three defender-knowledge-level variants (D-/S-/T-KNAP) with specific loss-reduction percentages — a possibly different framing than "sample efficiency." Flagged in all three docs as needing a primary-text recheck before the paper's Section III language is finalized, not silently rewritten on unconfirmed secondary information.

**SAC-AP came through cleanest** — correct DOI, correct authors, and its 30%-vs-DDPG claim was confirmed directly from Semantic Scholar's primary abstract field (not a snippet). Only a minor title-prefix correction needed ("SAC-AP:" was dropped).

**A structural note for future sessions:** primary abstract text was blocked on 4 of the 5 papers this pass — SpringerLink's explicit login wall for KNAP and Multi-Critic, ScienceDirect's HTTP 403 for TD3-AP and AlertPro. All quantitative performance figures for those four (dataset lists, percentage improvements) are currently **search-snippet corroborated only**, not primary-text confirmed, and are flagged as such inline in the docs. Getting real institutional/library access to pull these four PDFs directly remains an open task — the titles/DOIs are now solid, but the specific numeric claims attributed to them in ARSS's own paper aren't yet independently confirmed at the same standard as everything else.

**Signed document impact:** `ARSS_Scope_Document_v2.md` still carries the old wrong TD3-AP DOI and the old mistitled AlertPro citation — left untouched per the standing rule. This brings the signed-document correction list to **6 items**: fabricated alert-volume stat, fabricated RADAMS figure, A2C citation mismatch, mistitled MITREtrieval, wrong TD3-AP DOI, mistitled AlertPro.

A second, parallel task — checking whether any of the 16 unpublished-preprint citations have since been published, and searching for genuinely published alternatives to reduce reliance on preprints — was launched alongside this one and is still pending as of this entry.

### What's Next

- [ ] Reconcile the pending preprint-reduction agent run once it completes
- [ ] Get real institutional access to KNAP, Multi-Critic, TD3-AP, and AlertPro's primary PDFs to confirm the still-snippet-only quantitative claims
- [ ] Resolve KNAP's "sample efficiency" vs. "defender-knowledge-level variants" framing question against primary text
- [ ] Signed document now has 6 items needing a supervisor conversation before Sept 28 — this list keeps growing and needs an actual decision, not just tracking
- [ ] Everything else carried over from earlier Sept 21 entry still stands

---

*Journal updated: September 21, 2026 (continued session)*

> **The Bottom Line:** The "never re-verified" pile is the pile that actually mattered most — a wrong DOI is a worse failure mode than a wrong title, because it doesn't just misdescribe a real source, it points the reader at someone else's paper entirely. That's fixed now. What's still open is real institutional access — four papers' actual numeric claims are still resting on search snippets, not primary text, and that gap won't close without a library login, not another search pass.

---

## 📁 SESSION: September 21, 2026 (professor practice-defense session)
**Focus:** Real, hard questions from the supervisor — working out genuinely defensible answers, not rehearsed ones

---

### Context

The team brought back five real questions the professor asked in a practice/clarification session, each aimed at a specific soft spot: the dataset choice, the "novelty" of the action space, the choice of RL over supervised ML, the word "design" applied to the state space, and the overall novelty statement. Worked through each one properly rather than defending the existing framing reflexively — two of the five (the action-space claim and the "design the state space" wording) turned out to have a real, fair criticism underneath that's worth fixing in the actual materials, not just answering around.

### Q1 — Dataset justification

Settled answer: CIC-IIoT 2025 chosen because (a) confidentiality is why the whole field uses lab-generated benchmarks instead of real company data — not unique to this project; (b) it comes from the Canadian Institute for Cybersecurity (UNB), the same group behind CICIDS2017/CIC-IDS2018/CIC-IoT2023, giving a track record of consistent, credible methodology; (c) it's the most current IoT-relevant public option — KDD99/NSL-KDD are now considered outdated/methodologically weak citations, CICIDS2017 predates modern IoT attack patterns; (d) it matches the exact same class of dataset every cited competitor paper already uses (TD3-AP: MQTT-IoT-IDS2020, DARPA 2000, CSE-CIC-IDS2018) — comparable footing, not a workaround.

### Q2 — "IDS/IPS already take these actions — what's novel?"

**This one required a real concession first.** If the pitch is "we invented new actions," that's wrong and deserves the pushback it got — IPS already blocks, SOAR already automates via playbooks. The corrected claim: the four actions (Ignore/Log/Block/Isolate) aren't novel, but *what decides which one fires* is — a policy trained from outcomes vs. a static rule or hand-written playbook that never changes unless a human edits it. Landed on a clean analogy for the room: any thermostat can turn on the heat; the interesting part is what decided *when*, not the action itself. **Action item:** never again phrase the pitch as "new actions" — always "new decision mechanism, existing action vocabulary."

### Q3 — "Why RL when any ML model recognizes patterns well?"

Worked out the actually-correct, non-hand-wavy answer: classifying attack type has ground-truth labels available at training time; choosing the *right response* doesn't — its correctness is only knowable later, from the outcome, which no dataset can label in advance. Supervised learning needs an instant correct-answer label and simply cannot represent that delayed-consequence structure, regardless of pattern-recognition quality. The "just label what analysts would do" alternative is imitation learning, which hits the already-established Charlotte AI ceiling (replicates historical decisions and their biases, cannot discover better ones). This is the one-sentence answer to memorize verbatim, not reconstruct live in the room.

### Q4 — "State spaces are always there — how can you 'design' one?"

**A fair, technically correct catch, partially conceded.** The true underlying state of a live network is real and not invented by anyone. What ARSS actually builds is a **state representation** (or observation) — a chosen, finite slice of that much larger reality, handed to the agent as input. Every applied RL system makes this same choice; it's legitimate, standard practice, just not correctly named in the current materials. **Action item:** replace "design the state space" with "design the state representation" / "define the observation space" across slides and the paper — a small wording fix that removes a real objection entirely.

### Q5 — Novelty isn't convincing as currently stated

The hardest one. Professor is right that listing three differences reads as a checklist, not an argument, and doesn't answer "why does anyone care." Also directly asked: if an active research chain (SAC-AP → TD3-AP → KNAP → Multi-Critic → AlertPro → RADAMS → L2DHF → Homayoun, 2022-2026) already exists, how is this novel?

**Reframe worked out this session:** the chain's existence isn't evidence against novelty — it's evidence the problem is real and has had sustained expert attention, which makes a gap that survived six-plus iterations across four years *more* significant, not less. The fix is presenting one underlying mechanism with three symptoms, not three independent bullet facts: every existing system either (1) doesn't know enough (collapses attack type into one risk number, so a Recon scan and a Credential-Access attack at the same score are indistinguishable to the agent), (2) trusts an ungrounded signal (an invented, uncheckable reward), or (3) never finishes the decision (outputs a ranking, leaves the actual call to a human). ARSS's three design choices are the direct, causal repair for each specific symptom, not three unrelated differences. **Action item:** rewrite the novelty section of the paper and defense slides around this causal framing before Sept 28 — the current "three things together" phrasing needs to go.

### What's Next

- [ ] Rewrite the novelty statement (paper + slides) around the "one mechanism, three symptoms" framing
- [ ] Fix "design the state space" → "design the state representation" everywhere it appears
- [ ] Rework the action-space slide to lead with the concession (same actions, different decision mechanism) rather than implying new actions
- [ ] Memorize the Q3 (why RL) answer verbatim — it's precise and shouldn't be reconstructed live under pressure
- [ ] Everything carried over from the Sept 21 continued-session entry still stands

---

*Journal updated: September 21, 2026 (professor practice-defense session)*

> **The Bottom Line:** Two of these five questions weren't just hard to answer — they were right. The action-space claim was overstated and the state-space wording was imprecise, and both are now fixed at the source rather than argued around. The other three needed sharper, more causal reasoning, not new facts — everything needed to answer them was already true, it just wasn't argued well yet. That's the difference between having done the work and being able to defend it.

---

## 📁 SESSION: September 23, 2026
**Focus:** A major architectural realization — Block/Isolate as raw enforcement actions may be the wrong layer entirely

---

### The Realization

After a conversation with friends and the supervisor, the team identified a real architectural problem: Block and Isolate, as ARSS's action space, are **enforcement-layer** actions (executed against live network traffic or a live device), not naturally **alert-triage-layer** decisions (deciding what to do with an alert given limited analyst attention). The two layers had been conflated since the April redesign.

**One nuance worth recording precisely, since the initial framing overstated it slightly:** it is not literally true that "an alert can never lead to an action" — real SOAR platforms already trigger enforcement (isolate via EDR API, block via firewall API) from an alert, so that mechanism does exist in practice. The sharper, more defensible version of the realization: the *natural* job at the alert-triage layer is allocating scarce human analyst attention — prioritize, escalate, defer, dismiss, request enrichment — not deciding raw network actions. This reframing has real strength behind it independent of the discomfort that prompted it: every piece of prior work ARSS is already positioned against (RADAMS, AlertPro, SAC-AP/TD3-AP/KNAP/Multi-Critic, L2DHF, Homayoun) is already, at its core, about attention/priority allocation, not enforcement. Moving ARSS onto that exact ground both fixes the layer-conflation problem and sidesteps the recurring "isn't this just IDS/IPS" criticism by construction, since human-analyst attention allocation isn't something IDS/IPS/EDR do at all.

**New candidate framing, explicitly NOT yet confirmed as the gap:** adaptive decision-making for alert triage under analyst capacity limits — routing/prioritization that responds to current analyst backlog and workload, not just to properties of the alert itself. Team's own explicit standing principle going forward: **problem first, method second** — RL stays a candidate mechanism, not a forced conclusion; if a different technique (bandits, queueing theory, scheduling, supervised ranking) turns out to be the natural fit once the problem is actually understood, that's the honest outcome to follow, not a result to avoid.

**Scope constraint stated explicitly by the team:** whatever gets proposed needs to be substantial enough to justify three people working for one year — not a narrow idea stretched thin to look like a full FYP.

### Research Launched (evidence-gathering before any decision)

Two agents launched in parallel, both explicitly instructed not to presuppose RL or any conclusion:
1. **Commercial + open-source SIEM/SOAR survey** — what Splunk, Microsoft Sentinel, IBM QRadar, Cortex XSOAR, Google SecOps, CrowdStrike, Elastic Security, Wazuh, TheHive+Cortex, Security Onion, Graylog, and Shuffle actually take as input for alert decisions, whether any of them incorporate analyst feedback or adapt over time, and specifically whether any explicitly model analyst capacity/workload as a decision factor.
2. **Fresh 2025-2026 literature search** — specifically hunting for work framing alert triage around analyst capacity/workload as a first-class factor, and any non-RL methods (bandits, queueing theory, scheduling) already applied to this exact problem, to genuinely test whether RL is the right tool or just the one already in hand.

Both pending as of this entry.

### Timeline Tension (flagged, not resolved)

Title defense is ~September 28 — five days from this entry. A genuine re-scoping of the core research problem this close to a defense is high-stakes. Two live possibilities, not yet decided by the team: present this as a validated direction with an honest account of the live course-correction, or attempt to fully lock a new problem statement before the 28th. Needs a decision once the research above lands, not before.

### What's Next

- [ ] Reconcile both research agents once they land — do NOT decide the new framing until real evidence is in
- [ ] Team decision on the timeline question above, once the evidence is in
- [ ] If the analyst-capacity framing holds up: redefine the action space around triage decisions (prioritize/escalate/defer/dismiss/request-context) rather than enforcement primitives, and redo the novelty statement, system model, and MITRE-grounding argument accordingly — this would be a substantial rewrite of `ARSS_Paper.tex`, not a patch
- [ ] Everything from the Sept 21 practice-defense session (novelty reframing, state-representation wording, action-space concession) still stands as guidance regardless of how this resolves, since those lessons apply to whatever the final framing turns out to be

---

*Journal updated: September 23, 2026*

> **The Bottom Line:** This is the first time the pivot instinct has been "stop and gather real evidence before deciding" rather than "argue harder for what we already built" — that's a more mature research posture than anything that came before it, independent of how the evidence actually lands. Five days to defense makes this genuinely risky timing, and that risk is being named here rather than ignored.

---

## 📁 SESSION: September 23, 2026 (continued — both research agents landed)

---

### Consolidated Findings

Both agents launched earlier this session are back. Notably, they converged independently on the same core prior art (the Shah et al. / Ghadermazi lineage) without any cross-visibility into each other's work — a real consistency signal, not a coincidence to dismiss.

**Commercial/open-source platform survey (13 platforms checked directly against real docs — Splunk, Microsoft Sentinel, IBM QRadar, Cortex XSOAR, Google SecOps, CrowdStrike, Elastic Security, Wazuh, TheHive+Cortex, Security Onion, Graylog, OSSIM/AlienVault, Shuffle):**
- **No platform's triage-decision logic (priority/escalation/disposition) responds to current analyst backlog.** Confirmed, not assumed, across all 13.
- **The one real, shipped counterexample to have an answer ready for:** Cortex XSOAR's `less-busy-user` assignment mode is genuinely workload-aware — but it decides *who* handles a case, not *what happens* to the alert. Routing, not triage. Precise distinction to keep sharp if challenged.
- Feedback loops are almost universally manual everywhere checked (a human edits rules/thresholds after the fact) — no automatic self-updating scoring loop found in any core product.
- TheHive's own vendor (StrangeBee) explicitly names capacity as the core problem ("42% of alerts go uninvestigated simply due to capacity constraints") but their answer is better manual tooling, not an automated capacity-aware decision engine.
- **Correction worth keeping:** Homayoun's "isolation cost" reward term most likely refers to enforcement-action cost, not analyst bandwidth — probably not capacity-aware at all, despite surface-level similarity to the new framing. Don't conflate these going forward.

**Fresh 2025-2026 literature search:**
- "Capacity-aware alert triage" in general is **not** novel — Shah et al. (2019, operations research/MIP) and Ghadermazi et al. (2024, ACM Digital Threats, ML + mixed-integer optimization) already put analyst capacity directly into the triage decision. Neither uses RL. This needs to be cited and positioned against honestly, not treated as untouched ground.
- The narrower, still-open claim, independently confirmed by both agents: **a policy — RL or otherwise — that adapts triage decisions to real-time, live backlog changes, validated beyond a simulated queue.** A 2026 survey (arXiv 2605.08316) names this gap explicitly in its own words. Zero bandit-based attempts found anywhere. No RL paper found that conditions on live backlog as a state variable.
- Even the best deployed industrial non-RL system checked (Microsoft's Adaptive Incident Prioritization, real production scale) does not model capacity either — this gap isn't just an academic blind spot.

### Critical Unresolved Item — highest priority before anything gets locked into the paper

Several load-bearing sources were only reached at abstract/snippet level on both agents' attempts, blocked by paywalls: **Ghadermazi et al. 2024 (ACM Digital Threats, DOI 10.1145/3644393), both ACM Computing Surveys papers (Jalalvand 2024, Tariq 2025 — likely already in the existing bibliography, needs a direct check for overlap, not assumed new), and a GMV CERT/SOC "learning to rank for alert triage" study.** These sit directly under the new central claim. Full-text verification of these three is now the single highest-priority action item — not optional, not deferrable, given how much of the new framing leans on them.

### Recommendation Given the Timeline

Not a full rebuild. The verified parts of the existing design — category-conditioned state, MITRE-tactic-severity reward grounding, the existing literature positioning — don't need to be discarded. The precise, achievable fix: redefine the action space away from raw enforcement (Block/Isolate) toward genuine triage-layer decisions, and add live analyst-backlog as a state input the policy conditions on. An evolution of the existing verified work, not a restart from zero — realistically achievable to articulate by Sept 28, unlike fully verifying three paywalled sources and rewriting the whole novelty argument from scratch in five days.

For the defense itself: presenting this as the live, honest research process it actually was — a real architectural problem identified, real evidence gathered across 13 platforms and fresh literature, here's exactly where it lands and what's still unverified — is the safer and arguably stronger move than presenting a five-day-old, partially-unverified narrow claim as fully settled fact.

### What's Next

- [ ] Get full-text access to Ghadermazi et al. 2024, both ACM CSUR papers, and the GMV CERT/SOC study before locking any new framing into the paper
- [ ] Cross-check whether Jalalvand 2024 / Tariq 2025 are already in the existing bibliography (very likely yes) before treating as new sources
- [ ] Team decision (still open, carried over): present as live course-correction at the Sept 28 defense, or attempt a full lock beforehand
- [ ] If proceeding: redefine the action space around triage decisions (not enforcement primitives) and add live analyst-backlog as a state input — scoped as an evolution of the existing design, not a rewrite
- [ ] Keep the Cortex XSOAR `less-busy-user` distinction (routing vs. triage) ready as a specific, correct answer to the most likely "but doesn't X already do this" challenge

---

*Journal updated: September 23, 2026 (continued)*

> **The Bottom Line:** Two independent research agents landed on the same prior art without seeing each other's work — that's real signal. The honest picture: the broad idea has non-RL precedent that must be cited, not claimed as novel; the narrow, real-time-backlog-adaptive version still looks genuinely open, but three of the sources that claim rests on are still unverified past a paywall. Five days is enough time to redefine the action space honestly. It is not enough time to fully verify three paywalled papers and pretend otherwise.

---

## 📁 SESSION: September 23, 2026 (continued — adversarial counter-example hunt complete)

---

### Context: An Explicit, Deliberate Correction to the Framing

Team pushback, correctly taken: this is not a new problem statement or a rename — same registered ARSS title, sharper technical definition. Clean restated description locked in: ARSS sits above alerts, not on raw traffic (intelligence layer, not enforcement layer); receives SIEM alerts, triages, prioritizes, explains why, reduces noise, adapts over time from feedback. One open design question flagged, not yet answered: what exactly counts as "feedback" — direct analyst correction, or outcome-scored reward — since those imply different mechanisms.

**A real, consequential design tension surfaced and recorded, not smoothed over:** the team wants to downgrade MITRE ATT&CK from "the reward's grounding mechanism" to "a small context feature." This is not cosmetic — the strongest, most independently-verified finding in the whole project (zero of 56 surveyed papers combine ATT&CK with RL) is specifically a finding about MITRE grounding the *reward*. If MITRE becomes a minor input instead, that finding stops being the load-bearing novelty pillar, and the backlog/capacity-adaptive angle has to carry that weight instead — which is thinner and, until this session, less independently verified. Recorded as an open trade the team needs to make consciously, not a free change.

**Environment/dataset feasibility check, done directly rather than deferred:** CIC-IIoT 2025 contains no analyst-capacity or workload data of any kind — confirmed against its known feature set (network/sensor fusion only). Any backlog/capacity state variable requires a simulated layer built on top of the real network-derived alert stream, following the same precedent RADAMS already used (its "analyst stress" term was also a simulated function of alert arrival rate, not pulled from a labeled dataset). This keeps the eventual evaluation inside the same simulated-queue limitation the field's own 2026 survey already named as its current ceiling — an honest constraint to state plainly, not something to imply is solved.

### Adversarial Gap Analysis — Final Result

Per direct team instruction: actively tried to disprove the "real-time backlog-adaptive triage" gap rather than confirm it, applying the triage-vs-routing distinction rigorously to every candidate. Result is genuinely mixed, not a clean survival or a clean kill — recorded precisely rather than rounded in either direction:

**The RL/bandit-specific claim held up completely, and was actively reinforced.** Zero RL or bandit methods found anywhere conditioning a triage decision on live backlog/capacity. Two new 2025-2026 RL papers found in this pass (Homayoun/ESORICS 2025, a 2026 offline-RL leakage-free-benchmark paper) both had the opportunity to include backlog/capacity in their design and explicitly did not — active reinforcing evidence, not just absence of counter-evidence.

**The broader "any method" claim is genuinely dented, and the team needs to know this precisely, not vaguely:**
- **Lázaro et al. 2026** (Springer AIAI, DOI 10.1007/978-3-032-30805-4_11, published July 2026) — real production data (63,410 alerts, 16 months, GMV CERT/SOC), 141 workload-derived features feeding a supervised classifier that decides whether to escalate an alert, with the paper's own stated finding that workload modeling measurably improves the escalation decision. This is a genuine triage decision using real capacity signal, published this year — the strongest near-counter-example found across all three research passes this session.
- **Three specific, real differences keep this from closing the gap ARSS would target**, and need to be stated precisely, not glossed: (1) classifier, not RL/policy-based; (2) explicitly decision-support with the analyst in control, not autonomous action; (3) offline/retrospective validation, not a demonstrated live closed loop.
- **Corrected gap statement going forward**: no RL/bandit-based, autonomously-acting policy, validated in a live closed loop, has been shown to condition triage on real-time analyst backlog. Not "no method has ever done this" — that version is now contestable and should not be used.

**Two additional precise findings worth keeping on file:**
- A previously-missed Shah et al. 2020 paper (IEEE TPDS) genuinely uses RL and genuinely conditions on live capacity — but routes alerts between different SOC *sites* in a distributed organization, not the alert's own priority. Same routing-not-triage pattern as Cortex XSOAR, confirmed again at a different granularity — the distinction itself is holding up under repeated, independent testing.
- Microsoft Defender XDR shipped a real "Alert Tuning" feature (Jan 2026) that does auto-suppress/reopen — a genuine triage disposition — but driven by alert risk indicators, not analyst backlog. Fails the capacity-driven axis specifically, not the triage-vs-routing axis. Precise, ready answer if raised as a challenge.

**Resolved from prior unresolved items:** the previously-flagged "GMV CERT/SOC study, paywalled, snippet-only" was a mis-tracked reference to a different, older Sandia paper with a similar generic title — corrected; it's actually the Lázaro 2026 paper above, now reasonably well-characterized via Crossref + a Springer preview (dataset size, date range, feature counts, key finding), though full text/references remain paywalled. Ghadermazi's dissertation remains embargoed, but the journal version's full verbatim abstract was retrieved directly (Gold OA metadata, though the PDF itself still 403s) — confirms and sharpens prior snippet-level knowledge (60.16% backlog reduction figure now abstract-confirmed, not just snippet-triangulated).

### What This Means for the Three Candidate Directions

Not discarded. Direction 1 (RL policy conditioned on live backlog) is untouched by Lázaro's finding, since Lázaro never trains or evaluates a policy. Direction 2 (noise-reduction vs. baseline) gets meaningfully stronger: a Lázaro-style supervised-classifier baseline is now a legitimate, real, 2026-dated comparison point for evaluation, not a synthetic strawman.

### What's Next

- [ ] Team decision on the MITRE-downgrade trade-off — flagged, not resolved, this session
- [ ] Pin down what "feedback" means mechanically (direct analyst correction vs. outcome-scored reward) before it goes further
- [ ] Decide whether to pursue full-text access to Lázaro et al. 2026 given how central it now is to the gap statement's precise wording
- [ ] Gap-analysis phase is now substantively complete across three independent, adversarially-framed research passes — architecture-level next steps are unblocked per the team's own stated condition ("no redesign until the gap analysis proves something's missing"), pending the team's review of this consolidated finding
- [ ] Everything carried over from earlier Sept 23 entries (timeline decision, action-space redefinition direction) still stands

---

*Journal updated: September 23, 2026 (adversarial gap analysis complete)*

> **The Bottom Line:** Asked to actively try to prove itself wrong, the research did exactly that, and came back with a real, honest, mixed answer instead of either extreme. The RL-specific gap is now more solid than it was this morning, reinforced by papers that could have closed it and chose not to. The broader claim had to be narrowed because a real 2026 paper exists that does something close — and the team now knows exactly, precisely, in three stated points, why it isn't the same thing. That precision is worth more than either an unchecked "we're first" or a panicked "someone already did it."

---

## 📁 SESSION: September 23, 2026 (full reset — decision made)

---

### The Trigger

Team explicitly rejected incremental patching of the existing ARSS architecture as forced novelty — "most or even more part has been done and researched... creating something so forced and begged to be novel." Demanded a full first-principles reset: treat the current architecture as disposable, do not assume RL, do not assume the existing gap is valid, do not start coding. A ten-phase adversarial research brief was issued and executed across this session: current-project teardown (done directly), two independent triage/capacity-aware gap analyses, one adversarial counter-example hunt, a closed-loop-response literature maturity check, a response-execution commercial product teardown, and an evaluation-environment feasibility check — six research passes total across this reset.

### Phase 1 Finding — What Was Actually Wrong (undefended teardown)

The core conflation, confirmed at the document level: the signed scope document's own "Out of Scope" section excludes live SIEM/IPS integration, while the action space (Block/Isolate) presumed exactly that integration exists — a direct, written self-contradiction, not just a conceptual tension. The evaluation plan was quietly triage-shaped the whole time (autonomous-handling rate, false-negative/positive rates — all triage metrics) while the action vocabulary insisted on enforcement. The reward function scalarized two different pipeline layers (containment = enforcement-layer, workload = triage-layer) into one number, obscuring which was actually being optimized. Multiple components (DQN, the MITRE-as-reward design, the LLM narrative layer, CIC-IIoT 2025 itself) were identified as technology/dataset choices made first, with justification assembled afterward — not derived from a clearly-stated problem.

### Two Candidate Directions, Tested Adversarially — Final Verdict

**Direction A — Closed-loop autonomous response execution: FROZEN, not pursued.**
- Academically saturated: a sustained, single-group research program (Hammar et al., KTH, ~2021-2026) has already published provably-optimal response strategies, tree-search/counterfactual consequence prediction before acting, multi-objective collateral-damage modeling, and strategies validated against an *adapting* attacker on emulation testbeds — not just simulation. A Jan 2025 ACM Computing Surveys systematic review of this exact literature does not list closed-loop adaptation as a remaining gap.
- Commercially: confirmed absent everywhere checked (13+ platforms) — every real product is a fixed human-authored playbook, or single-action autonomy gated by static config; the one partial exception (Microsoft Defender XDR's Automatic Attack Disruption) uses real ML only to decide *when* to trigger a fixed action, never verifies real-world effect, never models collateral cost. But this is a technology-transfer/deployment gap, not a research gap — not something a 3-person FYP can claim as its own contribution.
- Environment check: CAGE Challenge 2 / CybORG++ is a genuinely practical, well-precedented evaluation environment (pip-installable, real consequence mechanics, published baselines) — but a good environment does not manufacture novelty against research that's already provably optimal. CIC-IIoT 2025 confirmed structurally incompatible with this direction regardless (no state-transition function — attack labels were generated by a fixed script regardless of any hypothetical response, so no way to recover "what if a different action had been taken").
- Two narrow academic threads remain technically open (LLM-agentic response validated against a reactive environment rather than static log replay; collateral-damage-model fidelity validated against real operational data) but both are thin, one likely infeasible for FYP scope without real operational data access.

**Direction B — Capacity/backlog-adaptive alert triage: SURVIVED, now the adopted direction.**
- Real, narrow gap confirmed independently by two separate research passes, one explicitly adversarial (instructed to try to kill it, not confirm it): an autonomously-acting policy — RL, bandit, or otherwise — that conditions its triage decision on *live*, real-time analyst backlog, validated beyond a simulated queue. Broad "capacity-aware triage" is not novel (Shah 2019, Ghadermazi 2024, both non-RL/optimization-based) and must be cited honestly, not claimed as untouched. The closest 2026 near-counter-example (Lázaro et al., GMV CERT/SOC) is real, uses production data, and shows workload features improving a genuine triage decision — but it's a supervised classifier advising a human, evaluated offline, not an autonomously-acting policy validated live. That precise, three-point distinction is the thing to keep sharp, not a vague "nobody's done this."
- No bandit-based attempt found anywhere for this exact problem — a second, independently confirmed open thread.

### The Adopted Redesign

**New framing:** an adaptive SOC triage/response-decision system whose behavior changes with current SOC operational workload — not "RL chooses Block or Isolate," but "given this alert, its risk, and current SOC state, what should happen to it right now."

**New state:** alert understanding (severity, attack type, confidence, asset importance, temporal context) + SOC state (queue depth, oldest-alert age, severity distribution, analyst availability/current workload). **New action space:** Auto-close / Defer-queue / Escalate-review, closing a loop through analyst feedback back into policy adaptation. **Safety mechanism:** a severity floor — critical/high alerts can never be auto-suppressed regardless of workload pressure; medium alerts are where the actual policy operates; the contribution is explicitly framed as the *dynamic workload adaptation inside that safety envelope*, not the floor itself.

**Method commitment — "problem first, method second," made concrete as an actual experimental ladder, not a slogan:** static threshold → supervised classifier → learning-to-defer → contextual bandit/offline policy → offline RL, compared empirically rather than RL assumed from the start.

**Primary research question:** can an adaptive alert-triage policy incorporating real-time SOC workload state reduce analyst workload while maintaining a fixed level of protection against high-severity threats? **Falsifiable hypothesis:** a workload-aware adaptive triage policy reduces analyst review burden during high-load periods without a statistically significant increase in missed high-severity alerts, versus workload-independent baselines. Stated so it can fail, not just succeed.

### What's Kept vs. Removed

**Kept, repositioned:** the two-stage detector (92.34%/92.83%, real evaluated work) — now an alert-generation/sensing module feeding the experimental alert stream, not the center of the contribution. CIC-IIoT 2025 — still useful for generating realistic attack/benign alert characteristics, not as a closed-loop environment. MITRE ATT&CK — demoted to optional severity/risk context, not the reward. The dashboard.

**Removed:** Block/Isolate as ARSS's own actions (the original conflation). The LLM explanation layer and the SHAP→LLM→RL narrative architecture as claimed research contributions (may survive later as an interface feature, not as thesis-central). MITRE-as-the-reward specifically.

**Explicitly not yet started:** no code changes. Team's own instruction, several times over: understand and decide first, build second.

### One Unresolved Verification Flag, Carried Forward

The redesign proposal cites specific findings from the 2026 offline-policy-learning paper (Okafor, ScienceDirect, DOI 10.1016/j.mlwa.2026.100984) — that some offline RL methods degenerate while recurrent behavioral cloning performs strongly, and that it uses a severity-floor precedent — more specifically than anything this session's agents could verify (every access attempt hit a paywall; only metadata/snippet-level confirmed). These claims may be accurate if read from a source outside this session's research, but per the project's own standing citation-verification discipline, they need primary-text confirmation before becoming load-bearing, citable facts in the actual paper — flagged, not yet resolved.

### What's Next

- [ ] Verify the specific Okafor 2026 claims (degeneration finding, severity-floor precedent) against primary text before citing them
- [ ] Formalize this decision into the full research-decision document structure (executive verdict, gap comparison table, 12-month roadmap) once requested
- [ ] Rewrite `ARSS_Paper.tex`, the scope document, and the slide decks around the new framing — not started, deliberately, pending the team's go-ahead
- [ ] Everything from the pre-reset session (citation fixes, defense-readiness Q&A, the RL primer) remains factually valid background material; the parts specifically describing Block/Isolate/MITRE-as-reward as the core contribution are now superseded and need updating wherever they appear
- [ ] Title defense is ~5 days out — the timeline tension from earlier in the day is now sharper, not resolved: this is a genuine reset, decided with real evidence, landing days before a defense

---

*Journal updated: September 23, 2026 (reset decision recorded)*

> **The Bottom Line:** Told to treat five months of work as disposable and find out what's actually true, the process did exactly that — six research passes, two directions tested adversarially, one frozen with reasons precise enough to defend, one kept with reasons precise enough to defend differently. The new direction is smaller, sharper, and actually falsifiable, which is a better place to stand in front of a panel than a bigger claim that doesn't survive contact. What's not resolved is time — this landed five days before the defense, and that's the real risk now, not the research.

---

## 📁 SESSION: September 24, 2026 — Direction locked, no further resets

---

### Context

FYP coordinator email received: Presentation 1 (Title Defence) window is Sept 28 – Oct 1, exact slot TBD. Format is a hard 10 minutes total — 5 minutes presenting, 5 minutes Q&A. Slides must be built against the Scope Document *and* the official rubric (still not in hand as of this entry — was promised early in this session, never actually shared, worth chasing down). Deadline for reporting a title/project/group-member change was the same day this entry covers; team's own read, after discussion: that deadline governs registration-level swaps (an entirely different project), not the kind of technical-approach refinement already done under the same registered title and problem area — and regardless, the window to file any such change is now closed.

### The Decision

**Workload-adaptive alert triage is now locked as the direction — no further ground-up resets.** Team's own words: "we stick to this and keep making it genuinely good... not just sound FYP level, make it work properly the way we want." This is a meaningfully different state than "adopted" (the Sept 23 entry) — that was a decision that could still be reopened; this is a commitment to execute.

**The one-sentence version the team is standardizing on, worth keeping verbatim since it's now the canonical framing:**
> "We're building a system that sits between a company's security alerts and the human security team, and instead of just ranking alerts by how dangerous they look, it also pays attention to how swamped the security team currently is — so it can be more careful about what it bothers a human with when they're overwhelmed, while still guaranteeing that genuinely serious threats never get missed just because it's a busy day."

**Standard going forward, stated explicitly so it doesn't quietly erode under time pressure:** "genuinely good, not just sound FYP-level" means claims still get verified before they're used, the falsifiable hypothesis stays falsifiable rather than being softened into something that can't fail, and the one still-open citation flag (Okafor 2026's specific claims about offline-RL degeneration and its severity-floor precedent — never independently confirmed past a paywall by this session's own agents) gets resolved before it's treated as settled fact anywhere official, not smoothed over because the clock is short.

### What's Actually Next

- [ ] Build the actual 5-minute Presentation 1 deck around the locked direction — current slide files still describe the old Block/Isolate architecture and are far too long for a 10-minute slot regardless; needs a real rebuild, not a trim
- [ ] Track down the official rubric — mentioned early this session, never received, and the coordinator's own email says slides should be built against it
- [ ] Resolve the Okafor 2026 verification flag before it's cited anywhere official
- [ ] `ARSS_Paper.tex`, the scope document's technical sections, and the existing slide decks all still describe the pre-reset architecture and need updating to match
- [ ] No further reconsideration of the core direction — remaining time goes to execution and materials, not more research

---

*Journal updated: September 24, 2026*

> **The Bottom Line:** The deadline closing the door on further registration-level changes turned out to remove a real source of churn, not just add pressure — there's now one direction, committed to, with a clear standard attached to it: actually good, not just good-sounding. Everything left is execution.
