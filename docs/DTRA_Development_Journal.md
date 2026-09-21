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
