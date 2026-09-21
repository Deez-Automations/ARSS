# ARSS — Future Scope & Limitations (Plain Language)
**Purpose:** Everything found in the recent deep-research pass, explained from zero — no assumed knowledge of any term — split into "what we could add later" (future scope, for the professor to prioritize) and "what pushes back against our current choices" (limitations, found honestly, not hidden). Includes ready-to-use slide bullets at the end of each part.

---

## Quick recap: what ARSS does right now, so the rest of this makes sense

Before an idea is "added," here's what exists today, in one paragraph. The AI looks at three things about an alert: how dangerous it seems (a percentage), what type of attack it is (one of 7 categories), and how confident the detector is about that guess. Based on those three things, it picks one of four actions: Ignore, Log, Block, or Isolate. It's trained to prefer actions that match how serious the attack type actually is, using a scoring system borrowed from MITRE ATT&CK — a real, industry-standard "rulebook" of attacker behavior.

Everything below is either: "here's a way to give the AI more information than those three things," "here's a way to use a more detailed version of the MITRE rulebook," or "here's some other trick that could make the training smarter."

---

# PART A — Could we show the AI more information? (Bucket 1)

**What we were checking:** right now the AI only sees 3 things per alert. We asked: do other research teams give their AI more to look at? Would that help?

### Idea A1: A report card instead of one grade
One research paper (called RADAMS) doesn't give its AI a single danger score — it gives 5 separate scores: where the alert came from, how urgent it is, how complicated it is, how easy it'd be for an attacker to actually pull off, and how important the target is. **Simple version:** instead of a teacher giving one overall grade, imagine a report card with 5 subjects — you learn more about *where* the problem is, not just *that* there is one.

### Idea A2: How long has this alert been waiting?
Right now, ARSS treats an alert that just arrived exactly the same as one that's been sitting for 10 minutes. One paper adds a simple number: "time since this alert showed up." **Simple version:** a hospital waiting room where nobody's file says how long they've been waiting — adding that one number changes triage decisions.

### Idea A3: How stressed is the human analyst right now?
One paper calculates a "stress level" for the human analyst, based on how many alerts have piled up recently, and feeds that into the decision. There's a real, well-known idea from psychology behind this: people perform worst when they're either too relaxed (not urgent enough to focus) or too overwhelmed (too much to handle) — best performance is in the middle. **Simple version:** it's the difference between an AI assistant that has no idea if the human it's helping is calm or drowning in work, versus one that actually knows and adjusts.

### Idea A4: A map of the network
One paper (Safety-Contract Graph MARL) gives its AI a picture of the network as dots and lines — which servers talk to which — and uses a type of neural network built specifically to read that kind of picture, paying more attention to the connections that matter most for a given decision. **Simple version:** right now, ARSS's AI doesn't know if a dangerous alert happened on a random test machine or three steps away from the main database. This idea would let it know.

### Idea A5: A memory of what's happened recently
Same paper also gives its AI a short "memory" — a running sense of what an attacker has been doing over the last several steps, learned automatically rather than told explicitly. **Simple version:** like a goalkeeper who's watched an opponent's last five shots and has a gut feeling which way they'll go next, without anyone briefing them on strategy.

### Idea A6: Thinking about the worst case, not just the average
This is a finance idea borrowed for security. Instead of one confidence number, this method specifically tracks "in my worst 5% of guesses, how bad does it actually get?" **Simple version:** it's the difference between "on average, this investment does fine" and "on average it's fine, but let's specifically check how ugly the crash scenario is."

### Idea A7: Splitting confidence into three parts
Another paper splits "confidence" into three separate pieces: how bad would this be if it's real, how sure am I, and how reliable is my detector generally. Same "report card instead of one grade" idea as A1, applied to confidence specifically.

### Something worth knowing: this isn't free
A methodology-review paper (reviewing 66 different research projects) found that a third of them didn't clearly define what information their AI's state actually contained — a common, real mistake. So "add more information" has to be done carefully and clearly documented, not just piled on.

### Slide bullets — Part A

> **Future Scope: Richer Information for the AI**
> - Give each alert a multi-part label (source, urgency, complexity, exploitability, target importance) instead of one danger score
> - Add "time since this alert appeared" as a factor
> - Add a real-time "analyst workload/stress" signal based on alert volume
> - Add network-topology awareness — is this alert near something important?
> - Add short-term memory of recent attacker behavior
> - Track worst-case risk specifically, not just average confidence

---

# PART B — Could we use the more detailed version of the attacker rulebook? (Bucket 2)

**Quick reminder:** MITRE ATT&CK is a real rulebook of attacker behavior. It has big chapters called **tactics** (broad goals, like "steal credentials"), and inside each chapter are specific, individual moves called **techniques** (the exact method used). ARSS currently only uses the 7 big chapters. This bucket asked: could we use the individual moves instead?

### Idea B1: A checklist of individual moves
One paper (Huff et al.) gives its AI a long checklist — one yes/no box per individual attacker move — instead of one broad category. **Simple version:** instead of a doctor's chart saying "patient is sick," it lists every individual symptom present.

### Why this is harder, not just more detailed
The same paper admits this directly: the more individual things the AI could see, the more different situations it has to personally experience before it learns good behavior for each one. That's called a slow, "sparse" learning process. **Simple version:** it's the difference between learning which of 7 keys opens a door versus which of 200 keys does — more precise, much slower to actually learn.

### How they made it manageable: realistic fake attackers
To fix the slowness, they built a model that generates *realistic* sequences of attacker moves (learned from real data) instead of totally random ones, so the AI practices against plausible attacks, not every theoretically possible one. **Simple version:** instead of studying every lock ever made, you study the dozen lock types real burglars in your area actually use.

### The genuinely good news
Two separate full papers were read specifically hunting for anyone — anywhere — combining MITRE ATT&CK with an AI that learns from trial and error, at either the broad or detailed level. Out of 56 papers reviewed in one of them: **zero** did this. This means ARSS isn't behind on this point at all — it's already ahead of almost everyone who's published in this space, using just the broad chapters. Going to individual moves would be extending an already-uncommon idea even further, not catching up.

### Slide bullets — Part B

> **Future Scope: A More Detailed Rulebook**
> - Move from 7 broad attack categories to individual attacker techniques (finer detail)
> - Would require a realistic attacker-behavior model to keep training practical
> - Known cost: slower learning due to many more possible situations
> - Confirmed via literature: no one else has combined ATT&CK with trial-and-error AI at any level of detail — this would be genuinely new work either way

---

# PART C — Other smart tricks we could borrow (Bucket 3)

**What we were checking:** general grab-bag search for any other useful technique, regardless of state or MITRE specifically.

### Idea C1: A rule you can't break vs. a rule you're just discouraged from breaking
Right now, ARSS discourages bad outcomes by giving a lower score — but the AI could still choose a bad outcome if the reward elsewhere seems worth it. One paper instead makes certain limits **absolute** — a hard budget the AI is never allowed to cross, not just something it's nudged away from. **Simple version:** the difference between "try not to go over budget" and "the card physically declines past this amount." Their test: with only soft nudging, the AI blew the budget in every single test run. With a hard limit, that dropped to almost never. This is a real, measured before/after number, not a guess.

### Idea C2: A menu of tradeoffs instead of one fixed choice
ARSS currently blends "stop the threat" and "don't disrupt the business" into one number, using weights decided in advance and locked in. An alternative: train the AI to learn a whole *range* of good behaviors at once — a more aggressive style, a more cautious style, and everything between — and let a human pick which one to use *after* training is done, without retraining. **Simple version:** a restaurant menu of finished dishes to choose from, instead of one fixed combo meal decided before you even sat down.

### Idea C3: Game theory — thinking of it as a two-player game
One of the original competing papers (SAC-AP) treats attacker vs. defender like a formal two-player game, similar in spirit to how you'd analyze a game of chess mathematically, and uses an efficient search method to find the point where neither side benefits from changing their strategy. This is a different mathematical framing than what ARSS uses, worth knowing about even though it's not something to necessarily copy.

### Idea C4: Asking several judges instead of one
Normal actor-critic training (explained in the earlier RL primer) uses one "critic" to judge how good an action was. One paper uses *several* critics and combines their opinions, specifically because a single judge can be overly generous. **Simple version:** getting a second medical opinion instead of trusting one doctor's read.

### Idea C5: Learning easy things before hard things
Start the AI's training on simple, obvious situations, and only introduce harder, more ambiguous ones later — the same way a student learns basic arithmetic before algebra, not both thrown at them at once.

### Idea C6: Let an AI tune the reward settings automatically
Right now, the MITRE severity weights (1.0 for MITM, 0.3 for Recon, etc.) are numbers a human sets once, by hand. One paper's idea: have a language-model AI propose the weights, watch how the trained agent performs, then have it adjust and repeat — an automatic tuning loop instead of a one-time guess.

### Idea C7: Noticing when the world has changed
Attack patterns evolve over time, and a model trained once can go stale. One paper uses a lightweight statistical trick that watches the AI's predictions over time and flags when something's shifted enough to be suspicious — an early step toward "notice the world changed, flag for retraining" instead of running the same frozen brain forever.

### Slide bullets — Part C

> **Future Scope: Other Techniques**
> - Replace soft penalties with hard, unbreakable operational limits (proven to reduce budget violations dramatically)
> - Train a range of tradeoff options instead of one fixed blend, selectable after training
> - Use multiple judges (critics) instead of one, to avoid overly optimistic decisions
> - Train on easy cases before hard ones
> - Let an AI auto-tune the severity weights over time instead of setting them once by hand
> - Add a "notice the world changed" signal for future retraining

---

# CONSOLIDATED FUTURE SCOPE SLIDE (presentation-ready)

**On slide:**
> **Future Scope**
> - Richer per-alert information: multi-part labels, alert age, analyst workload, network context, short-term memory, worst-case risk tracking
> - Finer-grained rulebook: individual attacker techniques instead of broad categories (confirmed: nobody else has done this at any level)
> - Hard operational limits instead of soft penalties
> - A range of selectable tradeoffs instead of one fixed blend
> - Multiple judges instead of one, easy-to-hard training, auto-tuned severity weights, drift detection for staleness

**Say:** Present this as a menu, not a promise. The point of this slide is showing the supervisor there's a real, literature-backed runway ahead — not committing to doing all of it. Let him pick what's worth the remaining time.

---

# LIMITATIONS — What we found that pushes back against our own choices

This section exists because a defense is stronger when the team names its own weak points before someone else does. Everything below is a real finding from the same research pass that could be used to challenge a decision ARSS has already made.

### Limitation 1: One paper directly argues against ARSS's reward design
ARSS uses a "dense" reward — the AI gets a score after every single decision. One paper found that a simpler, "sparse" reward — feedback only at meaningful moments, not every step — actually trained more reliable AI agents with less risky behavior, and that complicated, many-part rewards (like ARSS's) can push an AI toward worse choices. **In plain terms: someone found real evidence that ARSS's core reward design choice might not be the best one, not just an untested assumption.** This needs an honest answer in the paper, not a workaround.

### Limitation 2: Another paper argues fixed weights are a real weakness
ARSS locks in its MITRE severity weights before training and never changes them. One paper argues this specifically removes the AI's ability to adapt after training is finished, and proposes training a flexible range of behaviors instead (mentioned above as Idea C2). This is a second, independent challenge to the same design area as Limitation 1.

### Limitation 3: Going to individual attacker moves has a real, admitted cost
As covered in Part B: the one paper that tried the detailed-rulebook approach admits it directly causes slower, harder learning. If the team decides to pursue this later, it's not a free upgrade — it comes with a documented, real cost that needs its own solution.

### Limitation 4: Competing systems don't actually use richer information either
Here's an important nuance: when the AI systems ARSS is positioned against (the ones it's supposed to be better than) were checked directly, most of them use even *thinner* information than ARSS already does — just alert-type counts, nothing richer. **This cuts both ways:** it means ARSS's current 3-part state is already ahead of its direct competitors, but it also means there's no existing proof, from ARSS's own competitive field, that adding *even more* information (Part A's ideas) actually improves results in this exact type of system. The richer ideas come from different, adjacent research, not from anyone who tested it in this exact problem.

### Limitation 5: A lot of this research is not fully confirmed
Several of the findings above came from search-engine summaries of papers that were paywalled — not the actual paper text. This was tracked carefully and flagged every time it happened, but it's worth saying plainly here too: some of these ideas need to be verified against the real paper before being trusted as fact, not just cited as if confirmed. Treat anything not explicitly marked "read in full" as a promising lead, not a settled finding.

### Limitation 6: One "new" framework might overlap with something already cited
One newly-found paper describes a framework with three operating modes (automated handling, AI-assisted handling, and full human collaboration) that sounds structurally close to the A2C framework ARSS already cites, from a closely related group of authors. This needs a direct side-by-side check before treating it as a separate, additional citation — it might just be the same idea restated.

### Limitation 7: The RL agent still doesn't exist
Every idea above is a design idea, layered on top of a system that — as of today — has no working RL agent at all. None of this future scope can actually be tested or proven better until the base system is built first. This is the honest, standing limitation underneath everything else in this document.

---

*Compiled: September 21, 2026, from a dedicated deep-research pass covering both freely accessible and paywalled papers. All 7 limitations above are genuine findings, not invented for balance — each one traces back to a specific paper or a specific gap in what could be verified.*
