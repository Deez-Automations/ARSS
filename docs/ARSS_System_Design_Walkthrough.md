# ARSS — System Design Walkthrough

*A section-by-section understanding pass on the WHY, WHAT, and HOW of the project, done as a live back-and-forth between the team and Claude — questions asked, pushed on, and answered in the order it actually happened. Nothing here has been cleaned up or rewritten after the fact. This is the raw working session, formatted for readability, not smoothed into a summary. Where the team corrected something Claude said, the correction stands in the record, not edited away.*

*Purpose: so the whole team can read exactly how each design point was reached — the objection, the honest answer, and what's still open — instead of only seeing conclusions.*

---

## Section 1: The Problem

A Security Operations Center (SOC) is a team of people whose job is watching for cyberattacks. They don't watch raw network traffic directly — tools do that, and when something looks suspicious, the tool generates an "alert." A human then has to look at that alert and decide what it means and what to do about it.

The volume problem: these tools generate a lot of alerts. Most are false alarms or low-importance. A few are real. The team has to go through all of them to find the real ones, because you don't know which is which until someone looks.

The actual numbers, from a 2025 published study: 51% of SOC teams say they're overwhelmed by how many alerts they get. Analysts only get through 49% of what's assigned to them in a given workday. So roughly half the alerts a team is supposed to review don't get reviewed, just from volume alone.

Important distinction: this is not a detection problem. The tools that flag alerts are doing their job correctly. The failure is downstream — after an alert exists, nothing helps a human figure out what to prioritize when there are too many alerts and not enough time.

Second part of the problem, more specific: every tool currently used to help with this (SIEM, SOAR, ML-based scoring) scores an alert the same way regardless of how busy the team currently is. A tool doesn't know or care if the team has 5 open cases or 500 — it produces the same output either way. So even the "smart" existing tools don't adjust for how much capacity the team actually has left.

That's the whole problem in two parts: too many alerts for the available people, and nothing that adjusts to how bad that's gotten at any given moment.

---

## Section 2: What We're Building (The Solution)

Given that problem — too many alerts for the people available, and nothing adjusts based on how bad that's gotten right now — here's the actual response.

ARSS sits between the stream of incoming alerts and the human team. For every alert, it looks at two things together:

1. **What the alert itself looks like** — how dangerous it seems, what type of attack it resembles, how confident that assessment is.
2. **What the team's situation looks like right now** — how many alerts are already waiting, how long the oldest one has been sitting there, how loaded each analyst currently is.

Based on both of those together, it makes one of three calls on that alert:

- **Close it automatically** — not worth a human's time.
- **Put it in a queue** — worth looking at, but not urgent, deal with it when there's room.
- **Send it to a human right now** — this needs attention immediately.

The important part: the same alert can get a different call depending on when it arrives. On a quiet day, the system can afford to be more careful and flag more things for a human to check. On a day the queue is already huge, it has to be sharper about what actually deserves attention right now, because there isn't time to give everything the same careful treatment.

One fixed exception, already covered: if an alert is scored genuinely severe, it always goes to a human immediately, no matter how backed up the queue is. That rule doesn't bend based on workload.

What it does **not** do: it never blocks network traffic, isolates a device, or takes any action on the network itself. It only decides what a human sees and when they see it. Enforcement stays with whatever tools already do that job.

### Follow-up — clarifying the restriction as part of the functionality

*Team: "for the explanation of this section, clear out the restrictions covered in previous messege as they are relevant here as here were covering the functionality"*

**Why this boundary exists at all:** the earlier version of this project actually did include Block and Isolate as actions the system could take. That was the original design mistake that caused the whole project to get reset. Here's the reasoning for why it was wrong, and why the fix matters to the functionality, not just the safety story:

Blocking traffic and isolating a device are things that happen at a different layer of a company's security setup — firewalls, endpoint protection tools, intrusion prevention systems already do this job, and they need direct access to the network to do it. ARSS only ever receives an alert — a piece of information saying "something suspicious happened." It was never actually connected to the network in a way that would let it truly block or isolate anything for real. So the old design was asking the system to make decisions about actions it had no real way to carry out safely — a mismatch between what it was told to decide and what it was actually built to touch.

**What happens instead, concretely:** when ARSS decides an alert needs escalation, that decision goes to a human analyst. If that analyst then judges the threat is real and needs to be blocked or isolated, *they* use the existing tools built for that — the firewall, the endpoint protection system, whatever the company already has. ARSS's job stops at getting the right alert in front of the right person at the right time. It never performs the action itself.

**Why this is part of the functionality, not just a limitation:** it defines exactly where this system sits in the pipeline. The full chain looks like: raw traffic → detection tools flag it → it becomes an alert → **ARSS decides what happens to that alert** → if escalated, a human decides → if the human decides to act, separate enforcement tools carry it out. ARSS only ever owns one link in that chain — the decision about the alert itself. Understanding that boundary is understanding what the system actually is: a decision layer, not an enforcement layer. That's not a caveat tacked onto the functionality — it *is* the functionality, correctly scoped.

### Follow-up — the legal/governance angle on the severity floor

*Team: "not this , im talking about rementioning about why the functionality is exactly wt the legal entities expect and is excluded from any claims related to AI , e.g the severity policy"*

Recall from earlier research: companies operate under real legal deadlines — GDPR, NIS2, CIRCIA — requiring breaches to be detected and reported within a fixed time window. If a real threat gets buried and the company misses that window, that's not just a bad outcome, it's regulatory exposure, and in some of these frameworks, personal liability for named executives.

Here's the precise mechanical point: **the severity floor guarantees the AI's workload-based judgment can never be the reason a genuinely severe alert gets missed.** If an alert is correctly scored as severe, it goes to a human immediately, full stop, regardless of how busy the team is. The adaptive/learned part of the system has zero authority over that outcome — it literally cannot touch it.

**Why that excludes the system from "AI made a bad call" liability:** if something ever goes wrong — a real breach that should've been caught gets missed — there are only two possible explanations:

1. **The alert was correctly identified as severe, but the system still buried it.** The severity floor makes this outcome structurally impossible. It cannot happen, by design, not "unlikely."
2. **The alert was wrongly classified as non-severe in the first place.** This is a detection accuracy problem — the same category of risk that exists in *any* detection or scoring tool, rule-based or ML-based, that has existed in this industry for decades. It's not a new risk this project introduces.

So if a failure ever happens, the legal question becomes "was the classification accurate" — an ordinary, pre-existing question every security vendor already has to answer — instead of "did an AI autonomously decide a known-dangerous alert could wait." The second question is exactly the one that makes companies and regulators nervous about autonomous AI decision-making. The severity floor is built specifically so that question can never be asked about this system, because the AI never had the authority to make that call in the first place.

---

## Section 3: How It Works, Mechanically

The actual step-by-step path one alert takes through the system.

**Step 1 — An alert arrives.** The detector (already built, already tested at 92.34%/92.83%) reads it and produces three things: how dangerous it looks, what type of attack it resembles, and how confident that judgment is.

**Step 2 — At the same time, the system checks its own running count of the team's current state.** This isn't a one-time snapshot — it's a live number that goes up every time a new alert arrives and goes down every time one gets resolved. Alongside that: how long the oldest unresolved alert has been waiting, and how many open items each analyst currently has.

**Step 3 — The severity floor gets checked first, before anything else.** If the alert scored severe enough to trigger it, the process stops here — it goes straight to a human, no matter what the workload numbers say. This check happens before the adaptive part of the system gets any say at all.

**Step 4 — If it didn't trigger the floor, the adaptive policy makes the actual call.** It takes the alert's properties from Step 1 and the team's current state from Step 2 together, and picks one of three outcomes: close it automatically, put it in the queue, or send it to a human now.

**Step 5 — Whatever happened gets recorded.** Not just the decision itself, but eventually whether it turned out to be the right one — did a deferred alert later turn out to matter, did an auto-closed one need a second look.

**Step 6 — That record feeds back into the policy.** Over time, the system adjusts its future decisions based on whether its past ones actually held up, instead of running on a fixed set of rules that stay exactly as accurate as the day it was built.

That's one alert's full path, start to finish. It repeats continuously as alerts arrive — the queue count and analyst-load numbers from Step 2 are always current, not recalculated from scratch each time.

### Follow-up — two real design problems raised

*Team: "wouldnt the alert already come with the meta data already that you think youre going to get from the detectoer? also the running counter , IS THAT your metric to measure the soc attributes? the counter ? that can be bugedd , glitch or anything , that single mechanic cant decide complete soc metrics , this neeeds proper work because THIS is our novelity , so we have to gracefully handle it"*

**On the detector "already having" metadata:**

**Why the detector exists at all, in this project:** the dataset this project is built on (CIC-IIoT2025) gives raw network and sensor traffic — not alerts. There's no upstream tool in our test data that's already scored anything. So the detector isn't recomputing something that already exists in our data — it's *creating* the alert in the first place, playing the role that a real IDS or SIEM would play in an actual company's network. Without it, there's no alert to feed into anything downstream.

**But here's the honest open question:** in an actual company's real deployment, where ARSS plugs in after their existing SIEM, that SIEM has likely already attached some severity or category information to the alert before ARSS ever sees it. In that situation, does ARSS's "Alert Understanding" step still need to compute its own score from scratch, or should it just read and normalize whatever the upstream tool already provided? That's a real design decision that isn't fully resolved yet.

**On the counter — the critique was right, and needs a real answer, not reassurance:**

A single incrementing/decrementing number, with nothing checking it against reality, is genuinely fragile — and this is a real problem specifically *because* this is the part carrying the whole novelty claim.

What actually needs to happen, concretely:

1. **It can't be one number.** Queue depth, oldest-alert age, and per-analyst load together — not queue depth alone.
2. **The count needs to be checked against reality regularly, not trusted forever.** Periodic reconciliation: at intervals, recompute the true count from the actual source of truth and correct any drift.
3. **Impossible states need to be caught, not silently accepted.** A negative count, or an impossible jump, is a bug to flag, not a number to keep using.
4. **The two contexts are different:** in the simulated training/testing environment, the count is generated by the simulator itself — correct by construction, and the risk is ordinary software bugs, testable and fixable. In a real deployment, the count should come directly from the actual case-management system's live data — the real source of truth — rather than being reconstructed independently.

*Team: "these 2 issues are important , both are design work , after we have done all coverage of sections you will jounral plus save this wholeeeee CONVERSATION from the section1 ... so for current design decisions we will think about it after completing our sections , and work on it cuz system model is a part of defence presentation , that would be another haul , but we will get to it"*

Confirmed: both issues parked as real system-model design work, to be tackled once the full section walkthrough is done — not dropped, not patched quickly here.

---

## Section 4: Why This Differs From What Already Exists

Everything already in the market — SIEM correlation, SOAR playbooks, ML-based risk scoring — answers one question: how dangerous does this alert look, based on its own properties. That's real, working technology, not being reinvented here.

What was checked directly, against the actual technical documentation of over 13 major platforms, and confirmed absent in every single one: none of them let the team's current workload change what happens to an alert.

The precise claim, stated narrowly on purpose:

- The system **acts on its own**, not just advises a human what to do.
- It reacts to the team's **live, current** backlog, not a fixed snapshot taken once.
- It's meant to be tested by actually **running**, not just replaying old historical logs.

**Being honest about the closest real competitor:** a 2026 paper (Lázaro et al.) does something close. It uses real security-operations data and factors in workload when scoring alerts. But it's a tool that recommends a decision to a human — it doesn't make the call itself — and it was tested by replaying past records, not by running in a live setting.

### Follow-up — correcting the claim, softening the real-data claim, adding SIEM integration as a design point

*Team: "the tools also block , so you cant claim that it only says that the tools only solve the alert question absed on their properties , with the lazaro papre , it used actual soc data which is a good approach to test our model ... but we can make our simulation as good as real by working on test enviornment conditions well / also we might not even get a chance to live test on real data , so we will soften our claim of reald ata saying that it CAN work or is intended to work but havent tested due to company claims or rules ... e.g the siem integration is importatn , how well our agent integrates in any siem , understanding all siem architecture and smooth integrations so there sint any connection issue , this is also a design point"*

**Fixing the Section 4 claim:** SOAR platforms don't just score alerts — they take real actions through playbooks, including blocking and isolating. So "existing tools only answer how dangerous does this look" was wrong. They also act.

**The corrected, honest distinguishing claim:** it's not "they don't act, we do." It's narrower: whatever they do — scoring or acting — that behavior is fixed once configured, and doesn't change based on how busy the team currently is. A playbook that auto-blocks traffic when severity crosses a threshold blocks it the same way whether the team has 5 open cases or 500. That's the real, precise gap.

Worth being clear on: ARSS's own action space is deliberately *narrower* than SOAR's — it only ever chooses Auto-close / Defer / Escalate, never Block or Isolate. Enforcement already has good, mature tools. ARSS isn't trying to replace them — it's adding workload-adaptivity to the one decision nothing currently adjusts for.

**On softening the real-data claim — the right call:** the system is **intended** to work against real SOC data, following the same approach Lázaro's paper used, but it hasn't been tested that way — because getting a real company to hand over live alert access isn't something a student project can realistically obtain. Validated in simulation, designed to generalize to real deployment, not yet tested against live production data — and here's specifically why.

**SIEM integration as a real substitute for live testing:** instead of proving the system works on a real company's alerts, prove it can *plug into* a real company's stack without friction. The alert-ingestion side needs to understand and handle the formats real SIEMs actually use — CEF, Syslog, Splunk's HTTP Event Collector, Sentinel's Log Analytics API, Elastic's Common Schema — so the pipeline isn't built around one dataset's format by accident. Joins the parked design list.

### Follow-up — SIEM historical data, timestamps as a cold-start solution, validation profiles, and agent terminology

*Team: "also SIEM does have a record of alerts for last month ... so we can add a feature in agent that can read or train itself fetching that alert data ... BUT HOW would it learn the soc behaviour , it would be slow ... what if siem also has a timestamps or kind of metadata that can help us clue it ... for valdiation , we can choose highly rated soc behaviour profiles for testing it again soc workload data ... also can we refer this as agent decision making?"*

**SIEM historical data — yes, and the timestamp idea is the real answer to the cold-start question:** real SIEMs keep alert history, commonly 30-90 days, often longer for compliance. If a SIEM logs when an alert was **created** and when it was **resolved**, that's enough to reconstruct the entire historical queue-depth-over-time picture after the fact — without ever having watched it happen live. Take every alert in the last 30-90 days, mark it "open" between its creation and resolution timestamps, and you can compute exactly how backed up the queue was at any past moment. The system doesn't have to learn a new SOC's rhythm from zero — it can be pre-calibrated on that company's own recent history before it ever makes a live decision.

**The honest limit:** this solves the cold-start problem for training/calibration. It doesn't replace the live, ongoing tracking that has to keep running once deployed — that's the counter mechanism from Section 3, now with the reconciliation plan. Historical reconstruction gets it a running start; it still needs to track reality going forward. Folded into the same parked SIEM-integration item — both real-time ingestion and historical bootstrapping.

**Validation using realistic SOC profiles:** building a few distinct, well-reasoned "SOC behavior profiles" — grounded in published research on how different team sizes and maturity levels actually operate, not made up arbitrarily — and testing the agent across all of them is exactly the right way to make the simulation carry more weight in place of real data. Same idea as "make the simulation as good as real by working on test environment conditions well" — multiple realistic personas instead of one generic scenario.

**On calling it "agent decision-making":** yes, generally — with a precision point worth knowing. "Agent" in the strict technical sense means it perceives a state, chooses an action through a policy, and updates that policy based on feedback from its own past decisions. That description is guaranteed true only for the bandit and RL end of the comparison ladder. A static threshold rule doesn't learn from feedback at all. A supervised classifier sits in between, depending on whether it gets retrained. Safe usage: call the overall *system* an agent informally throughout the pitch — normal, accepted usage. If a panel asks specifically "is this an RL agent," the honest answer depends on which method actually wins the comparison, not settled yet.

### Follow-up — documentation standard and two more checklist items

*Team: "thats good , when you will combine everythign from section1 till now ... needs proper formatting and not missing any single dot and organized properly ... using soc profile is gorunded and reasearched needs more spotlight ... for hsitory continouation ... this is still a checklist to expect from us that NOT just a counter is a soc behaviour representative , we might even need to read papers to find approaches on how to learn soc behaviour from any tools cuz thats actuall human behavious learning"*

Confirmed: this live conversation stays raw and exploratory — that's intentional. The final document is a separate job: properly organized, every point captured, nothing dropped.

Two refinements folded in: SOC profiles being research-backed is a real framing point worth emphasis in the defense, not just a background detail. And representing SOC behavior is, underneath it, representing *human* behavior — its own research area. One real starting point already found without a fresh search: RADAMS's "operator stress," derived from alert arrival rate, grounded in the Yerkes-Dodson law (a real psychology concept about performance under pressure). Not a blank slate, but one paper isn't enough grounding for a system-design decision this central — stays on the checklist for when the system design/flow actually gets decided.

---

## Section 5: What's Honestly Still Open

- **The broad idea of "factor in workload" isn't brand new.** Two real papers (Shah 2019, Ghadermazi 2024) already touch it, using traditional optimization approaches rather than learning. Cited honestly, not glossed over.
- **The closest real competitor (Lázaro et al., 2026) is genuinely close.** Real operational data — a real strength. The differences are three specific, narrow things, not a claim of being first.
- **Whether a learned method actually beats a simple hand-written rule is genuinely unknown right now.** That's the actual test being run, not an assumed outcome.
- **One source still needs direct verification before it's cited as fact** — specific claims from a 2026 paper about method performance and a safety-floor precedent, never confirmed past a paywall.
- **How to represent "how busy the SOC is" isn't fully settled** — a bare counter isn't enough; the right representation is still open design work.
- **The system hasn't been tested against real company data, and won't be.** Intended to work, not proven — reasons stated honestly rather than hidden.
- **The complete system design and data flow itself isn't finalized yet.** Not a gap to hide — accurately where things stand before the design pass happens.

*Team: "very well done , no questions needed , moving on"*

---

## Section 6: What Actually Gets Delivered

- **A simulated SOC-workload environment** — alert arrivals, analyst capacity, live queue dynamics — built and documented as its own real piece of work, since no existing dataset captures this. Multiple realistic SOC profiles, grounded in published research, not arbitrary numbers.
- **Five triage methods, built and compared head-to-head** — static threshold, supervised classifier, learning-to-defer, contextual bandit, offline RL. The method that actually wins gets decided by the results, not picked in advance.
- **A falsifiable test, run and reported either way** — does workload-awareness reduce analyst burden without increasing missed high-severity alerts, compared against a workload-blind baseline. If the learned methods don't beat a simple rule, that's still a real, honest, reportable result.
- **A working prototype, evaluated against that hypothesis, by the end of the project.**

What does **not** get delivered, stated plainly: no enforcement actions — that stays with existing tools, by design. No validation against a real company's live production data — intended to work, explained honestly why it wasn't tested that way. No claim of being first to the broad idea of workload-aware triage — only the specific, narrower claim from section 4.

### Follow-up — the five methods explained properly, and SIEM integration added as a delivery goal

*Team: "five triage methods , you didnt explain it properly ... the delivery also includes siem integration which we will also demonstrate , our aim would be to make it integratable with as many siems possible ... our aim should be complete siem integration coverage as I wouldnt want it to be our obstacle"*

**The five triage methods, properly explained:**

1. **Static threshold** — a fixed, hand-set rule: "if queue depth is above X, auto-close anything below severity Y." No learning, no adjustment. This is essentially what a SOAR playbook could already do today — the baseline everything else has to actually beat.
2. **Supervised classifier** — trained on examples of what a human analyst actually decided to do with similar alerts in similar situations, and learns to predict that decision for new ones. Smarter than a fixed rule because it weighs many factors together, but treats every alert as a one-off guess — no reasoning about a sequence over time.
3. **Learning-to-defer** — a more specific version of the classifier idea: trained specifically to know when *it* should decide versus when it should hand the call to a human, based on how confident it actually is.
4. **Contextual bandit** — tries a decision, observes what happened, and adjusts based on that outcome — but treats each decision mostly on its own, not part of a long connected sequence.
5. **Offline RL** — reasons about sequences of decisions and their downstream effects, trained from a batch of past data rather than experimenting live. The one that fits the strict technical meaning of "agent."

**Why compare all five instead of assuming the fanciest wins:** each step up adds more ability to reason about nuance and consequence, but also more complexity, more data needed, and more that can silently go wrong. The comparison exists to find out where the real value actually is, not to assume it's at the top.

**SIEM integration, added as a real delivery goal:** the aim is broad, not narrow — integratable with as many SIEM platforms as realistically possible. Real friction (authentication requirements, platform-specific quirks) will only be fully known once that work starts, but the goal itself is full coverage, so it doesn't become a blocker later.

### Follow-up — why "triage," and offline RL explained properly

*Team: "the 5 triage are good but why call it triage what is a specific definiation of triage , also explain offline RL properly , i couldnt get it"*

**What "triage" actually means:** a medical term, from the French *trier* — to sort or sift. The formal definition: the process of sorting cases by urgency and severity when there isn't enough time or people to treat everyone immediately, so the most critical cases get attention first and the rest wait in order of how much they actually need it. It comes from battlefield and emergency-room medicine — a nurse at the front of an ER doesn't treat anyone, they decide who gets seen now, who can wait, and who needs a doctor immediately, because there are more patients than staff. That's exactly the shape of this problem: alerts arrive faster than analysts can review them, and someone has to sort them by urgency under that same limited capacity. "Alert triage" is already the standard industry term for this function — not a borrowed metaphor, the literal, accurate word.

**Offline RL, explained fully this time — the first pass was too compressed:**

*RL, the basic idea first:* learning through trial and error, like training a dog with treats. The system takes an action, sees what actually happens, gets a score for how good or bad that outcome was, and adjusts future behavior to get better scores over time. The key part: it reasons about *chains* of decisions, not one in isolation — closing this alert now changes how backed up the queue is for the next one, which changes what the right call is then, and so on.

*What "offline" specifically means:* normal ("online") RL learns by trying things live — take an action, see the real result right now, learn, repeat. **Offline RL learns entirely from a fixed batch of past records instead, and never tries anything live during training.** Picture a logbook from the last three months: every alert that came in, what a human decided to do with it, how busy the team was at that moment, and whether that decision turned out to be right. Offline RL studies that whole logbook and works out a better strategy purely from analyzing it, without ever experimenting on a real alert while still learning.

*Why this is the sensible choice here:* an AI that's still learning cannot be allowed to make live trial-and-error decisions on a real company's real alerts — a bad guess during "learning" could mean missing an actual attack. Offline RL avoids that entirely: all the learning happens beforehand, from historical records, before it's ever trusted with a live decision. This is exactly what the SIEM timestamp idea from the earlier follow-up would feed — that reconstructed historical logbook is precisely offline RL's training material.

---

## Part 2: System Model — Research Agents and Design Coupling

*What follows covers everything from the team launching dedicated research agents on the parked checklist items, through to the actual system model, the method choices, the tech stack, and the reward function. Same rule as Part 1: content preserved as it happened, not rewritten after the fact.*

### Three research agents launched on the parked checklist

*Team: "good , now I need you to launch few agents to start working on our system design work , we identify what we want to achive , as in this chat discussde and our approaches alll research backed , got it ?"*

Three of the five checklist items were genuinely separable research questions, launched in parallel:
1. **SOC workload representation** — digging past RADAMS for how human operator workload/capacity is modeled across security and adjacent fields.
2. **Robust live-state tracking** — real engineering patterns for keeping the SOC-state counter accurate against drift.
3. **SIEM formats and historical bootstrapping** — real alert formats/APIs, whether upstream metadata already exists, whether the timestamp-reconstruction idea has precedent.

*Team: "for contexxt , were currently exploring our options of desigining right , so after all these researches we will fine out what apporach coupliong can be used for system design"*

Confirmed: exploration phase, not committing to a final design until all research is in and the pieces get coupled together deliberately.

### Agent 2 report — robust SOC-state tracking, digested

Core recommendation: stop treating the running counter as the source of truth at all. Split into three layers — a real source of truth, a fast incremental estimate, and a reconciler that periodically recomputes the truth and treats drift as a signal, not something to silently patch. In the simulator: hard-fail invariant checks, reconciliation every episode reset and periodically mid-episode, idempotent event handling. In a real deployment: the estimate updates live on webhook events (deduplicated by ID), reconciled against the real case-management system's own API every 60-120 seconds and after any restart, with persistent drift escalated rather than quietly corrected. Independent validation found for the team's own "it can't be one number" instinct: real Kafka-monitoring practice argues raw backlog count alone is a known-bad metric — time-based lag (age of oldest item) matters just as much, which is exactly what the draft design already had (oldest-alert age alongside queue depth).

### Agent 3 report — SIEM formats, digested

**Does an alert already carry metadata?** Yes, but only at the correlation/incident layer (Sentinel Incidents, Splunk Risk-Based Alerting, QRadar Offenses) — raw event formats (bare Syslog, unenriched CEF) carry almost nothing beyond a bare severity. Recommendation: build Alert Understanding as a normalization layer with a per-connector trust-upstream-vs-recompute switch.

**Can historical timestamps reconstruct queue depth for bootstrapping?** Yes — a real, established queueing-theory technique, with a very close 2026 precedent (Etcibasi, Dobos & Koksal, arXiv:2604.10250) reconstructing organizational cyber-workload trajectories from bug-report/patch timestamps at 91-96% accuracy on real enterprise data. Their use is after-the-fact resource estimation; using the same technique for *pre-deployment policy calibration* appears to have no prior precedent — a legitimate, narrow novelty framing.

**Retention correction:** the earlier "commonly 30-90 days" claim doesn't hold — verified per platform, it ranges from 30 days (QRadar events) to 90 days (Splunk Cloud, Sentinel free tier) to 6 years (Splunk Enterprise self-hosted) to indefinite (unmanaged Elasticsearch).

**Integration friction:** Splunk HEC uses token auth with optional ack-channel complexity; Sentinel requires full OAuth2 + RBAC role grant; QRadar uses its own token system with no published rate limit; CEF/Syslog have no auth at the format level at all. One sharp trap: severity direction isn't consistent across platforms (some count up toward worse, some count down).

### Agent 1 report — SOC workload representation, digested

RADAMS re-examined more deeply: uses an arrival *rate* over a window (not a static count), folds in operator expertise, tracks staleness separately — but confirmed simulation-only, never validated against real humans. A 2026 Microsoft production system (CCS 2026, 1,000 real customer orgs, 473K org-days of data) calls itself "adaptive" and still never conditions on queue depth, analyst availability, or arrival rate anywhere in its model — strong independent corroboration of the core novelty claim. The closest SOC competitor (Jalalvand/CSIRO 2025) turned out to use a *fixed* capacity budget that never moves during a run — sharpening the gap rather than closing it. One real human-validated finding (Rosbach et al. 2024, n=28 real medical experts): time pressure doesn't make people defer to bad AI advice more often, but makes the resulting errors worse — a real justification for the severity floor staying workload-independent. Recommended additions to the SOC-state signal: arrival rate, severity-weighted burden, a capacity/utilization ratio, staleness as a distribution not just the oldest item, an analyst-expertise modifier, a trend term, and time-in-shift. Honest caveat found across every domain checked: nobody has validated that these workload proxies actually predict real human error rates in a SOC specifically — that's future work, not settled.

### Follow-up — explanation clarity, redone

*Team: "look youre again speaking unexplained language , please keep your previous level of explanation and tone so I can actually understand it"*

The three agent digests above were redone in fully plain language — no unexplained jargon, concrete phrasing throughout (e.g., "a real company Microsoft actually uses for 1,000 real companies" instead of "conditioning on live state").

### Follow-up — simulation limits and why companies haven't done this

*Team: "yeah but even for our case we are only gonna simulate on generated data , and why havent compaines actually made it possible despite of being billion dollar companies"*

Honest concession: this project has the exact same "simulation only, never tested on real people" limitation just criticized in RADAMS and the CSIRO paper — no exemption from that, and it needs saying plainly in the defense, not glossed over. On why companies haven't built this: the confirmed reason (from earlier research) is trust and liability, not lack of ideas — CISOs rank alert triage as the top thing they want automated, and it's simultaneously the least-deployed AI feature in the SOC. A further, honestly-labeled *reasoning* point (not verified fact): SOC alert traffic isn't neutral the way patients or phone calls are — some of it is generated by an adversary who may deliberately time attacks to exploit low-staffing windows.

*Team asked this be made factual, not guessed — verified via direct research:*
- **Field maturity, confirmed with real dates**: Erlang's queueing math dates to 1909-1917, adopted by Bell Telephone/British Post Office in the 1920s, standard for call-center staffing since the 1980s-1990s — over a century old at the root, ~40 years applied. SOC as a mature, standardized discipline dates only to roughly 2007-2013 (SIEM/DLP tooling standardizing) — 15-20 years old. One correction made: call-center maturity is mathematical (queueing theory), not psychological — only ATC specifically has real psychological measurement tools (NASA-TLX, 1988).
- **Adversarial timing, confirmed with real statistics**: 78% of companies cut SOC staffing 50%+ on holidays/weekends, 6% cut entirely, 21% run a skeleton crew cut up to 90%. More than half of all ransomware attacks in the past year landed on a holiday or weekend specifically. (Full figures and sources in `ARSS_Facts_and_Figures.md`, section 6.)

### The Facts and Figures reference document created

*Team: "for context, from section1 till now every single thing you searched, factual, cite it, focus on numbers, values, factual only"*

A new document, `docs/ARSS_Facts_and_Figures.md`, was created and has been maintained since as the numbered, sourced home for every verified statistic, formula, and citation surfaced across this whole design process — kept separate from this narrative walkthrough so the two serve different purposes (this document = the conversation and reasoning; that one = the numbers, quotable directly).

### Adversarial robustness — the "attacker mind" idea, verified

*Team, connecting the adversarial-timing stats to the severity floor and proposing training the policy against a simulated attacker, while flagging that a "council" of 2-3 agents might just add latency/overfitting without solving the real problem:*

Research confirmed: this is a real, named technique. **SA-MDP/ATLA** (Zhang et al., NeurIPS 2020 / ICLR 2021) trains an adversary model online, alongside the main policy, specifically for the case where an attacker perturbs the agent's *observation* without changing the true state — exactly this project's threat model. **Double-oracle** (used directly in Tong et al. 2020, see below) is the game-theoretic alternative, better matched to a strategic, budget-aware attacker. RADAMS's exact hypothesized attack — flooding with fake alerts to manufacture a false impression of overload — already has a formal name: **"Informational Denial-of-Service (IDoS)"** attacks. The council/ensemble suspicion was confirmed correct: the researchers who originated "ensemble adversarial training" as a defense later found, in their own paper's abstract, that a sufficiently adaptive attacker defeats it; a separate RL finding showed policies trained via self-play (an implicit council) were still reliably beaten by one crafted attacker using under 3% of the training compute. Real, measured tradeoff confirmed from ATLA's own results tables: adversarially-trained policies showed a real natural-performance cost on non-attack days (partially recoverable with better architecture choices), but **no added inference-time latency** — the robustness is trained in, not computed live.

### Precision deep-dive — Tong et al. 2020 and the RADAMS "20%" figure

*Team: "verdict is , the 2 faced RL agent is very riskier before its even deployed? and manipulations works parallely and equally, and that 2020 paper... needs a complete go through as it seems to be closest to ours, and against IDOS, only 20% risk reduction, what this metric represents, how? does this sound? give an explanation on only WHY did the council performed bad on our conditions when its supposed to be good"*

Answered directly: the adaptive/RL approach isn't uniquely risky by virtue of being RL — any system reacting to a live external signal it doesn't fully control has this exposure, true since the moment "react to live workload" was chosen as the core idea. Exposure is roughly equal across all five candidate methods (they all read the same signal); what's unequal is the *capacity to be hardened* — only the learned end (bandit, RL) can actually be trained to resist manipulation.

**Why the council fails, mechanically**: ensembles help when different models make different, independent mistakes on otherwise-good data — averaging cancels random error. They don't help when the *input itself* is corrupted, because every model in the council receives the identical false number and reacts to it the same way. There's nothing to disagree about. The real fix for a corrupted input is catching it at the source (the reconciliation mechanism from Agent 2's report), not adding more decision-makers downstream of the lie.

**Deep-dive results, from full end-to-end reads of both papers:**
- **Tong et al. 2020 (AAAI, arXiv:1906.08805)** — confirmed the closest prior art found in this entire project. Their "budget" is a fixed constant, never observed by the policy as input (confirmed directly from their equations and network architecture — the policy only ever sees alert-type counts), and their alert queue resets every period with no accumulating backlog. **The honest verdict, quoting the agent directly: "if ARSS's pitch stops there, this paper is a direct, damaging prior-art hit."** The genuine, defensible difference rests on two specific things this paper doesn't have: capacity as a *live, observed state feature*, and a *persistent, accumulating backlog* — both of which ARSS's design already has, but which now must be preserved precisely in implementation, since a panel could name this exact paper.
- **RADAMS's "20% risk reduction" — corrected, it was overstated.** "Risk" is a dollar-cost metric built from an author-chosen, uncited cost table. The 20% figure is the *best* of four tested categories under one benchmark setup (the other three only reached ~16%), and the paper's own sensitivity analysis shows this advantage can fall to *zero* under cheap, frequent feint attacks — the exact condition most relevant to this project's threat model. Correct citation form: "reduced an internally-defined cost metric by up to ~20% in the best case, with the improvement vanishing under some adversarial conditions," not a flat "20% risk reduction."

(Full numbers, formulas, and citations for all of the above are in `ARSS_Facts_and_Figures.md`, sections 7 and the Tong/RADAMS corrections.)

### The system model — synthesized

*Team: "good work , so this was a complete haul for the system design , so now i think were cleared so now do we have any kind of system model? system design, consdiering this complete section discussion on system model"*

Everything above was coupled into one architecture, six components: **(1) Ingestion** — two connector families (passive listeners for Syslog/CEF, authenticated pollers for HEC/Sentinel/QRadar-style APIs), each normalizing into one canonical format, with a trust-upstream-vs-recompute switch. **(2) Alert Understanding** — the existing detector, scoped to raw-source alerts. **(3) SOC-state tracking** — the enriched multi-signal state, built on the three-layer robust-tracking design. **(4) Severity floor** — checked first, external to the learned policy. **(5) Adaptive disposition policy** — the five-method comparison, hardened via adversarial co-training for the learned end. **(6) Feedback loop.**

### The six components, in plain language

*Team: "i need more clean explanation and lyman for each one cuz I confidently udnerstand it"*

1. **The front door (ingestion)** — translates whatever format a SIEM sends into one shared internal format, and checks whether the alert already comes pre-scored.
2. **Reading the alert (Alert Understanding)** — answers how dangerous, what kind, how confident — the already-built detector.
3. **Knowing how busy the team is (SOC-state tracking)** — several signals together (arrival rate, severity-weighted burden, utilization, staleness distribution, analyst expertise, trend, time-in-shift), checked against reality on a schedule so drift gets caught, not trusted blindly.
4. **The rule that never bends (severity floor)** — checked first; a genuinely dangerous alert always goes to a human, no exceptions, no matter how busy the team looks.
5. **The actual decision-maker (adaptive disposition policy)** — combines the alert's own properties with the current workload, chooses among the five compared methods by evidence, and for the learned end, is trained against a simulated attacker trying to manipulate the workload signal.
6. **Learning from what happened (feedback loop)** — outcomes get checked after the fact and feed back into the policy.

### Follow-up — normalization timing clarified

*Team: "when it check sthe format , it means it normalizes it ? or that normalization happens on next step ?"*

Normalization *is* what "checking the format" means — it happens right at ingestion, not later, because different tools use different severity scales (some ascending, some descending) and different field names, and nothing downstream should have to know which of many tools an alert came from. Separately, and only after normalization, comes the different decision of whether a usable score already exists (correlation-layer sources) or still needs computing (raw sources, handed to Alert Understanding).

### Choosing the actual models and techniques, with reasoning

*Team: "now we need to chose models and techniques , knowing that we have done alot of substantial research , we can now decide what fits us and WHY , not that this research said this is good , bnut an actual reasoning that justifies the usecase of what we use and what NOT and WHY not"*

First pass at this (criticized as "just defending" rather than teaching — see the more complete version below) covered: prioritizing the threshold, bandit, and offline RL methods for real engineering investment over supervised/learning-to-defer (which lack real labeled human-decision data and would mostly imitate a synthetic rule); choosing discrete-action offline RL algorithms (CQL/discrete BCQ) over Tong et al.'s DDPG, since DDPG fits continuous action spaces and this project's action space is discrete; choosing double-oracle over ATLA for adversarial training, since it matches the strategic, budget-aware IDoS threat model directly and is already validated on Tong et al.'s directly analogous problem; prioritizing the cheap, high-value state signals (arrival rate, severity-weighted burden, staleness distribution, trend) over the costlier ones (capacity ratio, analyst expertise, time-in-shift) for a first build; and explicitly rejecting ensembles as a primary defense and online RL as unsafe for this application.

*Team: "none of the explanation is clearing me concepts, its just defending, first tell me why not any other ML , give em a strong claim of how exactly we will prepare our dataset , which siem attributes will you idealize for trainign , i think we should go with the one which is mostly used by many pakistani orgs , than normalized at 1st step , 2nd step will make the statespace representation... if any attribute is missing , it will calcuate itself , but how? any math formula? ...than after that that is than passed for alert understanding process... but what that understanding even teaches when the real understanding of soc behaviour is on next layer?... after that it sverity layer sees if the trigger svere than I think the sverity layer should come before the soc understadnign... okay so after that if not triggered it takes defer and queue opptons, if triggered, than straight to priority panel... now explain me how RL helps here, bandit, offline RL learning, conservtive? what is conservative Q learning and descrete batch constrained q learning"*

The full, properly-taught version:

**Why RL/bandit over other ML categories at all**: most ML answers a question about one input in isolation (is this spam, what's tomorrow's weather). This problem has a chain — today's decision changes tomorrow's queue. RL/bandit methods exist specifically for that chain; ordinary classification/regression has no concept of it. A hand-derived formula was also rejected, since it would require already knowing the correct workload-to-decision relationship in advance — which is exactly the unknown this project tests.

**Dataset preparation, concretely**: CIC-IIoT2025 traffic → detector produces an alert stream (danger, category, confidence, ground truth) → fed into a discrete-event simulator (configurable analysts, handling-time distributions, live queue tracking) → produces a full historical record (arrival, decision, resolution, queue state at every moment) — this record *is* the training data, generated rather than found, run across multiple research-grounded SOC profiles rather than one scenario.

**Which SIEM to target, Pakistani orgs specifically**: flagged as genuinely unverified — not something to guess, and possibly better known through local/industry contacts than open research. Held open, not resolved.

**Pipeline reordering, validated as correct**: severity check should happen immediately after Alert Understanding, using only the alert's own score — before ever coupling in SOC-state, since a severe alert needs no workload context at all to make its call. SOC-state coupling only happens for alerts that don't trigger the floor, feeding the actual adaptive-policy decision.

**Why Alert Understanding matters even though the "real" understanding comes later**: like a doctor assessing a patient's actual symptoms before knowing how busy the ER is — that assessment is a fact about the patient, independent of context, and it's one of two things that later get combined (the other being current capacity). Neither piece alone is "the real decision" — the decision only exists once both are combined, but you can't combine something that was never computed on its own first.

**The missing-attribute formulas, with provenance stated honestly:**
- Arrival rate: λ = (alerts in a recent window) ÷ (window length) — standard queueing-theory rate estimate, same as RADAMS's own signal.
- Queue depth from timestamps: count every alert where creation ≤ t < resolution — the queue-reconstruction technique confirmed in the literature.
- Utilization ratio: ρ = λ ÷ (analysts × per-analyst rate) — the classic Erlang traffic-intensity formula.
- Severity-weighted burden: sum of danger scores of everything currently open — a direct combination of two already-established pieces, not itself a cited formula.
- Staleness distribution: mean or 90th-percentile of (now − creation time) across the open queue — standard statistics.

**RL, bandit, offline RL, and conservative methods, taught plainly**: RL learns which action leads to good long-term outcomes by watching consequences unfold, not judging one input alone. A bandit is a simpler version — like a slot machine, learn from each pull's payout, but pulling one arm doesn't change what the others pay next time; cheaper because it doesn't reason about long chains. Offline RL learns everything from one big pre-collected logbook instead of live trial and error — necessary here because an untrained system cannot safely experiment on real alerts. "Conservative" means the algorithm is built to distrust actions the historical data doesn't clearly support, instead of optimistically guessing about them — like assuming an unreviewed restaurant is great just because there's no bad review. **CQL** does this by actively pushing down the estimated value of poorly-supported actions. **Discrete BCQ** does it differently — it simply won't let the policy choose an action that wasn't reasonably common in the historical data in the first place.

### Follow-up — tech stack verification

*Team: "no its fine , can you now verify our teckstack ??"*

Verified against real docs, GitHub activity, and proceedings, not assumptions:
- **Offline RL: d3rlpy** — confirmed its DiscreteCQL/DiscreteBCQ genuinely match the papers' math; Ray RLlib ruled out (no discrete CQL, no BCQ at all), Stable-Baselines3 ruled out (not an offline-RL library), CORL ruled out (continuous-focused).
- **Contextual bandit: `contextualbandits`** (david-cortes), `mabwiser` as backup. Correction made: `banditpylib` has no Microsoft affiliation — an attribution error introduced in this session's own research prompt, caught by the agent.
- **Simulation: Gymnasium**, confirmed still the maintained standard.
- **Detector: XGBoost + PyTorch** (not TensorFlow) — both the general 2025-2026 trend and, more concretely, stack coherence with the PyTorch-based RL libraries.
- **SIEM parsing**: Sentinel best-covered (official Microsoft SDKs). Splunk HEC needs no SDK by design (plain HTTPS POST). Two genuine gaps found: **CEF** (no maintained library since 2018, needs adapting/writing one) and **QRadar** (no viable library at all, official or community — needs raw HTTP against the documented REST API).
- **Citation correction**: discrete BCQ is a separate paper from continuous BCQ, with a different author list (Fujimoto, Conti, Ghavamzadeh, Pineau, NeurIPS 2019 *workshop*, not the main track) — only Fujimoto carries over from the original (Fujimoto, Meger, Precup, ICML 2019).

### Rough-notes follow-up — MITRE scoring, floor-training-data, naming, reward formalization

*Team, via pasted rough notes: "we can call the 2 stage detector as supervised classifier, alsot he attack scoring would come from mitre? ...the agent might need to know what severe looks like... or should we keep trigger alerts completely aside from agent learning so it doesnt overfit... what would be our agent called... what is the agent chasing, any variable? how does an agent measure that the result of his action was good?... the database explanation is good and needed"* — plus a direct instruction to re-verify the detector stack.

- **"Supervised classifier" is accurate but now ambiguous** — there are two of them (the detection classifier and a possible triage-decision classifier); need distinct names going forward.
- **MITRE for scoring is fine** — only removed as the *reward*, not banned as context.
- **Severity-floor training data resolved**: the agent should never be trained to choose actions on floor-triggered alerts (it never has a real decision there, risking spurious learned patterns) — but the *fact* that severe alerts are active should still inform the SOC-state signal as context.
- **Agent naming**: offered as options, not decided — ATLAS (Adaptive Triage & Load-Aware Scheduler), SENTRY, TRIAGE-X.
- **Reward, formalized**: a small fixed cost for every escalation (real analyst time, regardless of outcome); a small positive reward for correctly auto-closing/deferring a genuinely low-risk alert; a large negative reward, scaled by severity, for auto-closing/deferring something that was actually a real attack (ground-truth-backed, since CIC-IIoT2025 has labels). The variable being optimized: expected cumulative cost — mirroring RADAMS's cost-based structure in shape, though with this project's own justified values, not borrowed numbers. The "database" is the outcome log itself: alert → decision → ground truth → cost, one row per alert.

### Follow-up — detector re-verification against 2025-2026 approaches

Verdict: **XGBoost + DNN remains defensible; nothing meaningfully better found.** Checked against CICIoT2023, NSL-KDD, CICIDS-2017/2018, UNSW-NB15 — gradient-boosted trees matched or beat deep tabular models and tabular foundation models on every comparable result. One real, actionable finding: a directly comparable hybrid study found standalone XGBoost matched or slightly beat their DNN-ensemble version — **recommended before the defense: run the XGBoost-alone vs. ensemble ablation on the project's own existing results**, since the gain isn't automatic. Also flagged: cannot claim validation against published CIC-IIoT2025 results specifically (too new, no comparative literature yet), and a feature-count discrepancy (71 vs. a third-party's 22) worth double-checking.

### Follow-up — why XGBoost wins, and untangling bandit vs. d3rlpy

*Team: "what made xgboost perform well and not that , and your explanation on choosing D3RLPY is a DCQL with contextual bandit and , bte is bandit a mechanism we use or library we use? cuz d3rlpy is a model? and bandits gets linked with RL for dealing with Discrete conservtive q learning"*

**Why XGBoost wins**: network-traffic data has no "neighborhood" structure the way images/text do (shuffling columns changes nothing), which is exactly what deep learning is built to exploit — so that strength has nothing to grab onto here. Trees don't care about a value's scale (just "above or below a threshold"), which suits messy, mixed, skewed security data natively. Trees also need less data to find good splits than deep nets need to find good patterns.

**Bandit vs. d3rlpy, corrected**: these are two of five *independent, separately-run* candidates, not linked components of one system. "Bandit" is a mechanism/category, built with the `contextualbandits` library. "Offline RL" is a different mechanism/category, built with `d3rlpy`. d3rlpy is a toolbox, not an algorithm — Discrete CQL and discrete BCQ are two specific algorithms *inside* it, both being tried for the offline-RL slot specifically, with no connection to bandit at all.

### Follow-up — how the five candidates actually produce a result

*Team: "so how they all work together for resulkt"*

They never run together. All five get tested against identical conditions (same simulated alert stream, same SOC profiles), each running its own separate, non-interacting pass, scored with the identical cost structure. After all five finish, their results get lined up side by side — that comparison table is the actual output. Whichever wins on both workload-reduction and missed-severe-alert-rate together becomes the real decision-maker; the rest stay in the writeup as the baselines proving why.

### Follow-up — the hybrid possibility and what each candidate actually contributes

*Team: "so 5 are the candidates out of which 1 will be selected? but wasnt offline RL policy needed so it can learn based on historical data as a cold start, and bandit for each step decision learning... but im just asking each of 5 have their contirbution no? i jsut cant understand how the 5 jsut happens to be there how to map em up"*

Correction to the earlier "flat comparison, pick one winner" framing: offline RL naturally fits learning from history before deployment; the bandit naturally fits continuing to learn live after deployment — these aren't just two rivals doing the same job, they suit two different phases of one possible lifecycle. The honest fuller picture: either one flat method wins outright, **or** the actual best system turns out to be a combination (offline RL for the historical head start, bandit for ongoing live refinement) — and which of those is true is itself part of what the comparison tests, not assumed either way.

**What each of the five actually isolates as a question**: threshold — is any learning needed at all? Supervised — is imitating a rule enough without learning from outcomes? Learning-to-defer — does knowing when it's unsure add value? Bandit — is per-decision outcome learning enough, kept live? Offline RL — does reasoning about long chains of consequence add value beyond the bandit's simpler view?

### Follow-up — the final map, corrected

*Team: "so youre saying bandit helps in taking decision at instance and offline policy helps in updating the policy after a run? and d3rply is the algorithm of descrete learning of RL, and learning algorithm is DCQL? can you make a map between all of 5 candiidates how they cordinae, th 5 explanation you gave got very confusing ebcaus eof prepectives"*

Two corrections: the bandit decides *and* updates together, continuously, every single step. Offline RL studies the entire completed historical record once, upfront, before ever making a live decision, then uses that fixed policy — it doesn't update "after a run" in the bandit's live sense. And again: d3rlpy is the toolbox, not an algorithm; DCQL is one candidate technique inside it, discrete BCQ is the other.

Final table, same four columns for all five, to stop the level-jumping:

| # | Approach | When it learns | Built with | Specific technique |
|---|---|---|---|---|
| 1 | Static threshold | Never — fixed rule | None needed | N/A |
| 2 | Supervised classifier | Once, upfront | Standard ML library | Trained classifier |
| 3 | Learning-to-defer | Once, upfront, plus confidence check | Same family as #2 | Defer-aware classifier |
| 4 | Contextual bandit | Continuously, live, every decision | `contextualbandits` | LinUCB / Thompson Sampling |
| 5 | Offline RL | Once, upfront, from the full historical batch | `d3rlpy` | Discrete CQL or discrete BCQ |

---

## Running Checklist of Parked Design Work — updated

### Resolved during the system-model pass (Part 2)

- [x] Alert Understanding's score-vs-normalize question — resolved with a trust-upstream-vs-recompute switch per connector, depending on whether the source is a correlation-layer or raw-layer platform
- [x] SOC-state measurement robustness — resolved with the three-layer design (source of truth / incremental tracker / reconciler), sim vs. real-deployment cadences specified
- [x] SIEM integration coverage — resolved with a concrete plan (two connector families, canonical internal format, per-vendor mapping); two genuine gaps flagged (CEF and QRadar both need custom/raw handling, no maintained library exists for either)
- [x] Research grounding for SOC-behavior representation — resolved with cross-domain findings (call-center, ED, ATC, dispatcher literature) and seven concrete signal additions; honest caveat recorded that none of it is validated against real SOC human data yet

### Resolved — SIEM target and naming

*Team: "now the part that is left, find out which siem is mostly used, and practically which one is easier, im avoidnig any codebase work right now, for the actual name, the agents name is the ARSS which is official now"*

- [x] **Naming — official**: no separate sub-name for the agent. It is ARSS, full stop.
- [x] **SIEM target, resolved**: Splunk confirmed as the dominant global platform (**45.91%** market share, vs. **15.34%** Microsoft Sentinel, **9.22%** IBM QRadar, per 6sense; 11 consecutive years as a Gartner Magic Quadrant Leader). Pakistan-specific market-share data could not be confirmed — real regulatory pressure was found (a national SOC mandate, State Bank of Pakistan compliance requirements for banks) but no Pakistan-specific platform breakdown exists in accessible sources. **Flagged during the final pre-slide audit**: the 6sense figures could not be re-verified in that pass (the source was blocked on re-check), and even if accurate, they're a vendor-modeled estimate from an install-base/intent-tracking panel, not audited industry-wide deployment data — cite with that caveat, or lean primarily on the independently-confirmed Gartner Magic Quadrant Leader status instead. **Decision: Splunk as the primary integration target**, justified on two independent grounds that happen to converge — it's both the most widely deployed globally *and* practically the easiest to build against (HEC needs no SDK, just a simple authenticated request, unlike Sentinel's OAuth2+RBAC setup or QRadar's complete lack of any library support, already established in the tech-stack research). Sentinel kept as the credible secondary given its official SDK coverage; QRadar deliberately deprioritized for integration work despite being common, given the lack of any library support.

### Still open

- [ ] Whether "agent" applies in the strict technical sense — depends on which method wins the five-way comparison
- [ ] The XGBoost-alone vs. ensemble ablation — recommended before the defense, not yet run
- [ ] Whether the final system is one flat winning method or a hybrid (offline RL for historical cold-start, bandit for live refinement) — deliberately left open, to be settled by the actual comparison results

---

*Compiled September 24, 2026, directly from the live design walkthrough. Content preserved as discussed — not rewritten or condensed after the fact.*
