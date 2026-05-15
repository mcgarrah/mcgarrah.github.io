# Why Your Data Scientists Need Production Data (And How to Give It to Them Safely)

**Subtitle:** The Platform Decision That Determines Whether Your AI Initiative Succeeds or Fails

**Author:** McGarrah

**Planned:** May 17, 2026

**URL:** TBD

**Tags:** Machine Learning, Data Science, Platform Engineering, Security, Compliance, AI, Leadership

---

A note on direction: my first two newsletters covered [building homelab infrastructure](https://mcgarrah.substack.com/p/from-homelabs-to-machine-learning) and [treating a blog like a software project](https://mcgarrah.substack.com/p/from-markdown-to-production-building). Both were strong technically, but they told the story of a senior engineer — not someone who has spent a decade navigating the organizational politics of getting data scientists access to the data they need while keeping security teams comfortable.

This newsletter shifts toward that broader perspective. The technical depth stays. What changes is the lens: technology decisions as organizational negotiations, platform architecture as a leadership discipline, and the recognition that the hardest problems in AI are not algorithmic — they are structural.

---

## The Conflict Nobody Talks About

Every enterprise building an AI capability hits the same wall within the first six months. The data science team needs production data to train useful models. The security team says production data stays in production. The standard software development lifecycle — synthetic data in dev, sanitized data in staging, real data only in prod — does not accommodate machine learning.

This is not a tooling problem you can solve with a better data catalog or a fancier anonymization pipeline. It is a fundamental architectural conflict between two legitimate requirements:

1. **Data scientists need interactive, flexible environments** — notebooks, experimentation, iterative exploration, the ability to fail fast and try again
2. **Production data requires production-grade security controls** — audit logging, access restrictions, compliance frameworks, the ability to demonstrate to auditors that sensitive data is protected

In the standard SDLC model, these requirements live at opposite ends of the environment hierarchy. Development is flexible but has no real data. Production has real data but no flexibility. Data science needs both simultaneously.

I have navigated this conflict across three industries — healthcare under HIPAA (Blue Cross NC), financial services under SOC 2 (Envestnet), and government under IRS Safeguard requirements (NC Department of Information Technology). The conversation always starts the same way: "Why can't they just use the staging data?" And the answer is always the same: because models trained on synthetic data learn the patterns of synthetic data, not the patterns of your business.

## The Framework

The resolution is a promotion framework purpose-built for data science workloads. Instead of forcing ML into the SDLC model, you build a parallel track that acknowledges the production data requirement from the start.

The full technical framework is in my blog post [Five Stages of a Successful Cloud Data Science Platform](https://mcgarrah.org/five-stages-cloud-data-science-platform/), but the executive summary is:

**Five environments, two tracks:**

- **Infrastructure Track** (no production data): Infrastructure Development → Infrastructure Pre-Production
- **Data Science Track** (production data from the start): Prod Discovery → Prod Integration → Final Production

The key insight is the "Prod Discovery" environment — it has production data (hence "Prod") but allows interactive, exploratory work (hence "Discovery"). It is not a development environment with production data bolted on. It is a production environment with controlled flexibility added. The distinction matters for compliance conversations.

## Why This Is a Leadership Problem, Not an Engineering Problem

The technical architecture is the easy part. Any competent platform engineer can build the infrastructure. The hard part is getting three constituencies to agree:

**The CISO** wants minimal data exposure, maximum controls, and no exceptions to the standard model. Their incentive structure punishes data breaches and audit findings. Saying "yes" to production data in a flexible environment is career risk.

**The Chief Data Officer** wants production data access with development-like flexibility and minimal friction. Their incentive structure rewards model accuracy and time-to-insight. Waiting six weeks for a data access request kills momentum.

**The business unit leaders** want ML models that actually work — which requires real data — without compliance risk that could result in regulatory action. They do not care about the architecture; they care about outcomes.

The five-stage framework gives each constituency what they need without requiring any of them to compromise their core requirements. Security gets production-grade controls on every environment with real data. Data science gets interactive access. Business gets models trained on real data with a documented compliance posture.

This is the kind of problem that an Executive MBA teaches you to see differently. The technical architecture is a negotiation artifact — it succeeds not because it is technically elegant, but because it gives each stakeholder a way to say yes.

## The Compliance Conversation

One pragmatic detail that saves weeks of debate: **do not call the interactive data science environment "Development."**

When a SOC 2 auditor sees an environment labeled "Development" with production data, they flag it immediately. The standard control framework says development environments should not have production data. Full stop.

When they see "Prod Discovery" with documented access controls, audit logging, network segmentation, and data classification policies, the conversation shifts from "this is architecturally wrong" to "are these controls adequate?" That is a much more productive conversation — and one you can win with evidence.

I learned this the hard way during the first Envestnet Payments SOC 2 Type 1 audit. Naming matters. Framing matters. The architecture is the same either way, but the compliance narrative is completely different.

## What This Means for AI Leaders

If you are building an AI organization — or evaluating whether your current platform can support one — this is the first infrastructure decision you need to get right. Everything downstream depends on it:

- **Model quality** depends on training data quality, which depends on production data access
- **MLOps maturity** depends on a promotion path from experimentation to production
- **Compliance posture** depends on controls designed into the architecture, not bolted on after the fact
- **Team velocity** depends on data scientists not waiting weeks for data access approvals
- **Talent retention** depends on data scientists having the tools and access to do meaningful work

The standard SDLC model will not give you this. You need a purpose-built framework that acknowledges the fundamental difference between application development and data science: production data is not the destination — it is the starting point.

For the full technical framework with environment diagrams and implementation details, see [Five Stages of a Successful Cloud Data Science Platform](https://mcgarrah.org/five-stages-cloud-data-science-platform/) on my blog.

---

## About Me

I'm Michael McGarrah. I've spent 30 years building and leading technology organizations — from enterprise architecture for North Carolina state government to cloud platforms running production ML models in healthcare and financial services. I hold an M.S. in Computer Science (AI/ML) from Georgia Tech and I'm completing an Executive MBA at UNC Wilmington, deliberately bridging the gap between technical depth and business strategy. I still write code, debug distributed systems, and build infrastructure — because the best technology leaders never stop being engineers.

You can find more of my writing at [mcgarrah.org](https://mcgarrah.org), my detailed resume at [mcgarrah.org/resume](https://mcgarrah.org/resume), and my profiles on [LinkedIn](https://www.linkedin.com/in/michaelmcgarrah/), [GitHub](https://github.com/mcgarrah), and [Google Scholar](https://scholar.google.com/citations?user=Lt7T2SwAAAAJ).
