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
