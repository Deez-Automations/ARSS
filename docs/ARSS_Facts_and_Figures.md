# ARSS — Facts and Figures Reference

*Every citable number, value, and confirmed fact surfaced from the Section 1 system-design walkthrough onward — not the original literature review from earlier in the project (that's covered elsewhere). Organized by source, numbered for reference. Each entry states what was verified and how strongly (primary source read in full vs. abstract/snippet only), matching this project's standing rule: nothing gets cited without checking, after a wrong DOI and a fabricated statistic were both caught and fixed earlier in this project's history.*

---

## 1. The core problem (Section 1)

1.1. **51%** of SOC teams report feeling overwhelmed by alert volume.
1.2. Analysts resolve only **49%** of alerts assigned to them within a workday.
— Tariq et al., *ACM Computing Surveys*, 2025. DOI 10.1145/3723158. [Verified against primary text.]

1.3. **13+** major commercial SOC platforms checked directly against their own technical documentation — none let current team workload change what happens to an alert. (Splunk, Microsoft Sentinel, CrowdStrike, IBM QRadar, Elastic, Google SecOps, and others, from the project's earlier product-teardown research.)

---

## 2. Robust live-state tracking (research agent, SOC-state counter design)

2.1. Kafka's consumer lag is computed as `log-end-offset (real, queried broker state) − committed-offset (locally tracked position)` — never trusted from the local position alone. — [Conduktor](https://www.conduktor.io/glossary/consumer-lag-monitoring), [Sematext](https://sematext.com/blog/kafka-consumer-lag-offsets-monitoring/)

2.2. Industry argument that raw backlog *count* is a misleading metric on its own — a large-but-fast-draining queue is fine, a small-but-stalled one is the real problem; time-based lag (age of oldest unprocessed item) is the more reliable signal. — [WarpStream](https://www.warpstream.com/blog/the-kafka-metric-youre-not-using-stop-counting-messages-start-measuring-time)

2.3. RabbitMQ's `messages_ready` metric is documented as a live-computed gauge from actual queue state, not an incremented/decremented counter. — [RabbitMQ docs](https://www.rabbitmq.com/docs/maxlength), [Datadog](https://www.datadoghq.com/blog/rabbitmq-monitoring/)

2.4. **Recommended reconciliation cadence for a real deployment: every 60-120 seconds**, plus immediately after any service restart/reconnect — standard range for ticketing/monitoring polling and consumer-lag monitoring in practice.

2.5. Azure's Event Sourcing pattern documentation gives a structurally identical worked example: a live incrementing/decrementing seat-availability counter under concurrent events, explicitly warning that without idempotency (deduplication by event ID), the projection drifts from the real event stream. — [Microsoft Learn, Event Sourcing pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)

---

## 3. SIEM formats, metadata, and retention (research agent, SIEM integration)

### 3.1 Severity/category/confidence fields, by platform

3.1.1. **CEF**: severity as string (Unknown/Low/Medium/High/Very-High) or integer **0-10** (0-3=Low, 4-6=Medium, 7-8=High, 9-10=Very-High); mandatory `deviceEventClassId` as category ID; **no native confidence field**. — [Micro Focus CEF Implementation Standard](https://www.microfocus.com/documentation/arcsight/arcsight-smartconnectors-8.4/pdfdoc/cef-implementation-standard/cef-implementation-standard.pdf)

3.1.2. **Syslog (RFC 5424)**: severity is half of the PRI value (`facility×8 + severity`), **0=Emergency through 7=Debug** — no category, no confidence. — [RFC 5424](https://www.rfc-editor.org/rfc/rfc5424.html)

3.1.3. **Microsoft Sentinel `SecurityAlert` schema**: `AlertSeverity` (Informational/Low/Medium/High), **`ConfidenceScore`** (real, **0.0-1.0**), `ConfidenceLevel` (string), `Tactics`/`Techniques` (MITRE ATT&CK mapping) — the closest real-world match to ARSS's own danger-score/category/confidence output. — [Microsoft Learn](https://learn.microsoft.com/en-us/azure/sentinel/security-alert-schema)

3.1.4. **IBM QRadar** `GET /siem/offenses`: returns `severity`, `magnitude`, `credibility`, `relevance`, `categories[]`, `status` (OPEN/HIDDEN/CLOSED). Magnitude is explicitly computed *from* the severity/credibility/relevance combination. — [QRadar API reference](https://ibmsecuritydocs.github.io/qradar_api_20.0/20.0--siem-offenses-GET.html)

3.1.5. **Splunk Enterprise Security Risk-Based Alerting**: `risk_score = impact_score × confidence_score` — documented worked example: impact 80 × confidence 70 → risk score **56**. — [Splunk RBA docs](https://help.splunk.com/en/splunk-enterprise-security-8/administer/8.6/risk-based-alerting)

### 3.2 Retention periods, verified per platform (correcting a previously-used inaccurate "commonly 30-90 days" claim)

| Platform | Verified default | Source |
|---|---|---|
| Splunk Enterprise (self-hosted) | `frozenTimePeriodInSecs` default = **188,697,600 seconds ≈ 6 years** | [indexes.conf reference](https://help.splunk.com/en/splunk-enterprise/administer/admin-manual/10.4/configuration-file-reference/10.4.0-configuration-file-reference/indexes.conf) |
| Splunk Cloud Platform | **90 days** uncompressed, extendable via paid Archive | [Splunk Cloud Service Details](https://docs.splunk.com/Documentation/SplunkCloud/9.3.2408/Service/SplunkCloudservice) |
| Microsoft Sentinel / Log Analytics | **90 days free**, extendable to **2 years (730 days)** at ~$0.10/GB/month | [Sentinel billing docs](https://learn.microsoft.com/en-us/azure/sentinel/billing) |
| IBM QRadar (events/flows) | **30 days**, then deleted absent custom retention buckets | [QRadar 7.5 Data retention](https://www.ibm.com/docs/en/qsip/7.5.0?topic=tasks-data-retention) |
| IBM QRadar (offenses) | Configurable up to ~2 years; specific default **unconfirmed** — flagged, do not cite without direct verification | — |
| Elastic/Elasticsearch | **No platform-wide default** — indefinite if unmanaged; some subsystems (Kibana event log, APM) default to 90 days | [ILM overview](https://www.elastic.co/docs/manage-data/lifecycle/index-lifecycle-management) |

### 3.3 Integration friction

3.3.1. Microsoft Sentinel REST API: requires OAuth2 via Microsoft Entra ID app registration + client-credentials flow, plus an actual RBAC role grant — real IT-admin-mediated setup, not just an API key. Documented throttling around **10,000 items/minute** on at least the threat-intel indicator endpoint.

3.3.2. IBM QRadar: SEC-token auth, no publicly documented numeric rate limit — IBM's own guidance is to avoid tight polling loops.

### 3.4 Historical bootstrapping precedent

3.4.1. Etcibasi, Dobos & Koksal, "Organizational Security Resource Estimation via Vulnerability Queueing," arXiv:2604.10250 (2026) — reconstructs organizational cyber-workload trajectories solely from bug-report/fix and discovery/patch timestamps, on real multi-year private enterprise cyber-ticket data, reporting **91-96% accuracy** estimating organizational resourcing from the reconstructed trajectory alone. [Verified: abstract read directly.] Confirmed as a real precedent for the timestamp-reconstruction technique itself — applying it to *pre-deployment policy calibration* (rather than after-the-fact resource estimation) appears to have no prior published precedent.

---

## 4. SOC workload representation (research agent, human-behavior modeling)

### 4.1 RADAMS — Huang & Zhu [verified in full, read via arXiv HTML]

4.1.1. *Computers & Security*, 2022. DOI 10.1016/j.cose.2022.102844.
4.1.2. Stress level formula: `y_SL^t = f_SL(n^t)`, where `n^t` = alert arrivals during the *current inspection window* — a rate, not a static count.
4.1.3. Experiments used synthetic 24-hour SOC shifts, **400 alerts/hour** Poisson arrival rate assumption.
4.1.4. **Validation status: simulation-only.** No user study, no physiological data, no real SOC log.

### 4.2 Microsoft Security Research — "Adaptive Incident Prioritization for Security Operations at Scale," CCS 2026 [verified in full, arxiv.org/html/2607.16963v1]

4.2.1. Evaluated on **1,000 customer organizations'** expert-reviewed queues.
4.2.2. **473,000** organization-day queue telemetry records.
4.2.3. Public dataset extension: **9,980 incidents across 499 organization queues** (GUIDE dataset).
4.2.4. Confirmed: prioritization model uses only incident content and global corpus statistics — **no queue depth, analyst availability, arrival rate, or handling time appears anywhere in the scoring model.**
4.2.5. Its "adaptive" mechanism (bounded tenant-feedback multiplier) is explicitly **not enabled in production**; adaptation is daily retraining on a rolling 30-day corpus for alert-type drift, not live workload.

### 4.3 Jalalvand, Baruwal Chhetri, Nepal, Paris (CSIRO Data61), 2025 [verified in full, arxiv.org/html/2506.18462]

4.3.1. Analyst capacity modeled as a **fixed, static time budget**: ~80% of an hour reviewing alerts (**~48 min/hour**).
4.3.2. Per-severity handling times: critical = **4.5 min**, high = **3.5 min** (and further severity tiers below that).
4.3.3. Evaluated on synthetic benchmark datasets: **UNSW-NB15, CICIDS2017**, approximately **2 million alerts each**, simulated **400 alerts/hour** Poisson arrivals (same figure as RADAMS — likely a borrowed assumption, not independently measured), with simulated (not real) analyst decisions.

### 4.4 Rosbach, Ganz, Ammeling, Riener, Aubreville — automation bias under time pressure, 2024 [verified in full, arxiv.org/abs/2411.00998]

4.4.1. Real controlled study: **n=28** trained pathology experts, within-subjects time-pressure manipulation.
4.4.2. Automation-bias error rate approximately **7%** under both time-pressure conditions — frequency of wrongly deferring to bad AI advice did **not** increase under pressure.
4.4.3. Severity of errors **did** increase under time pressure — the one real-human-validated result in this whole research pass linking pressure to degraded human-AI teaming, though outside cybersecurity (computational pathology).

### 4.5 Air traffic control workload research [citation-chain-confirmed via arxiv.org/html/2307.10559, foundational works not independently read]

4.5.1. Dynamic Density model — Masalonis et al., 2003.
4.5.2. NASA-TLX — Hart & Staveland, 1988.
4.5.3. SWAT — Reid & Nygren, 1988.
4.5.4. Ground truth in the citing paper: self-reported workload ratings collected **every 3 minutes**; the paper's own authors flag their collected ratings as poor quality and note a correction was required (citing Lieber, 2020).

### 4.6 Call-center queueing (Koole) [partially verified, PDF extraction incomplete]

4.6.1. Confirmed M/M/s (Erlang C) state variables: arrival rate λ, service rate μ, server count s, queue length, abandonment rate, waiting time.

### 4.7 Tier-2 sources — snippet/abstract level only, flagged as unverified leads, not settled citations

4.7.1. ACM Computing Surveys 2025, "Alert Fatigue in Security Operations Centres" — cites SIEM scale of **50-500 billion events/day**, **500-3,000 detection rules** per the search snippet only; full text not read.
4.7.2. Shah, Ganesan, Jajodia, Cam, IEEE TIFS 2019, and Shah et al., IEEE TPDS 2020 — CSOC-level alert reallocation across sites; snippet-only, needs direct verification before citing.

---

## 5. Field maturity — verified history (this session)

5.1. Erlang's original queueing-theory work dates to **1909-1917**, developed at the Copenhagen Telephone Exchange Company. — [INFORMS, History of O.R. Excellence](https://www.informs.org/Explore/History-of-O.R.-Excellence/O.R.-Methodologies/Queueing-Models)
5.2. Adopted by Bell Telephone Company and the British Post Office in the 1920s.
5.3. Became the standard tool specifically for call-center staffing in the **1980s-1990s**.
5.4. **Correction to earlier framing:** Erlang C is a mathematical/queueing model, not a psychological one — the "field maturity" claim holds, but not because of human-factors research specifically, for this field.

5.5. SOC conceptual origins trace to the **1960s-1970s**, military/government mainframe-era monitoring. — [SystemTek SOC history](https://www.systemtek.co.uk/2026/05/the-history-of-the-security-operations-center-soc-from-early-monitoring-rooms-to-ai-driven-cyber-defense/)
5.6. Enterprise/bank adoption began **after 2000**.
5.7. The field's own "golden age" — SIEM and modern SOC tooling standardizing — was **2007-2013**.
5.8. **Conclusion:** SOC as a mature, standardized discipline is roughly 15-20 years old versus call-center staffing science's 40+ years of applied practice (and 100+ years of mathematical foundation).

---

## 6. Adversarial timing of attacks — verified statistics (this session)

6.1. **78%** of companies cut SOC staffing by 50% or more during holidays and weekends.
6.2. **6%** cut SOC staffing entirely during these periods.
6.3. **44%** of respondents reduce security staff by as much as 70% on weekends/holidays.
6.4. **21%** operate a skeleton crew, cutting staff by as much as 90%.
6.5. **More than half** of all ransomware attacks in the past 12 months occurred during a holiday or weekend.
6.6. **56%** of U.S. ransomware attacks and **47%** of healthcare-specific attacks occur during weekends/holidays; **73%** of healthcare organizations cut SOC staffing by half or more during these periods.
6.7. Ransomware groups launch **52%** of their attacks during weekends specifically.
6.8. **34%** of organizations hit during a weekend/holiday attack struggled to quickly assemble their incident response team.

— [Cybersecurity Dive](https://www.cybersecuritydive.com/news/cyberattacks-weekends-holidays/636956/), [Semperis study](https://www.semperis.com/press-release/semperis-study-reveals-majority-ransomware-attacks-continue-during-holidays-weekends/)

---

## 7. Adversarial robustness of the learned policy (research agent, "attacker mind" training)

### 7.1 The attack this addresses, formally named

7.1.1. **"Informational Denial-of-Service (IDoS)" attacks** — an attacker deliberately generates a large volume of low-cost "feint" alerts to deplete a SOC's finite attention/workload capacity and hide real attacks among the noise. Formally defined and modeled in: Huang & Zhu, *Computers & Security*, 2022 (RADAMS / arXiv:2111.03463). [Verified: full text read end-to-end.]

7.1.2. **Correction to the "20% risk reduction" figure — the original framing overstated this.** "Risk" = Expected Cumulative Cost (ECuC), a discounted, dollar-denominated cost built from an author-chosen cost table (Table VII: correctly dismissing a feint = −$80, correctly escalating a real physical-layer attack = −$500, correctly escalating a real cyber-layer attack = −$300, incomplete/no response = +$100) — **this cost table has no cited empirical source**, unlike the paper's arrival-time and inspection-time parameters, which do cite references. The reduction is measured against the paper's own "default" strategy (de-emphasis filtering switched off, not a no-detection baseline). **~20% is the single best result among four tested alert categories under one fixed benchmark setup** — the other three categories reached only ~16%. The paper's own sensitivity analysis (Fig. 7a) shows this advantage **can fall to zero** when fake alerts are cheap and frequent (feint probability >80%, low feint cost) — the exact attack condition most relevant to this project's threat model. **Correct citation form: "in their case study, a learned policy reduced an internally-defined cost metric by up to ~20% in the best case, with the improvement vanishing under some adversarial conditions" — not a flat "20% risk reduction."**

### 7.2 Real, named techniques for training a policy against this

7.2.1. **SA-MDP (State-Adversarial MDP)** — Zhang, Chen, Xiao, Liu, Li, Boning, Hsieh, NeurIPS 2020 (Spotlight). Formalizes an attacker perturbing the agent's *observation* of the state, not the true state itself — the correct framing for "attacker fools the system about workload without changing real danger levels." [Verified at abstract level.]

7.2.2. **ATLA (Alternating Training with Learned Adversaries)** — Zhang, Chen, Boning, Hsieh, ICLR 2021 (arXiv:2101.08452). Trains an adversary model online, in alternation with the main policy, throughout training — not tested for weakness only after training is done. [Verified: full text read.]

7.2.3. **Double-oracle** — the game-theoretic approach used directly on alert triage (see 7.3.1): both sides iteratively compute their best response to the other's current strategy, converging toward equilibrium.

7.2.4. Explicitly tested and found weaker in the ATLA paper's own comparison: simply adding adversarial noise to the training buffer (Kos & Song 2017; Behzadan & Munir 2017 style) — described as "not sufficient to lead to a robust policy under stronger attacks."

### 7.3 Prior art directly in this domain — needs adding to the project's related-work list

7.3.1. Tong, Laszka, Yan, Zhang, Vorobeychik, **"Finding Needles in a Moving Haystack: Prioritizing Alerts with Adversarial Reinforcement Learning,"** AAAI 2020 (arXiv:1906.08805). [Verified: full text read end-to-end, both times.] An RL agent choosing which alerts to investigate under a hard budget/capacity constraint, trained against a strategic attacker via the double-oracle method. Results: beat a uniform baseline by **~50%** on network intrusion detection; beat prior game-theoretic baselines (GAIN, RIO) by **≥25%** on fraud detection; robust to attacker-budget misestimation (**±50%** error → only **5%** performance degradation); converged in **<15 iterations** empirically, though no formal convergence guarantee over infinite policy spaces.

7.3.2. **Resolved — this is the closest prior art found in the entire project and needs its own related-work entry, worded precisely.** Confirmed directly from the paper's own equations (Table I, Eq. 1-2):
- The budget `B` is a **fixed constant**, held identical across every time period within a run — it is not a live signal. Experiments sweep it across different fixed values *between* runs (e.g., 500 vs. 1500), never within one.
- **The policy never observes capacity as input at all.** Direct quote: *"the defender only observes N(k), the numbers of remaining uninvestigated alerts... we assume that the defender knows the attack budget."* The neural network's input dimension (Table II) is confirmed to be only the alert-type-count vector — budget is baked into how the action gets normalized, never fed in as a state feature.
- **The alert queue does not carry a persistent backlog forward** — confirmed from the explicit state-update rule: next period's alert count is a fresh draw of new alerts, with no term for alerts left uninvestigated from the prior period. Attack-detection status also resets each period.
- **The precise, defensible ARSS differentiation, stated honestly:** this paper's core framing ("RL agent + adversarial training + alert budget") is *not*, by itself, novel — Tong et al. already built it. The genuine difference has to rest on two specific things this paper does not have: (1) capacity as a **live, observed state feature** the policy actually reads, not just an invisible constraint; (2) a **persistent, accumulating backlog** — real queue pressure building over time, not resetting each round. ARSS's design (a continuously incrementing/decrementing counter, read by the policy alongside the alert, from Section 3 of the system-design walkthrough) already satisfies both — but this needs to stay true in the actual implementation, since a panel could name this exact paper directly.

### 7.4 Ensemble/"council" defenses — checked and found insufficient as a primary defense

7.4.1. Tramèr, Kurakin, Papernot, Goodfellow, Boneh, McDaniel, "Ensemble Adversarial Training: Attacks and Defenses," ICLR 2018 (arXiv:1705.07204) — the paper that originated "ensemble adversarial training" as a concept. Its own abstract, amended by the authors in **April 2020**, states subsequent work found more elaborate black-box attacks "could significantly enhance transferability and reduce the accuracy of our models." [Verified: abstract read in full, including the amendment.]
7.4.2. Gleave et al., "Adversarial Policies," ICLR 2020 (arXiv:1905.10615) — policies trained via self-play (a form of implicit ensemble/diverse-opponent training) were still reliably beaten by a single crafted adversarial policy, using **less than 3%** as much training compute as the victim used. [Verified at abstract level.]

### 7.5 Real, measured tradeoffs of adversarial training (from ATLA's own results tables)

7.5.1. Natural (non-attack) performance cost, confirmed with real numbers from the paper: Hopper environment, vanilla PPO natural reward **3167** vs. adversarially-trained ATLA-PPO(MLP) **2559**; Ant environment, vanilla **5687** vs. ATLA-PPO(MLP) **4894**.
7.5.2. This cost is partially recoverable with better architecture choices — their LSTM+regularization variant on HalfCheetah: **7117** (vanilla) vs. **6157** (robust variant) natural reward — a much smaller gap — while robustness under attack improved from **-660** to **+4806**.
7.5.3. **No added inference-time latency** — the robustness is trained in, not computed at runtime; the deployed policy is the same size/architecture as a non-adversarially-trained one.

---

## 8. Implementation tech stack (verified against docs/GitHub/proceedings, not marketing claims)

### 8.1 Confirmed choices

8.1.1. **Offline RL: d3rlpy.** `DiscreteCQL` and `DiscreteBCQ` confirmed at the doc/code level to implement the actual papers' math (log-sum-exp conservative penalty for CQL; imitation-network threshold formulation for discrete BCQ), not adapted continuous-action code. Latest release **v2.8.1 (2026-03-02)**, commits as recent as **2025-09-10**, Gymnasium-native.
8.1.2. **Ruled out, with evidence**: Ray RLlib — confirmed via current official docs that its CQL is continuous-actions-only and it does not implement BCQ at all. Stable-Baselines3 — confirmed not an offline-RL library. CORL — confirmed continuous-focused; maintainers direct discrete-action users elsewhere.
8.1.3. **Contextual bandit: `contextualbandits`** (david-cortes), most recent maintenance activity of the options checked (commits through 2026-06-28); **`mabwiser`** (Fidelity) as a close second.
8.1.4. **Correction**: `banditpylib` has **no Microsoft affiliation** — an attribution error introduced in this session's own research prompt, corrected by the agent against the actual repository.
8.1.5. **Simulation environment: Gymnasium**, confirmed still the maintained standard (releases through v1.3.0, 2026-04-22), both offline-RL library candidates build on it directly.
8.1.6. **Detector: XGBoost + PyTorch DNN** (not TensorFlow) — PyTorch chosen both as the more common choice for new 2025-2026 work and, more concretely, because both RL libraries above are PyTorch-based, avoiding two mismatched deep-learning runtimes in one stack.

### 8.2 SIEM/alert-format parsing — two genuine gaps, not solved by picking a library

8.2.1. **CEF: no actively maintained parsing library exists.** The only real option (`pycef`) has had no commits since **2018**. Recommended approach: adapt its parsing logic directly or write an equivalent small parser — CEF's pipe-delimited format makes this realistic.
8.2.2. **Syslog (RFC 5424)**: `syslog-rfc5424-parser` (EasyPost-maintained fork) — real, functional, grammar-based parser.
8.2.3. **Splunk HEC: not actually a gap.** No SDK needed by design — confirmed via Splunk's own docs that HEC is a simple authenticated HTTPS POST; Python's `requests` library is the standard, documented approach.
8.2.4. **Microsoft Sentinel: best-covered format** — official Microsoft SDKs confirmed (`azure-monitor-query`, `azure-mgmt-securityinsight`), both part of the official Azure SDK monorepo.
8.2.5. **IBM QRadar: no viable library, official or community.** IBM's own `qpylib` only works for code running inside QRadar's own app framework, not as an external client. The one community client found (`qradar4py`) has been abandoned since **July 2020**. Recommended approach: direct HTTP calls against QRadar's documented REST API.

### 8.3 CQL / discrete BCQ citations, precisely verified

8.3.1. **CQL**: Kumar, Zhou, Tucker, Levine, "Conservative Q-Learning for Offline Reinforcement Learning," **NeurIPS 2020** (arXiv:2006.04779). Confirmed via official NeurIPS proceedings — exactly as expected.
8.3.2. **BCQ (original, continuous)**: Fujimoto, Meger, Precup, "Off-Policy Deep Reinforcement Learning without Exploration," **ICML 2019** (arXiv:1812.02900).
8.3.3. **Discrete BCQ — correction: a separate paper, different author list.** "Benchmarking Batch Deep Reinforcement Learning Algorithms," Fujimoto, Conti, Ghavamzadeh, Pineau, arXiv:1910.01708, **NeurIPS 2019 Deep RL Workshop** (not the main conference track). Only Fujimoto carries over from the original BCQ author list. This citation must not be conflated with the continuous BCQ paper's authors.

## 9. Detector re-verification against current benchmarks (2025-2026)

9.1. **Verdict: XGBoost + DNN remains defensible; no evidence found that a different model family currently beats it for this task.** Checked against CICIoT2023, NSL-KDD, CICIDS-2017/2018, and UNSW-NB15 — gradient-boosted trees (XGBoost/LightGBM) consistently matched or beat deep tabular models (TabNet, FT-Transformer) and the newest tabular foundation models (TabPFN) on every comparable result found.

9.2. Representative verified numbers (Bouke et al., "Multi-Level Distributional Entropy for Explainable Network Intrusion Detection," arXiv:2606.29797, Table 6, full text read): NSL-KDD — XGBoost F1=**0.9878** vs. FT-Transformer F1=**0.9818**, TabNet F1=**0.9705**. CICIDS-2017 — LightGBM F1=**0.9989**, XGBoost F1=**0.9987** vs. TabNet F1=**0.9687**. UNSW-NB15 — XGBoost F1=**0.9935** vs. best DNN (FT-Transformer) F1=**0.9881**. **Framing correction**: this paper's main contribution is entropy-based feature engineering, not a dedicated tree-vs-deep-learning benchmark study — the classifier comparison above is a secondary baseline table within it (Table 6), confirmed accurate, but should not be cited as if the paper's purpose was this comparison.

9.3. **Cannot claim validation against published CIC-IIoT2025 results specifically** — the dataset is too new; essentially no independent comparative literature exists on it yet. The defensible claim is validation against the closest well-studied comparable benchmarks (9.2), not this exact dataset.

9.4. **A real, actionable precedent found, not just reassurance**: a directly comparable hybrid study (FFNN+XGBoost on CIC-IoT2023) found standalone XGBoost (**99.66%** binary / **99.31%** multiclass) matched or slightly beat their hybrid ensemble — the DNN addition did not clearly help in that case. **Recommended before the defense**: run an ablation — XGBoost alone vs. DNN alone vs. the actual soft-voting ensemble — on the project's own existing results, to confirm the ensemble earns its added complexity rather than assuming it does.

9.5. **Flagged discrepancy, needs checking**: a third-party summary described a preprocessed CIC-IIoT2025 variant with 685,671 flow samples but **22 features**, not 71. If "71 features" traces to an external source rather than the project's own engineered feature set, this needs verifying before further citation.

---

*Compiled September 24, 2026. Every figure above is traceable to the source listed beside it — where verification was only partial (abstract/snippet-level), that's stated explicitly rather than presented as equal-confidence fact.*
