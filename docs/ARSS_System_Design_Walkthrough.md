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

---

## Running Checklist of Parked Design Work

*Carried forward from this walkthrough, to be resolved together once the full section pass is complete — this is system-model work for the defense presentation, its own separate effort.*

- [ ] Whether "Alert Understanding" should compute its own score from scratch or read/normalize metadata already attached by an upstream SIEM, depending on deployment context
- [ ] Making the SOC-state measurement robust: multiple signals, periodic reconciliation against ground truth, bounds-checking for impossible states, and a clear distinction between the simulated environment (correct by construction) and a real deployment (must pull from the authoritative source, not a self-maintained counter)
- [ ] Broad SIEM integration coverage — real-time ingestion across common formats (CEF, Syslog, Splunk HEC, Sentinel Log Analytics API, Elastic Common Schema) plus historical-data bootstrapping using creation/resolution timestamps to reconstruct past queue-depth patterns and avoid a cold start
- [ ] Proper research grounding for how "SOC behavior" gets represented — this is human-behavior modeling, not just an engineering counter; RADAMS's operator-stress concept (Yerkes-Dodson law) is one existing starting point, more literature needed before finalizing
- [ ] Deciding, once the above is settled, whether "agent" in the strict technical sense applies — depends on which method wins the five-way comparison

---

*Compiled September 24, 2026, directly from the live design walkthrough. Content preserved as discussed — not rewritten or condensed after the fact.*
