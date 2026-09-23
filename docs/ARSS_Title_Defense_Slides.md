# ARSS
### Workload-Adaptive Alert Triage for Security Operations Centers

Muhammad Daniyal (2023406) · Haider Iqbal (2023416) · Syed Daud (2023677)
Supervisor: Dr. Muhammad Fawad Khan · Co-Supervisor: Miss Hadia Abbas
BS Cybersecurity, Faculty of Computer Science and Engineering, GIKI
Title Defense — September 2026

---

# The Problem

Security teams are not failing to detect threats. They are failing to keep up with what they've already detected.

- **51%** of SOC teams report feeling overwhelmed by alert volume
- Analysts resolve only **49%** of alerts assigned to them within a workday
- The gap isn't detection — it's what happens to an alert *after* it's flagged

*Source: Tariq et al., ACM Computing Surveys, 2025, DOI 10.1145/3723158*

---

# The Gap, and Our Answer

Every existing SOC tool — SIEM, SOAR, even the newest ML-scored platforms — decides what an alert deserves the same way, whether the team has 5 open cases or 500. Checked directly across 13+ major platforms: none of them let current team workload change that decision.

**ARSS is the layer that does.**

It reads an alert's risk and the SOC's current state together, and decides what should happen to it right now — while guaranteeing a genuinely severe alert can never be missed just because the team is busy.

---

# Scope and Main Modules

1. **Alert Understanding** — severity, category, confidence, built on a working two-stage detector (92.34% / 92.83%)
2. **SOC-State Awareness** — live queue depth, oldest-alert age, analyst load
3. **Adaptive Disposition Policy** — Auto-close / Defer / Escalate
4. **Severity Floor** — a hard rule: critical and high-severity alerts are never auto-suppressed
5. **Feedback Loop** — the policy adjusts based on whether past decisions were right

ARSS makes no enforcement decisions. It decides what a human sees next — not what the network does.

---

# How It Works

```
Alert Stream ──→ Alert Understanding ─┐
                                       ├──→ Adaptive Policy ──→ Auto-close / Defer / Escalate
SOC State (queue, load, age) ────────┘                                  │
                                                                         ▼
                                                        Analyst Feedback ──→ Policy Adapts
```

The severity floor sits underneath every decision — no policy output can override it for a critical or high-severity alert.

---

# What We're Delivering

- A simulated SOC-workload environment — alert arrivals, analyst capacity, live queue dynamics — built and documented, since no existing dataset captures this
- **Five triage methods, compared head-to-head:** static threshold, supervised classifier, learning-to-defer, contextual bandit, offline RL — the method is chosen by evidence, not assumed upfront
- **A falsifiable test:** does workload-awareness reduce analyst burden without increasing missed high-severity alerts, against a workload-blind baseline
- A working prototype, evaluated against that hypothesis, by the end of this project

---

*Draft 2 — September 24, 2026. Rebuilt for the confirmed 10-minute Presentation 1 format (5 min presenting, 5 min Q&A) and the locked workload-adaptive triage direction. Supersedes Draft 1's Block/Isolate/MITRE-reward architecture in full.*
