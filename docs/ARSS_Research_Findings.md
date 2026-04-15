# ARSS — Research Findings & Gap Analysis
**Compiled:** April 15, 2026
**Purpose:** Scope document literature review — all findings with full citations

---

## Part 1 — What the Academic Literature Shows

### Finding 1: RL for alert triage is real but small
The entire body of peer-reviewed RL work on alert prioritization fits in one lab: Chavali et al. at RMIT/IIT. They produced 4 papers from 2022–2025 (SAC-AP → TD3-AP → KNAP → Multi-Critic). Outside this group, only Wang et al. (2024) and Huang & Zhu (2022) exist as independent contributions. The field is genuinely nascent.

**Sources:**
- Chavali L., Gupta T., Saxena P. — "Soft Actor-Critic Based Deep Reinforcement Learning for Alert Prioritization" — IEEE CEC 2022. DOI: 10.1109/CEC55065.2022.9870423
- Chavali L., Krishnan A., Saxena P., Mitra B., Chivukula A.S. — "Off-Policy Actor-Critic Deep Reinforcement Learning for Alert Prioritization" — *Computers & Security*, Vol. 142, 2024. DOI: 10.1016/j.cose.2024.103893
- Chavali L., Saxena P., Mitra B. — "KNAP: Knowledge-Empowered Deep Reinforcement Learning for Alert Prioritization" — AINA 2024, Springer LNCS. DOI: 10.1007/978-3-031-57916-5_34
- Chavali L., Saxena P. — "Multi-Critic Deep Reinforcement Learning for Enhanced Alert Prioritization" — AINA 2025, Springer LNDECT Vol. 249. DOI: 10.1007/978-3-031-87775-9_15

---

### Finding 2: Every RL paper uses a synthetic, game-theoretic reward function
All four Chavali papers model alert prioritization as an adversarial Markov game between attacker and defender. The reward is abstract "defender loss" or "attack cost" — synthetic values invented for the game, with no connection to real-world threat intelligence frameworks. The agent optimizes for a mathematical objective that does not map to how real SOC analysts rank threats.

**Direct evidence:**
- SAC-AP (2022): "We model the interaction between the IDS and the attacker as a two-player zero-sum Markov game... the defender's loss function is defined as the expected cumulative cost of the attacker's actions." — reward is fully synthetic.
- TD3-AP (2024): Extends SAC-AP. Evaluates on MQTT-IoT-IDS2020, DARPA 2000, CSE-CICIDS2018 but reward function remains game-theoretic attack cost. No MITRE ATT&CK reference in paper.
- KNAP (2024): Injects "knowledge" via an attack graph heuristic — not the MITRE ATT&CK TTP taxonomy. Knowledge injection improves sample efficiency but doesn't ground reward in real threat intelligence.

**Sources:** Same as Finding 1.

---

### Finding 3: No paper uses MITRE ATT&CK to weight RL rewards
Across the entire surveyed literature (2022–2026), zero peer-reviewed papers ground RL reward in the MITRE ATT&CK framework. The closest is MITREtrieval (Huang et al. 2024), which extracts TTPs from threat reports using BERT — but doesn't close the feedback loop to a triage policy or reward function.

**Source:**
- Huang Y.T., Vaitheeshwari R., Chen M.C., Lin Y.D., Hwang R.H. et al. — "MITREtrieval: Fusing BERT with MITRE ATT&CK Ontology for TTP Extraction" — *IEEE Transactions on Network and Service Management*, Vol. 21, No. 4, 2024. DOI: 10.1109/TNSM.2024.3401200

**Gap confirmed:** MITRE ATT&CK + RL reward = zero papers.

---

### Finding 4: AlertPro is the closest prior art — and still has two critical gaps
Wang et al. (2024) built a two-module system: context inference (extracts alert sequence features) + self-evolution module (RL with analyst feedback for re-ranking). It achieves sub-500ms latency and explicitly incorporates analyst feedback. This is the most production-realistic RL triage paper.

**But it has two gaps ARSS fills:**
1. Analyst feedback is a simple binary signal (correct/incorrect). No MITRE ATT&CK severity weighting — a MITM at 70% gets the same reward signal as a Recon scan at 70%.
2. Output is a ranked list only. No discrete response actions. The analyst still decides what to do with every alert.

**Source:**
- Wang X., Yang X., Liang X. et al. — "AlertPro: Context-Aware Reinforcement Learning for Alert Prioritization" — *Computers & Security*, Vol. 137, 2024. DOI: 10.1016/j.cose.2023.103583

---

### Finding 5: RL state space is universally impoverished
Every surveyed RL paper collapses the detector output into a single risk score or danger bucket before feeding it to the agent. None preserve attack category or classification confidence as separate state dimensions.

- SAC-AP, TD3-AP: state = alert feature vector mapped to scalar risk
- KNAP: state = risk score + attack graph node embedding
- AlertPro: state = alert sequence context embedding

**The problem:** Two alerts with identical danger scores but different attack types require completely different responses. A Recon scan at 0.80 should be Logged. A MITM at 0.80 should trigger Isolate. An agent that only sees "0.80" cannot learn this distinction.

**ARSS fixes this with:** `State = [danger_score, attack_category (one-hot, 7 classes), category_confidence]`

---

### Finding 6: No paper has a discrete 4-action response space
All prior RL work outputs a priority score or ranking. None implement a discrete action space (Ignore / Log / Block / Isolate) at the SIEM triage layer.

- SAC-AP/TD3-AP/KNAP: continuous priority score output
- AlertPro: re-ranked alert list
- RADAMS: alert de-emphasis weight (no response action taken)

RADAMS is notable because it does address the RL-at-triage-layer concept, but for attention management (reducing cognitive load by de-emphasizing low-value alerts), not for taking automated response actions.

**Source:**
- Huang L., Zhu Q. — "RADAMS: Resilient and Adaptive Alert and Attention Management Strategy Against Informational Denial-of-Service Attack" — *Computers & Security*, 2022. arXiv: 2111.03463

**Gap confirmed:** Discrete 4-action response space at SIEM layer = zero papers.

---

### Finding 7: Two systematic reviews have independently flagged this exact gap
Two ACM Computing Surveys papers (the highest-impact venue in the field, IF 23.8) have both independently identified the CTI-grounded + RL intersection as underexplored.

**Jalalvand et al. 2025 (Alert Fatigue Survey):**
> Reports 4,484 alerts/day average; 67% ignored by overwhelmed analysts. Identifies four root causes: inadequate monitoring, improper thresholds, missing feedback loops, analyst cognitive load. Explicitly flags RL at the triage layer as underexplored.

**Jalalvand et al. 2024 (Alert Prioritization Survey):**
> Builds a taxonomy of prioritization methods. Identifies the CTI-criteria + RL-method intersection as the least-explored quadrant of the solution space.

**Sources:**
- Tariq S., Chhetri M.B., Nepal S., Paris C. — "Alert Fatigue in SOCs: Research Challenges and Opportunities" — *ACM Computing Surveys*, Vol. 57, Issue 9, Article 224, 2025. DOI: 10.1145/3723158
- Jalalvand F., Chhetri M.B., Nepal S., Paris C. — "Alert Prioritisation in Security Operations Centres: A Systematic Survey" — *ACM Computing Surveys*, Vol. 57, No. 2, Article 42, 2024. DOI: 10.1145/3695462

---

### Finding 8: The A2C framework provides theoretical foundation for ARSS triage philosophy
Chhetri et al. (2024) propose the Automate-Augment-Collaborate (A2C) framework: routine alerts → full automation; novel threats → human-AI collaboration. This is a conceptual framework without a concrete RL implementation.

ARSS operationalizes A2C: the LOG action is exactly the "Collaborate" mode — deferring to human analyst when the agent lacks confidence. IGNORE/BLOCK/ISOLATE are the "Automate" mode.

**Source:**
- Chhetri M.B., Tariq S., Singh R., Jalalvand F., Paris C., Nepal S. — "Human-AI Teaming for Alert Fatigue: An A2C Framework Approach" — *ACM Transactions on Internet Technology*, Vol. 24, No. 3, 2024. DOI: 10.1145/3670009

---

## Part 2 — What the Commercial Landscape Shows

### Finding 9: Zero commercial SOC platforms use RL for triage decisions
As of 2026, no SOAR/SIEM vendor publicly uses RL as the mechanism for triage decision-making. The commercial landscape uses three approaches: rule-based playbooks, supervised ML scoring, and LLM agents.

| Platform | Triage Mechanism | RL? |
|----------|-----------------|-----|
| Splunk SOAR | Rule-based playbooks | No |
| Palo Alto XSOAR | Rules + ML risk scoring | No |
| Microsoft Sentinel | Graph-based ML (Fusion engine) | No |
| CrowdStrike Charlotte AI | Supervised imitation learning + LLM | No |
| IBM QRadar | Rules + NLP enrichment | No |
| Dropzone AI | LLM multi-agent triage | No |
| Exaforce | LLM multi-agent | No |

**Source:** Gartner AI in Security Operations 2025 capability list. RL is not named as a technique in any commercial platform's documented approach.

---

### Finding 10: CrowdStrike Charlotte AI is the strongest commercial product — and still has a fundamental ceiling
Charlotte AI is trained on millions of analyst decisions from Falcon MDR (managed detection and response) customers via imitation learning. It replicates past analyst decisions with high fidelity.

**The limitation:** Imitation learning can only replicate — it cannot discover better policies. If human analysts historically over-blocked Recon scans and under-responded to MITM, Charlotte AI learns and perpetuates that bias. An RL agent trained on MITRE ATT&CK severity can potentially outperform the average analyst, not just replicate them.

---

### Finding 11: The 2024–2026 agentic SOC wave is LLM-first, not RL-first
The commercial trend is LLM multi-agent systems (Dropzone, Exaforce, CORTEX). These agents can read unstructured threat reports, write playbooks, and generate incident summaries. But they are not policy learners — they cannot improve from feedback without retraining. RL-based triage is not part of the agentic SOC conversation.

---

## Part 3 — Confirmed Novelty Gaps

Three specific combinations that do not appear in any surveyed peer-reviewed paper:

| Gap | Evidence |
|-----|----------|
| MITRE ATT&CK severity weights used directly in RL reward function | Zero papers. MITREtrieval extracts TTPs but doesn't feed them back to a reward function. |
| Discrete 4-action response space (Ignore/Log/Block/Isolate) at SIEM triage layer | Zero papers. All prior work outputs rankings, not response actions. |
| Category-conditioned state space [danger_score, attack_category, confidence] | Zero papers. All prior work collapses to scalar risk score. |

Combination of all three = ARSS's claimed research contribution.

---

## Part 4 — For the Scope Document Literature Review Table

Format: **Application Name | Key Features | Weakness | Relevance to ARSS**

| Application | Key Features | Weakness | Relevance to ARSS |
|-------------|-------------|----------|-------------------|
| SAC-AP (Chavali et al., IEEE CEC 2022) | RL for alert prioritization; adversarial Markov game; SAC algorithm | Synthetic game-theoretic reward, no MITRE ATT&CK grounding; ranking only, no response actions | Establishes RL viability for alert triage; ARSS advances by grounding reward in real CTI |
| TD3-AP (Chavali et al., C&S 2024) | Off-policy actor-critic; evaluates on real IDS datasets (MQTT-IoT, DARPA 2000, CICIDS2018) | Same abstract reward as SAC-AP; no CTI grounding; no analyst feedback | Strongest academic baseline; ARSS addresses its core limitation |
| KNAP (Chavali et al., AINA 2024) | Attack graph knowledge injection into DRL; improved sample efficiency | Attack graph ≠ MITRE ATT&CK; still no real threat intelligence grounding | Shows knowledge injection improves RL; ARSS uses MITRE as the knowledge source |
| AlertPro (Wang et al., C&S 2024) | Analyst feedback loop; context-aware alert re-ranking; sub-500ms latency | Binary feedback signal only; no MITRE weighting; ranking output, not response actions | Closest prior art; ARSS extends with severity-weighted feedback and discrete response actions |
| RADAMS (Huang & Zhu, C&S 2022) | RL for alert de-emphasis against flooding; analyst attention modeling | Manages attention, doesn't take response actions; no CTI grounding | Shows RL can operate at triage layer; ARSS moves from de-emphasis to actual response actions |
| Alert Fatigue Survey (Tariq et al., ACM CSUR 2025) | Systematic review; 4,484 alerts/day; 67% ignored; flags RL at triage as underexplored | Survey only — no implementation | Primary problem statement; directly flags the gap ARSS fills |
| Alert Prioritization Survey (Jalalvand et al., ACM CSUR 2024) | Full taxonomy of prioritization methods; identifies CTI+RL intersection as underexplored | Survey only — no implementation | Positions ARSS in the solution space; confirms gap is peer-recognized |
| A2C Framework (Chhetri et al., ACM TOIT 2024) | Conceptual Automate-Augment-Collaborate framework for dynamic automation modes | Conceptual only — no RL policy implemented | ARSS operationalizes A2C: LOG = Collaborate, IGNORE/BLOCK/ISOLATE = Automate |
| MITREtrieval (Huang et al., IEEE TNSM 2024) | BERT + MITRE ATT&CK ontology for TTP extraction from threat reports | Extracts TTPs but doesn't close feedback loop to triage policy or RL reward | Validates MITRE ATT&CK as ML-compatible; supports ARSS's reward grounding approach |
| CrowdStrike Charlotte AI (Commercial, 2024) | Imitation learning on millions of MDR analyst decisions; LLM explanation layer | Cannot discover policies better than average analyst; replicates analyst bias | ARSS can potentially exceed average analyst performance through RL optimization |
| Splunk SOAR / Palo Alto XSOAR (Commercial) | Rule-based playbooks; ML risk scoring; workflow automation | Rules don't adapt; ML scores without learning from outcomes; no RL policy | Shows market does not use RL for triage; ARSS fills this commercial gap |

---

*Compiled: April 15, 2026*
*Team: Daniyal (2023406), Haider (2023416), Daud (2023677)*
*Course: CS 351 — FYP Scope Document*
