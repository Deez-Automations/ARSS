# ARSS — RL Concepts Primer
**Purpose:** A from-zero refresher on the reinforcement learning vocabulary needed to read ARSS's own literature review and competitor papers, tied at every step to ARSS's actual design choices — not generic RL theory for its own sake.
**Audience:** Anyone on the team returning to the project after a break, who needs to be able to open a paper abstract and understand what it's claiming without re-deriving RL from scratch.

---

## Checkpoint 0 — What RL actually is

Every RL system is one loop, repeated over and over:

**Agent looks at a situation (state) → picks an action → gets a reward (or penalty) → updates its behavior so it picks better next time.**

The formal name for this loop is a **Markov Decision Process (MDP)**. Every RL paper is a different flavor of this same loop.

**For ARSS:** the "situation" is an alert that came out of the detector. The "action" is Ignore/Log/Block/Isolate. The "reward" is whether that was the right call — a large penalty for ignoring a real MITM attack, a smaller penalty for blocking something harmless.

---

## Checkpoint 1 — The three things that define ANY RL problem

Every paper is really just making three design choices. Once you can spot these three in a paper, you understand what it's claiming.

1. **State space** — what information the agent sees before deciding.
   - *Old ARSS (pre-redesign):* a single danger bucket (0-9).
   - *New ARSS:* `[danger_score, attack_category (7-way one-hot), confidence]` — sees *what kind* of attack, not just *how dangerous*.
2. **Action space** — the menu of things the agent is allowed to do.
   - *ARSS:* Ignore / Log / Block / Isolate — four discrete choices.
3. **Reward function** — the scorecard telling the agent whether an action was good or bad, after the fact.
   - *ARSS:* tied to MITRE ATT&CK severity — missing a high-severity attack costs far more than missing a low-severity one.

Most competitor papers differ from ARSS in exactly one of these three — that's how the entire gap statement is built. When reading any paper's abstract, hunt for these three first.

---

## Checkpoint 2 — How the agent learns: Q-values

The agent keeps a running estimate, for every (state, action) pair, of "how good is it, long-term, to take this action in this state?" — the **Q-value**, written `Q(s, a)`.

After every action, the agent nudges its Q-value estimate toward what actually happened (reward received + best guess of future reward). That nudge rule is the **Bellman update**:

```
Q(s,a) ← Q(s,a) + α[R + γ·max(Q(s',a')) − Q(s,a)]
```
- α = learning rate (how fast it updates)
- γ = discount factor (how much it values future reward vs. immediate reward)

**Exploration vs. exploitation** — should the agent keep doing what it currently thinks is best ("exploit"), or occasionally try something else to check ("explore")? Papers mentioning "epsilon-greedy" or "entropy bonus" (SAC does this) are managing this tradeoff.

---

## Checkpoint 3 — Tabular Q-Learning vs. Deep Q-Network (DQN)

The single most important technical distinction in ARSS's own history — it's why the professor rejected the first approach (Feb 4, 2026 pivot).

- **Tabular Q-Learning** (what v1/v2 currently runs): a literal lookup table — one row per state, one column per action. Fine for a handful of states (danger bucket 0-9 × 4 actions = 40 cells). **Breaks down** once the state space is richer — ARSS's new state `[danger_score, category, confidence]` has effectively infinite combinations; no table can hold that.
- **Deep Q-Network (DQN):** replace the table with a neural network that takes the state as input and outputs a Q-value per action. The network *generalizes* — it can estimate a sensible Q-value even for a state it's never exactly seen, because it learns patterns, not a memorized table. **This is what ARSS's redesign commits to.**

Jargon that comes attached to DQN papers:
- **Replay buffer** — stores past experiences, re-trains on random samples from this memory instead of only the most recent step. Stabilizes training.
- **Target network** — a second, slowly-updated copy of the network used to compute the "future reward" half of the Bellman update, so the agent isn't chasing a constantly-moving target.

---

## Checkpoint 4 — Beyond DQN: algorithms in the competitor papers

DQN only works cleanly with a **discrete** action space (a fixed menu — exactly ARSS's case). Most competitor papers (SAC-AP, TD3-AP, KNAP) use different algorithms because their action space is a **continuous priority score**, not a discrete menu.

- **Policy Gradient methods** — the network directly learns a *policy* (probability of taking each action) and adjusts it to increase the probability of actions that led to good outcomes, instead of learning Q-values first.
- **Actor-Critic** — a hybrid: one network (the "actor") decides the action, a second network (the "critic") estimates how good that action was, and the critic's feedback trains the actor. Most algorithms below are actor-critic variants.
  - **SAC (Soft Actor-Critic)** — actor-critic + an entropy bonus rewarding the agent for staying exploratory. Used by SAC-AP.
  - **TD3 (Twin Delayed DDPG)** — actor-critic with tricks against overestimating action quality. Used by TD3-AP.
  - **PPO (Proximal Policy Optimization)** — a stable, popular policy-gradient method that limits how much the policy changes per update. **Used by Homayoun 2026 — ARSS's closest competitor.**

ARSS does **not** need to implement any of these — it stays with DQN because its action space is discrete. Recognizing the acronyms and knowing "actor-critic family, used because their action space is continuous" is enough.

---

## Checkpoint 5 — On-policy vs. off-policy

- **Off-policy** (DQN, SAC, TD3 — and ARSS): the agent can learn from old experience, even from an earlier version of itself. This is why the replay buffer works.
- **On-policy** (PPO, classic policy gradient): can only learn from experience collected under the *current* policy — discards old data after each update. More stable, less sample-efficient.

When a paper argues "off-policy suits alert environments better" (a claim already in ARSS's own Related Work, from TD3-AP), it means: alerts are rare/sparse events, so reusing old experience matters more than the stability on-policy provides.

---

## Checkpoint 6 — Reward shaping (sparse vs. dense)

- **Sparse reward:** feedback only at the very end of something (e.g., "breach happened or not"). Hard to learn from.
- **Dense/shaped reward:** feedback after every single action — exactly what ARSS does, since every triage decision is scored immediately against MITRE severity.

Relevant counterpoint in the literature: "Beyond Rewards in Reinforcement Learning for Cyber Defence" (Bates, Hicks, Mavroudis, arXiv 2602.04809) argues well-aligned *sparse* rewards can be more reliable than badly-shaped *dense* ones. ARSS's counterargument: its dense reward isn't arbitrarily hand-tuned — it's anchored to an external, industry-standard taxonomy (MITRE ATT&CK), which is a different, more principled kind of "dense" than an ad hoc one. Hold onto this distinction when reading that paper.

---

## Checkpoint 7 — MITRE ATT&CK, in one paragraph

A public, industry-maintained catalog of how real attackers operate, in two layers:
- **Tactics** = the attacker's *goal* at a given stage (e.g., "Credential Access," "Discovery," "Impact") — think chapter titles.
- **Techniques** = the *specific method* used to achieve that goal, nested under a tactic.

**ARSS uses tactic-level severity weights** — e.g., MITM maps to Credential Access/Collection → weight 1.0 (critical); Recon maps to Discovery → weight 0.3 (low). When a paper claims "MITRE ATT&CK-grounded," check whether it operates at the tactic level (broad severity, ARSS's approach) or the technique level (fine-grained) — a real distinction a panel may probe.

---

## Checkpoint 8 — How it all maps onto ARSS (recap table)

| RL concept | ARSS's specific choice |
|---|---|
| State space | `[danger_score, attack_category (7-way one-hot), confidence]` |
| Action space | Discrete: Ignore, Log, Block, Isolate |
| Algorithm | DQN (discrete action space → DQN, not actor-critic) |
| Reward | Dense, shaped, MITRE ATT&CK tactic-severity-weighted |
| On/off-policy | Off-policy (DQN family) |
| Exploration strategy | Not yet decided/implemented — open item |

---

## Checkpoint 9 — Quick glossary

- **MDP** — the formal state/action/reward/transition setup underlying all of RL.
- **Policy (π)** — the agent's strategy: a function from state → action (or action-probabilities).
- **Episode** — one full run from start to some end condition.
- **Discount factor (γ)** — how much the agent values future reward vs. immediate reward.
- **Convergence** — when training stabilizes and the policy stops meaningfully changing.
- **Baseline** — the simpler method a paper compares its RL agent against, to prove the RL is adding value.

---

*Compiled: September 19-20, 2026, from a team-refresher session after a months-long gap. Written to be read alongside `ARSS_Literature_Review.md` and `ARSS_Research_Findings.md` — this doc explains the vocabulary; those docs apply it to specific papers.*
