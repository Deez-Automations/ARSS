# 🛡️ ARSS — Autonomous Response System for SOC

![Status](https://img.shields.io/badge/Status-Research%20Phase-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **A workload-adaptive alert-triage system. It decides what happens to a security alert, close it, hold it in a queue, or send it to a human, based on the alert's risk and how overloaded the SOC team currently is.**

---

## 🎯 The Problem

SOC analysts routinely receive more alerts than they can review:

- **51%** of SOC teams report feeling overwhelmed by alert volume.
- **49%** of alerts assigned to an analyst get resolved within a workday.
- **78%** of companies cut SOC staffing by 50%+ on weekends and holidays.
- **52%** of organizations report ransomware attacks specifically targeting those windows.

This isn't a detection failure. Modern detection tools reliably flag real threats. The unresolved problem sits downstream, at the point of deciding what to actually do with an alert, under conditions where team capacity shrinks exactly when attackers are most active.

---

## ❓ Why ARSS — Hasn't This Been Solved?

Checked directly against the technical documentation of more than a dozen major commercial platforms, Splunk, Microsoft Sentinel, IBM QRadar, Cortex XSOAR, Google SecOps, CrowdStrike, Elastic, Wazuh, and others, including the newest "agentic" AI offerings: **none of them let the team's current backlog change what happens to an alert.** A playbook or scoring model behaves identically whether the team has five open cases or five hundred.

The gap isn't entirely unclaimed in research either, and ARSS doesn't pretend otherwise. The closest published work either only *suggests* a decision to a human and never acts on its own, or treats analyst capacity as a fixed constant that doesn't change during a run. No system has been shown to decide on its own, autonomously, from a live, changing picture of SOC workload.

> ARSS reads an alert's risk together with the SOC's current state, and decides, automatically, what happens to it. A hard safety rule guarantees a genuinely severe alert is never the one that waits.

---

## 🏗️ Where ARSS Sits

```
Alerts (from SIEM / detection & correlation layer)
        │
        ▼
    [ ARSS ]   ← workload-adaptive triage layer
        │
        ▼
  Human SOC Analyst
```

ARSS sits between the alerts a SIEM produces and the analyst who would otherwise review every one of them. It does not replace detection, and it does not perform network enforcement (blocking, isolating), those remain the job of the tools already built for that purpose.

---

## 🧩 System Architecture

ARSS is composed of six functional components:

1. **Ingestion** — normalizes incoming alerts from different source formats (Splunk is the primary target).
2. **Alert Understanding** — scores each alert for risk, attack category, and confidence.
3. **SOC Workload State** — a live, multi-signal picture of the team's current load: demand, capacity, backlog, analyst availability, utilization, and recent workload trend.
4. **Severity Floor** — a hard, non-learned rule: a high-severity alert always goes straight to a human, regardless of workload.
5. **Triage Agent** — for everything else, reads the alert and the current SOC state together and directly carries out one of three actions: **Auto-Close**, **Defer**, or **Escalate**.
6. **Feedback Loop** — every decision's outcome updates the SOC state, which the next alert is judged against.

---

## 🔬 The Core Experiment

No decision method is assumed best in advance. Four triage methods, of increasing adaptivity, are compared under identical simulated conditions:

| | Static Threshold | Supervised Learning | Contextual Bandit | Sequential RL |
|---|---|---|---|---|
| **Decides by** | Fixed risk-score cutoffs | A model that predicts the right action | Picks the action that pays off best *right now* | Weighs how each action affects *later* alerts too |
| **Learns from** | Nothing; rules are hand-set | Past alerts with known outcomes | A reward after each decision | Trial and reward in the simulated SOC |
| **Adapts over time?** | No | Only when retrained | Yes, after every decision | Yes, and plans ahead |

**Falsifiable hypothesis:** a workload-adaptive triage policy reduces analyst review burden during high-load periods, without a statistically significant increase in missed high-severity alerts, relative to workload-blind baselines.

---

## 📐 Scope

**In scope:** a simulated SOC workload environment, the four-method comparison above, a live SOC-state representation driving every decision, a hard severity floor, Splunk as the primary target SIEM format.

**Out of scope:** live production deployment, real-time packet capture, network enforcement or traffic blocking, replacing existing SIEM/EDR/SOAR tools.

---

## 📍 Current Status

Stated honestly, not aspirationally:

- **Built and trained:** an alert-scoring model that produces the risk/category/confidence values the Alert Understanding component relies on.
- **Not yet implemented:** the SOC-state simulation environment, the severity floor, and all four triage methods above. The project is currently at the design and research-verification stage for this direction; implementation has not started.

Full research documentation, literature positioning, and the current scope document live in [`docs/`](docs/).

---

## 👥 Team

| Name | ID |
|------|----|
| Muhammad Daniyal | 2023406 |
| Haider Iqbal | 2023416 |
| Syed Daud | 2023677 |

**Supervisor:** Dr. Muhammad Fawad Khan — **Co-Supervisor:** Miss Hadia Abbas

*GIKI — BS Cybersecurity, Faculty of Computer Science and Engineering — Senior Design Project*
