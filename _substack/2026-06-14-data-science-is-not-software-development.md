# Data Science Is Not Software Development (And Managing It Like Software Development Is Why Your AI Initiatives Fail)

**Subtitle:** Why the research model — not the SDLC — is the correct operational framework for machine learning teams

**Author:** McGarrah

**Published:** June 14, 2026

**URL:** TBD

**Tags:** Machine Learning, Data Science, Leadership, Platform Engineering, Research, AI/ML, Management

---

Last month I wrote about [why your data scientists need production data](https://mcgarrah.substack.com/p/why-your-data-scientists-need-production-data) — the platform architecture decision that determines whether your ML models train on real patterns or synthetic noise. That article solved the infrastructure question. This one addresses the operational model question that sits on top of it.

The short version: most organizations manage data science teams using software development processes. Sprint planning, story points, predictable delivery timelines. And it fails — not because the data scientists are bad at their jobs, but because the work itself follows a fundamentally different success model.

---

## The Numbers

Good software development succeeds more than 4 out of 5 times. You gather requirements, design, build, test, ship. The outcome is predictable.

Good data science succeeds less than 1 out of 5 times. You form a hypothesis, design an experiment, run it, and discover your hypothesis was wrong. This is not failure — this is the process working correctly.

When you apply the software development model to data science, that 80% "failure" rate looks like a team performance problem. Managers ask why the team is not delivering. Stakeholders lose confidence. The team starts gaming metrics — reporting incremental progress on doomed approaches rather than honestly documenting failures and pivoting.

I have watched this pattern destroy data science initiatives at multiple organizations. The team is not underperforming. The management model is wrong.

## The Research Model

Academic research solved this problem centuries ago. The model is: hypothesis → experiment → document result (success or failure) → iterate. Documented failure is a first-class output. A paper demonstrating "approach X does not work under conditions Z" is publishable, citable, and valuable — it prevents the next researcher from wasting time on the same dead end.

Enterprise data science should work the same way:

- A model that does not improve on the baseline is a documented experiment that narrows the solution space
- Feature engineering that does not improve performance is evidence about what the data does and does not contain
- A hypothesis about customer behavior that the data refutes is organizational learning

The organizations that get this right — Google Brain, DeepMind, Meta FAIR — all operate on the research model internally. They publish papers about what did not work. They celebrate negative results. They measure progress in knowledge gained, not just models shipped.

## The Platform Connection

In my [Five Stages framework](https://mcgarrah.org/five-stages-cloud-data-science-platform/), the environment architecture maps directly to this operational model:

- **Prod Discovery** is the research lab — hypothesis testing, experimentation, documented failure. The research model operates here.
- **Prod Integration** is the engineering phase — automating confirmed results into reproducible pipelines. The software development model operates here.
- **Final Production** is deployment — serving customers.

The key insight: the research model and the software development model both have a place — but in different stages. Trying to apply one model across all stages is the root cause of most DS team dysfunction.

## What This Means If You Lead an AI Organization

**Staff for research, not just engineering.** Data scientists with research backgrounds understand the failure model intuitively. Engineers retrained as data scientists often struggle with the ambiguity.

**Budget for exploration, not just delivery.** A DS team that must justify every experiment with a business case will only pursue safe, incremental work. Breakthroughs come from exploratory work that might fail.

**Measure knowledge, not just output.** The documented experiment notebooks — including failures — are the team's intellectual property. They represent accumulated understanding of what works and what does not for your specific data and business.

**Separate the research phase from the engineering phase.** Do not apply engineering management to research work, or research timelines to engineering work.

Think of it as portfolio management: you invest across a portfolio of hypotheses knowing most will not pay off — but the ones that do will more than compensate. The same logic that makes venture capital work makes data science work. You need the organizational patience to let the portfolio mature.

## The Two-Article Foundation

This newsletter and the [production data access](https://mcgarrah.substack.com/p/why-your-data-scientists-need-production-data) piece from last month form a complete argument:

1. **Platform**: Give data scientists production data access with appropriate security controls (Five Stages)
2. **Operations**: Manage them using the research model, not the software development model (this article)

Together, they answer the question every Head of AI faces on day one: "How do I build an organization that can sustain long-term investment in ML — not just ship one model, but systematically build capability?"

The platform without the operational model produces expensive infrastructure that frustrated data scientists underutilize. The operational model without the platform produces brilliant hypotheses that can never be tested against real data. You need both.

For the full technical framework with architecture diagrams: [Why Data Science Follows the Research Model](https://mcgarrah.org/research-model-for-data-science/)

---

*If you're building an AI organization and this resonates, share it with someone who manages data scientists using sprint velocity. They need to hear this.*

## About Me

I'm Michael McGarrah. I've spent 30 years building and leading technology organizations — from enterprise architecture for North Carolina state government to cloud platforms running production ML models in healthcare and financial services. I hold an M.S. in Computer Science (AI/ML) from Georgia Tech and I'm completing an Executive MBA at UNC Wilmington, deliberately bridging the gap between technical depth and business strategy. I still write code, debug distributed systems, and build infrastructure — because the best technology leaders never stop being engineers.

You can find more of my writing at [mcgarrah.org](https://mcgarrah.org), my detailed resume at [mcgarrah.org/resume](https://mcgarrah.org/resume), and my profiles on [LinkedIn](https://www.linkedin.com/in/michaelmcgarrah/), [GitHub](https://github.com/mcgarrah), and [Google Scholar](https://scholar.google.com/citations?user=Lt7T2SwAAAAJ).
