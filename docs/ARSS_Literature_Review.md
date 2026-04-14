# ARSS — Literature Review
**Topic:** RL for SOC Alert Triage — Academic & Commercial Landscape (2022-2026)
**Date Compiled:** April 15, 2026
**Purpose:** FYP proposal literature review foundation

---

## How to Read These Papers — A Practical Guide

> This guide is for someone who understands ARSS well but hasn't done academic paper reading before. Follow this exactly for each paper.

---

### Step 1: Don't Read It Fully (Yet)

First pass should take 10-15 minutes max. Do this in order:

1. **Read the Abstract** — What problem are they solving? What's their claim?
2. **Read the Introduction (last 2 paragraphs)** — This is where they state their contribution clearly.
3. **Read the Conclusion** — What did they prove? What are their limitations?
4. **Skim the figures and tables** — Results tables, architecture diagrams. What numbers did they get?

After this you'll know: is this paper directly relevant to ARSS or just background? If it's background, stop here. If it's directly relevant, go to Step 2.

---

### Step 2: Read With ARSS in Mind (30-40 minutes)

Now read the full paper but ask these questions as you go:

**About their problem:**
- What exact problem are they solving?
- Is it detection, prioritization, or response? (This tells you which layer they're at)
- Who is their system built for — researchers or real SOCs?

**About their RL design (the most important part for us):**
- What is their **state space**? (What does the RL agent see?)
- What is their **action space**? (What can it do?)
- What is their **reward function**? (What is it optimizing for?)
- Is the reward grounded in real threat intelligence or is it abstract/invented?

**About their results:**
- What dataset did they use? Is it the same as ours (CIC-IIoT 2025)?
- What metrics did they report? (Accuracy, recall, FP reduction, etc.)
- Did they compare against a baseline? What baseline?

**About their limitations (gold mine for your gap statement):**
- What do they admit they didn't solve?
- What future work do they suggest?
- This is where ARSS comes in — their limitation is your contribution.

---

### Step 3: Fill This Template (For Every Paper)

Copy this and fill it in after reading:

```
## Paper: [Title]
**Authors:**
**Year:**
**Venue:**
**DOI:**

### Their Problem
What exact problem do they solve?

### Their RL Design
- State space:
- Action space:
- Reward function:
- Is reward grounded in real threat intel? Yes / No

### Their Results
- Dataset used:
- Key metric:
- Compared against:

### Their Limitations (What They Admit)
-
-

### How It Connects to ARSS
- Do we cite this as related work or as the gap we fill?
- What specific sentence in our paper will reference this?

### ARSS Advantage Over This Paper
- What does ARSS do that this paper doesn't?
```

---

### Step 4: How to Get the PDF

Most of these papers are behind paywalls. Options:

1. **GIKI Library Portal** — Log in with your university credentials and access IEEE Xplore + Elsevier
2. **Sci-Hub** — Search by DOI. Paste the DOI directly: `sci-hub.se/[DOI]`
3. **Google Scholar** — Search the title, click "All versions" — sometimes a free PDF link appears
4. **ResearchGate** — Search the title, request full-text from the authors (they usually share within 24 hours)
5. **arXiv** — Some IEEE papers have a free arXiv version (check the arXiv links in this document)

---

### Step 5: What to Do With Your Notes

After reading each paper, do two things:

1. **Update the template above** with your filled notes
2. **Write one sentence** that explains how this paper will appear in your literature review

Example sentence:
> "Chavali et al. (2024) propose TD3-AP, an off-policy actor-critic RL agent for IDS alert prioritization, but ground their reward in abstract adversarial game costs rather than real-world threat semantics — a limitation ARSS addresses through MITRE ATT&CK severity-weighted reward shaping."

That sentence is literally copy-paste ready for your proposal. Do this for every paper and your literature review writes itself.

---

### Reading Order (Follow This Exactly)

| Order | Paper | Time Needed | Why This Order |
|-------|-------|-------------|----------------|
| 1st | Jalalvand et al. 2025 (ACM CSUR — Alert Fatigue Survey) | 1 hour | Sets the whole problem context. Read this first so everything else makes sense. |
| 2nd | Jalalvand et al. 2024 (ACM CSUR — Prioritization Survey) | 1 hour | Shows the solution landscape. You'll see exactly where ARSS fits. |
| 3rd | Chavali et al. 2024 (C&S — TD3-AP) | 45 mins | Your strongest related work. Understand it deeply. |
| 4th | Wang et al. 2024 (C&S — AlertPro) | 45 mins | Closest prior art. Know it better than the authors. |
| 5th | Chavali et al. 2022 (IEEE CEC — SAC-AP) | 30 mins | First in their series. Read after TD3-AP so you understand the evolution. |
| 6th | Huang & Zhu 2022 (RADAMS) | 30 mins | Original RL triage work. Shows where the field started. |
| 7th | Chhetri et al. 2024 (ACM TOIT — A2C) | 30 mins | Theoretical backing for ARSS philosophy. |
| 8th | Huang et al. 2024 (IEEE TNSM — MITREtrieval) | 30 mins | Supports MITRE grounding. Read last as it's supporting, not core. |

**Total estimated time: 6-7 hours spread across multiple days. Don't rush it.**

---

## The Gap Statement

> "Prior RL work (Chavali et al. 2022-2025, Wang et al. 2024) frames alert prioritization as an adversarial game with synthetic reward functions decoupled from real-world threat semantics. No published peer-reviewed work grounds the RL reward directly in MITRE ATT&CK TTP severity — the closest work (Huang et al. 2024) extracts TTPs without closing the feedback loop to a triage policy. ARSS bridges this gap by proposing a category-conditioned RL agent with MITRE ATT&CK grounded rewards operating at the SIEM triage layer with a discrete 4-action response space (Ignore/Log/Block/Isolate)."

---

## Section 1 — The Problem (Alert Fatigue)

### P1. Alert Fatigue in SOCs: Research Challenges and Opportunities
- **Authors:** Shahroz Tariq, Mohan Baruwal Chhetri, Surya Nepal, Cécile Paris
- **Venue:** ACM Computing Surveys, Vol. 57, Issue 9, Article 224 — **IF 23.8**
- **Year:** 2025
- **DOI:** 10.1145/3723158
- **Link:** https://dl.acm.org/doi/10.1145/3723158
- **Summary:** Systematic review of alert fatigue through lenses of automation, augmentation, and human-AI collaboration. Identifies four root causes: inadequate monitoring, improper thresholds, missing feedback loops, analyst cognitive load. Reports 4,484 alerts/day average; 67% ignored by overwhelmed analysts. Explicitly flags RL at the triage layer as underexplored.
- **How to cite:** Foundational problem statement. Use to justify why alert fatigue is unsolved and why RL is the right direction.

### P2. Alert Prioritisation in SOCs — Systematic Survey
- **Authors:** Fatemeh Jalalvand, Mohan Baruwal Chhetri, Surya Nepal, Cécile Paris
- **Venue:** ACM Computing Surveys, Vol. 57, No. 2, Article 42 — **IF 23.8**
- **Year:** 2024
- **DOI:** 10.1145/3695462
- **Link:** https://dl.acm.org/doi/10.1145/3695462
- **Summary:** Comprehensive systematic review classifying prioritization criteria (severity, context, CTI, analyst feedback) and methods (rule-based, ML, RL, graph-based). Builds a taxonomy of the alert prioritization solution space. Identifies CTI-criteria + RL-method intersection as underexplored.
- **How to cite:** Use to position ARSS within the solution taxonomy — we sit at the CTI-grounded + RL intersection that the survey flags as a gap.

---

## Section 2 — Direct Related Work (RL for Alert Triage)

### R1. SAC-AP — Soft Actor-Critic DRL for Alert Prioritization
- **Authors:** Lalitha Chavali, Tanay Gupta, Paresh Saxena
- **Venue:** IEEE Congress on Evolutionary Computation (CEC) 2022 — CORE B
- **Year:** 2022
- **DOI:** 10.1109/CEC55065.2022.9870423
- **Link:** https://ieeexplore.ieee.org/document/9870423/
- **Summary:** Models alert prioritization as an adversarial Markov game between attacker and defender. Uses Soft Actor-Critic with maximum entropy RL to optimize defender resource allocation across IDS alerts. ~16% reduction in defender loss vs DDPG baseline.
- **Gap vs ARSS:** Reward is abstract "defender loss" — not grounded in MITRE ATT&CK or analyst feedback. Ranking only, no 4-action response space.

### R2. Off-Policy Actor-Critic DRL for Alert Prioritization (TD3-AP + SAC-AP Extended)
- **Authors:** L. Chavali, A. Krishnan, P. Saxena, B. Mitra, A.S. Chivukula
- **Venue:** Computers & Security, Vol. 142 (Elsevier) — **IF 5.6, Q1**
- **Year:** 2024
- **DOI:** 10.1016/j.cose.2024.103893
- **Link:** https://www.sciencedirect.com/science/article/abs/pii/S016740482400155X
- **Summary:** Extends SAC-AP with TD3 variant. Evaluates on MQTT-IoT-IDS2020, DARPA 2000, CSE-CICIDS2018 with Snort alerts. Demonstrates off-policy methods outperform on-policy for sparse-reward alert environments.
- **Gap vs ARSS:** Same game-theoretic framing. Reward function is synthetic attack cost. No MITRE grounding, no analyst feedback, no response actions.

### R3. KNAP — Knowledge-Empowered DRL for Alert Prioritization
- **Authors:** L. Chavali, P. Saxena, B. Mitra
- **Venue:** Advanced Information Networking and Applications (AINA 2024), Springer LNCS — CORE B
- **Year:** 2024
- **DOI:** 10.1007/978-3-031-57916-5_34
- **Link:** https://link.springer.com/chapter/10.1007/978-3-031-57916-5_34
- **Summary:** Three KNAP variants (D-KNAP, S-KNAP, T-KNAP) using DDPG/SAC/TD3 enhanced with attack graph domain knowledge. Knowledge injection improves sample efficiency and reward convergence.
- **Gap vs ARSS:** "Knowledge" is an attack graph heuristic, not MITRE ATT&CK TTP taxonomy. Still no analyst feedback integration or response actions.

### R4. Multi-Critic DRL for Enhanced Alert Prioritization
- **Authors:** L. Chavali, P. Saxena
- **Venue:** AINA 2025, Springer LNDECT Vol. 249
- **Year:** 2025
- **DOI:** 10.1007/978-3-031-87775-9_15
- **Link:** https://link.springer.com/chapter/10.1007/978-3-031-87775-9_15
- **Summary:** Multiple critic networks to reduce Q-value overestimation in alert prioritization. Improved stability over single-critic TD3/SAC variants.
- **Gap vs ARSS:** Architectural refinement on the same abstract game-theoretic framing. No CTI grounding.

### R5. AlertPro — Context-Aware RL Alert Prioritization
- **Authors:** X. Wang, X. Yang, X. Liang et al.
- **Venue:** Computers & Security, Vol. 137 (Elsevier) — **IF 5.6, Q1**
- **Year:** 2024
- **DOI:** 10.1016/j.cose.2023.103583
- **Link:** https://www.sciencedirect.com/science/article/abs/pii/S0167404823004935
- **Summary:** Two-module system: context inference extracts alert sequence features, self-evolution module uses RL with analyst feedback to re-rank alerts for multi-step attack detection. Sub-500ms latency.
- **Gap vs ARSS:** **Closest prior art.** Has analyst feedback loop but reward is a simple binary signal — no MITRE ATT&CK severity weighting. Ranking only, no discrete response actions.

### R6. RADAMS — RL for Alert De-Emphasis Against Alert Flooding
- **Authors:** Linan Huang, Quanyan Zhu
- **Venue:** Computers & Security (Elsevier) — **IF 5.6, Q1**
- **Year:** 2022
- **DOI:** (see arXiv 2111.03463)
- **Link:** https://arxiv.org/abs/2111.03463
- **Summary:** RL-based adaptive alert de-emphasis strategy against Informational DoS (alert flooding). Models analyst attention dynamics using Yerkes-Dodson and sunk cost theory. 95.89% recall, 5.86% FPR on 500K+ alerts.
- **Gap vs ARSS:** De-emphasizes alerts to reduce cognitive load — doesn't take response actions (no Block/Isolate). No MITRE ATT&CK. Manages attention, not triage decisions.

---

## Section 3 — Supports ARSS Architecture

### A1. Human-AI Teaming for Alert Fatigue — A2C Framework
- **Authors:** Mohan Baruwal Chhetri, Shahroz Tariq, Ronal Singh, Fatemeh Jalalvand, Cécile Paris, Surya Nepal
- **Venue:** ACM Transactions on Internet Technology, Vol. 24, No. 3 — **IF 3.9**
- **Year:** 2024
- **DOI:** 10.1145/3670009
- **Link:** https://dl.acm.org/doi/10.1145/3670009
- **Summary:** Proposes A2C (Automate-Augment-Collaborate) framework for dynamic transitions between automation modes based on alert complexity. Routine alerts → automation; novel threats → collaborative human-AI. Conceptual framework, not implemented system.
- **How to cite:** ARSS operationalizes the A2C philosophy with a concrete RL policy. Cite as the theoretical foundation for our triage philosophy.

### A2. MITREtrieval — Extracting MITRE ATT&CK Techniques from Threat Reports
- **Authors:** Y.T. Huang, R. Vaitheeshwari, M.C. Chen, Y.D. Lin, R.H. Hwang et al.
- **Venue:** IEEE Transactions on Network and Service Management, Vol. 21, No. 4 — **IF 5.3, Q1**
- **Year:** 2024
- **DOI:** 10.1109/TNSM.2024.3401200
- **Link:** https://ieeexplore.ieee.org/document/10539631/
- **Summary:** Fuses BERT with MITRE ATT&CK ontology to extract TTP techniques from unstructured CTI reports. Validates that MITRE ATT&CK can be used as a structured intelligence framework in ML pipelines.
- **How to cite:** Supports grounding our reward function in MITRE ATT&CK — cites the framework as ML-compatible and operationalizable.

### A3. Dynamic Alert Prioritization — HMM + Active Learning
- **Venue:** IEEE Transactions on Information Forensics and Security (TIFS) — **IF 6.8, top-tier**
- **Year:** 2025 (IEEE Early Access)
- **Link:** https://ieeexplore.ieee.org/document/11095625/
- **Summary:** Models dynamic alert prioritization as active learning within a hidden Markov model. Minimizes MSE of analyst belief state using query budget. Complementary state-estimation approach.
- **How to cite:** Reference for belief-state modeling of analyst workload.

---

## Section 4 — Commercial Landscape (No RL Used)

### Key Finding
No commercial SOC/SOAR platform publicly uses RL as the triage decision mechanism (2022-2026).

| Platform | Triage Approach | RL? |
|----------|----------------|-----|
| Splunk SOAR | Rule-based playbooks | No |
| Palo Alto XSOAR | Rules + ML scoring | No |
| Microsoft Sentinel | Graph-based ML (Fusion) | No |
| CrowdStrike Charlotte AI | Supervised imitation learning + LLM | No |
| IBM QRadar | Rules + NLP enrichment | No |
| Dropzone, Exaforce, CORTEX | LLM multi-agent | No |

**CrowdStrike Charlotte AI** is the strongest commercial product — trained on millions of Falcon MDR analyst decisions via imitation learning. It replicates past decisions but cannot discover better policies. RL-based triage decisions are unclaimed in commercial deployments.

Gartner's 2025 AI SOC Agent capability list does not include RL as a named technique.

---

## Section 5 — Reading Priority Order

| Priority | Paper | Why |
|----------|-------|-----|
| 1 | Jalalvand et al. 2025 (ACM CSUR) | Problem statement |
| 2 | Jalalvand et al. 2024 (ACM CSUR) | Solution taxonomy |
| 3 | Chavali et al. 2024 (C&S) — TD3-AP | Strongest related work |
| 4 | Wang et al. 2024 (C&S) — AlertPro | Closest prior art |
| 5 | Chhetri et al. 2024 (ACM TOIT) — A2C | Theoretical foundation |
| 6 | Chavali et al. 2022 (IEEE CEC) — SAC-AP | First in the series |
| 7 | Huang & Zhu 2022 (C&S) — RADAMS | Original RL triage work |
| 8 | Huang et al. 2024 (IEEE TNSM) — MITREtrieval | MITRE + ML support |

---

*Compiled: April 15, 2026*
*Team: Daniyal (2023406), Haider (2023416), Daud (2023677)*
