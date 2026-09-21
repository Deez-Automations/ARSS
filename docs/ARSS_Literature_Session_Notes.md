# ARSS — Literature Review Working Notes (Raw)
**Purpose:** The unpolished, running working notes behind the literature review — status snapshots, search-agent findings, verification reasoning, open questions. This is the "how we got there" doc. `ARSS_Literature_Review.md` and `ARSS_Research_Findings.md` are the polished, citation-ready output; this doc is the scratchpad behind them, kept because the reasoning itself is worth preserving, not just the conclusions.

---

## Status snapshot (as of September 19-20, 2026)

### The honest current count
- **`ARSS_Paper.tex` bibliography: 29 bibitems** — this is the real, current source of truth, not the standalone Literature Review/Research Findings docs, which were last substantively updated April 15, 2026 and did not pick up the July 19-20 corrections or additions until this session's edits.
- Of the 29: ~23 are genuine literature-review sources; 6 are supporting/technical citations (XGBoost, SHAP, DQN/Mnih 2015, MITRE ATT&CK itself, the CIC-IIoT 2025 dataset paper, one RL-formulation analogy paper).
- Informal target: 35 (borrowed benchmark from Daniyal's CY315 project — not a hard quota, quality over count).

### Verification depth breakdown
- **Fully read/verified (3):** Tariq et al. 2025 (downloaded PDF, full-text searched), Jalalvand et al. 2024 (downloaded PDF), RADAMS/Huang & Zhu 2022 (full 15-page PDF read via arXiv, not saved locally).
- **Abstract-verified (~19):** most of the July-September additions — checked against a real abstract/DOI, not full text.
- **Paywalled, trusted from the original April compilation, NOT independently re-verified (4):** TD3-AP, KNAP, Multi-Critic, AlertPro. This is a real gap — these four are cited on faith from a compilation pass that later turned out to contain fabrications elsewhere. Flagged as a to-do, not yet resolved.

### Best paper, two different senses
- **Highest authority/most citable:** Tariq et al. 2025 (ACM Computing Surveys, Impact Factor 23.8) — nothing else in the bibliography approaches this; it's the problem-statement anchor.
- **Most dangerous to the novelty claim / most important to pin down:** Homayoun 2026 — closest conceptually (reward encodes threat criticality/confidence/isolation cost), least verified until this session's deep-dive (see below).

---

## Citation integrity corrections made this session (Sept 19-20, 2026)

Same failure pattern as the July 19-20 audit, again: **a correct DOI/link carrying a wrong title or wrong figure.** Worth treating as a standing risk category, not a one-off.

- **MITREtrieval title was wrong.** Recorded everywhere as "Fusing BERT with MITRE ATT&CK Ontology for TTP Extraction from Threat Reports" — this is a paraphrase, not the real title. Actual: **"MITREtrieval: Retrieving MITRE Techniques From Unstructured Threat Reports by Fusion of Deep Learning and Ontology"** (IEEE TNSM, Vol. 21, No. 4, pp. 4871-4887, 2024, DOI 10.1109/TNSM.2024.3401200). Confirmed same paper via matching DOI + IEEE Xplore document ID (10539631) across IEEE Xplore, ACM DL, ResearchGate, and two university research-portal pages for the authors. Fixed in `ARSS_Paper.tex`, `ARSS_Research_Findings.md`, `ARSS_Literature_Review.md`. Left both Scope Documents untouched (see below).
- **Recommendation arising from this:** do a verbatim title-vs-DOI spot check across the remaining ~25 bibliography entries at some point. Every integrity error found across two sessions now has been this exact shape (title/figure wrong, DOI/link right) — worth assuming there could be more, not assuming this is now clean.

### Signed document still not corrected (unchanged policy, now 4 items on the list)
`docs/ARSS_Scope_Document_v2.md` — the actual signed, submitted SDP — still contains, uncorrected, on the standing team decision that fixing a signed document is a supervisor-level call, not something to silently patch:
1. "4,484 alerts/day, 67% uninvestigated" (fabricated stat)
2. RADAMS "95.89% recall, 5.86% FPR on 500K+ alerts" (fabricated figure)
3. A2C citation pointing at a mismatched title/DOI
4. MITREtrieval mistitled (found this session)

This needs a decision before Sept 28 — not fixed by this pass.

---

## Homayoun 2026 — full deep-dive (resolved this session, via agent search)

**Bibliographic facts, cross-verified across 3 independent sources** (Aalborg University research portal, springerprofessional.de, AutonomousCyber 2025 workshop program):
- Sole author: **Sajad Homayoun**, Aalborg University, Dept. of Electronic Systems.
- Venue: ESORICS 2025 International Workshops (AutonomousCyber 2025, 2nd International Workshop on Autonomous Cybersecurity), Toulouse, France, Sept 25-26, 2025. Session 2, paper 6 of 7 accepted (from 24 submissions).
- Published: Springer LNCS, *Computer Security – ESORICS 2025 International Workshops*, Part III, pp. 92-104 (2026). DOI: 10.1007/978-3-032-16165-9_6.

**Full abstract (verbatim):**
> "Security operations centers (SOCs) are increasingly turning to machine learning to help analysts manage the growing volume of alerts. Although many of these systems use static classifiers, they often lack the ability to adapt to changing threat contexts or analyst feedback. Reinforcement learning (RL) offers a way to train agents that can learn from experience and make context-aware decisions. In this work, we investigate how the reward function, rather than the algorithm itself, can influence agent behavior in simulated SOC environments. We introduce a risk-aware reward formulation that encodes operational factors such as threat criticality, confidence, and isolation cost. We then evaluate whether a standard RL agent (PPO) can learn more useful behavior purely through reward shaping. Our experiments show that reward design plays a critical role: agents trained with shaped rewards not only achieve better performance, but also demonstrate more adaptive and risk-sensitive behavior, especially under uncertainty. These findings highlight the importance of aligning reward signals with real-world decision trade-offs in practical security settings."

**What's confirmed vs. unknown:**

| Question | Finding |
|---|---|
| Algorithm | Confirmed: standard PPO. Contribution is reward shaping only, explicitly not an algorithmic change. |
| Environment | Confirmed: custom Gym-compatible SOC simulation, two profiles ("standard," "high-risk"). |
| Reward taxonomy | **Confirmed NOT MITRE ATT&CK-grounded.** Explicitly threat criticality + confidence + isolation cost — a bespoke operational taxonomy for this paper, not derived from ATT&CK. This is the key differentiator and is safe to state directly, straight from the abstract. |
| State space | Not confirmed / inaccessible from any open source. |
| Action space | Not confirmed / inaccessible. An isolate-type action almost certainly exists (it's named in the reward), but whether it's a discrete 4-action set like ARSS's or something coarser is unknown. |
| Dataset | Not confirmed — "simulated SOC environments" only, no named public dataset found. |
| Results | Qualitative only ("better performance," "more adaptive... especially under uncertainty") — no numbers recoverable from open sources. |

**Bottom line:** full text is paywalled (Springer/ACM DL login walls hit directly by the search agent) — this is a hard blocker on state/action space details, not a search failure to retry differently. What's safe to claim in the paper: Homayoun's reward is NOT MITRE-grounded (verified). What's NOT safe to claim: anything about its state or action space — leave those unstated or explicitly caveated as unverified until the team gets institutional access.

---

## New candidate papers found (2024-2026 agent search, round 2 — round 1 confirmed cancelled)

13 candidates surfaced, quality-filtered against the standing bar (real, verified, specific job in the argument, no padding). Round 1 (a separate parallel search launched the same session) was explicitly stopped/cancelled before finishing and is not recoverable — round 2 already covers the same ground, so nothing is actually missing.

**Role summary:**
- **Direct RL-for-alert-triage competitors:** an offline-RL SOC-triage benchmark (#1 below); a Splunk-integrated hybrid LLM+RL triage framework (#5).
- **Non-RL competitors:** fuzzy-logic alert prioritization (#2); active-learning alert-fatigue reduction, PACT (#3, same lead author as the already-cited Ndichu survey — legitimate newer follow-on, not a duplicate); a post-hoc confidence-calibration decision layer (#4); a tiered human-AI autonomy framework for SOCs (#6).
- **MITRE ATT&CK + RL, different sub-problem:** DRL-MD — RL for mitigation *deployment planning* grounded in ATT&CK technique relationships, not per-alert triage (#9); governance-to-mitigation RL via NIST CSF + ATT&CK (#10).
- **Reward-design theory:** "Beyond Rewards in RL for Cyber Defence" (#11) — argues *for* sparse rewards, a genuine counterpoint worth engaging rather than only citing favorably; LLM-generated reward design (#12) — useful contrast case ("invented/LLM reward" vs. ARSS's "framework-grounded reward").
- **State-space precedent (non-RL):** AlertSAGE (#7) — semantic/graph-based alert representation, supports the "categorical richness beats scalar collapse" argument without being RL itself.
- **Recent surveys for context:** a broad RL-for-network-security survey+tutorial (#8); an agentic-AI-in-cybersecurity survey (#13).

### Verified bibliographic details (Sept 21, 2026 re-verification pass)

Every entry below was independently re-confirmed via the arXiv API directly, the Crossref API, and publisher pages — not trusted from the round-2 search summary. Two title discrepancies were found and are flagged, not silently normalized (per the standing citation-verification rule).

| # | Title | Authors | Venue/Year | DOI | arXiv |
|---|---|---|---|---|---|
| 1 | A leakage-free benchmark of offline policy learning for SOC alert triage | Emmanuel Okafor | *Machine Learning with Applications* (Elsevier), 2026 | 10.1016/j.mlwa.2026.100984 | none (confirmed absent via arXiv API) |
| 2 | Risk Averse Alert Prioritization for IDS Using Subnormal Gaussian Fuzzy Models | Murat Moran | arXiv, May 2026 | none | [2605.27299](https://arxiv.org/abs/2605.27299) |
| 3 | PACT: Reducing Alert Fatigue in Low-Prevalence SOC Streams with Triggered Active Learning | Ndichu, Ban, Ozawa, Takahashi, Inoue | arXiv, May 2026 | none | [2605.22324](https://arxiv.org/abs/2605.22324) |
| 4 | Decision-Aware Trust Signal Alignment for SOC Alert Triage | Chowdhury, Tanvir | arXiv, Jan 2026 | none | [2601.04486](https://arxiv.org/abs/2601.04486) |
| 5 | Policy-Guided Threat Hunting: An LLM enabled Framework with Splunk SOC Triage | Sahay et al. (8 authors) | arXiv, v3 | none | [2603.23966](https://arxiv.org/abs/2603.23966) |
| 6 | A Unified Framework for Human AI Collaboration in Security Operations Centers with Trusted Autonomy | Mohsin, Janicke, Ibrahim, Sarker, Camtepe | ACM Trans. Internet Technology, Jul 2026 | 10.1145/3837073 | [2505.23397](https://arxiv.org/abs/2505.23397) |
| 7 | AlertSAGE: Semantic-Aware Alert Graph Embedding for Cybersecurity Incident Discovery | S. Jiang, Z. Liu, Y. Wang, Z. Zhang, H. Wang, Y. Hu (initials only — full given names unrecoverable) | SEC 2026, Springer IFIP AICT | 10.1007/978-3-032-27993-4_29 | none (confirmed absent) |
| 8 | Beyond Reinforcement Learning for Network Security: A Comprehensive Survey and Tutorial | Javadpour, Ja'fari, Taleb, Turkmen, Benzaïd | J. Information Security and Applications, vol. 96, 2026 | 10.1016/j.jisa.2025.104294 | none (confirmed absent) |
| 9 | Optimization of mitigation deployment using DRL over an enhanced ATT&CK (DRL-MD) | Liu, Guo, Ranjan, Chen | *Computing* (Springer), 2024 | 10.1007/s00607-024-01344-4 | none (confirmed absent) |
| 10 | Operationalizing Cybersecurity Governance for Mitigation Planning with Attack-Path Modeling and RL | Huff, Dale, Guduru, Singh, Li | arXiv, May 2026 | none | [2605.09792](https://arxiv.org/abs/2605.09792) |
| 11 | Beyond Rewards in Reinforcement Learning for Cyber Defence | Bates, Hicks, Mavroudis | arXiv, v3 | none (only arXiv's own blanket DOI) | [2602.04809](https://arxiv.org/abs/2602.04809) |
| 12 | LLM-Based Reward Design for DRL-Driven Autonomous Cyber Defense | Mukherjee, Chatterjee, Purvine, Fujimoto, Emerson | AAAI-26 Workshop (AICS) | none yet (workshop proceedings) | [2511.16483](https://arxiv.org/abs/2511.16483) |
| 13 | A Survey of Agentic AI and Cybersecurity: Challenges, Opportunities and Use-case Prototypes | Lazer, Aryal, Gupta, Bertino | arXiv, Jan 2026 | none | [2601.05293](https://arxiv.org/abs/2601.05293) |

**Tally:** 1 of 13 has both DOI and arXiv (#6) · 4 have DOI only, no preprint exists — confirmed arXiv-absent by direct API query, not inferred (#1, 7, 8, 9) · 8 have arXiv only, no publisher DOI yet, several still pending venue acceptance (#2, 3, 4, 5, 10, 11, 12, 13).

**Flagged, not silently fixed:**
- **#6** — arXiv's title has no hyphen ("Human AI Collaboration"), vs. "Human-AI" as originally recorded. Authors/DOI/abstract all match exactly; likely a typographic variant of the ACM-published form. Confirm before citing formally.
- **#8** — Crossref/ScienceDirect store the title in sentence case ("network security," "comprehensive" lowercase) vs. title case as originally recorded. Same likely-benign caveat.

**Status:** none of these 13 are in the formal bibliography yet — pending a decision on which 5-6 to actually fold in.

---

## The 4 never-independently-verified legacy citations — closed out (Sept 21, 2026)

SAC-AP, TD3-AP, KNAP, Multi-Critic, and AlertPro had been cited since the original April 2026 compilation without ever going through the same re-verification rigor applied to everything else. Ran a dedicated pass. Findings, worst first:

**TD3-AP — wrong DOI, not a mistitling.** `10.1016/j.cose.2024.103893` (what was recorded everywhere) resolves via Crossref to an unrelated paper by different authors (Bingu et al.). Correct DOI: **10.1016/j.cose.2024.103854** — a single-digit transposition (893 → 854), copied forward into every document without anyone clicking through until now. Worse than any prior error: a wrong title still describes a real source; a wrong DOI sends the reader to someone else's paper entirely. Real title also confirmed: "Off-policy actor-critic deep reinforcement learning methods for alert prioritization in intrusion detection systems" (adds "methods" and "in intrusion detection systems," both dropped previously).

**AlertPro — substantially mistitled.** Real title (three-way confirmed, Crossref + Semantic Scholar + dblp): "Combating alert fatigue with AlertPro: Context-aware alert prioritization using reinforcement learning for multi-step attack detection." What was recorded dropped both the paper's actual framing and its actual technical scope. Full author list corrected from "et al." to the real six names.

**KNAP and Multi-Critic — real title errors, less severe.** Both missing their actual subtitles ("...to Prioritize Alerts Generated by Intrusion Detection Systems" / "...in Intrusion Detection Systems"). Corrected.

**Open, unresolved concern on KNAP specifically:** ARSS's own paper describes KNAP as improving "sample efficiency." Secondary sources (primary abstract still paywalled, Springer login wall) instead describe its headline contribution as three defender-knowledge-level variants (D-/S-/T-KNAP) with specific defender-loss-reduction percentages — a possibly different framing. Not confirmed either way against primary text. Flagged inline in all three docs; do not resolve by guessing, resolve by getting the actual PDF.

**SAC-AP — cleanest of the five.** Correct DOI, correct authors, 30%-vs-DDPG claim confirmed directly from Semantic Scholar's primary abstract field (not a snippet). Only needed a title-prefix fix ("SAC-AP:" restored).

**Access reality check:** primary abstract text was blocked on 4 of 5 papers — SpringerLink login wall (KNAP, Multi-Critic), ScienceDirect HTTP 403 (TD3-AP, AlertPro). All quantitative figures attributed to those four in ARSS's own paper (dataset lists, percentage improvements) are currently **search-snippet corroborated only**, flagged as such at every location, not primary-text confirmed. This is now the clearest concrete case for getting real institutional/library access before the paper is finalized — not a "nice to have."

**Fixed in:** `ARSS_Paper.tex`, `ARSS_Literature_Review.md`, `ARSS_Research_Findings.md`. **Left untouched (as always):** both Scope Documents — this brings the signed document's correction backlog to 6 items (fabricated alert stat, fabricated RADAMS figure, A2C mismatch, mistitled MITREtrieval, wrong TD3-AP DOI, mistitled AlertPro).

---

## Open questions / not yet decided
- Which 5-6 of the 13 new candidates actually get added to the formal bibliography (quality > count — don't just add all 13).
- Whether/how to raise the 4 uncorrected signed-document items with Dr. Khan before Sept 28.
- Whether to chase the 4 paywalled Chavali/Wang papers via IEEE access before the defense, given time is short.
- Reward function coefficients ($\lambda_{\text{miss}}$, $C_{\text{analyst}}$, $C_{\text{biz}}$) still placeholders — a real design pass is separate work from literature review.

---

## Working notes for whoever (human or AI) picks this project back up

This section is deliberately written for the *next* session, not for a reader trying to understand ARSS itself. Two sessions in a row started with "prior session was lost, rebuilding context from scratch" — this is here so the next rebuild is faster and repeats fewer mistakes.

### The one pattern that matters most: correct DOI ≠ correct citation
Every single citation-integrity error found across both audit sessions (July 19-20 and Sept 19-20) had the exact same shape: **the DOI and publisher link were right, but the title text or a result figure attached to it was wrong** — a paraphrase, a misquote, or a mismatch. A DOI resolving to a real paper is necessary but not sufficient. The actual check that catches these errors is: pull the verbatim title from the publisher page itself (IEEE Xplore / ACM DL / ScienceDirect / SpringerLink) and diff it character-by-character against what's recorded, not just confirm "yes this DOI exists." Do this for any citation touched, not just new ones — old, previously-"verified" entries have failed this check twice now (RADAMS's figure, MITREtrieval's title).

### The signed document is off-limits for silent edits, permanently
`ARSS_Scope_Document_v2.md` was signed and submitted. Its known errors (fabricated alert-volume stat, fabricated RADAMS figure, wrong A2C citation, mistitled MITREtrieval) have been left in place across two sessions, deliberately, because correcting a signed academic document is the team's and supervisor's call, not something to fix quietly in the background. Keep flagging it as an open decision in the journal; never patch it without being asked.

### Working with this specific repo
- The project lives on a UNC network path (`\\...\GIKI\...\DTRA`). Git reports "dubious ownership" on every bare git command here — the fix is `git -c safe.directory='*' <command>` on every invocation (a per-command flag, never a saved config change; do not run `git config --global add safe.directory` even though it would "fix" this more permanently — that's a standing instruction, not just caution for this session).
- Commit author for this project, when instructed: `Muhammad Daniyal <johnnytylor88@gmail.com>` (`git commit --author="..."`), not whatever default identity is locally configured.
- When staging for a commit, never `git add -A` or `git add .` on this repo — it accumulates real landmines: binary ML model files that change without an explained reason, a supervisor's signature PDF, another team's project documents, Word lock files (`~$*.docx`). Stage an explicit file list every time, and read `git status` first to see what's actually sitting there — this repo had **months of documentation that existed only on one laptop and had never been pushed**, discovered only by actually looking.
- Pushing to GitHub on this environment requires an explicit permission grant separate from the user's instruction to push — expect a possible block on the first attempt and surface it clearly rather than silently retrying past it.

### On spawning research agents for literature search
Giving the agent the *exact* already-cited bibliography (not just "avoid duplicates") and an explicit, non-negotiable verification bar ("real first, no exceptions — never report a title from training-data memory, only from a live, confirmed search result") produced clean, well-calibrated results with honest confidence labels (full-text / abstract-verified / metadata-only) and zero fabrication. That prompt shape is worth reusing verbatim for the next literature push, not reinvented each time.

### On this team's actual state, so it doesn't get re-litigated
The idea is sound and has survived two rounds of professor scrutiny. The research/citation layer is in genuinely good shape as of this session. The implementation is not — zero lines of the redesigned RL agent exist in code. Don't let a good literature session create a false impression that the project is further along than it is; the honest gap is engineering time, not research quality.

---

*Written: September 19-20, 2026. Companion to `ARSS_Literature_Review.md` (polished) and `ARSS_RL_Concepts_Primer.md` (vocabulary reference).*
