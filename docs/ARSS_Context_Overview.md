# ARSS — Project Context Overview

*A complete, self-contained explanation of the ARSS project, written for readers outside the team who need to understand it without prior context.*

**Project:** ARSS — Autonomous Response System for SOC
**Team:** Muhammad Daniyal (2023406), Haider Iqbal (2023416), Syed Daud (2023677)
**Supervisor:** Dr. Muhammad Fawad Khan — **Co-Supervisor:** Miss Hadia Abbas
**Program:** BS Cybersecurity, Faculty of Computer Science and Engineering, GIKI

---

## 1. What ARSS Is, in One Paragraph

A Security Operations Center (SOC) is the team that watches an organization's network around the clock for cyberattacks. Security tools raise alerts; analysts decide what to do with each one. ARSS is a research system that sits between those alerts and the analysts. Its decision is not a score or a suggestion for a human to act on, it is the disposition itself: **Auto-Close** and **Defer** are carried out directly, with no human sign-off required, while only **Escalate** and any alert that trips the severity floor are handed to a human. That disposition is decided from two things together: how dangerous the alert looks, **and** how overloaded the SOC team currently is. No major commercial platform checked during this project's research does the second part. A hard safety rule guarantees that a genuinely severe alert is always escalated to a human immediately, regardless of how busy the team is.

---

## 2. The Problem

SOC analysts routinely receive more alerts than they can review, and this is measured, not assumed:

- **51%** of SOC teams report feeling overwhelmed by alert volume.
- **49%** of alerts assigned to an analyst get resolved within a workday.
- **78%** of companies cut SOC staffing by 50% or more during nights, weekends, and holidays.
- **52%** of organizations report ransomware attacks specifically targeting weekends and holidays.

(Sources: Tariq et al., *ACM Computing Surveys*, 2025; Semperis, *2025 Ransomware Holiday Risk Report*.)

The key point: **this is not a detection problem.** Modern detection tools, including well-tuned machine-learning classifiers, reliably flag real threats. The unresolved problem sits *downstream* of detection, at the point of deciding what to actually do with an alert, under conditions where team capacity shrinks exactly when attackers are most active.

---

## 3. Why Existing Tools Don't Solve This

This project checked the actual technical documentation of more than a dozen major commercial platforms directly, not just their marketing material: **Splunk, Microsoft Sentinel, IBM QRadar, Cortex XSOAR, Google SecOps, CrowdStrike, Elastic Security, Wazuh, TheHive+Cortex, Security Onion, Graylog, OSSIM/AlienVault, and Shuffle.**

Finding, confirmed across all of them: **a playbook or scoring model behaves identically whether the team has five open cases or five hundred.** None of them let the team's current backlog change what happens to an alert.

This was re-checked specifically against CrowdStrike's newest "agentic" AI offering (Charlotte AI / Agentic SOAR) in case its broader autonomy already covered this. It doesn't: capacity/workload appears in CrowdStrike's own material only as an *output* metric ("restores 40 hours/week of analyst time"), never as an *input* that changes a decision. Its autonomy is governed by human-set presets per workflow, not live conditions.

One real, close exception worth naming honestly: Cortex XSOAR's `less-busy-user` feature **is** workload-aware, but it decides *who* handles a case, not *what happens* to the alert. That's routing, not triage, a distinction this project checked carefully because it's the most likely "but doesn't X already do this" challenge.

**The gap is also not entirely unclaimed in academic research**, and this project does not present it as one:
- Shah et al. (2019/2020) and Ghadermazi et al. (2024) already put analyst capacity into triage decisions, but with non-learned optimization methods, not reinforcement learning or an autonomously-acting policy.
- Lázaro et al. (2026) used real SOC data (63,410 alerts, 16 months) with workload features improving a triage decision, but it's a supervised classifier that advises a human, evaluated offline, not an autonomous policy validated live.

The specific, narrow, stated gap: **no autonomously-acting policy has been shown to condition its triage decision on live, real-time analyst backlog, validated as more than a replay of historical logs.**

---

## 4. The Core Idea

The same alert can and should receive a different response depending on the team's current capacity. A borderline alert on a quiet Tuesday afternoon might reasonably go to a human for review. The same alert at 3 AM on a skeleton holiday crew, with a 200-alert backlog already queued, might need to wait, or might need to be handled automatically, depending on what the evidence says actually works.

ARSS evaluates each alert's own risk **together with** the SOC's live operational state, rather than treating every alert as if the team were always equally available.

---

## 5. System Architecture

ARSS is composed of six functional components:

1. **Ingestion** — normalizes incoming alerts from different source formats (Splunk is the primary target), and checks whether an alert already carries usable severity/category/confidence from an upstream system, or needs scoring from raw signal.
2. **Alert Understanding** — the project's existing two-stage detection ensemble (XGBoost + Deep Neural Network) produces a danger score, an attack category, and a confidence value for alerts that need scoring.
3. **SOC Workload State (Dynamic State)** — a live, multi-signal picture of the team's current load: **demand** (incoming alert rate), **capacity** (analytical capacity), **backlog** (queued alerts), **analyst availability**, **utilization** (current load %), and **recent workload history** (trend over time). This is built to be checked against a real source of truth on a schedule, not trusted as a single unverified running count.
4. **Severity Floor** — a hard, non-learned rule: if an alert is high-severity, it skips the adaptive decision entirely and goes straight to a human analyst, regardless of workload. This guarantees the system's adaptivity can never cost a genuinely dangerous alert being missed.
5. **Triage Agent (Adaptive Disposition Policy)** — for alerts that don't trigger the severity floor, this component reads the alert and the current SOC state together and directly carries out one of three actions: **Auto-Close** (alert resolved, no human involved), **Defer** (kept in queue for later handling, no human involved yet), or **Escalate** (sent to a human analyst now). Auto-Close and Defer are executed outcomes, not recommendations awaiting approval; only Escalate and the severity floor route an alert to a human.
6. **Feedback Loop** — every decision's outcome is logged, the SOC state is updated (queue length, workload, analyst availability), and that updated state is what the *next* alert is judged against. This closes the loop back into the simulation and, eventually, into the policy.

---

## 6. The Core Experiment: Four Triage Methods, One Fair Comparison

ARSS's central research contribution is not "we built an RL agent." It's a controlled experimental comparison that tests whether increasing decision-making sophistication actually earns its complexity, rather than assuming a more advanced method is automatically better. No method is assumed best in advance.

| | **A. Static Threshold** | **B. Supervised Learning** | **C. Contextual Bandit** | **D. Sequential RL** |
|---|---|---|---|---|
| **Decides by** | Fixed risk-score cutoffs | A model that predicts the right action | Picks the action that pays off best *right now* | Weighs how each action affects *later* alerts too |
| **Learns from** | Nothing; rules are hand-set | Past alerts with known outcomes | A reward after each decision | Trial and reward in the simulated SOC |
| **Adapts over time?** | No | Only when retrained | Yes, after every decision | Yes, and plans ahead |

All four choose from the same three actions (Auto-Close / Defer / Escalate) under identical simulated conditions, so the comparison is fair. The ladder runs from a fixed rule to a fully adaptive, sequential learning agent specifically to answer one question empirically: **does conditioning on live SOC workload, and reasoning about a decision's downstream effects, actually reduce analyst burden without increasing missed high-severity alerts, or does a simpler method already do just as well?**

Within the Sequential RL condition, the exact algorithm (an offline method such as Conservative Q-Learning or discrete Batch-Constrained Q-Learning, or an online method such as DQN) is itself an empirical implementation choice, not assumed in advance, since offline methods risk unsafe over-optimism on actions the historical data doesn't cover well, while online methods can adapt continuously but are riskier to deploy un-validated.

**Falsifiable hypothesis:** a workload-adaptive triage policy reduces analyst review burden during high-load periods, without a statistically significant increase in missed high-severity alerts, relative to workload-blind baselines. This is written so it can fail, not just succeed.

---

## 7. Closest Prior Work and How ARSS Differs

| Work | What it does | Why it isn't the same as ARSS |
|---|---|---|
| **Lázaro et al. (2026)** | AI-driven alert triage using real SOC data, human-in-the-loop | Only *suggests* a decision; a human makes the final call. Evaluated as a backtest, not a live loop. |
| **Tong et al. (2020)** | RL for alert prioritization with adversarial training, under a fixed alert-investigation budget | The "budget" is a fixed constant the policy never observes as live state, and the queue resets every period, so real backlog never accumulates or shapes decisions. Also uses DDPG, built for continuous actions, a poor fit for discrete close/defer/escalate decisions. |
| **RADAMS (Huang & Zhu, 2022)** | RL-based defense against alert-flooding ("Informational Denial-of-Service") attacks | Its best reported result (~20% cost reduction) is the best of four tested categories under one benchmark, and that advantage can fall to zero under cheap, frequent feint attacks, the exact adversarial condition most relevant here. Validated only in simulation. |
| **Shah et al. (2019/2020)** | Non-learned, optimization-based reallocation of alerts across distributed SOC sites | Site-to-site load balancing at a coarser granularity, not a per-alert, per-decision policy. |
| **Jalalvand et al. (2025)** | Deep RL for learning-to-defer, trained with analyst feedback | Analyst capacity modeled as a *fixed* time budget that doesn't change during a run. |
| **Microsoft Adaptive Incident Prioritization (2026)** | Real production system, evaluated on 1,000 organizations | Despite being described as adaptive, confirmed directly from its own model description to never condition on queue depth, analyst availability, or arrival rate. |

Both closest papers (Lázaro and Tong) leave the same gap: **no system decides on its own, autonomously, from live SOC workload.** ARSS is built to close that specific gap, not to claim detection, alerting, or automated response in general is novel, those problems are already well-addressed by existing commercial tools.

---

## 8. Why This Is a Complex Computing Problem

| # | Attribute | Why it applies to ARSS |
|---|---|---|
| 1 | Conflicting requirements | Reducing analyst workload can conflict directly with maintaining security coverage. |
| 2 | Depth of analysis | Four triage methods are compared because no single approach is assumed optimal in advance. |
| 3 | Depth of knowledge | Requires combining cybersecurity, machine learning/reinforcement learning, and SOC workload modeling. |
| 4 | Familiarity of issues | Alert automation is well-studied; workload-conditioned, autonomous triage remains insufficiently explored. |
| 5 | Level of problem | Requires alert processing, SOC-state modeling, a decision policy, and a feedback loop to work together as one system. |
| 6 | Consequences | Incorrect triage either delays response to a genuine threat or buries analysts in unnecessary extra work. |
| 7 | Interdependence | Every decision changes the SOC workload state, which then shapes how the next alert is judged. |

---

## 9. Scope

**In scope:**
- A simulated SOC workload environment (alert generation, queue management, analyst-capacity modeling).
- Four triage methods compared under identical conditions.
- A live, multi-signal SOC-state representation used in every triage decision.
- A hard severity floor that always escalates high-severity alerts to a human.
- Splunk as the primary target SIEM format, with the ingestion design intended to generalize to others.

**Explicitly out of scope:**
- Live production deployment or real-time packet capture.
- Network enforcement or traffic blocking (blocking/isolating remain the job of existing tools ARSS sits alongside, not replaces).
- Direct replacement of existing SIEM/EDR/SOAR tools.
- Evaluation against a real organization's live alert stream (a constraint of timeline and of a student project's practical inability to obtain production SIEM access, stated plainly).

---

## 10. Current Implementation Status (as of this document)

Stated honestly, since this project's own internal discipline is to never present planned work as already done:

- **Built and trained:** the two-stage detection ensemble (XGBoost + Deep Neural Network) that produces the danger score, attack category, and confidence value. This dates from an earlier phase of the project and has been validated against comparable published benchmarks.
- **Not yet implemented:** the SOC-state simulation environment, the severity floor, and all four triage-decision methods (static threshold, supervised classifier, contextual bandit, sequential RL) described above. The current technical direction, workload-adaptive triage rather than the project's earlier, since-superseded autonomous network-response direction, was locked after a deliberate, evidence-based research reset. Implementation of the new architecture has not yet started; the project is currently at the design and research-verification stage for this direction, with literature positioning and the experimental design worked out in detail ahead of building it.

---

## 11. Key References

1. Tariq, S., Chhetri, M. B., Nepal, S., & Paris, C. (2025). Alert Fatigue in SOCs: Research Challenges and Opportunities. *ACM Computing Surveys*, 57(9), Article 224.
2. Lázaro, M., et al. (2026). AI-Driven Alert Triage in Security Operations Centers: Imbalanced Learning with Human-in-the-Loop Contextual Bias Modeling. *AIAI 2026*, IFIP AICT vol. 794, pp. 150–164.
3. Tong, Y., Laszka, A., Yan, C., Zhang, N., & Vorobeychik, Y. (2020). Finding Needles in a Moving Haystack: Prioritizing Alerts with Adversarial Reinforcement Learning. *AAAI*. arXiv:1906.08805
4. Huang, L., & Zhu, Q. (2022). RADAMS: Resilient and Adaptive Alert and Attention Management Strategy Against Informational Denial-of-Service Attack. *Computers & Security*. arXiv:2111.03463
5. Shah, A., Ganesan, R., Jajodia, S., & Cam, H. (2019/2020). Optimal alert selection and adaptive alert management for distributed CSOCs. *IEEE TIFS* / *IEEE TPDS*.
6. Microsoft Security Research (2026). Adaptive Incident Prioritization for Security Operations at Scale. *ACM CCS*. arXiv:2607.16963

*A full literature review, bibliography, and citation-verification log are available on request in `docs/ARSS_Scope_Document_v3.md` and `docs/ARSS_Facts_and_Figures.md`.*

---

*This document is a snapshot compiled from the project's internal scope and research documentation. For the most current version, contact the ARSS team.*
