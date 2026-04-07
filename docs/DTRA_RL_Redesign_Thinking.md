# DTRA RL Redesign — Core Thinking
**Date:** April 7, 2026
**Context:** FYP research direction session — identifying the fundamental flaw in current approach and defining the path forward.

---

## What DTRA Actually Is

This is not an IDS. The goal from Day 0 was to solve the **human problem** — SOC analyst burnout from alert fatigue.

The system sits here in the real-world stack:

```
Raw Traffic
→ Firewall
→ IDS/IPS (Snort, Suricata — signatures, sequence analysis)
→ SIEM (dumps thousands of alerts)
→ [DTRA sits here]
→ Human SOC Analyst
```

DTRA intercepts the already-filtered alert stream, auto-handles what's obvious, and only surfaces what genuinely needs human judgment. The three layers exist for one purpose:

- **Stage 1 (Binary):** Is this noise or a real threat?
- **Stage 2 (Categorical):** If real, what kind of attack?
- **RL Agent:** Given what we know — do we handle it automatically or does a human need to see this?

The detection layers exist purely to feed the decision layer. The RL agent is the actual product. Everything else is infrastructure.

---

## The Core Flaw

### What the RL agent is currently optimizing for:
> "Is this packet dangerous?"

### What the ML already answered:
> "Is this packet dangerous?"

**The RL agent is repeating what the detector already said.** It's dressed up as a decision, but it's just a threshold. High danger score → Block. Low danger score → Ignore. That's not a learned policy. That's an if/else statement.

### What the RL agent SHOULD optimize for:
> "Given everything I know about this alert, what action minimizes analyst interruption while maximizing threat containment?"

Those are two competing objectives. Real SOC triage lives in the tension between them:
- Block too aggressively → analyst drowns in false positive escalations
- Block too passively → real threats slip through unattended

The RL should be learning to **balance that tradeoff dynamically.** Not echoing the detector.

---

## Why The Current Reward Function Is Wrong

The current reward is purely danger-level based:

```
High danger (>70%) → reward Block/Isolate
Medium danger (40-70%) → reward Block
Low danger (<30%) → reward Ignore
```

A real analyst doesn't just care about danger level. They care about:

1. **Attack type semantics** — A recon scan at 70% confidence is not the same urgency as a MITM at 70% confidence. Same score, completely different response.
2. **Cost of being wrong** — Blocking a legitimate user has real business impact. The agent should know that.
3. **What can be auto-handled vs what needs human eyes** — Some attack types are routine and can be Blocked silently. Others need an analyst to investigate the broader context.

The current reward function has none of this. The agent learned to mirror the detector output — which means the RL layer adds zero intelligence beyond what Stage 1 already gave you.

---

## What Needs To Change

Two design-level changes. No new pipeline, no new models.

### 1. Expand the State Space

**Current state:** `danger_bucket` (integer 0-9)

The agent is flying blind. The detector just processed 71 features and produced rich output — danger score, attack category, confidence — and all the RL gets is a single bucketed number.

**Redesigned state:**
```
State = [
    danger_score,        # continuous 0.0 - 1.0, not bucketed
    attack_category,     # one-hot encoded (7 classes)
    category_confidence  # how sure Stage 2 is about the category
]
```

Now the agent knows: *"This is a MITM at 87% confidence with 0.91 danger score"* — not just *"bucket 9."*

This means Block decisions for a DoS look different from Block decisions for a MITM at the same danger level. The agent learns **category-specific response policies.** That's genuinely different from what the detector gives you.

### 2. Redesign the Reward Function

Ground the reward in the actual optimization objective — **analyst workload vs threat containment tradeoff** — using MITRE ATT&CK severity as the foundation.

**MITRE ATT&CK Severity Weights (per attack category):**

| Attack Type | MITRE Tactic | Severity Weight |
|-------------|--------------|-----------------|
| MITM | Collection / Credential Access | 1.0 (Critical) |
| Malware | Execution / Persistence | 1.0 (Critical) |
| DDoS | Impact | 0.8 (High) |
| DoS | Impact | 0.7 (High) |
| Brute Force | Credential Access | 0.6 (Medium) |
| Web Attacks | Initial Access | 0.5 (Medium) |
| Recon | Discovery | 0.3 (Low) |

**Redesigned Reward Logic:**

```
Correctly auto-handling a true attack:
    reward += MITRE_severity_weight × action_appropriateness

Escalating a false positive to analyst:
    reward -= false_positive_penalty   # analyst time wasted

Missing a real threat (Ignore on true attack):
    reward -= MITRE_severity_weight × 100   # scales with severity

Blocking legitimate traffic:
    reward -= business_disruption_cost
```

Now the agent knows: missing a MITM is catastrophically worse than missing a Recon scan. And that's not something the detector can tell it — that's knowledge about business impact and attack consequences. The RL layer is now adding intelligence the detector genuinely can't provide.

---

## Why This Is The Novel Contribution

The standard pipeline in literature:

```
Features → ML Classifier → Risk Score → RL Agent → Action
```

The RL agent in almost every paper uses the risk score as state, and optimizes for detection accuracy.

**Our redesigned pipeline:**

```
Features → Stage 1 (Binary) → Stage 2 (Category + Confidence)
                                        ↓
                    State = [score, category, confidence]
                                        ↓
                    DQN Agent (MITRE ATT&CK grounded reward)
                                        ↓
                    Optimizes for: analyst workload × threat severity tradeoff
```

**Three specific things no single paper does together:**

1. **Category-conditioned state space** — agent sees attack semantics, not just risk score
2. **MITRE ATT&CK grounded reward** — eliminates hand-crafted heuristics, ties reward to industry threat intelligence
3. **Dual objective optimization** — explicit tradeoff between analyst interruption cost and missed threat severity

On the CIC-IIoT 2025 dataset — the most recent IIoT benchmark with very few published evaluations — this is a defensible research contribution.

---

## What Stays The Same

- Stage 1 ensemble (XGBoost + DNN binary)
- Stage 2 categorizer (XGBoost + DNN, 7 classes)
- SHAP explainability layer
- Flask API and SOC dashboard
- CIC-IIoT 2025 dataset

Only the RL decision layer is being redesigned. The architecture above it doesn't change.

---

## The Contribution Statement (For Paper / Defense)

> "We propose a category-conditioned autonomous alert triage agent that operates on a semantically-rich state representation — combining threat probability, attack category, and classification confidence — rather than discretized risk buckets. The response policy is trained using a reward function grounded in MITRE ATT&CK threat severity taxonomy, explicitly optimizing the tradeoff between analyst workload reduction and missed threat cost. Evaluated on the CIC-IIoT 2025 dataset, our system demonstrates autonomous triage of X% of alerts without analyst intervention while maintaining Y% threat containment."

---

## Next Steps

- [ ] Map all 7 attack categories to MITRE ATT&CK tactics and severity weights
- [ ] Define the full state vector and verify dimensions
- [ ] Design the complete reward function with exact penalty values
- [ ] Decide: DQN or keep Q-table with expanded state? (key architectural decision)
- [ ] Find 3-5 research papers that validate each design choice
- [ ] Run baseline comparison: current RL vs redesigned RL on same test set

---

*Document created: April 7, 2026*
*Authors: Daniyal (2023406) + Haider (2023416)*
*Course: CS 351 AI Lab — FYP Research Direction*
