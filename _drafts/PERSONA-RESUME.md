---
layout: none
date: 1999-12-31
sitemap: false
---

# Resume ↔ LinkedIn Cross-Reference & SVP Positioning

Cross-reference between the full resume (mcgarrah.org/resume/print, sourced from
`../resume/_data/data.yml`) and the LinkedIn profile (`PERSONA-LINKEDIN.md`).
Identifies discrepancies, missing content, and SVP-relevant details that should
surface on LinkedIn.

Reference: `_drafts/PERSONA-LINKEDIN.md`, `_drafts/PERSONA-SVP.md`

Created: 2026-04-29
Resume source: `/Users/michael.mcgarrah/Personal/Github-mcgarrah/resume/_data/data.yml`
Resume URL: https://mcgarrah.org/resume/print

---

## Title Discrepancies

| Role | Resume Title | LinkedIn Title | Action |
|------|-------------|---------------|--------|
| BD Biosciences | IT Engineer (IT Director) | IT Engineer | **Change to IT Director.** Sole IT person for manufacturing plant, one part-time direct report, managed IT budgets, dotted line to CIO, direct report to plant manager. This is director-level scope. |
| Envestnet | Lead Principal Engineer (Cloud & ML Focus) | Lead Principal Platform Engineer (cloud focus) | Minor — resume adds "ML Focus" which is better for SVP positioning. Consider updating LinkedIn to match. |
| NC DOR | Application and Network Security Specialist | IT Security Specialist | Resume title is more descriptive and shows breadth. Consider updating LinkedIn. |
| NCSU (1999-2000) | Development Manager / Operations Manager | Applications Manager / Operations Manager | Resume says "Development Manager" which is stronger leadership language. |

## Resume Content Missing from LinkedIn

### ISSIP Excellence Award (Blue Cross NC)
The resume documents the CarePath deep learning models in detail, including:
> "The CCM model was recognized with an Excellence In Service Innovation Award from the
> International Society of Service Innovation Professionals (ISSIP) and the H2H model
> with an Innovator Award from Healthcare Innovation."

**Action:** Add to Blue Cross NC LinkedIn description AND to Honors & Awards section.

### ISC2 Certified in Cybersecurity (CC)
Resume shows: `Certified in Cybersecurity (CC)`, Nov 2024 – Nov 2027, ISC2.
LinkedIn certifications section doesn't include this.

**Action:** Add to LinkedIn certifications. Current and relevant for security positioning.

### AWS Certifications (Expired)
Resume shows:
- AWS Certified SysOps Administrator – Associate (2017-2020)
- AWS Certified Solutions Architect – Associate (2017-2020)

LinkedIn doesn't list these. Even expired, they show AWS depth.

**Action:** Add to LinkedIn with expired dates noted. Shows the certification history.

### SAS Certifications (Full Set)
Resume shows 6 SAS certifications. LinkedIn only shows 2.

**Action:** Add the missing four (Base Programmer, Clinical Trials, Data Integration,
Statistical Business Analyst). These support the data science narrative.

### RHCE (Red Hat Certified Engineer)
Resume mentions RHCE earned at NCSU (2001). Not on LinkedIn.

**Action:** Add if still relevant to the narrative. Shows early Linux depth.

### Solaris Certified Systems Administrator
Resume shows Solaris cert (2003). Not on LinkedIn.

**Action:** Low priority — dated, but shows breadth.

## LinkedIn Descriptions to Rewrite with Leadership Language

### Envestnet (Current Role) — Highest Priority

**Current LinkedIn:**
> Building large scale cloud platforms for financial services and data science initiatives.
> A combination of AWS cloud and data center infrastructures are included in the architecture
> allowing for flexible integration between on-prem and cloud services. An automation first
> attitude pervades this work.

**Resume has much richer detail:**
- Unified Portfolio Accounting (UPA) — EKS, Airflow (MWAA), service mesh, IaC
- SMB Portal — cloud-native microservices, migration from on-prem/alternate cloud
- Data Science Initiatives — serverless ML (Lambda/Step), SageMaker, container deployment
- Data Marketplace — external vendor integration, security concerns

**Proposed LinkedIn rewrite:**
> Leading cloud platform architecture for financial services, designing infrastructure that
> supports data science initiatives, portfolio accounting, and marketplace integration across
> the organization. Driving automation-first strategy integrating AWS cloud and on-premises
> data center infrastructure.
>
> Led the 2025 SOC 1 and SOC 2 compliance initiative across the majority of product lines —
> managing cross-team evidence gathering, automating collection from multiple sources, and
> serving as the primary technical liaison to external auditors. Automated evidence gathering
> replaced manual processes with repeatable tooling, and new operational controls brought
> previously inconsistent product areas into alignment. Provided subject matter expertise
> across development workflow, CI/CD pipelines, authentication and authorization, OS
> configuration, and DevOps practices. Expanding scope for 2026 to cover all product areas
> with increased leadership over the compliance process.
>
> Key initiatives: Unified Portfolio Accounting platform (EKS, Airflow/MWAA, service mesh,
> IaC-managed infrastructure), serverless ML pipelines (Lambda/Step Functions, SageMaker),
> Data Science/AI/ML platform (SageMaker account migration, VPC endpoint architecture for
> ML inference pipelines, dedicated Data Science EKS cluster), cloud-native microservices
> migration, and cross-platform data marketplace integration.

### Blue Cross NC — High Priority

**Current LinkedIn:**
> Building a data science platform incorporating a data-warehouse, data-lake and
> data-execution environment using containerized cloud-first technologies to support
> data driven decision making for a value-based healthcare approach.

**Resume has extensive detail including:**
- Built complete multi-account AWS platform from ground up (VPC, IAM, RDS, EKS, EMR)
- CarePath deep learning models — ISSIP Excellence Award
- Medicare Guided Selling Tool — production serverless implementation
- Drug Lookup and Calculation API — enterprise-wide REST API
- EKS with spot instances, GPU nodes, zero-scaling

**Proposed LinkedIn rewrite:**
> Architected and led development of the enterprise data science platform — multi-account
> AWS infrastructure (EKS, EMR, RDS, Lambda), containerized ML execution environment, and
> CI/CD pipelines — powering production deep learning models for healthcare predictions.
>
> Built the CarePath ML framework that produced models for Complex Case Management,
> Hospital-to-Home transitions, and cardiovascular/diabetes risk prediction. CCM model
> recognized with ISSIP Excellence in Service Innovation Award. Implemented production
> serverless systems (Medicare Guided Selling, Drug Lookup API) and enterprise Kubernetes
> platform with GPU-enabled spot instances and zero-scaled nodes for cost optimization.

### USPS — Medium Priority

**Current LinkedIn:**
> Engaged in advanced analytics with multiple platforms. Primary focus on a SAS 9.4 and
> SAS Viya in-memory cluster with linkage to Hadoop Datalake inching up on 1Pb of data.

**Proposed LinkedIn rewrite:**
> Administered a 25-node SAS Viya in-memory analytics cluster (26TB RAM) with connectivity
> to a 50+ node Hadoop data lake approaching 1PB. Stabilized platform operations, built
> administration automation (Python Fabric, Ansible), and provided data science support
> for advanced analytics in a high-security federal environment. Built a complete Hadoop
> development platform replicating production for upgrade planning.

### NC DIT — Minor Polish Only

Already strong leadership language ("Accountable for developing, maintaining and overseeing").
Resume adds detail about:
- RFI for network modernization
- RFP for security standards rewrite with State Risk Officer
- Cloud initiatives (Azure, OpenShift, direct Amazon engagement)
- SDI strategy (storage, network, compute, orchestration)

**Action:** Consider adding one line: "Led the Request for Information (RFI) for statewide
data center network modernization and co-authored the RFP for security standards rewrite
based on NIST and DoD frameworks."

### BD Biosciences — Title Change + Rewrite

**Current LinkedIn:** "IT Engineer" with generic description.

**Proposed LinkedIn rewrite (with corrected title):**
> **IT Director** — Sole IT leader for the BD Treyburn manufacturing plant. Managed all IT
> services, budgets, and one direct report. Dotted-line reporting to CIO, direct report to
> plant manager. Scope included Windows/UNIX administration, Oracle DBA, network management
> (Nortel/Cisco), manufacturing PLC integration (Allen & Bradley ControlLogix), and Six Sigma
> project management. Oversaw migration from Windows NT domain to Active Directory.

## Resume Career Profile — Needs SVP Update

**Current resume career profile:**
> With over three decades of IT experience, my background includes work in data science &
> analytics, cloud computing, development, database & multi-platform platform management,
> security and compliance, networking, and R&D. That diverse experience makes me rapidly
> effective in your business.

This is generic and undersells. Should match the LinkedIn summary tone.

**Proposed resume career profile:**
> Technology leader with 30+ years bridging enterprise architecture, AI/ML, and cloud
> platforms. Career spans engineering leadership (IT Director, Development Manager),
> enterprise architecture (statewide technology standards for North Carolina state
> government), and hands-on platform engineering (AWS, EKS, production ML models).
> Currently completing an Executive MBA at UNC Wilmington, deliberately complementing
> technical depth with business strategy and organizational leadership.

## Resume Tagline — Needs SVP Update

**Current:** "Cloud Architect / Data Scientist / Technical Leader"

**Proposed:** "Engineering Leader | Enterprise Architecture · AI/ML · Cloud Platforms"
(Match the LinkedIn headline for consistency.)

## Early Career Roles — Keep on LinkedIn

Per your note: the old companies help find former colleagues, and the old certs show
certification depth before the BS and MS. These serve a networking purpose on LinkedIn
that they don't serve on a resume. Keep them on LinkedIn; consider consolidating on the
resume's print version for brevity.

## Priority Actions

| # | Action | Where | Effort |
|---|--------|-------|--------|
| 1 | Change BD Biosciences title to "IT Director" | LinkedIn + Resume | 5 min |
| 2 | Rewrite Envestnet description | LinkedIn | 15 min |
| 3 | Rewrite Blue Cross NC description + add ISSIP award | LinkedIn + Honors | 15 min |
| 4 | Rewrite USPS description | LinkedIn | 10 min |
| 5 | Add ISC2 CC certification | LinkedIn | 5 min |
| 6 | Add expired AWS certs | LinkedIn | 5 min |
| 7 | Add missing SAS certs (4) | LinkedIn | 10 min |
| 8 | Add one line to NC DIT (RFI/RFP) | LinkedIn | 5 min |
| 9 | Update resume career profile | Resume data.yml | 10 min |
| 10 | Update resume tagline | Resume data.yml | 2 min |
| 11 | Rewrite BD Biosciences description | LinkedIn | 10 min |

Total: ~90 minutes for all LinkedIn + resume updates.

---

## Reference

- **LinkedIn profile snapshot:** `_drafts/PERSONA-LINKEDIN.md`
- **SVP positioning plan:** `_drafts/PERSONA-SVP.md`
- **Persona voice guide:** `_drafts/PERSONA.md`
- **Resume data:** `../resume/_data/data.yml`
- **Resume URL:** https://mcgarrah.org/resume/print
- **LinkedIn profile:** https://www.linkedin.com/in/michaelmcgarrah/
