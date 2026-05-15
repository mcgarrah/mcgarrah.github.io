# Why Your Data Scientists Need Production Data (And How to Give It to Them Safely)

**Subtitle:** A five-stage framework for the platform decision that determines whether your AI initiatives succeed or fail

**Author:** McGarrah

**Published:** May 17, 2026

**URL:** TBD

**Tags:** Machine Learning, Data Science, Platform Engineering, Security, Enterprise Architecture, AI/ML, Leadership

---

A quick note before we begin: if you've been reading my earlier newsletters — [From Homelabs to Machine Learning](https://mcgarrah.substack.com/p/from-homelabs-to-machine-learning) and [From Markdown to Production](https://mcgarrah.substack.com/p/from-markdown-to-production-building) — you'll notice a shift in tone here. Those pieces established the technical foundation: the infrastructure I build, the engineering discipline I practice, the tools I create. This newsletter builds on that foundation but steps back to the strategic level. The question is no longer "how do I build this?" but "how do I design the platform architecture that lets an entire data science organization succeed?" That shift reflects where I am professionally — bridging deep technical execution with the organizational and business strategy decisions that determine whether AI initiatives deliver value or die in pilot.

I am not abandoning the technical articles — those will continue roughly once a month as the foundation they have always been. What I am adding is a second thread focused on the "why" and the architecture: the platform decisions, the organizational patterns, and the leadership thinking that sits above the implementation. Think of it as two cadences: the technical pieces show I still build things; the strategic pieces show I know which things to build and why.

---

Every enterprise I have worked in over the past decade has hit the same wall.

Data scientists need production data to build useful models. The standard software development lifecycle assumes production data stays in production. These two facts are architecturally incompatible — and most organizations resolve the conflict by either giving data scientists garbage data (producing garbage models) or granting security exceptions that erode their compliance posture.

Neither outcome is acceptable. And the root cause is not a tooling problem — it is an organizational architecture problem that sits at the intersection of data engineering, security, compliance, and platform engineering.

## The Conflict

In classic SDLC, the environment hierarchy is clean: development has synthetic data, staging has sanitized data, production has real data. Security and flexibility are inversely correlated as you move up the stack. This works because application developers do not need real data to write and test code.

Data science is fundamentally different. Training a machine learning model on synthetic or sanitized data produces a model that has learned the patterns of synthetic data — not the patterns of your actual business. Feature engineering on sanitized datasets misses the edge cases, distributions, and correlations that exist in production. The entire value proposition of ML depends on learning from real data.

I have had this argument with development managers, project managers, and security teams across healthcare, financial services, and government. The conversation always starts the same way: "Why can't they just use the staging data?" And the answer is always the same: because staging data is not production data, and the model quality difference is measurable.

## The Framework

The resolution is a promotion framework designed specifically for data science workloads. Instead of forcing DS into the SDLC model, you build a parallel track that acknowledges the production data requirement from the start.

**Five stages:**

1. **Infrastructure Development** — where you develop the platform itself. No production data. Standard IaC development.
2. **Infrastructure Pre-Production** — validated infra changes before release to production-data environments.
3. **Prod Discovery** — the interactive, exploratory environment where data scientists work. **Has production data.** Notebooks, feature engineering, model experimentation. Extensive monitoring and audit logging.
4. **Prod Integration** — automation layer. No interactive work. Automated pipelines validate DS work before it reaches customers.
5. **Production (Final Prod)** — where customers consume AI/ML insights. Most restrictive controls.

The "Prod" prefix on Discovery is deliberate. It signals to security and compliance teams that this environment holds real data and requires production-grade controls — while also providing the interactive flexibility data scientists need to do their work.

For the full technical framework with architecture diagrams and implementation details, I wrote a companion blog post: [Five Stages of a Successful Cloud Data Science Platform](https://mcgarrah.org/five-stages-cloud-data-science-platform/).

## Why This Is a Leadership Problem, Not a Technical Problem

The technical architecture is the straightforward part. The hard part is getting three constituencies to agree:

**The CISO** wants minimal data exposure, maximum controls, and no exceptions to the standard SDLC model. Their incentive structure punishes data breaches and audit findings — not slow model development.

**The CDO / Data Science team** wants production data access with development-like flexibility and minimal friction. Their incentive structure rewards model accuracy and time-to-production — not security posture.

**The business unit leaders** want ML models that actually work (which requires real data) without compliance risk. Their incentive structure rewards revenue impact — not architectural elegance.

The five-stage framework gives each constituency what they need: security gets production-grade controls and audit logging on every environment with real data; data science gets interactive access to production data; business gets models trained on real data with a documented compliance posture.

This is a negotiation artifact, not a technical specification. The framework succeeds because it gives each stakeholder a way to say yes without compromising their core requirements.

## Where I Have Applied This

This is not theoretical. I have built or operated variants of this framework across:

- **Regulated industries (BD Biosciences, NC DOR, SAS Institute — 2006–2013)** — FDA quality systems, IRS Safeguard compliance, and pharmaceutical clinical trial data under CFR Part 11. These roles established the principle that interactive access to sensitive data and auditable controls are not mutually exclusive — you design for both simultaneously.
- **Machine learning at scale (Measurement Incorporated — 2013–2015)** — PhD researchers building NLP models for automated essay scoring. The chaos of researchers breaking production with untested model changes is where I first witnessed the DS-vs-SDLC conflict and began evolving toward this framework.
- **Healthcare (BCBSNC — 2019–2021)** — Where the framework was fully realized and tested. CarePath ML platform on EKS under HIPAA constraints, processing claims data from all NC members. It survived production pressure and became the standard I carried forward.
- **Financial services (Envestnet — 2021–present)** — SageMaker and Bedrock across shared services and workload accounts. The mature DataLake (vEMR, Snowflake, Airflow) exemplifies this model in data engineering — phased promotion with gates at every stage.

The pattern is consistent across industries: the organizations that get this right build the platform first, then scale AI initiatives on top of it. The organizations that get it wrong try to bolt security onto an ad-hoc data access model after the data scientists have already built dependencies on it.

## The Decision Point

If you are building an AI organization — or evaluating whether your current platform can support one — this is the first infrastructure decision you need to get right. Everything downstream depends on it:

- **Model quality** depends on training data quality, which depends on production data access
- **MLOps maturity** depends on a promotion path from experimentation to production
- **Compliance posture** depends on controls designed into the architecture, not bolted on after the fact
- **Team velocity** depends on data scientists not waiting weeks for data access approvals

The standard SDLC model will not give you this. You need a purpose-built framework that acknowledges the fundamental difference between application development and data science: production data is not the destination — it is the starting point.

---

*If you found this useful, share it with someone building a data science platform. The full technical framework with architecture diagrams is on my blog: [Five Stages of a Successful Cloud Data Science Platform](https://mcgarrah.org/five-stages-cloud-data-science-platform/).*

## About Me

I'm Michael McGarrah. I've spent 30 years building and leading technology organizations — from enterprise architecture for North Carolina state government to cloud platforms running production ML models in healthcare and financial services. I hold an M.S. in Computer Science (AI/ML) from Georgia Tech and I'm completing an Executive MBA at UNC Wilmington, deliberately bridging the gap between technical depth and business strategy. I still write code, debug distributed systems, and build infrastructure — because the best technology leaders never stop being engineers.

You can find more of my writing at [mcgarrah.org](https://mcgarrah.org), my detailed resume at [mcgarrah.org/resume](https://mcgarrah.org/resume), and my profiles on [LinkedIn](https://www.linkedin.com/in/michaelmcgarrah/), [GitHub](https://github.com/mcgarrah), and [Google Scholar](https://scholar.google.com/citations?user=Lt7T2SwAAAAJ).
