# DTRA Research Paper Collection
## Literature Review for RL-Based Autonomous SOC Decision Making

> **Goal:** Read these papers to find gaps, understand state-of-art, and define our unique contribution.
> **Current State:** Q-Learning is too basic. Everyone uses ML→Risk Score→RL pipeline. We need novel approach.

---

## 🔴 PRIORITY 1: MUST READ (Core Understanding)

### 1. Multi-Agent RL for Cyber Defense (Survey)
- **Title:** Multi-Agent Reinforcement Learning in Cybersecurity: From Fundamentals to Applications
- **Source:** NATO Science and Technology Organization Symposium, May 2025
- **arXiv:** https://arxiv.org/abs/2501.XXXXX (search: "Multi-Agent Reinforcement Learning cybersecurity NATO 2025")
- **Why Read:** Covers MARL fundamentals, AICA agents, Cyber Gyms, scalability challenges

### 2. Entity-based RL for Network Defense (Generalization)
- **Title:** Entity-based Reinforcement Learning for Autonomous Cyber Defence
- **Source:** arXiv, October 2024
- **Link:** https://arxiv.org/abs/2410.XXXXX
- **Why Read:** Uses Transformers for policy, generalizes across network topologies. Beyond basic Q-table.

### 3. The Path to Autonomous Cyber Defense
- **Title:** The Path To Autonomous Cyber Defense
- **Source:** arXiv, April 2024
- **Link:** https://arxiv.org/abs/2404.XXXXX
- **Why Read:** Roadmap paper. Where is the field going? What problems remain unsolved?

### 4. Deep RL for Intrusion Detection (Survey)
- **Title:** Deep Reinforcement Learning Applications for Network Intrusion Detection
- **Source:** NIH/PMC, 2024
- **Link:** https://www.ncbi.nlm.nih.gov/pmc/articles/PMCXXXXXXX/
- **Why Read:** Comprehensive survey of DRL in IDS. Understand what's been done.

---

## 🟡 PRIORITY 2: ADVANCED TECHNIQUES

### 5. Offline RL for Cyber Defense Agents
- **Title:** Offline Reinforcement Learning for Autonomous Cyber Defense Agents
- **Source:** Winter Simulation Conference, January 2025
- **Link:** https://informs-sim.org/wsc25papers/XXXX.pdf
- **Why Read:** Trains agents from historical data only, no real-time environment needed. Addresses training gap.

### 6. RL in Partially Observable Networks (POMDP)
- **Title:** Reinforcement Learning of Defensive Strategies Against Attacks in Partially Observable LANs
- **Source:** Cybersecurity Journal, December 2025
- **Why Read:** Realistic scenario - defender can't see everything. Probabilistic shielding.

### 7. Quantum-Inspired Deep RL for Cyber Defense
- **Title:** Autonomous Cyber Defence by Quantum-Inspired Deep Reinforcement Learning
- **Source:** ICISSP 2025
- **Link:** https://www.scitepress.org/Papers/ICISSP/2025/XXXXX.pdf
- **Why Read:** Novel training efficiency approach. Cutting edge.

### 8. Rainbow DQN for Intrusion Detection (2025)
- **Title:** Rainbow DQN for Intrusion Detection
- **Source:** ResearchGate, 2025
- **Why Read:** Unified DRL approach (Double DQN + Dueling + PER + N-step + Distributional + Noisy Nets)

---

## 🟢 PRIORITY 3: POTENTIAL GAP AREAS

### 9. Safe RL with Constraints
- **Title:** Safe Exploration in Reinforcement Learning (Survey)
- **Source:** arXiv, 2024
- **Why Read:** How to constrain RL to avoid dangerous actions. Penalty alone isn't enough.

### 10. Natural Language Constraints for Safe RL
- **Title:** Interpreting Natural Language Constraints for Safe RL
- **Source:** NeurIPS 2024
- **Link:** https://neurips.cc/virtual/2024/poster/XXXXX
- **Why Read:** **NOVEL DIRECTION** - convert analyst's rules to constraints. Underexplored in cyber.

### 11. Inverse RL for Attacker Modeling
- **Title:** Inverse Reinforcement Learning for Adversary Behavior Modeling
- **Source:** arXiv, May 2025
- **Link:** https://arxiv.org/abs/2505.XXXXX
- **Why Read:** Learn reward from attacker behavior. Could flip to learn from DEFENDER behavior too.

### 12. Human-in-the-Loop RL for Cybersecurity
- **Title:** HITL-RL Frameworks for Risk-Sensitive Environments
- **Source:** ResearchGate, 2024-2025
- **Why Read:** **UNDEREXPLORED** - incorporating analyst feedback into RL loop. Trust + adaptation.

### 13. CyberBattleSim Environment
- **Title:** CyberBattleSim: A Gamified RL Environment for Cyber Operations
- **Source:** Microsoft Research (GitHub)
- **Link:** https://github.com/microsoft/CyberBattleSim
- **Why Read:** Industry-standard RL environment. We should benchmark against this.

---

## 🔵 PRIORITY 4: SUPPORTING KNOWLEDGE

### 14. Transfer Learning + RL for IDS
- **Title:** Transfer Learning for Cross-Network Intrusion Detection
- **Source:** ResearchGate, 2024-2025
- **Why Read:** How to train in one network, deploy in another. Generalization problem.

### 15. RL-Guided Transfer Learning for ICS
- **Title:** Adaptive Deep Learning-Based IDS for ICS/OT Environments
- **Source:** MDPI, 2025
- **Link:** https://www.mdpi.com/XXXX
- **Why Read:** Uses RL to guide fine-tuning. Novel fusion approach.

### 16. Multi-Agent Deep RL for Cyber Operations
- **Title:** Multi-Agent Deep Reinforcement Learning for Autonomous Cyber Operations
- **Source:** arXiv, October 2024
- **Link:** https://arxiv.org/abs/2410.XXXXX
- **Why Read:** MADRL with Actor-Critic. Collaborative agent defense.

### 17. Adversarial Drift in Network Security
- **Title:** Multi-Agent RL for Adversarial Drift in Network Security
- **Source:** arXiv, June 2025
- **Why Read:** How attacks evolve, how defender adapts. Continuous learning.

### 18. RL for Zero-Day Vulnerability Detection
- **Title:** Novel RL Methodology Using DQN for Zero-Day Detection
- **Source:** ResearchGate, 2024
- **Why Read:** Real-time learning without prior knowledge of vulnerabilities.

---

## 📊 SEARCH TIPS FOR DOWNLOADING

### ArXiv Papers (Free PDF)
1. Go to arxiv.org
2. Search: `"reinforcement learning" "cyber defense" OR "intrusion detection"`
3. Filter by: cs.CR (Cryptography and Security), cs.LG (Machine Learning)
4. Sort by: Submission date (newest first)

### Google Scholar
1. Search: `"reinforcement learning" "SOC" "alert triage" OR "intrusion response"`
2. Filter: Since 2024
3. Click "All versions" to find PDF links

### ResearchGate
1. Search the title directly
2. Request full-text if not available

### IEEE/ACM (If you have university access)
1. Use GIKI library portal for IEEE Xplore
2. Download via VPN if off-campus

---

## 🎯 WHAT WE'RE LOOKING FOR

### Gap Type 1: Environment
- Do papers use proper gym-like environments?
- Do agents learn continuously post-deployment?
- Is there a standard SOC simulation?

### Gap Type 2: Algorithm
- Who uses beyond basic Q-Learning?
- What about hierarchical RL? Meta-RL?
- Is there inverse RL for learning from analysts?

### Gap Type 3: Human Integration
- Does anyone use analyst feedback to improve?
- Can users correct RL decisions and have it learn?
- Is explainability tied to RL decisions (not just detection)?

### Gap Type 4: Safety
- Are there safety constraints on RL actions?
- What prevents RL from blocking legitimate traffic?
- Is there formal verification of policies?

---

## 📝 READING TEMPLATE

For each paper, document:

```markdown
## Paper: [Title]
**Authors:** 
**Year:** 
**Source:** 

### Problem
What problem do they solve?

### Method
- RL Algorithm:
- Environment:
- State Space:
- Action Space:
- Reward Function:

### Results
Key metrics and claims.

### Limitations
What they admit or we observe.

### Relevance to DTRA
How does this connect to our work?

### Potential Gap
What could we do better/differently?
```

---

*Created: February 4, 2026*
*Purpose: Literature review for DTRA research contribution*

