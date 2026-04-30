---
layout: none
date: 1999-12-31
sitemap: false
---

# Envestnet — Consolidated Work History (2021–2026)

Consolidated from Jira-sourced reviews (`2022-2023-resume-review.md`, `2024-resume-review.md`,
`2025-2026-resume-review.md`) plus context not captured in Jira. Organized oldest-to-newest
to show progression from platform builder → cross-enterprise operator → compliance leader →
AI/ML initiator.

Reference: `_drafts/PERSONA-RESUME.md`, `_drafts/PERSONA-SVP.md`

Created: 2026-04-29

---

## Year 1: The Trust-Building Campaign (Oct 2021 – Dec 2022)

### The Data Lake Initiative — Earning Enterprise Access

The first year was about earning trust across a siloed organization. The mandate was to
extract data from every product group into the central data lake. The reality was political:

- **~1/3 of teams collaborated willingly** — saw the value, provided access, worked with me
  on data extract design
- **~1/3 placated and stalled** — agreed in meetings, delayed in practice, hoped the initiative
  would lose momentum
- **~1/3 refused outright** — told me to go away, sometimes rudely, sometimes through passive
  non-response

The approach was deliberate: start with the willing teams, deliver visible results, use those
wins to build credibility with the fence-sitters. For the holdouts, I documented detailed
plans of action — not "force them to comply" but "here's how we approach them to make
participation easy and valuable" — and escalated to upper management with specific,
constructive proposals rather than complaints.

The result: over 90% coverage of data extracts across the enterprise within the first year.
The small number of remaining holdouts were escalated with plans that management could act on.

**Why this matters for SVP positioning:** This wasn't an engineering project — it was an
organizational influence campaign executed without positional authority. The technical work
(data extracts, pipeline design, access provisioning) was the easy part. The hard part was
navigating organizational politics, building trust across teams that had no reporting
relationship to me, and converting skeptics into collaborators. This is exactly the skill
set a Head of AI needs when rolling out ML capabilities across business units that don't
report to you.

### EDI Portfolio — 15+ AWS Accounts Across Four Product Lines

Simultaneously served as the dedicated SRE resource for the entire EDI (Envestnet Data &
Innovation) portfolio:

- **EDI-DataLake** (4 accounts) — predecessor to current DataLake work
- **EDI-WealthDataInsights / WDP** (4 accounts) — Wheelhouse/WDP data platform
- **EDI-Innovation** (3 accounts) — data science and UX experimentation
- **EDI-SMBPortal / upSWOT** (4 accounts) — partner-managed SMB product

Key accomplishments:
- **Harbr Data Marketplace** — managed a vendor-partnered platform with shared AWS ownership,
  coordinating software upgrades with time-limited IAM roles for external vendor access
- **Hadoop-to-AWS migration support** — S3 data transfer, Terraform IaC-Executor roles for
  GitLab pipelines
- **upSWOT lifecycle** — provisioned the partnership infrastructure, then managed the full
  shutdown of 4 AWS accounts when the partnership ended
- **Security incident response** — multiple GuardDuty investigations for S3 logging tampering,
  root access without MFA, and unauthorized cross-border IAM activity

### UPA Platform Build-Out — Greenfield Infrastructure

Built greenfield AWS cloud-native infrastructure for the Unified Platform Architecture (UPA)
and Microservices-Accounting platforms:

- Provisioned Terraform Cloud workspaces, EKS clusters, and ArgoCD deployment pipelines
  across Dev/QA/UAT/Prod environments
- Managed IAM access controls and AWS SSO for 40+ engineers across UPA, MDS, DataLake,
  and SalesOps accounts
- Responded to infrastructure incidents including Kubernetes service outages, network issues,
  and security alerts

### Scale-to-Zero EKS Workloads — Brought from BCBSNC

Implemented scale-to-zero workload patterns on the UPA Kubernetes clusters — a technique
I brought directly from my BCBSNC work where I'd designed the same pattern for GPU-enabled
spot instance nodes running CarePath ML model training and scoring.

At BCBSNC, zero-scaled GPU nodes with taint/toleration scheduling meant the expensive GPU
instances only ran when ML workloads were active — no idle GPU costs. At Envestnet, I
applied the same pattern to UPA's EKS clusters: workloads that didn't need to run 24/7
scaled to zero replicas and the underlying nodes scaled down, keeping the platform within
a reasonable budget that would have been impossible with always-on infrastructure.

This was a significant cost win that made the UPA platform financially viable on the
budgets available. It also demonstrated a pattern that later informed the Karpenter
migration work in 2025–2026 — moving from Cluster Autoscaler's reactive scaling to
Karpenter's more intelligent node provisioning.

**Why this matters for SVP positioning:** This is a concrete example of cross-organization
knowledge transfer — taking a pattern proven in one enterprise (healthcare ML workloads)
and applying it to a different domain (financial services platform). A Head of AI does
this constantly: recognizing that the GPU scheduling pattern from the ML team applies to
the data engineering team, or that the cost optimization from one business unit works for
another.

### Data Science / AI / ML Platform (SageMaker) — Started 2022

Managed the Data Science and AI/ML infrastructure from initial deployment, a scope that
continued through 2024. This was early evidence of the AI/ML platform engineering capability
that later led to the Bedrock ADP-AI work in 2025.

- Managed SageMaker infrastructure-as-code via GitLab (`envcloud-ml-sagemaker-infra` repo)
- Migrated AI/ML resources from the shared EnvCloud-Microservices-Dev account to a dedicated
  DataScience-SharedServices-Dev account, then decommissioned the legacy resources
- Created SageMaker VPC endpoints across all 4 UPA/Microservices-Accounting accounts
  (Dev/QA/UAT/Prod) to fix Lambda→SageMaker batch transform API connectivity for ML
  inference pipelines
- Provisioned network access from SageMaker notebook environments to internal services
  (GitLab, Nexus, Harbor) for ML development workflows
- Operated the `datascience_shared_prod_01` EKS cluster, including resolving KubeCost
  service outages
- Provisioned data science users (Yodlee team) for EDI-dev accounts

**Why this matters for SVP positioning:** This wasn't just infrastructure support for a data
science team — it was building the ML platform from scratch. Account migration, VPC endpoint
architecture for inference pipelines, network connectivity for notebook environments, and
EKS cluster operations for ML workloads. Combined with the Georgia Tech ML background and
the BCBSNC CarePath production ML experience, this establishes a continuous thread of AI/ML
platform engineering across three organizations.

**The cross-enterprise commando role:** The data lake initiative and EDI portfolio work
established a pattern that defined the rest of the tenure — being the person who could drop
into any product team, any AWS account, any technology stack, diagnose the problem, and fix
it. This cross-enterprise mobility became the foundation for everything that followed:
compliance work (needed access to every product), cost optimization (needed visibility into
every account), and AI/ML initiatives (needed to understand every data source).

---

## Year 2: Platform Operations, ACE/IMPACT Recovery, and Scope Expansion (2023)

### ACE/IMPACT Project Recovery — The Turning Point

This was the event that changed the trajectory of the Envestnet tenure.

A colleague (Alexander) had been responsible for the ACE/IMPACT project — a critical
integration effort. The project fell behind, deliverables weren't met, and the situation
deteriorated until Alexander was eventually let go for gross negligence. The project was
in crisis.

I stepped in and recovered the project by working around the clock for three weeks straight.
The recovery required the same cross-enterprise access and trust built during the data lake
initiative — touching multiple product teams, multiple AWS accounts, and multiple technology
stacks simultaneously. The work is reflected in Jira and was visible to leadership.

Two outcomes made this a career-defining moment:

1. **Proof of cross-enterprise capability.** The recovery demonstrated — under pressure, with
   leadership watching — that I could operate across the entire enterprise technology stack,
   integrate systems that had never been connected, and deliver under a deadline that most
   people would have called impossible. This wasn't theoretical breadth; it was demonstrated
   under fire.

2. **Executive sponsorship.** Noah Krieger became my executive sponsor as a direct result of
   this project. Having an executive sponsor who had seen the work firsthand — not just heard
   about it in a status meeting — changed the dynamics for every initiative that followed.
   The SOC compliance leadership, the AI/ML initiatives, the cross-team cost optimization
   work — all of it was easier because Noah had seen what happened with ACE/IMPACT.

### Automated Observability — New Relic Adoption

As part of the ACE/IMPACT recovery and subsequent stabilization, I implemented automated
observability systems using New Relic. The implementation was effective enough that it got
adopted across the company as a standard practice — another example of work done for one
project becoming an enterprise-wide capability.

**Why this matters for SVP positioning:** The ACE/IMPACT recovery is the clearest single
demonstration of the "drop in anywhere and fix it" capability. But the more important
leadership signal is what happened after: the executive sponsorship, the observability
standard that spread across the company, and the trust that made every subsequent
cross-enterprise initiative possible. A Head of AI doesn't just build systems — they
build the organizational credibility that lets them drive change across business units.

### UPA Platform Stabilization

Operated and stabilized the UPA cloud-native platform:

- Resolved 15+ incidents including a SEV-2 production export failure
- Fixed ArgoCD ALB TargetGroup misconfigurations registering all vEMR instances
- Resolved multiple Kubernetes service outages across environments
- Corrected AWS Secrets Manager values for Okta authentication tokens

### Data Science Platform Operations (continued)

- Provisioned network access from SageMaker notebook environments to internal services
  (GitLab, Nexus, Harbor) for ML development workflows
- Upgraded self-service SSO library for Data Science accounts alongside UPA and DataLake

### DataLake Infrastructure Expansion

Expanded scope into DataLake operations, foreshadowing the broader BILLINGPRO team:

- Optimized Airflow environments in DataLake-PreProd
- Managed DataSync agents and configurations
- Supported data pipeline infrastructure across environments

### Transition to BILLINGPRO

This period laid the groundwork for the 2024 team reorganization into BILLINGPRO, where
the scope expanded from UPA/EDI to include Revenue Manager, Wealth Manager, BillFin,
Payments, Tamarac, UMP, ERS, and WDP — essentially every billing and data product in the
company.

---

## Year 3: Migration, Compliance, and Cost Optimization (2024)

### Team: BILLINGPRO — 20+ AWS Accounts

The BILLINGPRO reorganization formalized what had already been happening informally: one
engineer with cross-enterprise access and trust, now responsible for infrastructure across
every billing and data platform.

### Revenue Manager Tableau → AWS Migration

Migrated the RM Tableau BI workload from IBM data center to AWS, establishing cloud-native
BI infrastructure using S3, Glue, Athena, and QuickSight.

### EKS Upgrades Across 3 Platforms

- Upgraded Microservices-Accounting EKS clusters (v1.28→1.29, then 1.29.3→1.29.5)
- Upgraded Payments EKS clusters (1.29.3→1.29.5)
- Resolved Cluster Autoscaler image tag issue that was retaining orphaned EC2 instances
  in ASGs — delivering real cost savings across both platforms

### Envestnet Payments SOC 2 Type 1 Audit — Inaugural

Primary infrastructure evidence provider for the first-ever Envestnet Payments SOC 2 Type 1
audit. Completed 25+ compliance tasks covering availability, security, change management,
data processing, and confidentiality controls. This was the beginning of the compliance
leadership role that expanded dramatically in 2025.

### MDS Internal ALBs with TLS & DNS

Designed and implemented internal ALB infrastructure with ACM certificates and Route53 DNS
for Market Data Service, supporting Hybrid Apigee API gateway integration.

### SageMaker Account Migration (Data Science Platform — Final Phase)

- Migrated SageMaker AI/ML resources from shared EnvCloud-Microservices-Dev to dedicated
  DataScience-SharedServices-Dev account, then decommissioned legacy resources
- Created SageMaker VPC endpoints across all 4 Microservices-Accounting accounts
  (Dev/QA/UAT/Prod) for Lambda→SageMaker batch transform API connectivity
- Resolved KubeCost outage in the `datascience_shared_prod_01` EKS cluster
- Cleaned up leftover VPC endpoints after networking changes

This completed the multi-year Data Science platform build that started in 2022 — from
initial SageMaker deployment through IaC management, network provisioning, and finally
account migration to a dedicated environment.

### Neo4J AWS Account Decommissioning

Decommissioned 3 unused AWS accounts (Dev/QA/QL), reducing account sprawl and costs.
Coordinated cross-team cleanup of resources, SSO configurations, and account closure.

---

## Year 4: Compliance Leadership, AI/ML First, and Security Hardening (2025)

### SOC Compliance — From Isolated Evidence Requests to Enterprise Leadership

The SOC compliance work tells a clean leadership progression story across four years:

| Year | Scope | Role |
|------|-------|------|
| 2022–2023 | Ad-hoc evidence requests | IC/SME — provided evidence in isolation without context. Security background not yet shared; focused on infrastructure build-out, automation, and documentation |
| 2024 | 1 audit (Payments SOC 2 Type 1) | Primary evidence contributor — first formal SOC engagement, learned the full audit process |
| 2025 | 8 simultaneous audits (RM, WM, BillFin, Payments, Tamarac, UMP, ERS, WDP) | Led evidence collection, automated gathering, standardized practices across inconsistent teams |
| 2026 (Jun) | All product areas | **Taking over the entire compliance space** — leading the initiative across the enterprise for the first time |

The 2022–2023 period is important context: the team was in transition, people were leaving,
and I was inheriting roles and permissions from exiting personnel while simultaneously
building infrastructure, creating automation tooling, and documenting extensively to shore
up gaps. SOC evidence requests came in isolation — "give us this screenshot" or "provide
this config" — without the broader audit context. I hadn't yet surfaced my NC DOR/ETAAC
security and compliance background because the immediate priority was infrastructure
stabilization and consolidating the many different ways teams were doing things.

The shift happened in 2024 when the Payments SOC 2 Type 1 became the first formal audit
I was embedded in end-to-end. That's when the security background became visible to
leadership, and the scope expanded rapidly from there.

This is a textbook scope expansion: from providing evidence without context, to contributing
to one full audit, to leading eight, to owning the enterprise-wide compliance program. Each
step was earned by delivering on the previous one.

The 2025 details:

Led infrastructure compliance evidence collection for 8 simultaneous SOC 1/SOC 2 Type 2
audits across every platform in the portfolio:

| Product | Audit Type |
|---------|------------|
| Revenue Manager | SOC 1 Type 2 |
| Wealth Manager | SOC 1 Type 2 |
| BillFin | SOC 2 Type 2 |
| Envestnet Payments | SOC 2 Type 2 |
| Tamarac | SOC 2 Type 2 |
| UMP | SOC 2 Type 2 |
| ERS | SOC 2 Type 2 |
| WDP/Wheelhouse | SOC 2 Type 2 |

Completed 40+ individual evidence tasks. Automated evidence collection from multiple sources,
replacing manual processes with repeatable tooling. Established standardized evidence
practices that brought previously inconsistent product areas into alignment. Served as
primary technical liaison to external auditors and SME across development workflow, CI/CD
pipelines, authentication and authorization, OS configuration, and DevOps practices.

### AI/ML — First Production Workload on Billing Platform

Evaluated AWS AI/ML services for automated document processing (ADP-AI). Trialed multiple
approaches; AWS Bedrock Data Automation won the POC. Delivered production-ready
infrastructure — the first AI/ML production workload on the Billing platform.

### EKS Cost Optimization

Right-sized Microservices-Accounting EKS nodes from 4xlarge to 2xlarge across all 4
environments, delivering direct compute cost savings.

### QuickSight CI/CD Automation

Built GitLab CI/CD pipeline automation for AWS QuickSight asset management — export/import
automation, SSO role-based access, and policy deployment across environments.

### KubeCost Implementation

Implemented KubeCost across Payments and Microservices-Accounting EKS clusters for granular
Kubernetes cost allocation and visibility.

### Security Hardening

- Restricted Revenue Manager security groups to specific IP ranges, adding defense-in-depth
  network segmentation beyond the Palo Alto firewall layer
- Remediated high-severity Wiz CSPM findings across Billing & Payments accounts (KMS
  excessive access, service account privilege issues)

---

## Year 5 (YTD): Complex Migrations, Security Enforcement, AI Expansion (2026)

### Datalake EKS 1.32 Upgrade — Complex Migration

Led the most complex EKS upgrade to date across all 4 DataLake environments. Navigated
aws-auth ConfigMap deprecation, external-dns migration, and coordinated Airflow helm chart
upgrade (1.15→1.17) requiring custom container image rebuilds with engineering.

### IMDSv2 Enforcement

Enforced IMDSv2 across Payments and SalesOps compute resources, eliminating instance
metadata v1 attack surface as part of company-wide security hardening initiative.

### Wiz Remediation — Round 2

Completed second round of Wiz KMS findings remediation across DataLake Dev/QA/Prod.

### SOC 2026 — Expanding Leadership

Expanding SOC compliance scope for 2026 to cover all product areas with increased leadership
over the process — defining audit preparation timelines, managing auditor relationships, and
driving remediation of control gaps identified in the 2025 cycle.

### Active Initiatives

- EMR on EKS infrastructure setup for DataLake
- SalesOps Aurora Serverless v2 RDS migration
- DataLake EKS 1.33.4 upgrade planning
- Keycloak access restriction implementation for WM/BillFin (prod and non-prod)
- Karpenter migration from Cluster Autoscaler in DataLake
- CrowdStrike Falcon sensor upgrades across EKS clusters
- Amazon Linux 2023 upgrade planning
- WAF configuration implementation
- AI-assisted operational workflows using Kiro for daily digests, team reporting,
  Jira automation, and infrastructure-as-code analysis

---

## SVP-Relevant Highlights

The Envestnet tenure demonstrates five capabilities that map directly to SVP / Head of AI:

### 1. Crisis Recovery and Executive Sponsorship

The ACE/IMPACT recovery is the single most compelling leadership story in the Envestnet
tenure. A critical project failed due to a colleague's negligence. Rather than letting it
die or waiting for someone else to step in, I recovered it in three weeks of around-the-clock
work — touching every product team and technology stack in the enterprise. The direct result
was executive sponsorship from Noah Krieger, which unlocked every subsequent cross-enterprise
initiative. The observability systems built during the recovery (New Relic) became a
company-wide standard. This is the story of someone who earns leadership through demonstrated
capability under pressure, not through title or org chart position.

### 2. Organizational Influence Without Positional Authority

The Year 1 data lake initiative is the clearest example. Achieving 90% data extract coverage
across a siloed organization — where a third of teams actively resisted — required the same
influence, stakeholder management, and escalation skills that a Head of AI needs when rolling
out ML capabilities across business units.

### 3. Cross-Enterprise Technical Breadth

No other engineer at Envestnet has operated across every product line's AWS infrastructure.
The BILLINGPRO scope (20+ accounts, 8+ products) exists because of the trust and access
earned in Year 1. This breadth is the "one-stop shopping" capability — understanding every
data source, every deployment pipeline, every security control across the enterprise.

### 4. Compliance as Leadership

The SOC compliance progression tells a leadership story:
- **2024**: Primary evidence contributor for 1 inaugural audit (Payments SOC 2 Type 1)
- **2025**: Led evidence collection for 8 simultaneous audits across all products, automated
  evidence gathering, standardized practices across inconsistent teams
- **2026**: Expanding to full process leadership — audit timelines, auditor relationships,
  remediation management

This is a trajectory from IC contributor to program leader, demonstrated through measurable
scope expansion.

### 5. AI/ML Initiative Ownership

The ADP-AI project (AWS Bedrock Data Automation) was the first AI/ML production workload on
the Billing platform. Evaluated multiple approaches, selected the winner, and delivered
through production. This demonstrates the ability to evaluate AI technologies, make
build-vs-buy decisions, and deliver production infrastructure — exactly what a Head of AI does.

### 6. Cost Discipline and Business Awareness

Multiple cost optimization wins across the tenure:
- Scale-to-zero EKS workloads on UPA clusters (2022) — pattern brought from BCBSNC GPU
  scheduling, made the platform financially viable on available budgets
- Cluster Autoscaler fix eliminating orphaned EC2 instances (2024)
- EKS node right-sizing from 4xlarge to 2xlarge (2025)
- KubeCost implementation for cost visibility (2025)
- Karpenter migration for intelligent node provisioning (2026)
- Neo4J account decommissioning (2024)
- upSWOT account shutdown (2022)

Each of these connects technical decisions to business outcomes — the language of a
technology leader, not just an engineer.

### 7. Security Depth Across the Full Stack

The security work spans every layer:
- **Network**: Security group IP restrictions, Palo Alto integration
- **Compute**: IMDSv2 enforcement, CrowdStrike Falcon
- **Identity**: Keycloak access controls, IAM hardening, SSO management
- **Data**: KMS remediation, encryption controls, backup retention
- **Compliance**: SOC 1/SOC 2 across 8 products, Wiz CSPM remediation
- **Incident response**: GuardDuty investigations, unauthorized access resolution

Combined with the NC DOR (IRS SafeGuard) and SAS Institute (FDA CFR Part 11) experience,
this is a 15+ year security narrative that runs from federal audits through cloud-native
compliance.

---

## IOG & OKR Alignment (2026)

Sourced from `~/.kiro/previews/resume-master-summary.md`. These are the Infrastructure
Operations Governance initiatives and OKRs that directly map to work I own or lead.

### IOG Initiatives I Own or Contribute To

| IOG | Initiative | My Role | SVP Signal |
|-----|-----------|---------|------------|
| IOG-13 | Enforce IMDSv2 across compute | Leading implementation across Payments, SalesOps, RM, BillFin | Security hardening at enterprise scale |
| IOG-7 | SQL Vulnerability patching | Executing across AWS & on-prem | Compliance discipline |
| IOG-9 | WAF Configurations | Implementing URL-level WAF controls | Defense-in-depth architecture |
| IOG-22 | BillFin Complete Rebuild | Account migration epics | Platform modernization |
| IOG-93 | System Patching — All Wealth Platforms | Cross-platform patching coordination | Enterprise-wide operational scope |
| IOG-94 | Maintenance / KTLO | Keycloak, Wiz, certs, SOC compliance | Operational leadership |
| IOG-95 | Infrastructure Optimizations — Payments & Billing | EKS upgrades, EMR on EKS, Karpenter, QuickSight | Modernization and cost optimization |

### OKR Alignment

**OKR 1 — Technology Spend Governance:** DataLake EKS right-sizing, Karpenter adoption,
RM instance right-sizing (r7i.4xlarge at <5% CPU), WM over-provisioned fleet identification.
Direct cost savings through technical decisions.

**OKR 3 — Cyber Security (heaviest alignment):** 12+ epics across IMDSv2 enforcement,
Keycloak access restrictions (prod and non-prod), Wiz KMS remediation, WAF configurations,
SQL vulnerability patching, MongoDB vulnerability remediation, RM database password rotation,
RM direct laptop access prevention. This is the single largest OKR alignment — security
work touches every product line.

**OKR 4 — Modernization and Automation:** DataLake EKS 1.32/1.33 upgrades, Karpenter
migration from Cluster Autoscaler, EMR on EKS, SalesOps RDS cluster migration. Platform
modernization across the portfolio.

**OKR 5 — AI:** AI-assisted operational workflows using Kiro for daily digests, team
reporting, Jira automation, and IaC analysis. Pioneering AI agent adoption in infrastructure
operations.

**Why this matters for SVP positioning:** The IOG/OKR mapping shows work that spans all five
organizational priorities simultaneously — cost governance, security, modernization, AI, and
operational maintenance. No other individual contributor touches all five OKRs. This is the
"one-stop shopping" breadth that a Head of AI or SVP needs to demonstrate.

---

## Technologies Across Full Tenure

- **AWS**: EKS, EC2, RDS Aurora, S3, IAM, SSO, ACM, Route53, ALB, KMS, EMR, Airflow (MWAA),
  QuickSight, Bedrock, Glue, Athena, DataSync, GuardDuty, CloudTrail, Lambda, DynamoDB, SQS,
  CrowdStrike Falcon, Wiz
- **Kubernetes**: EKS (v1.28–v1.33), Karpenter, KubeCost, Cluster Autoscaler, ArgoCD,
  Argo Workflows, helm chart management, external-dns, ingress-nginx
- **IaC**: Terraform, Terraform Cloud, GitLab CI/CD, CloudFormation (legacy)
- **Security**: IMDSv2, Wiz CSPM, Keycloak, WAF, security group hardening, SOC 1/SOC 2
  compliance, GuardDuty incident response, CrowdStrike Falcon
- **AI/ML**: AWS Bedrock Data Automation, SageMaker, serverless ML (Lambda/Step), Kiro AI
  agent development
- **Data**: Airflow, EMR, DataSync, Glue, Athena, QuickSight, Neo4J, Snowflake, Hadoop
- **Monitoring**: New Relic (infrastructure, APM, NRQL, CloudWatch Metric Streams)
- **Vendor Platforms**: Harbr Data Marketplace, ScaleGrid (MongoDB), Octopus Deploy, Qlik

---

## Reference

- **Source files:** `~/.kiro/previews/2022-2023-resume-review.md`, `2024-resume-review.md`,
  `2025-2026-resume-review.md`
- **Resume data:** `../resume/_data/data.yml`
- **LinkedIn profile:** `_drafts/PERSONA-LINKEDIN.md`
- **SVP positioning:** `_drafts/PERSONA-SVP.md`
