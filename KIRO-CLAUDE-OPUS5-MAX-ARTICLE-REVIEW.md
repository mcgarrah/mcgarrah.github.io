# Article Review & Managed Release Schedule

**Purpose:** Convert an accumulating pile of engineering-driven drafts into a managed, gated publication pipeline.

**Created:** 2026-09-02
**Author of plan:** Kiro (Claude Opus 5) — commissioned review
**Status:** Phase 0 complete, Phase 7 partly done (INTAKE.md), Phases 1-6 and 8 not started. Re-audited 2026-11-24: buffer still 0, 71 days since last publish, 84 drafts, 28 untracked. See `Amendment 2` at the end and `.article-review/STATE.yaml`.
**State file:** `.article-review/STATE.yaml`

> **This document is resumable.** Every phase writes its output to a file in `.article-review/`
> and updates `STATE.yaml`. If a session dies, read `STATE.yaml`, find the first phase not marked
> `done`, and restart at that phase's Step 1. No phase depends on in-memory context from a prior
> session — only on the artifacts on disk. See [Resume Protocol](#resume-protocol).

---

## Table of Contents

- [Part I — Diagnosis](#part-i--diagnosis)
- [Part II — The Release Mechanism](#part-ii--the-release-mechanism)
- [Part III — Resume Protocol](#resume-protocol)
- [Part IV — The Phases](#part-iv--the-phases)
  - [Phase 0 — Baseline & State](#phase-0--baseline--state)
  - [Phase 1 — Reconcile the Control Plane](#phase-1--reconcile-the-control-plane)
  - [Phase 2 — Triage All Drafts Against a Rubric](#phase-2--triage-all-drafts-against-a-rubric)
  - [Phase 3 — Archive, Merge, Kill](#phase-3--archive-merge-kill)
  - [Phase 4 — Verification Sweep](#phase-4--verification-sweep)
  - [Phase 5 — Commit to the Schedule](#phase-5--commit-to-the-schedule)
  - [Phase 6 — Enforce the Gate in Tooling](#phase-6--enforce-the-gate-in-tooling)
  - [Phase 7 — Cross-Repo Intake](#phase-7--cross-repo-intake)
  - [Phase 8 — Published-Post Debt](#phase-8--published-post-debt)
- [Appendix A — Verified Audit Numbers](#appendix-a--verified-audit-numbers)
- [Appendix B — Cross-Repo Candidate Inventory](#appendix-b--cross-repo-candidate-inventory)
- [Appendix C — Stale Claims Register](#appendix-c--stale-claims-register)

---

## Part I — Diagnosis

### The headline

**The drafts are not the problem. The control plane is.**

There are 68 article drafts holding roughly 93,000 words. A large fraction of them are genuinely
finished pieces of writing about genuinely finished engineering work. The blog published 71 articles
in 2026 through August 21. This is not a productivity problem.

What broke is the layer that decides *what ships when*. Four specific failures:

### 1. The trackers have decoupled from the filesystem

| Claim | Reality |
|-------|---------|
| `DRAFTS.md`: "Drafts in `_drafts/`: 56" | 68 article drafts (+ 17 tracker files) |
| `DRAFTS.md`: "Last updated: 2026-06-10" | Body contains content dated 2026-08-12 |
| `SCHEDULED.md`: "**Today:** 2026-06-11" | 12 weeks stale |
| `SCHEDULED.md`: Jul/Aug/Sep shown as mostly open slots | 14 articles actually published in that window |
| `TODO.md`: "122 of 173 posts missing `description`" | 0 of 131 modern posts are missing it |

**13 of 68 drafts are invisible to `DRAFTS.md` entirely** (12 of those are absent from
`SCHEDULED.md` too) — including the whole 5-part Proxmox 8→9 cluster upgrade series (parts 1, 3, 4,
5), the whole 5-article Run Jekyll extension cluster, and all four August 2026 drafts. That is
roughly 30,000 words. The largest and most recent body of work in the repo is not on the
publication tracker.

This matters because `DRAFTS.md` is where promotion decisions get made. Work that isn't listed
there doesn't get considered, no matter how finished it is.

### 2. The cadence has been declared three times and enforced zero times

`SCHEDULED.md` states: *"Cadence: Once per week, Monday (EDT). Reduced from MWF effective June 2026."*

What actually happened:

| Month | Posts | Pattern |
|-------|-------|---------|
| Apr 2026 | 22 | Relaunch burst, near-daily |
| May 2026 | 22 | Peak, near-daily |
| Jun 2026 | 7 | Tapering |
| Jul 2026 | 4 | Every Tuesday — not Monday |
| Aug 2026 | 10 | Mon/Wed/Fri bursts — not weekly |
| Sep 2026 | 0 | **12-day silence as of today** |

The declared schedule was never the operating schedule. Each new declaration described an intent
rather than a mechanism, so it decayed the moment a busy week arrived.

### 3. There is no definition of done

Front matter is machine-enforced and in good shape — `scripts/lint-frontmatter.py` has a proper
tiered schema, CI runs it, and a January cleanup commit (`3f51c81`) filled the schema gaps across
34 WIP drafts. All 68 drafts have complete `title`/`description`/`tags`/`categories`/`last_modified_at`.

That is exactly the problem. **Front matter completeness now signals nothing about readiness.**
A 20-word stub and a 3,200-word verified writeup have identical, passing front matter and sit
side by side in the same directory. There is no machine-readable or human-readable marker that
distinguishes them.

Concretely, `_drafts/` currently holds:

- **21 stubs under 600 words** — including a 20-word file (`2025-03-01-thoughts-on-directions-for-aiml.md`)
  and a 36-word file (`2024-12-31-jekyll-add-header-links.md`)
- **2 oversized drafts** needing splits — PVE8→9 Part 3 at 8,364 words, Part 2 at 4,088 words
- Genuinely publishable work with no flag saying so

### 4. Verification debt — the one that actually risks public embarrassment

Status headers across drafts and source repos assert things that are no longer true. Because
articles get written *from* those headers, the errors propagate into published content.

The register is in [Appendix C](#appendix-c--stale-claims-register). The worst examples:

- `jellyfin-plugin.../ARR-INTEGRATION-PROPOSAL.md` header: *"Status: Proposal — not started.
  no code in this repo has been changed to implement it."* All four phases shipped (PRs #77–80).
- `k8s-proxmox/articles/08-CLUSTER-AUTOSCALER.md` documents `cloudProvider=proxmox`, a value that
  **does not exist** in upstream Cluster Autoscaler. The repo's own `docs/AUTOSCALER.md` says so
  explicitly: *"As written, it would not have worked."* Publishing that article would spread a
  known-broken config.
- `k8s-proxmox/articles/13-CALICO-NETWORK-POLICIES.md` — Calico was replaced by Cilium. This file
  is the last Calico reference in the repo.
- Plugin `README.md` links to `CODE_REVIEW.md` four times. That file has never existed in git history.

### 5. The real inventory is ~40% larger than anyone thinks

| Source | Publishable candidates |
|--------|----------------------|
| `_drafts/` (after archiving stubs/superseded) | ~40 |
| `k8s-proxmox/docs/` | ~10 (see [Appendix B](#appendix-b--cross-repo-candidate-inventory)) |
| `jellyfin-plugin-media-integrity-scanner` | ~6 |
| **Total** | **~56** |

At one article per week, that is **over a year of runway from material that already exists.**
The scarce resource is not content. It is review capacity and a gate.

### The k8s-proxmox correction

One finding deserves separating out, because it inverts an assumption baked into `DRAFTS.md`
(which lists "Kubernetes on Proxmox — series of articles from `k8s-proxmox/articles/`, 20 planned").

**`k8s-proxmox/articles/` is a 21-file article plan for a Kubernetes cluster that does not exist.**
Four independent sources in that repo confirm it:

- `PRE-K8S-TASKS.md` — every task in Phases 1–4 is `Status: ⬜ Not Started`. The "Ready for
  Kubernetes" gate is entirely unchecked. The decisions log is still `### Date: ____`.
- `README.md` — *"this cluster's own PVE9 OS upgrade is still pending, this deployment targets the
  post-upgrade state."*
- `TODO.md` — *"Kubernetes Deployment — After site-to-site VPN complete."*
- `JMM-TODO.md` (2026-08-28) — the K8s 1.36 / Cilium / CAPI work *"was written and reviewed as
  docs/manifests, not confirmed applied against the live cluster."*

`articles/ARTICLES.md` has an "✅ Completed" list that reads as *infrastructure done*. It means
*a file exists at that path*. That distinction is the single most misleading thing in either repo.

**The correction:** stop treating `articles/` as a publication queue. Write from `k8s-proxmox/docs/`,
which contains 50 actively-maintained files documenting work that actually shipped. Full candidate
table in [Appendix B](#appendix-b--cross-repo-candidate-inventory).

---

## Part II — The Release Mechanism

### The insight that makes this work

The deploy pipeline already contains the solution and it isn't being used.

`.github/workflows/jekyll.yml` runs a **daily cron at 10:05 UTC** and builds **without `--future`**.
That means a post in `_posts/` dated in the future is invisible in production until its date
arrives, at which point the next cron run publishes it automatically.

So the schedule does not need to be enforced by remembering to publish on Wednesdays. It can be
enforced by **maintaining a buffer of future-dated posts** and letting the cron drain it.

### The rule set

**1. Anchor day: Wednesday.**
Wednesday already has the most historical posts (15) and lands mid-week. More importantly, it is
not Monday — Monday carries three failed declarations and the associated guilt. Pick a new day
and let the old one go.

**2. Baseline cadence: one article per week.**
This is what the last three months actually sustained once the Apr/May relaunch burst ended, and
it is honest against a full-time Principal Engineer role plus an Executive MBA. Do not declare two
per week. If capacity appears, spend it on the buffer, not on the cadence.

**3. Optional second slot: Saturday, series parts only.**
When a multi-part series is fully drafted and verified end to end, its parts may occupy consecutive
Wednesday *and* Saturday slots to keep the narrative tight. Never use Saturday for standalone posts —
that is how MWF crept back in.

**4. Buffer discipline — this is the actual mechanism.**

| Buffer state | Future-dated posts in `_posts/` | Action |
|--------------|--------------------------------|--------|
| 🟢 Healthy | ≥ 4 (one month runway) | Publish nothing. Work on drafts. |
| 🟡 Low | 2–3 | Promote at the next available review session. |
| 🔴 Empty | 0–1 | **Stop all new engineering-driven drafting.** Promote or skip a slot deliberately. |

**Never promote from an empty queue.** A skipped slot with a healthy pipeline is a scheduling
choice. A skipped slot with an empty queue is the failure mode that produced the current 12-day gap.

**5. Batch promotion, not just-in-time promotion.**
Promote 4–6 articles in one session with future Wednesday dates assigned. The site then publishes
itself for a month with no further intervention. This matches how the work actually happens —
in concentrated sessions, not in weekly increments.

**6. Series integrity rule.**
Do not promote Part N until Part N+1 is at minimum draft-complete and verified. The published
archive currently has series where later parts sat in `_drafts/` for months after earlier parts
shipped. Readers hitting Part 2 of 5 with no Part 3 is worse than waiting.

**7. Skipping is legal. Silent skipping is not.**
If a slot goes empty, record it in `SCHEDULE.md` with a one-line reason. The record is what
prevents a skipped week from becoming a skipped quarter.

### Capacity math

Weekly cadence, ~56 candidates → **~13 months of runway.** The constraint is review throughput:
roughly 45–90 minutes per article to run the readiness gate properly. At one review session per
week that is comfortable; at one per month it needs 4–6 articles per session, which is a half-day.

Budget **one half-day session per month** for batch review and promotion. That is the whole
operating cost of the schedule.

### Definition of Done — the readiness gate

An article ships only when all seven gates pass. This is the artifact that has been missing.

| # | Gate | Check |
|---|------|-------|
| **G1** | **Front matter** | `python3 scripts/lint-frontmatter.py <file>` passes; `image:` present and the OG asset exists on disk |
| **G2** | **Claims verified** | Every factual assertion about state — repo stats, version numbers, node counts, test counts, "N of M" figures — checked against the source today. No claim inherited from a stale header. |
| **G3** | **Work actually done** | The article describes something that exists and was observed working. Aspirational plans are labeled as plans in the title or opening, or the article does not ship. |
| **G4** | **No orphan references** | Internal links resolve. `{% post_url %}` targets exist. Cross-repo links point to files that exist on the default branch. Series prev/next links resolve both directions. |
| **G5** | **Voice pass** | The four `_drafts/PERSONA.md` patterns applied where they fit: opening leads with *why*, rejected alternatives shown, one enterprise-pattern sentence, "what this enables" closing. Light tactical posts are explicitly exempt — record the exemption. |
| **G6** | **Supersession checked** | No published post or other draft already covers this ground. If it partially does, the overlap is resolved by merge, split, or explicit cross-link — not left ambiguous. |
| **G7** | **Local build clean** | `./jekyll-start.sh` with drafts renders the article without Liquid errors, and `jekyll-checks.sh` reports no new tag-slug collisions. |

G2 and G3 are the ones that failed historically. They are the reason this plan exists.

---

## Resume Protocol

If you are picking this up cold — a new session, a crashed session, or weeks later:

1. **Read `.article-review/STATE.yaml`.** It records the current phase, per-phase status,
   and the last completed step within the active phase.
2. **Read the artifacts listed for every phase marked `done`.** They are the accumulated
   findings. Do not redo completed phases; their output is authoritative.
3. **Re-run the audit if `STATE.yaml`'s `baseline_date` is more than two weeks old.**
   `python3 .article-review/audit.py` regenerates the numbers. Drift matters — the whole
   diagnosis above is about trackers drifting from reality, and this plan is a tracker.
4. **Resume at the first phase not marked `done`, at Step 1 of that phase.** Steps within a
   phase are idempotent by design — rerunning a completed step is safe and cheap.
5. **Update `STATE.yaml` at the end of every step, not every phase.** A step is the unit of
   recovery.

### State file schema

```yaml
baseline_date: 2026-09-02        # when audit.py last ran
current_phase: 1
phases:
  "0": {status: done, completed: 2026-09-02, artifacts: [BASELINE.md, audit.py, STATE.yaml]}
  "1": {status: not_started, last_step: null, artifacts: []}
  # ... through phase 8
counts:                          # from the last audit run — drift detector
  posts: 190
  drafts: 68
  trackers: 17
  buffer: 0                      # future-dated posts in _posts/
```

### Rules for whoever resumes

- **Append, never rewrite.** Phase artifacts are the record. Correct them with a dated
  amendment section, don't silently edit.
- **If a phase's exit criteria cannot be met, mark it `blocked` with a reason and move on.**
  Phases 2–4 are strictly ordered. Phases 6, 7, and 8 are independent and may run in any order
  or in parallel once Phase 5 is done.
- **Do not let this document become the thing it diagnoses.** If `STATE.yaml` disagrees with the
  filesystem, the filesystem wins. Re-run the audit.

---

## Part IV — The Phases

Effort estimates assume focused work. Total: roughly 20–26 hours across Phases 0–6, then
Phases 7 and 8 are ongoing background work.

---

### Phase 0 — Baseline & State

**Status:** ✅ done (2026-09-02)
**Effort:** 30 min
**Purpose:** Freeze a measured starting point so later drift is detectable.

**Entry criteria:** none.

**Steps:**

1. Create `.article-review/` (dot-prefixed so Jekyll ignores it; add to `.gitignore` only if
   you want the review private — recommended to **commit** it, since the whole point is a
   durable record).
2. Write `.article-review/audit.py` — the front-matter and readiness-signal audit. Emits
   `.article-review/audit.json` and a human-readable summary.
3. Run it. Write `.article-review/BASELINE.md` with the numbers.
4. Write `.article-review/STATE.yaml`.

**Exit criteria:** `BASELINE.md` exists with real numbers; `STATE.yaml` initialized.

**Artifacts:** `.article-review/audit.py`, `.article-review/audit.json`,
`.article-review/BASELINE.md`, `.article-review/STATE.yaml`

---

### Phase 1 — Reconcile the Control Plane

**Effort:** 2–3 hours
**Purpose:** Make the trackers describe reality, and reduce 17 tracker files to a navigable set.
**Also handles** one unrelated hygiene finding surfaced during the audit — see Step 7.

**Entry criteria:** Phase 0 done.

**Steps:**

1. **Generate the ground-truth draft inventory.**
   `python3 .article-review/audit.py --inventory > .article-review/INVENTORY.md`
   One row per draft: filename, word count, section count, code blocks, images, TODO markers,
   whether it appears in `DRAFTS.md`, whether it appears in `SCHEDULED.md`.

2. **Add the 13 orphaned drafts to `DRAFTS.md`.** All 13 are absent from `DRAFTS.md`; the first
   one below is the only one that at least appears in `SCHEDULED.md`, which is why
   `audit.py` reports the drift count as 12.
   - `2026-06-10-forking-jekyll-run-to-run-jekyll.md`
   - `2026-06-15-run-jekyll-vscode-marketplace-publisher-setup.md`
   - `2026-06-19-run-jekyll-bug-fixes-and-code-review.md`
   - `2026-06-24-run-jekyll-testing-and-test-harness.md`
   - `2026-06-29-run-jekyll-new-features-clean-doctor-tests.md`
   - `2026-08-05-proxmox-8-to-9-cluster-upgrade-part-1.md`
   - `2026-08-12-proxmox-8-to-9-cluster-upgrade-part-3.md`
   - `2026-08-15-proxmox-8-to-9-cluster-upgrade-part-4.md`
   - `2026-08-16-proxmox-8-to-9-cluster-upgrade-part-5.md`
   - `2026-08-17-claude-code-tmux-persistence-proxmox-ha.md`
   - `2026-08-26-claude-code-persistent-plain-shell-windows.md`
   - `2026-08-28-idempotent-workspace-provisioner-agent-lxc.md`
   - `2026-08-29-cephfs-gapfill-throttle-tuning.md`

3. **Correct `DRAFTS.md`'s stale internal claims.** The summary table counts, the
   "Last updated" date, and the Kiro cluster note that says "Both articles published" when
   three are.

4. **Retire `SCHEDULED.md`.** It is a hand-maintained calendar, which is precisely the thing
   that rotted. Replace it with `_drafts/SCHEDULE.md`: a forward-only slot table (next 12 weeks),
   a buffer-health line, and a skipped-slot log. Past months come out — `_posts/` is the record
   of what published, and duplicating it invites disagreement.

5. **Tier the 17 tracker files** in `DRAFTS.md`, so it's obvious which ones are live:
   - **Control plane (2):** `DRAFTS.md`, `SCHEDULE.md`
   - **Standards (1):** `PERSONA.md`
   - **Active project trackers:** the ones whose projects are moving
   - **Dormant / reference:** everything else, with a one-line "last real activity" note

   Do not delete dormant trackers. Label them. `PERSONA-SVP.md` at 45K and `AASR-PROJECT.md`
   at 43K represent real thinking; they just aren't release-pipeline documents.

6. **Correct `TODO.md`'s Front Matter Hygiene section.** It describes a solved problem. The
   modern-post gaps are closed; what remains is 59 legacy posts, which is Phase 8.

7. **Decide on repo-file exposure (new finding — pre-existing, unrelated to this review).**
   `_config.yml` has no `exclude:` key, so Jekyll's built-in defaults apply and nothing
   repo-specific is excluded. These working files are currently copied into `_site/` and served
   publicly:

   `TODO.md`, `REFACTOR.md`, `Caddyfile`, `package.json`, `requirements.txt`,
   `jekyll-start.sh`, `jekyll-caddy.sh`, `jekyll-clean.sh`, `bin/` (2 Python scripts),
   `scripts/lint-frontmatter.py`

   None of it is secret, but a reverse-proxy config and an internal TODO list being reachable at
   `mcgarrah.org/Caddyfile` and `mcgarrah.org/TODO.md` is probably unintended. **This document
   is at the repo root and inherits the same exposure** — it contains candid internal assessment
   and a stale-claims register.

   The fix needs care: adding an `exclude:` key **replaces** Jekyll's defaults rather than
   extending them, so the defaults must be restated or `node_modules`, `vendor/`, and `Gemfile`
   start leaking instead:

   ```yaml
   exclude:
     # Jekyll defaults — must be restated, an explicit exclude replaces them
     - Gemfile
     - Gemfile.lock
     - node_modules
     - vendor/bundle/
     - vendor/cache/
     - vendor/gems/
     - vendor/ruby/
     # Repo working files
     - "*.sh"
     - "*.md"          # root-level only; _posts/ and _drafts/ are unaffected
     - bin/
     - scripts/
     - Caddyfile
     - package.json
     - requirements.txt
     - .venv/
   ```

   Verify with a local build and `ls _site/` before deploying — `- "*.md"` is the entry to
   check most carefully, since it must not affect collection content.

**Exit criteria:** `DRAFTS.md` lists all 68 drafts and its counts match `audit.json`.
`SCHEDULE.md` exists and is forward-only. `TODO.md` no longer asserts fixed problems.
An exposure decision is recorded (fix or accept) in `PHASE1-CHANGES.md`.

**Artifacts:** `.article-review/INVENTORY.md`, `.article-review/PHASE1-CHANGES.md` (log of
what was corrected and why)

---

### Phase 2 — Triage All Drafts Against a Rubric

**Effort:** 4–6 hours — **batch this.** 10 drafts per sitting, 7 sittings.
**Purpose:** Produce one ranked queue, replacing the Tier 1–5 scheme that no longer maps to reality.

**Entry criteria:** Phase 1 done. `INVENTORY.md` exists.

The existing Tier 1–5 system in `DRAFTS.md` mixes two different axes — how much work is left,
and whether the underlying engineering happened. A draft can be 95% written and 0% publishable
because the thing it describes was never built. Split those axes.

**The rubric — score each draft on two axes:**

**Axis 1 — Writing state** (how much authoring is left)
- `W4` Complete prose, reads end to end
- `W3` Complete structure, some sections thin
- `W2` Outline with real content in places
- `W1` Stub — headings and notes only

**Axis 2 — Substrate state** (does the thing exist and was it observed working)
- `S4` Done and verified; author watched it work
- `S3` Done, verification stale or partial
- `S2` Partially done
- `S1` Not built — plan or aspiration only

Then the disposition follows mechanically:

| Score | Disposition |
|-------|-------------|
| W4/W3 + S4 | **PUBLISH QUEUE** — run the G1–G7 gate, assign a slot |
| W4/W3 + S3 | **VERIFY** — re-check the claims, then queue |
| W2/W1 + S4 | **WRITE** — the work is done, the article isn't. Highest-value writing time. |
| any + S2 | **BLOCKED** — finish the engineering first. Not a writing task. |
| any + S1 | **RECAST OR ARCHIVE** — reframe honestly as a plan/evaluation, or archive |
| W1 + S1 | **ARCHIVE** — no salvage value |

**Steps:**

1. Define the batches in `.article-review/TRIAGE-BATCHES.md` — 7 groups of ~10, grouped by
   cluster so related drafts get judged together.
2. For each batch: read every draft, score both axes, record the disposition and a one-line
   reason. Write to `.article-review/triage/BATCH-NN.md`.
3. **Update `STATE.yaml` after each batch.** This is the phase most likely to span sessions.
4. After all batches: merge into `.article-review/QUEUE.md`, ranked. Ranking key:
   PUBLISH QUEUE first, then WRITE items with the highest reader value, then VERIFY.

**Known inputs from this review** (don't re-derive):
- 21 drafts are under 600 words → most will land W1
- The 5-part PVE8→9 series and the 4 Claude Code / agent-LXC drafts look W4/S4 — these are
  probably the front of the queue
- The four Homelab Infrastructure drafts (`overview`, `checklist`, `roadmap`, `upgrades`) are
  a known 4-way overlap. Resolve as one merge decision, not four independent scores.
- `2026-08-12-proxmox-8-to-9-cluster-upgrade-part-3.md` at 8,364 words needs a split before
  it can be queued. Treat the split as its own queue item.

**Exit criteria:** every one of the 68 drafts has a W score, an S score, a disposition, and a
reason. `QUEUE.md` exists and is ranked.

**Artifacts:** `.article-review/TRIAGE-BATCHES.md`, `.article-review/triage/BATCH-01..07.md`,
`.article-review/QUEUE.md`

---

### Phase 3 — Archive, Merge, Kill

**Effort:** 2–3 hours
**Purpose:** Get non-shippable material out of `_drafts/` so the directory means something.

**Entry criteria:** Phase 2 done.

**Steps:**

1. **Create `_drafts/archive/`.** Jekyll's `--drafts` flag does not recurse into subdirectories,
   so archived files stop appearing in local draft builds while staying in git history and
   remaining greppable. Verify this with one file before moving 20.

2. **Move everything scored ARCHIVE.** Prepend a three-line header to each: date archived,
   reason, and what superseded it if anything. Never delete — the git history and the notes have
   residual value, and a stub can become a real article when the underlying work happens.

3. **Execute the merge decisions** from Phase 2. Known ones:
   - Homelab Infrastructure 4-way overlap → one article
   - `2024-06-11-promox-sdn-options.md`, `2024-09-09-proxmox-sdn-openwrt-lxc.md`,
     `2024-09-13-proxmox-lxc-template-openwrt.md` → superseded by
     `2026-02-02-openwrt-lxc-native-implementation-journey.md`; salvage the
     `openwrt.common.conf` detail before archiving
   - `2025-02-20-ceph-reef-to-squid-upgrade.md` (40 words) → superseded by the PVE8→9 series

4. **Split the oversized drafts.** PVE8→9 Part 3 (8,364 words) into two coherent articles.
   Published median is ~1,019 words; 8,364 is eight times that and will not hold a reader.

5. **Re-run the audit** and confirm `_drafts/` contains only material with a live disposition.

**Exit criteria:** `_drafts/` (top level) contains only PUBLISH QUEUE, VERIFY, WRITE, and BLOCKED
items plus the tracker files. Every archived file carries a reason header.

**Artifacts:** `.article-review/PHASE3-DISPOSITIONS.md` (every move, with reason),
`_drafts/archive/` populated

---

### Phase 4 — Verification Sweep

**Effort:** 30–60 min per article in the PUBLISH QUEUE and VERIFY sets
**Purpose:** Kill the verification debt before it reaches readers. This is gate G2/G3 applied in bulk.

**Entry criteria:** Phase 3 done.

**Steps:**

1. **Fix the upstream stale headers first.** Articles get written from these, so correcting the
   source prevents the error from propagating. Full list in
   [Appendix C](#appendix-c--stale-claims-register). Minimum set:
   - `jellyfin-plugin-media-integrity-scanner/ARR-INTEGRATION-PROPOSAL.md` — status header says
     not started; all four phases shipped
   - `jellyfin-plugin-media-integrity-scanner/README.md` — four dead `CODE_REVIEW.md` links,
     "298 unit tests" (actual: 363 test attributes), Features section omits Arr integration,
     Blog Series list omits published article 6
   - `k8s-proxmox/docs/MEDIA-CLEANUP.md` — "No ARR suite yet" framing is stale
   - `k8s-proxmox/articles/ARTICLES.md` — annotate that "✅ Completed" means *the file exists*,
     not *the infrastructure runs*
   - `k8s-proxmox/articles/` H1 numbering: article 04 says "Article 8", 15 says "Article 16",
     19 says "Article 20", 20 says "Article 15"

2. **Mark the known-wrong k8s articles.** Add a header to
   `articles/08-CLUSTER-AUTOSCALER.md` and `articles/13-CALICO-NETWORK-POLICIES.md` stating they
   are superseded and must not be published as-is. `08` documents a config that cannot work;
   `13` documents a CNI no longer in use.

3. **Per-article verification pass** on each queued article. Extract every factual claim and
   check it. The recurring categories:
   - Repo statistics (file counts, test counts, LOC) — these age fastest
   - Version numbers (Proxmox, Ceph, Kubernetes, gem and NuGet versions)
   - Node/host counts and hardware inventory
   - "N of M" figures — tag counts, post counts, drive counts
   - PR and issue numbers, and whether the PR actually merged
   - External links (`.lychee.toml` config already exists — use it)

4. **Record every correction** in `.article-review/VERIFICATION-LOG.md`. Patterns in this log
   tell you which claim types to stop making, or to generate rather than hand-write.

**Exit criteria:** every PUBLISH QUEUE article has a completed verification record. Upstream
stale headers corrected. Known-wrong articles flagged in place.

**Artifacts:** `.article-review/VERIFICATION-LOG.md`, `.article-review/G-GATE-RESULTS.md`
(G1–G7 pass/fail per queued article)

---

### Phase 5 — Commit to the Schedule

**Effort:** 1–2 hours
**Purpose:** Assign real dates and build the first buffer. After this phase the site publishes itself.

**Entry criteria:** Phase 4 done for at least 6 articles.

**Steps:**

1. **Write `_drafts/SCHEDULE.md`** with the rules from [Part II](#part-ii--the-release-mechanism):
   anchor day Wednesday, weekly baseline, Saturday for series parts only, buffer thresholds,
   skip logging.

2. **Fill the first 12 Wednesday slots** from `QUEUE.md`:

   | # | Date | # | Date | # | Date |
   |---|------|---|------|---|------|
   | 1 | 2026-09-09 | 5 | 2026-10-07 | 9 | 2026-11-04 |
   | 2 | 2026-09-16 | 6 | 2026-10-14 | 10 | 2026-11-11 |
   | 3 | 2026-09-23 | 7 | 2026-10-21 | 11 | 2026-11-18 |
   | 4 | 2026-09-30 | 8 | 2026-10-28 | 12 | 2026-11-25 |

3. **Batch-promote the first 4–6.** For each: move to `_posts/`, set the filename date, `date:`,
   `last_modified_at:`, `seo.date_published`, and `seo.date_modified`; run
   `bin/generate-og-images.py` if `image:` is missing; run `scripts/lint-frontmatter.py`.

4. **Verify the buffer works.** Build locally without `--future` and confirm the future-dated
   posts do not appear. This is the mechanism the whole schedule rests on — test it once,
   explicitly, rather than assuming.

5. **Record the buffer count in `STATE.yaml`** and set a recurring monthly reminder for the
   review-and-promote session.

**Exit criteria:** ≥4 future-dated posts in `_posts/`. `SCHEDULE.md` reflects the operating rules.
Local no-`--future` build confirms they're hidden.

**Artifacts:** `_drafts/SCHEDULE.md`, `.article-review/PHASE5-PROMOTIONS.md`

---

### Phase 6 — Enforce the Gate in Tooling

**Effort:** 2–3 hours
**Purpose:** Make readiness machine-visible, so the next 12 months don't recreate the current state.

**Entry criteria:** Phase 5 done.

The lesson from the front-matter work: **the checks that got automated stayed fixed; the checks
that stayed manual rotted.** Front matter is clean because `lint-frontmatter.py` runs in CI.
Readiness is a mess because nothing checks it.

**Steps:**

1. **Add a `readiness:` front-matter key to drafts.** Values map to the Phase 2 rubric:
   `queue` / `verify` / `write` / `blocked` / `archive`. One field makes disposition visible in
   the editor, greppable, and reportable — replacing a hand-maintained table in `DRAFTS.md`.

2. **Write `scripts/draft-status.py`.** Reads `_drafts/`, groups by `readiness:`, prints the
   buffer count and its health color, warns when the buffer is below 4. Run it from
   `jekyll-checks.sh` so it appears every time the dev server starts.

3. **Write `scripts/promote-draft.py`** — a promotion runbook as code. Takes a draft and a target
   date; rewrites all five date fields consistently, checks `image:` and the OG asset, runs the
   linter, refuses on G1 failure, moves the file. The five-date-field update is exactly the kind
   of manual step that silently drifts.

4. **Generate the `DRAFTS.md` inventory table** from `readiness:` front matter instead of
   maintaining it by hand. Keep the prose sections — cluster analysis and per-draft notes are
   real editorial judgment. Automate only the table that went stale.

5. **Add a CI staleness check.** Fail (or warn) if `SCHEDULE.md`'s buffer line disagrees with the
   actual count of future-dated posts. A tracker that can silently disagree with reality
   eventually will.

**Exit criteria:** `draft-status.py` and `promote-draft.py` exist and work. `DRAFTS.md`'s
inventory table is generated. `jekyll-checks.sh` reports buffer health.

**Artifacts:** `scripts/draft-status.py`, `scripts/promote-draft.py`,
`.article-review/PHASE6-TOOLING.md`

---

### Phase 7 — Cross-Repo Intake

**Effort:** ongoing; 2 hours to set up the intake list
**Purpose:** Pull the ~16 candidates from `k8s-proxmox/docs/` and the jellyfin plugin into the queue.
**Independent of Phase 8 — either order.**

**Entry criteria:** Phase 5 done (there needs to be a queue to feed).

**Steps:**

1. **Create `.article-review/INTAKE.md`** from [Appendix B](#appendix-b--cross-repo-candidate-inventory).
   One row per candidate: source file, working title, substrate score, blocked-on, effort.

2. **Start with the four lowest-risk**, in this order:
   - **Jellyfin B** — the "Future Work, six weeks later" follow-up. Published article 6 named
     specific gaps; PRs #66–69 closed them. The narrative is pre-written by the article's own
     admissions, and it's auditable against itself. Rare and worth using.
   - **Jellyfin A** — Radarr/Sonarr remediation loop, 2 parts. The flagship: 90% source material,
     shipped and tested, and completely absent from the published series.
   - **`k8s-proxmox/docs/GPU-PCIE-RTD3-INVESTIGATION.md`** — fix validated on all four P620 nodes
     Aug 13. No competing draft. A real root-cause story with a confirmed fix.
   - **`k8s-proxmox/docs/CEPHFS-LXC-PERMISSIONS.md`** — self-contained, pairs with plugin PR #40.

3. **Scope the two big series** before starting either:
   `docs/ARR-SUITE-DEPLOYMENT-PLAN.md` (170K → 3–4 parts) and `docs/SITE-TO-SITE-VPN.md`
   (85K, live at 3 of 5 sites → scope to what's deployed). Both are the largest untapped bodies
   of verified work available. Both will sprawl without a part-boundary decision up front.

4. **Respect the do-not-write list** in Appendix B. Planning-only docs and superseded docs stay
   unwritten. This is gate G3 applied at intake, which is much cheaper than applying it after drafting.

**Exit criteria:** `INTAKE.md` exists and is prioritized. Candidates enter `QUEUE.md` as they're
drafted.

**Artifacts:** `.article-review/INTAKE.md`

---

### Phase 8 — Published-Post Debt

**Effort:** batched background work
**Purpose:** Clean up the 190 published posts. **Independent of Phase 7.**

**Entry criteria:** Phase 5 done. Do not start this before the schedule is running — it is
lower value than shipping, and it is the kind of work that expands to fill available time.

Three separable projects:

**8a — Legacy archive (59 posts, pre-2023).** All 59 lack `description` and `image`; 50 lack
`tags`; 35 lack `last_modified_at`. These are 2001–2016 posts carried through WordPress → Blogger →
Jekyll migrations. `lint-frontmatter.py` correctly treats them as warn-only.

Decide the policy before doing the work, because it changes the effort by an order of magnitude:
- **(i)** Leave as-is, accept them as an archive
- **(ii)** Bulk-add `description` and `tags`, skip images — scriptable, a few hours
- **(iii)** Full modernization including OG images — days

Recommendation: **(ii)**. `description` drives search snippets and `tags` drive navigation.
OG images on a 2011 post about a Seagate NAS have no meaningful return.

**8b — SVP strengthening edits (8 posts).** `DRAFTS.md` already scoped these: ~2.5 hours total
for targeted 2–3 paragraph insertions, ranked by impact. Highest four: QuickSight Vanity URLs,
Managing AI Agent Context, AI Context Files Reference, Google Service Sprawl. This is a
well-specified, bounded task — just do the top four in one sitting.

**8c — Series navigation.** Multi-part series use hand-written cross-references. There are now
several 3–5 part series. `2026-07-20-jekyll-post-series-navigation.md` is the draft for this —
note it's a 315-word stub, so the *work* comes before the *article*. Correct order: build it,
retrofit the existing series, then write the article. That sequencing is the whole thesis of this
plan applied to itself.

**Exit criteria:** per sub-project. Each is independently completable.

**Artifacts:** `.article-review/PHASE8-LEGACY.md`, `.article-review/PHASE8-SVP.md`

---

## Appendix A — Verified Audit Numbers

Measured 2026-09-02 by `.article-review/audit.py`. Regenerate rather than trusting these
if `baseline_date` is stale.

### Inventory

| Metric | Value |
|--------|-------|
| Published posts (`_posts/`) | 190 |
| Article drafts (`_drafts/`) | 68 |
| Tracker files (`_drafts/*.md`, non-article) | 17 |
| Total draft words | ~92,800 |
| Total published words | ~220,800 |
| Future-dated posts (the buffer) | **0** |

### Front matter — modern posts (2023-01-01 and later, n=131)

| Field | Missing |
|-------|---------|
| `description` | 0 |
| `last_modified_at` | 0 |
| `image` | 0 |
| `tags` | 1 |
| `categories` | 2 |

This is the correction to `TODO.md`, which claims 122 of 173 posts lack `description`.

### Front matter — legacy posts (pre-2023, n=59)

| Field | Missing |
|-------|---------|
| `description` | 59 |
| `image` | 59 |
| `tags` | 50 |
| `last_modified_at` | 35 |

### Front matter — drafts (n=68)

| Field | Missing |
|-------|---------|
| `description`, `tags`, `categories`, `last_modified_at` | 0 |
| `image` | 49 |
| excerpt separator | 7 |

Commit `3f51c81` ("fill front matter schema gaps across 34 WIP drafts") is why these pass — and
why front matter no longer discriminates ready from unready.

### Size distribution

| | min | p25 | median | p75 | max |
|---|---|---|---|---|---|
| Drafts | 20 | 423 | 1,233 | 1,754 | 8,364 |
| Posts | 19 | 329 | 1,019 | 1,698 | 6,306 |

21 drafts under 600 words. 2 drafts over 4,000. The published p75 of 1,698 is the practical
target band; 8,364 is an outlier that needs splitting.

### 2026 publishing cadence

| Month | Posts |
|-------|-------|
| Jan | 2 |
| Feb | 3 |
| Mar | 1 |
| Apr | 22 |
| May | 22 |
| Jun | 7 |
| Jul | 4 |
| Aug | 10 |
| Sep | 0 |

Day-of-week across 2026: Wed 15, Mon 13, Tue 12, Fri 10, Thu 9, Sat 9, Sun 3.
Last post 2026-08-21. **Current gap: 12 days.**

---

## Appendix B — Cross-Repo Candidate Inventory

From a dedicated read-only inventory of both repos. Substrate scores use the Phase 2 axis.

### `k8s-proxmox/docs/` — write from here

| Source | Working title | Substrate | Blocked on | Effort |
|--------|--------------|-----------|-----------|--------|
| `GPU-PCIE-RTD3-INVESTIGATION.md` | Chasing a GPU That Falls Off the PCIe Bus: RTD3 D3cold on the P620 Fleet | S4 | nothing — validated on all 4 nodes 2026-08-13 | 3–5h |
| `ARR-SUITE-DEPLOYMENT-PLAN.md` (170K) | The *arr Suite on Proxmox LXC (3–4 parts) | S3/S4 | Phase 1 round-trip test open; Phase 3 open. Enough verified for 3–4 parts | 12–16h |
| `SITE-TO-SITE-VPN.md` (85K) | Multi-Site WireGuard with GL.iNet Brume (series) | S3 | live at 3 of 5 sites; Brume 3 migration not done. Scope to deployed | 10–14h |
| `CEPHFS-LXC-PERMISSIONS.md` | Unprivileged LXC UID Mapping for Shared CephFS Media | S4 | nothing | 3–4h |
| `MEDIA-CLEANUP.md` (34K) | What an Integrity Scanner Found in a Real 2,000-Title Library | S3 | "No ARR suite yet" framing stale — reconcile first | 5–7h |
| `NVIDIA-GPU-KERNEL-PINNING.md` (43K) | Kernel Pinning on Proxmox and Why DKMS Drivers Need It | S3 | newer findings not yet folded in; pin the scope | 5–7h |
| `CEPHFS-BACKUP-PIPELINE.md` + `ZFS-USB-REPLICATION.md` | A 3-Tier CephFS Backup After Finding the Old One 6.5 Months Stale | S3 | built and Grafana-monitored but **deliberately not in cron** — needs honest framing or wait | 4–6h |
| `TECHNITIUM-DNS.md` (18K) | Multi-Site DNS with Technitium and Tailscale Replication | S3 | DHCP not migrated; RFC2136 untested | 4–6h |
| `AUTOSCALER.md` | The Proxmox Cluster Autoscaler Config Everyone Copies Doesn't Exist | S4 (as correction) | works without a live cluster; CAPI half unverified | 4–5h |
| `REVERSE-PROXY-COMPARISON.md` | Picking a Reverse Proxy, Then Having the Answer Archived Under You | S3 | evaluation not deployment; hook is ingress-nginx's Mar 2026 archival | 4–5h |
| `PIKVM-AIMOS-KVM.md` (27K) | PiKVM v3 + 8-Port AIMOS Switch: What Actually Works | S2 | bench verification not done. Draft exists: `_drafts/2024-04-03-pikvm-and-kvm.md` | 6–8h after bench |

### `jellyfin-plugin-media-integrity-scanner` — 6 candidates

Published series covers through **v0.1.1** (2026-08-02). Since then: v0.2.0, v0.3.0, and 55 dev
builds through v0.3.0-dev.55. Roughly 40 feature/fix commits uncovered.

| ID | Working title | Substrate | Notes |
|----|--------------|-----------|-------|
| **A** | Closing the Loop: Forwarding Corrupt Files to Radarr and Sonarr (2 parts) | S4 | Strongest candidate. `ARR-INTEGRATION-PROPOSAL.md` 56K + PRs #77–80 + 20 source files + 8 test files. Absent from published series. |
| **B** | Everything on the Future Work List, Six Weeks Later | S4 | Published article 6 named gaps; PRs #66–69 closed them, several verbatim. Auditable follow-up. |
| **C** | Scoped Scans, and the Bug That Found Zero TV Episodes | S4 | PRs #71–76. #75 is a proper bug story: scoped queries never set `Recursive`. |
| **D** | Operational Tooling: Backup, Restore, VACUUM, CSV Export | S4 | PRs #53/#60/#62. Two were on the published Future Work list. |
| **E** | Proving Cross-Platform Support by Running on Windows | S4 | PRs #69/#63. Thin alone — fold into B. |
| **F** | Hardware vs Software Decode, Tracked Per Result | S3 | PR #63 + the k8s GPU investigation. Best cross-repo pairing available. |

Project maturity, for the record: 363 test attributes across 34 test files, 6 CI workflows,
Playwright E2E with 7 specs, 57 tags, 4 stable releases, 80 PRs, active Dependabot. This is a
mature project and the writing should say so.

### Do not write

**`k8s-proxmox/articles/` — factually wrong now:**
`08-CLUSTER-AUTOSCALER.md` (documents a nonexistent `cloudProvider` value),
`13-CALICO-NETWORK-POLICIES.md` (Calico replaced by Cilium),
`06-INGRESS-CERT-MANAGER.md` (nginx-ingress archived Mar 2026),
`00-PROXMOX-FOUNDATION.md` (5 nodes/Reef vs actual 6 nodes/Squid),
`03-KUBERNETES-DEPLOYMENT.md` (1.33+Calico vs 1.36+Cilium),
plus `02` and `15` (stubs) and the two `.OLD` files.
`06-PROMETHEUS-GRAFANA-MONITORING.md.OLD` has ~250 lines of real content stranded under a
"Topics to Cover" heading — salvage the content, don't publish the file.

**`k8s-proxmox/docs/` — planning only, nothing built:**
`EBOOK-STACK-DEPLOYMENT-PLAN.md`, `NETWORK-VLAN.md`, `WYSE3040-HA.md`, `PVE9-UPGRADE-PLAN.md`,
`MEDIA-INTEGRITY-DB-MIGRATION-PLAN.md`, `PROFILARR-VS-RECYCLARR-EVALUATION.md`.

**Superseded:** `HOMARR.md`, `CLUSTER-SUMMARY.md` (self-labeled point-in-time snapshot from
Jan 2026 with wrong version numbers — do not quote as current state).

**Status unverified:** `NUT-UPS-MANAGEMENT.md` reads as complete guidance, but `PRE-K8S-TASKS.md`
lists the whole NUT/UPS deployment as Not Started. Verify before writing.

**Already covered by existing drafts or posts** — don't re-pitch: `HOMEPAGE.md`/`HOMARR.md`
(3 drafts), `CLIENT-BACKUP.md` (UrBackup draft), `AGENT-DEV-LXC.md` (3 drafts),
`PVE9-UPGRADE-PLAN.md` (5 drafts), `BOOT-DRIVE-ANALYSIS.md` (published, ZFS boot mirrors 1–5),
`USB-SMART-MONITORING.md` (published), `CADDY-UI.md`/`PROXY-SERVICES.md` (3 published),
`CEPH-OSD-SSD-ACCELERATION.md` (published).

---

## Appendix C — Stale Claims Register

Every one of these is a claim that will propagate into a published article if not corrected first.
Fix the source, then write. Phase 4, Step 1.

| Location | Stale claim | Reality |
|----------|-------------|---------|
| `jellyfin.../ARR-INTEGRATION-PROPOSAL.md` header | "Proposal — not started. no code in this repo has been changed" | All 4 phases shipped, PRs #77–80 |
| `jellyfin.../README.md` (×4) | Links to `CODE_REVIEW.md` | File never existed in git history |
| `jellyfin.../README.md` | "298 unit tests" | 363 test attributes |
| `jellyfin.../README.md` | Features list | Omits Radarr/Sonarr integration |
| `jellyfin.../README.md` | Blog Series list has 5 entries | 6 published |
| `k8s-proxmox/docs/MEDIA-CLEANUP.md` | "No ARR suite yet" | Suite built; plugin Arr integration shipped |
| `k8s-proxmox/articles/ARTICLES.md` | "✅ Completed" list | Means *the file exists*, not *the infra runs* |
| `k8s-proxmox/articles/04, 15, 19, 20` | H1 article numbers | Say 8, 16, 20, 15 respectively |
| `k8s-proxmox/articles/08` | `cloudProvider=proxmox` | Value does not exist upstream. `docs/AUTOSCALER.md`: "would not have worked" |
| `_drafts/DRAFTS.md` | "Drafts in `_drafts/`: 56" | 68 |
| `_drafts/DRAFTS.md` | "Last updated: 2026-06-10" | Contains 2026-08-12 content |
| `_drafts/DRAFTS.md` Kiro cluster | "Both articles published" | Three are |
| `_drafts/SCHEDULED.md` | "Today: 2026-06-11" | 12 weeks stale |
| `_drafts/SCHEDULED.md` | Jul/Aug/Sep mostly open slots | 14 articles published in that window |
| `_drafts/SCHEDULED.md` | "Cadence: once per week, Monday" | Jul was Tuesdays; Aug was Mon/Wed/Fri |
| `TODO.md` Front Matter Hygiene | "122 of 173 missing description" | 0 of 131 modern posts |
| `TODO.md` | "51 of 173 missing tags" | 1 of 131 modern; 50 are legacy pre-2023 |

---

## Closing Note

The engineering in these two repos is strong and the writing about it is largely good. What's
missing is a hundred lines of glue: a gate that says *this is done*, a buffer that publishes on a
schedule without anyone remembering to, and trackers that can't silently disagree with the
filesystem.

Phases 0–5 install that glue. Phase 6 makes it hard to remove. Everything after is cleanup that
can wait.

One caution worth stating plainly: **this document is itself a tracker, and trackers in this repo
have a track record.** The mitigation is Phase 6, Step 5 — a CI check that fails when the tracker
and the filesystem disagree. Until that exists, re-run the audit before trusting any number here.


---

## Amendment 2 — 2026-11-24 reassessment

Re-measured with `python3 .article-review/audit.py` (run from the repo root) after fetching all
remotes. Nothing was published and no phase advanced between 2026-10-30 and today. The only
change is that the queue of unpublished work grew.

### Numbers

| Metric | 2026-09-02 | 2026-10-30 | 2026-11-24 | Since 10-30 |
|--------|-----------:|-----------:|-----------:|------------:|
| Published posts | 190 | 191 | 191 | 0 |
| Article drafts | 68 | 71 | 84 | +13 |
| Draft words | 92,848 | 98,041 | 131,432 | +33,391 |
| Future-dated buffer | 0 | 0 | 0 | none |
| Days since last publish | 12 | 46 | **71** | +25 |
| Last published | 2026-08-21 | 2026-09-14 | 2026-09-14 | |
| Drafts absent from trackers | 12 | 15 | **28** | +13 |
| Drafts with `readiness:` set | 0 | 0 | 0 | none |
| Drafts over 4,000 words | 2 | 2 | 3 | +1 |
| Stubs under 600 words | 21 | 21 | 21 | none |
| Drafts missing `image` | 49 | 50 | 60 | +10 |

Draft median is 1,474 words (was 1,233) and p75 is 2,105. The new drafts are longer than the
published p75 of about 1,700.

### Verdict on the original diagnosis

The headline holds and is stronger: **the control plane is the problem, not the content.** The
failure it predicted has continued for 71 days. In the same period the draft pile grew by 18%
in count and 34% in words. Every one of the 13 new drafts was written after the review recommended
"stop all new engineering-driven drafting" while the buffer is red, and the buffer has been red
the whole time.

| Original finding | Status 2026-11-24 |
|------------------|-------------------|
| 1. Trackers decoupled from the filesystem | **Worse.** `DRAFTS.md` and `SCHEDULED.md` were last touched 2026-08-12/13. 28 drafts are invisible to them (was 12). No `SCHEDULE.md` exists; `audit.py` already looks for one. |
| 2. Cadence declared but never enforced | **Confirmed.** No cadence at all since 2026-09-14. |
| 3. No definition of done | **Confirmed.** `readiness:` is unset on all 84 drafts. Several new drafts are visibly finished and revised (RTX 3060, USB3 PCIe, Seagate UAS), but nothing marks them so. |
| 4. Verification debt | **Partly improving, unproven.** Recent commits show the right habit: "withdraw the usb-storage inference", "revert April cross-links until the WAL/DB migration article is published". That is ad hoc verification, not Phase 4. The `INTAKE.md` open verifications are unresolved (see below). |
| 5. Inventory ~40% larger than believed | **Understated.** The 13 new drafts add to the ~56 candidates, mostly from the same Ceph/homelab work that `INTAKE.md` called the best-covered material. |

### What is new since 10-30

1. **13 new drafts**, grouped:
   - *Seven Ceph Nodes* series, now numbered 1 to 4 (commit `80c873a`, 2026-11-11): Part 1 (the plan before any data moved), Part 2 (live media to erasure coding), Part 4 (USB resets, a slow SSD, a rate limit), plus the SSD tier for LXC root disks.
   - Hardware/diagnosis one-offs: RTX 3060 and cheap PSU (5,631 words, now over the 4,000 split threshold), USB3 PCIe link stuck at 2.5 GT/s, Seagate USB SMART/UAS quirk, Ceph mon election storm.
   - A status article (`2026-11-03-business-law-ceph-repairs-and-the-proxmox-9-wait.md`) that lists the draft queue itself.
   - **Gitea/GitHub replication** (`2026-11-21-gitea-local-github-replication.md`), a new infrastructure topic.
2. **Series numbering has a gap.** The Seven Ceph Nodes series has titled Parts 1, 2 and 4. `2026-11-06-ceph-ssd-osds-fast-root-disks-for-lxc.md` is dated between Parts 2 and 4 and has no part number in its title, so it is probably Part 3. Retitle it or write a Part 3 before scheduling; a series cannot publish with a hole.
3. **The status article is a symptom.** The repo now has a draft whose job is to say what the draft queue holds. That is the tracker problem being solved in prose by hand, which is the failure mode this plan was written to prevent.
4. **Infrastructure changed under the release mechanism.**
   - Gitea is now `origin`. GitHub gets commits through the 5-minute sync bridge (`.gitea/workflows/gitea-github-sync.yml`). The build, the daily 10:05 UTC cron and the drafts deploy still run on GitHub, so the Part II mechanism works only if the bridge has pushed. A sync PR left unmerged means GitHub does not have the latest drafts or promotions. Phase 6 tooling must check both remotes.
   - `jekyll.yml` and the other workflows were pinned to `ubuntu-24.04` on 2026-11-10 to fix a Ruby setup failure. **Checked 2026-11-24 with `gh run list`:** the daily 10:05 UTC cron succeeded every day from 2026-09-08 to 2026-11-23 except 2026-11-09 and 2026-11-10, which failed at Setup Ruby (and the drafts deploy failed the same two days). Nothing was due on those days, so no post was lost. The gap is purely the empty buffer, not a broken pipeline.
   - Ten dependency PRs were merged on 2026-11-10, so the build toolchain changed. Run a full build before promoting anything.
5. **Local working tree.** `_posts/2026-07-28-resume-machine-view-ats-validation.md` has a 2-line uncommitted edit. It is outside the plan but sits in the published area, so commit or discard it before Phase 5 promotions.

### Changes to the plan

| Area | Original | Revised |
|------|----------|---------|
| Phase 5 target | buffer >= 4 | Unchanged, but pick the first 4 from the *verified, already-revised* drafts (RTX 3060 after a split, USB3 PCIe, Seagate UAS, Ceph mon election storm) so it can start without Phase 2 finishing. |
| Phase order | 1 -> 2 -> 3 -> 4 -> 5 | Run a **fast path**: Phase 5 minimum (promote 4) first, then Phase 1 and the rest. 71 days of delay is a larger cost than doing the phases out of order. |
| Phase 1 | Reconcile trackers by hand | Replace `DRAFTS.md` and `SCHEDULED.md` with generated output from `audit.py --inventory`. Hand-edited trackers drifted three times. |
| Phase 6 | Draft status and promote scripts | Add: refuse to run when `origin` and the GitHub copy differ, and list `sync/github/*` branches that are awaiting review. |
| Phase 7 | Intake from k8s-proxmox and the plugin repo | Add the Ceph/erasure-coding material, now largely drafted, and mark it covered so it is not rewritten from the repos. |
| Phase 8 | Published-post debt | Unchanged; still last. |

### Still unverified or unresolved

- `INTAKE.md` open verifications (openwrt-vm 1001 PBS backup fix, *arr round-trip test, gap-fill copy status) have not been rechecked. The new drafts may have settled some of them.
- The PVE 8 to 9 series (5 parts) still cannot conclude: the 2026-11-03 status article is titled around "the Proxmox 9 wait", which suggests Part 5's upgrade has still not run. The 10-30 recommendation (publish 1-4, hold 5) stands.
- I did not read the 13 new drafts for factual accuracy. Their readiness is judged from titles, size and commit messages only.
- GitHub Actions history was checked (see item 4 above); the Gitea Actions history for the sync bridge was not.

### Recommended next three actions

1. Promote four verified drafts as future-dated posts (Phase 5 fast path). That ends the red buffer.
2. (Done 2026-11-24: production builds are healthy.) Run one full local build after the 2026-11-10 dependency bumps before promoting.
3. Stop adding drafts until the buffer is at least 4. The plan says this already; the data shows it was not followed.
