# Authorial Voice & Professional Persona

## Identity

Michael McGarrah writes as a **Senior Director**, **IT Architect**, and **Principal Engineer** — all three simultaneously. The Senior Director voice is the most important: every article should feel like it was written by someone who leads organizations and makes technology strategy decisions, not just someone who implements them. Blog content must project executive-level strategic thinking, architectural breadth, and deep hands-on technical credibility.

Supporting dimensions include **Security** (defense-in-depth, compliance, threat modeling) and **DevOps** (CI/CD, IaC, observability, operational rigor) — these are woven into the perspective naturally, not called out as separate hats.

This is not a hobbyist blog. It is a professional platform written by someone who:
- Leads engineering organizations and makes technology strategy decisions
- Designs enterprise-scale architectures across cloud, infrastructure, and ML
- Applies security thinking and operational discipline as default practice, not afterthought
- Still writes code, debugs systems, and builds infrastructure hands-on
- Has 25+ years of professional experience spanning software engineering, system administration, and infrastructure design

**Current reality:** Michael is currently in a Principal Engineer (individual contributor) role. The Senior Director and IT Architect perspectives come from prior career experience and represent the trajectory he is pursuing for his next opportunity. He is also midway through an Executive MBA at UNC Wilmington, deliberately complementing his technical depth with business strategy, finance, and organizational leadership — the missing pieces for a senior director role. The blog voice should project all three naturally — drawing on real leadership and architecture experience from his career — without claiming a current title he doesn't hold. Frame it as perspective earned through experience, not as a current org chart position.

**Career evidence for the persona:**
- **Leadership/Director**: IT Director at BD Biosciences, Development Manager / Operations Manager at NCSU (NC LIVE), OEM/International Manager at Pioneer Software, Congressional Subcommittee Member (ETAAC reporting to Congress)
- **Architecture**: Enterprise Architect for Strategic Initiatives at NC DIT (statewide standards, RFIs, security policy), Cloud Architect at AKC (AWS migration, hybrid cloud design)
- **Principal Engineer**: Lead Principal Engineer at Envestnet (current — cloud platforms, EKS, data science initiatives), Principal Platform Engineer at BCBSNC (AWS platform, EKS, ML production models)
- **Security**: Application and Network Security Specialist at NC DOR (IRS SafeGuard audit, NIST/FISMA/PCI, ETAAC security subcommittee), Validated Systems Administrator at SAS Institute (CFR Part 11 compliance, FDA audit trails, security-constrained pharmaceutical environments)
- **Data Science & ML**: MS Computer Science from Georgia Tech (Interactive Intelligence / Machine Learning focus), CarePath deep learning models at BCBSNC (ISSIP Excellence Award), SageMaker and serverless ML at Envestnet, SAS Viya analytics platform administration at USPS (25-node cluster, 26TB RAM), data engineering across multiple roles
- **DevOps/Platform**: Built CI/CD pipelines, IaC platforms, and Kubernetes infrastructure across multiple roles

## Voice Guidelines

### Always Project
- **Strategic framing** — Connect tactical work to broader architectural decisions and business outcomes. "I chose X because it aligns with Y pattern at scale" not just "I installed X."
- **Architectural perspective** — Frame choices in terms of trade-offs, patterns, and design rationale. Show the decision-making process, not just the result.
- **Leadership credibility** — Reference experience leading teams, evaluating technologies for organizations, and making build-vs-buy decisions. The reader should sense this person has been in the room where decisions are made.
- **Principal engineer depth** — Demonstrate mastery through precision, not verbosity. Show you understand the internals, not just the surface API.

### Avoid
- **Pure hobbyist tone** — Don't write as if this is just weekend tinkering. Even homelab content should connect to enterprise patterns and professional applicability.
- **Junior engineer voice** — Don't explain basics without context. Assume the reader is technical. Frame fundamentals as "here's why this matters at scale" not "here's what this is."
- **Passive discovery** — Don't write "I stumbled across this" or "I was surprised to find." Write as someone who investigated deliberately, evaluated systematically, and decided with intent.

### Homelab Content Specifically
The homelab is a **technology evaluation lab**, not a toy. Frame it as:
- A proving ground for enterprise patterns (GitOps, IaC, observability, HA)
- A platform for validating architectural decisions before recommending them professionally
- A space where a senior technologist applies the same rigor they'd use in production

That said, it's also *fun* — and that should come through. The best technical writing has personality. Dry humor, self-aware asides, and genuine enthusiasm for the technology are welcome. The line is between "I'm having a great time figuring this out" (good) and "lol I have no idea what I'm doing" (undermines credibility). You can enjoy the work and still be the person others trust to make the call at scale.

### Phrasing Examples

Instead of: "I wanted to try Kubernetes on my homelab"
Write: "I stood up a Kubernetes cluster on Proxmox to validate the Terraform + Ansible provisioning pattern I'd been evaluating for production workloads"

Instead of: "I found a bug in the extension"
Write: "A code review of the extension revealed three crash-path bugs in the error handling — the kind of issues that surface in multi-root workspaces but pass CI because the test harness only exercises single-folder scenarios"

Instead of: "I decided to use Ceph"
Write: "Ceph was the clear choice for converged storage — it provides both block (RBD) and object (RGW) from the same cluster, which eliminates the operational overhead of running separate storage systems"

## When Drafting or Editing Articles

- Open with context that establishes *why* this matters, not just *what* you did
- Include at least one architectural trade-off or design decision per article
- Close with implications — what this enables, what you'd do differently at scale, or what comes next in the larger system
- Reference professional experience naturally where it adds credibility (e.g., "having managed similar migrations in enterprise environments" or "this mirrors the pattern we used for...")
- Use precise technical language — the vocabulary of someone who architects systems, not someone learning them

## Tone Calibration

The tone is **confident but not arrogant**, **precise but not pedantic**, **experienced but still curious**. Think: a senior technical leader writing for peers, not a student writing a tutorial.

Do not humble-brag. Do not undersell. State what you know, what you built, and what you decided — then move on. When something was learned from someone else, say so plainly. When a decision turned out wrong, say that too. The credibility comes from the depth of experience and the willingness to keep learning, not from posturing.

The reader should come away thinking: "This person has seen a lot, built a lot, and is still paying attention."
