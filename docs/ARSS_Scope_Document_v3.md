# Ghulam Ishaq Khan Institute of Engineering Sciences and Technology (GIKI)

---

# Project Scope Document

**for**

# ARSS: Autonomous Response System for SOC

Version 3.0

*by*

| **Muhammad Daniyal** | **2023406** |
|----------------------|-------------|
| **Haider Ali**       | **2023416** |
| **Daud**             | **2023677** |

*Supervisor*
**Dr. Muhammad Fawad Khan**

*Co-Supervisor*
**Miss Hadia Abbas**

*Bachelor of Science in Cybersecurity (2023-2027)*

**Faculty of Computer Science and Engineering (FCSE)**

---

## Table of Contents

- Abstract
- 1. Introduction
  - 1.1 Problem Statement
  - 1.2 Problem Solution / Objectives of the Proposed System
    - 1.2.1 Objectives
- 2. Related System Analysis / Literature Review
  - 2.1 Vision Statement
- 3. Scope
- 4. Project Stakeholders and Roles
  - 4.1 References

---

## Abstract

Security Operations Centers (SOCs) receive far more alerts than analysts can meaningfully review. Tariq et al. (2025) found that 51% of SOC teams report feeling overwhelmed by alert volume, and analysts resolve only 49% of alerts assigned to them within a workday. This is not a detection failure. The tools flagging alerts are working correctly. The unresolved problem sits downstream, at the point of deciding what to actually do with each alert, under a team's real, fluctuating operational capacity. Existing automated tools, including SIEM correlation engines, SOAR playbooks, and machine-learning risk scoring, decide what an alert deserves based solely on the alert's own properties. Checked directly against the technical documentation of more than a dozen major commercial platforms, including the newest agentic offerings, none of them let a team's current workload change what happens to an alert. This project proposes ARSS, a workload-adaptive alert-triage system that reads an alert's own risk profile together with the SOC's live operational state, including queue depth, arrival rate, and analyst capacity, and decides whether that alert should be closed automatically, deferred to a queue, or escalated to a human analyst immediately. A hard, learning-independent safety rule, external to the adaptive policy, guarantees that any alert scored as genuinely severe is always escalated regardless of current workload. The disposition decision itself is evaluated across five methods of increasing complexity: a static threshold, a supervised classifier, a learning-to-defer model, a contextual bandit, and offline reinforcement learning. This comparison demonstrates the value of learned adaptation empirically against real baselines, rather than assuming it in advance. Because no existing public dataset records live SOC workload alongside alert data, the system is trained and evaluated in a purpose-built simulation environment, generated from real network traffic and grounded in published research on operator workload from security operations and adjacent fields.

---

## 1. Introduction

Security Operations Centers handle thousands of alerts daily from Intrusion Detection Systems (IDS), firewalls, and SIEM platforms. Detection technology has matured substantially. Modern classifiers, including well-tuned gradient-boosted models, reliably separate benign traffic from attacks and categorize confirmed attacks by type. The problem that remains unsolved is not detection. It is triage: deciding what actually happens to a flagged alert, under conditions where the number of alerts routinely exceeds the team's capacity to review them.

Existing tools address parts of this problem without addressing workload. SIEM platforms aggregate and correlate signals across sources. SOAR platforms go further and take real actions, including blocking and isolating, through pre-configured playbooks. Machine-learning risk scoring, rule-based and increasingly agentic, ranks or scores alerts by estimated danger. All of this is real, working technology. What none of it does, confirmed by checking the actual technical documentation of platforms including Splunk, Microsoft Sentinel, IBM QRadar, Elastic, and Google SecOps, is let a team's current backlog change the decision. A playbook or a scoring model behaves identically whether the team has five open cases or five hundred.

ARSS sits downstream of the SIEM, reading its output, and adds specifically the one input confirmed missing everywhere: the SOC's live operational state. It does not perform network enforcement. Blocking and isolating remain the responsibility of the tools already built for that purpose. ARSS's own response to an alert is a disposition decision: close it automatically, defer it to a queue, or escalate it to a human analyst now. A severity floor, sitting outside the learned decision-making entirely, guarantees this adaptivity can never come at the cost of a genuinely severe alert being missed.

### 1.1 Problem Statement

SOC analysts routinely handle more alerts than they can meaningfully review, and the gap is measured, not assumed. Over three-quarters of security teams report cutting staffing by half or more during nights, weekends, and holidays, and documented attack patterns show adversaries disproportionately timing real attacks for exactly those low-staffing windows. No existing triage mechanism, rule-based or learned, adjusts its behavior to that reality. A SOAR playbook that auto-closes low-severity alerts applies the same threshold at 3 AM on a skeleton crew as it does on a fully staffed Tuesday afternoon.

The broader idea of factoring workload into triage is not entirely unexplored. Prior work has proposed optimization-based reallocation of alerts across distributed SOC sites, and a static-capacity learning-to-defer model using real operational data. What has not been demonstrated is a system that makes the disposition decision autonomously, conditions that decision on a live, continuously updated measure of team capacity, and is evaluated as more than a replay of historical logs. That is the specific, narrow gap this project addresses, stated precisely so it can be checked rather than asserted as an unqualified claim that nobody has done this.

### 1.2 Problem Solution / Objectives of the Proposed System

ARSS is composed of six functional components. An ingestion layer normalizes incoming alerts from different source formats and determines whether an alert already carries usable severity, category, and confidence information from an upstream correlation layer, or requires scoring from raw signal. An alert-understanding component, the project's two-stage detection ensemble combining XGBoost with a Deep Neural Network, produces a danger score, an attack category, and a confidence value for alerts that require scoring. A SOC-state tracking component maintains a live, multi-signal picture of the team's current operational load, including queue depth, arrival rate, severity-weighted burden, and staleness of pending alerts. This tracking is built to be checked against a real source of truth on a schedule rather than trusted as a single, unverified running count. A severity floor, external to any learned component, escalates a genuinely severe alert immediately regardless of the state of the queue. An adaptive disposition policy, evaluated across five candidate methods, makes the actual triage call for alerts that do not trigger the floor. A feedback mechanism records whether each decision held up, and that record is used to improve the policy over time.

#### 1.2.1 Objectives

- To reuse and validate the project's existing two-stage detection ensemble (XGBoost + DNN) as the alert-scoring component, benchmarked against comparable published results on related network/IoT intrusion-detection datasets.
- To design a SOC-state representation combining alert arrival rate, queue depth, severity-weighted burden, and alert staleness, and to build a discrete-event simulation environment capable of generating realistic training and evaluation data, since no existing public dataset records live SOC workload.
- To implement a severity floor as a hard, non-learned constraint that guarantees escalation of high-severity alerts independent of the adaptive policy's output.
- To implement and empirically compare five triage-decision methods, a static threshold, a supervised classifier, a learning-to-defer model, a contextual bandit, and offline reinforcement learning, under identical simulated conditions, so that the method used in the final system is selected by evidence rather than assumed in advance.
- To test the falsifiable hypothesis that workload-adaptive triage reduces analyst review burden during periods of high alert load without a statistically significant increase in missed high-severity alerts, relative to workload-blind baselines.
- To evaluate the adaptive policy's resilience against deliberate manipulation of the workload signal, consistent with documented "Informational Denial-of-Service" attack patterns in the literature.

---

## 2. Related System Analysis / Literature Review

**Table 1: Related System Analysis with Proposed Project Solution**

| Application Name | Features | Weakness | Relevance with Proposed System |
|-----------------|----------|----------|-------------------------------|
| **Alert Fatigue Survey** (Tariq et al., ACM CSUR 2025) [1] | Systematic review; 51% of SOC teams report feeling overwhelmed, 49% alert resolution rate. | Survey only, no implementation. | Establishes the motivating problem and its scale. Bibliographic entry verified; the exact wording of the 51%/49% figures within the paper itself is pending a direct re-check past ACM's access restriction (see note under References). |
| **Lázaro et al., AIAI 2026** [2] | Supervised classifier incorporating workload features, evaluated on real GMV CERT/SOC operational data over a 16-month period. | Advisory tool. Final decisions remain with the human operator, confirmed verbatim in the paper. Evaluated via a chronological backtest explicitly designed to mimic deployment, not a live closed loop. | The closest published work to ARSS's problem. ARSS differs specifically on autonomy and live evaluation, not on the broad idea of using workload as a feature. |
| **Tong et al., AAAI 2020** [3] | RL trained adversarially against a strategic attacker under an alert-investigation budget constraint, via double-oracle equilibrium computation. | Budget is a fixed constant, never observed by the policy as state. Alert queue resets every period; no persistent, accumulating backlog. | The closest published work combining RL and adversarial training for alert allocation. ARSS differs specifically by making live capacity an observed state feature and by modeling a persistent backlog. |
| **RADAMS** (Huang & Zhu, Computers & Security 2022) [4] | RL-based attention-management policy defending against Informational Denial-of-Service (IDoS) attacks, where an attacker floods the system with low-cost feint alerts to hide real ones. | Validated only in simulation, never against real SOC data or human operators. | Formally names and models the exact adversarial threat ARSS's policy is hardened against; informs the adversarial-training approach. |
| **Shah et al.**, IEEE TIFS 2019 / IEEE TPDS 2020 [5] | Optimization-based (non-learned) reallocation of alerts across geographically distributed CSOC sites in response to site-level load. | Site-to-site load balancing, not a per-alert, per-decision workload-adaptive policy. | Real, directly relevant prior art for "capacity-aware triage" at a coarser granularity, cited honestly rather than omitted. |
| **Jalalvand et al.** (CSIRO), 2025 [6] | Deep reinforcement learning for learning-to-defer, trained with analyst feedback. | Analyst capacity modeled as a fixed time budget that does not change during a run. | Reinforces the precise novelty claim: ARSS conditions its decision on a live, changing capacity signal, which this closely related work does not. |
| **Adaptive Incident Prioritization at Scale** (Microsoft Security Research, CCS 2026) [7] | Real production system, evaluated on 1,000 customer organizations and 473,000 organization-days of queue telemetry. | Confirmed, directly from the model description: prioritization never conditions on queue depth, analyst availability, or arrival rate, despite being described as adaptive. | Independent, large-scale, real-production confirmation that the workload-blindness gap ARSS addresses is not merely a research artifact. |
| **Commercial platform survey (13+ platforms)** | Splunk, Microsoft Sentinel, IBM QRadar, Elastic, Google SecOps, and other major SOC platforms, checked directly against their own technical documentation. | Confirmed absent in every platform checked: none allow current team workload to change an alert's scoring or disposition. | Establishes that the gap ARSS addresses is real in current commercial practice, not only in the academic literature. |

### 2.1 Vision Statement

ARSS is a decision layer for the alert an analyst is about to see, not a replacement for the tools that generate or enforce a response to it. It sits between existing detection and orchestration infrastructure and the human analyst, adjusting what gets automatically closed, deferred, or escalated based on how the team's operational capacity is actually changing, while guaranteeing through a severity floor that a genuinely dangerous alert is never affected by that adjustment. The project's central claim is deliberately narrow and testable: that conditioning the disposition decision on live workload state measurably helps, tested against real alternative baselines rather than assumed, with the honest possibility that a simpler method proves sufficient.

---

## 3. Scope

ARSS covers the design, development, and evaluation of a workload-adaptive alert-triage system. The system will:

- Accept alert data from a simulated alert stream generated from real network traffic (CIC-IIoT 2025), standing in for the output of a SIEM's detection and correlation layer.
- Normalize incoming alert data into a single internal representation, with the design supporting multiple SIEM source formats. Splunk is the primary target, given its dominant market position and the comparative simplicity of its ingestion API.
- Score alerts requiring it through the project's existing two-stage detection ensemble, producing a danger score, attack category, and confidence value.
- Maintain a live, multi-signal SOC-state representation within a purpose-built discrete-event simulation environment, since no existing dataset records real SOC workload.
- Apply a severity floor that escalates high-severity alerts unconditionally, independent of the learned policy.
- Implement and compare five candidate disposition methods: static threshold, supervised classifier, learning-to-defer, contextual bandit, and offline reinforcement learning, under identical simulated conditions.
- Record decision outcomes and use them to update the adaptive policy over time.
- Evaluate the system against a falsifiable hypothesis: whether workload-adaptive triage reduces analyst review burden without a significant increase in missed high-severity alerts, relative to workload-blind baselines.

The project will focus on prototype-level implementation, evaluated in simulation rather than against a real organization's live alert stream. This is a constraint of the timeline and of the practical impossibility of a student project obtaining production SIEM access, stated plainly rather than implied otherwise. Real-time deployment, live production SIEM integration, and any form of network enforcement action are explicitly outside the current scope. Enforcement remains the responsibility of existing tools the system is designed to sit alongside, not replace. The system is designed with SIEM-format compatibility as a broader goal, and the ingestion layer's design is intended to generalize beyond the primary target platform without architectural change.

---

## 4. Project Stakeholders and Roles

- **Students (Developers):** Responsible for system design, implementation, testing, and documentation.
- **Supervisor:** Provides technical guidance, evaluates progress, and ensures academic quality.
- **SOC Analysts (End Users):** The primary beneficiaries of workload-adaptive triage, and the source of the operational reality the system is designed around.
- **Academic Institution:** Evaluates the project as part of degree requirements.

### 4.1 References

[1] S. Tariq, M. B. Chhetri, S. Nepal, and C. Paris, "Alert Fatigue in SOCs: Research Challenges and Opportunities," *ACM Computing Surveys*, vol. 57, no. 9, Article 224, 2025. DOI: 10.1145/3723158

[2] M. Lázaro, L. Álvarez-Pérez, F.-J. González-Serrano, A. Gutiérrez-López, J.-L. Álvarez-Aldana, M. Gil-López, A. Izquierdo-Núñez, and J. Montero-Santos, "AI-Driven Alert Triage in Security Operations Centers: Imbalanced Learning with Human-in-the-Loop Contextual Bias Modeling," in *Artificial Intelligence Applications and Innovations (AIAI 2026)*, IFIP Advances in Information and Communication Technology, vol. 794, Springer, Cham, 2026, pp. 150-164. DOI: 10.1007/978-3-032-30805-4_11

[3] Y. Tong, A. Laszka, C. Yan, N. Zhang, and Y. Vorobeychik, "Finding Needles in a Moving Haystack: Prioritizing Alerts with Adversarial Reinforcement Learning," *AAAI*, 2020. arXiv: 1906.08805

[4] L. Huang and Q. Zhu, "RADAMS: Resilient and Adaptive Alert and Attention Management Strategy Against Informational Denial-of-Service Attack," *Computers & Security*, 2022. arXiv: 2111.03463

[5] A. Shah, R. Ganesan, S. Jajodia, and H. Cam, "A Two-Step Approach to Optimal Selection of Alerts for Investigation in a CSOC," *IEEE Transactions on Information Forensics and Security*, 2019; A. Shah, R. Ganesan, S. Jajodia, P. Samarati, and H. Cam, "Adaptive Alert Management for Balancing Optimal Performance among Distributed CSOCs Using Reinforcement Learning," *IEEE Transactions on Parallel and Distributed Systems*, 2020.

[6] F. Jalalvand, M. B. Chhetri, S. Nepal, and C. Paris, "Adaptive Alert Prioritisation in Security Operations Centres," arXiv:2506.18462, 2025 (published version: *Information Sciences*, 2026, DOI: 10.1016/j.ins.2026.124128).

[7] Microsoft Security Research, "Adaptive Incident Prioritization for Security Operations at Scale," *ACM CCS*, 2026. arXiv: 2607.16963

**Note on this reference list:** Every citation above traces to a source checked directly during this project's research process, either full text or a verified abstract, per the project's own citation log in `docs/ARSS_Facts_and_Figures.md`. Two items from the prior version of this document have been removed pending verification: the CrowdStrike Charlotte AI commercial reference and the Gartner 2026 cybersecurity trends citation. Neither was checked against a primary source during this project's research. The earlier document is on record as having contained at least one unverified statistic previously, so neither should be reinstated without that check. Reference [1]'s bibliographic data is confirmed, but the exact 51%/49% wording inside the paper is pending a direct re-check, since ACM's access restriction blocked full-text verification during this project's research. One unconfirmed lead suggests the two figures may originate from Trend Micro and IBM industry reports respectively, cited by Tariq et al. rather than originated by them.

---

*Version 3.0, September 2026. Rewritten in full to reflect the project's locked technical direction: workload-adaptive alert triage, not autonomous network response. Version 2.0 is retained in this repository for the project's own record of how the direction evolved, not as a current or competing description of the system.*
