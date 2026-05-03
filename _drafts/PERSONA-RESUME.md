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
Updated: 2026-08-01
Resume source: `/Users/michael.mcgarrah/Personal/Github-mcgarrah/resume/_data/data.yml`
Resume URL: https://mcgarrah.org/resume/print

---

## Resume Status: Complete

The resume has been fully rewritten with SVP-voiced summaries, leadership language,
and detailed `summary` + `details` sections for every role. All items originally
flagged in this file have been addressed on the resume side. The remaining work is
**LinkedIn-only** — updating the LinkedIn profile to match the resume.

### Resume Items Completed Since Original Assessment (2026-04-29)

| Item | Original State | Current State |
|------|---------------|---------------|
| Career Profile | Generic ("diverse experience makes me rapidly effective") | ✅ SVP-voiced: leadership, SOC compliance, ETAAC, EMBA Candidate |
| Tagline | "Cloud Architect / Data Scientist / Technical Leader" | ✅ "Engineering Leader \| Enterprise Architecture · AI/ML · Cloud Platforms" |
| EMBA graduation | "Expected Graduation: Fall 2026" | ✅ "EMBA Candidate — Expected Graduation: Spring 2027" |
| BD Biosciences title | "IT Engineer" | ✅ "IT Engineer (IT Director)" with director-scope summary |
| BD Biosciences description | Generic | ✅ Apriso MES with Oracle/SAP integrations, Lotus Notes/Domino for 200+ users |
| Envestnet description | One generic paragraph | ✅ Full rewrite: ACE/IMPACT data strategy advisory, observability framework (New Relic + Confluence + Terraform), EKS Working Group (cross-team leadership by influence), SOC 1/SOC 2 (8 audits + vendor transition), AI/ML (Bedrock Data Automation), KEDA, Calico CNI, EMR on EKS, cost optimization |
| Blue Cross NC description | One generic paragraph | ✅ Full rewrite: ISSIP award, CarePath, MGS, platform architecture, director-equivalent authority |
| USPS description | "Engaged in advanced analytics" | ✅ Rewritten: 25-node/26TB metrics, Chief Data Scientist, NIST 800-53, data engineering (ArcGIS), past-tense voice pass |
| AKC description | Generic, present tense | ✅ Full rewrite: cloud evangelist, $30K→$5K, MongoDB Atlas, past-tense voice pass |
| NC DIT description | Decent but missing specifics, had repetition | ✅ Full rewrite: State CIO reporting, RFI/RFP, CISO collaboration, deduped networking section |
| Measurement Inc description | Generic | ✅ Full rewrite: ML moonshot, AWS pivot, Georgia Tech connection, FinOps, Analytics Server as early data engineering platform |
| SAS Institute description | Generic | ✅ Full rewrite: FDA CFR Part 11, DR implementation, 80+ customers, 6 certs in 6 months (fastest in any division) |
| NC DOR title | "IT Security Specialist" | ✅ "Application and Network Security Specialist" |
| NC DOR description | Generic compliance language | ✅ Full rewrite: IRS SafeGuard, skip-level to Secretary, ETAAC, AG liaison, on-call security monitoring |
| NCSU 1999-2000 title | "Applications Manager" | ✅ "Development Manager / Operations Manager" |
| NCSU 1998 description | "First role at NCSU Engineering" | ✅ "First professional role at NCSU after years of federal work-study student positions" |
| Teaching Assistant / Library | Generic student roles | ✅ Federal work-study positions that fully funded college without outside assistance |
| Interpath 1998 | No overlap noted | ✅ "held concurrently with the Ziff-Davis position" |
| ISC2 CC certification | Missing | ✅ Added (Nov 2024 – Nov 2027) with Credly link |
| AWS certs (expired) | Missing | ✅ Added (SysOps Admin + Solutions Architect, 2017-2020) with Credly links |
| All 6 SAS certs | 2 present | ✅ All 6 with Credly links |
| RHCE | Missing | ✅ Added (2001-2006) |
| Solaris cert | Missing | ✅ Added (2003-2005) |
| Skills — IaC | Terraform only | ✅ Added OpenTofu |
| Skills — CI/CD | Missing several | ✅ Added CruiseControl, CruiseControl.Net, PVCS, MOVEit Automation, Ansible Tower, OpenTofu |
| Skills — AWS | Missing KEDA, Karpenter, EMR on EKS, Bedrock | ✅ Added EMR on EKS (vEMR), KEDA, Karpenter, Bedrock, Bedrock Data Automation |
| Skills — Data Analytics | Missing several | ✅ Added FiveTran, Qlik Open Lakehouse, DataHub |

### New Resume Content Added (2026-07-31 / 2026-08-01)

Content added during this session that didn't exist in any prior version:

- **Envestnet ACE/IMPACT** — expanded from 3 sentences to 4 paragraphs: data engineering advisory role, BCBSNC experience transfer, observability framework (New Relic + Confluence workbooks + Terraform), legacy us-east-1 → us-east-2 migration arc
- **Envestnet UPA** — added KEDA event-driven autoscaling, Calico CNI replacing AWS VPC CNI for IP exhaustion, split node group architecture (spot workers + on-demand orchestration)
- **Envestnet EMR on EKS** — new breakout section: DataLake modernization, Karpenter spot/on-demand, Airflow integration, scoped IAM per pipeline stage, four-year arc narrative
- **Envestnet EKS Platform Operations** — added MDS and UMP platforms
- **Envestnet EKS Working Group** — new subsection: founded and led cross-team bi-weekly forum (2+ years), birds-of-a-feather model from RFC/standards experience, drove Calico/KEDA/Karpenter/ArgoCD/Istio decisions through influence, built self-sustaining community of Kubernetes experts
- **Envestnet AWS QuickSight** — replaced broken "FIX THIS SECTION" placeholder with full rewrite: Tableau→QuickSight migration, Terraform POC, Okta SSO federation, GitLab CI/CD asset promotion, namespace multi-tenancy, IP-restricted client instances, vanity URLs, embedding API, hundreds of thousands in annual Tableau licensing savings, multi-region (us-east-1 + eu-west-2)
- **Removed redundant Platform Engineering section** — all content (KEDA, Calico, scale-to-zero, KubeCost, Karpenter, account decommissioning) already covered in UPA, EKS Platform Operations, and Cost Optimization subsections
- **Updated QuickSight demo project** — richer description connecting to enterprise work and vanity URL module
- **Envestnet Cost Optimization** — added KEDA, Calico subnet optimization
- **Envestnet SOC Compliance** — added audit vendor transition (2025 mid-cycle) and full vendor migration (2026)
- **USPS Data Science Engineering Support** — new subsection: ArcGIS boundary data extraction, broader data engineering pattern
- **USPS details voice pass** — all subsections converted from present to past tense
- **AKC MongoDB Atlas** — managed service vs local/EC2 instances
- **AKC details voice pass** — all subsections converted from present to past tense
- **Measurement Inc Analytics Server** — reframed as early data engineering platform
- **SAS Institute cert speed** — "six consecutive months, fastest in any division at SAS"
- **NC DOR AG liaison** — designated primary liaison to Attorney General's Office
- **NC DOR on-call monitoring** — cellular modem, hundreds of security feeds
- **NC DIT deduplication** — removed repeated RFP paragraph from Networking section
- **BD Biosciences** — Apriso MES with Oracle/SAP integrations, Lotus Notes/Domino from Ziff-Davis
- **Interpath 1998** — overlap with Ziff-Davis noted
- **NCSU 1998** — "first professional role at NCSU" (not first professional role overall — that's Pioneer)
- **Teaching Assistant / Library** — federal work-study funding
- **Bedrock distinction** — "AWS Bedrock" vs "AWS Bedrock Data Automation" as separate products

---

## LinkedIn Actions Remaining

All actions below are **LinkedIn-only**. The resume is the source of truth — copy the
`summary` fields from `data.yml` into LinkedIn descriptions.

### Title Changes

| Role | Current LinkedIn | Resume Title | Action |
|------|-----------------|-------------|--------|
| BD Biosciences | IT Engineer | IT Engineer (IT Director) | Change to "IT Director" or "IT Engineer (IT Director)" |
| Envestnet | Lead Principal Platform Engineer (cloud focus) | Lead Principal Engineer (Cloud & ML Focus) | Update to match — adds ML positioning |
| NC DOR | IT Security Specialist | Application and Network Security Specialist | Update — more descriptive, shows breadth |
| NCSU (1999-2000) | Applications Manager / Operations Manager | Development Manager / Operations Manager | Update — "Development Manager" is stronger |

### Experience Description Rewrites

For each role below, the resume `summary` field is ready to paste into LinkedIn.
These summaries reflect all changes made through 2026-08-01.

#### Envestnet — Highest Priority

**Current LinkedIn:**
> Building large scale cloud platforms for financial services and data science initiatives.
> A combination of AWS cloud and data center infrastructures are included in the architecture
> allowing for flexible integration between on-prem and cloud services. An automation first
> attitude pervades this work.

**Resume summary (paste this):**
> Leading cloud platform architecture across 20+ AWS accounts spanning every billing and data
> platform in the enterprise. Recovered a critical cross-enterprise data engineering project
> under pressure, then served as technical advisor to the engineering team on AWS data pipeline
> architecture — accelerating delivery by leveraging prior BCBSNC experience with similar
> patterns. Founded and led the cross-team EKS Working Group, driving Kubernetes architecture
> decisions and building an enterprise community of practice through influence rather than
> mandate. Built the observability framework (New Relic with Confluence-linked runbooks and
> Terraform-provisioned dashboards) that became a company-wide standard. Led SOC 1/SOC 2
> compliance from a single inaugural audit to eight simultaneous audits across all products,
> automating evidence collection and serving as primary technical liaison to external auditors.
> Delivered the first AI/ML production workload on the Billing platform (AWS Bedrock Data
> Automation). Drove measurable cost optimization through EKS right-sizing, scale-to-zero
> workloads, and Karpenter migration.

#### Blue Cross NC — High Priority

**Current LinkedIn:**
> Building a data science platform incorporating a data-warehouse, data-lake and
> data-execution environment using containerized cloud-first technologies to support
> data driven decision making for a value-based healthcare approach.

**Resume summary (paste this):**
> Architected and led development of the enterprise data science platform — multi-account AWS
> infrastructure (EKS, EMR, RDS, Lambda), containerized ML execution environment, and CI/CD
> pipelines — powering production deep learning models processing claims data from all NC
> members, emergency rooms, and hospitals under near-real-time requirements. Operated with
> director-equivalent authority: conducted performance reviews, drove salary increases,
> executed performance improvement plans, led hiring, and dotted-line reported to the SVP.
> Managed cost controls across the EKS platform and the team of platform engineers building
> it — spot-instance and GPU-enabled node groups with scale-to-zero scheduling, activity-based
> cost tracking, and remediation workflows for developers and data scientists provisioning AWS
> resources. Delivered the Medicare Guided Selling system as a fast-track serverless deployment
> (Lambda, API Gateway, DynamoDB) to meet an SVP-driven timeline before the full platform was
> ready. Built the CarePath ML framework that produced award-winning models for Complex Case
> Management (ISSIP Excellence in Service Innovation Award), Hospital-to-Home transitions, and
> cardiovascular/diabetes risk prediction.

**Condensed version (if LinkedIn truncates):**
> Architected the enterprise data science platform (multi-account AWS: EKS, EMR, RDS, Lambda)
> powering production deep learning models for healthcare predictions. Operated with
> director-equivalent authority (performance reviews, hiring, SVP dotted-line). Built the
> CarePath ML framework — ISSIP Excellence in Service Innovation Award. Delivered Medicare
> Guided Selling as a fast-track serverless system. Managed cost controls with spot/GPU
> scale-to-zero scheduling.

#### USPS — High Priority

**Current LinkedIn:**
> Engaged in advanced analytics with multiple platforms. Primary focus on a SAS 9.4 and
> SAS Viya in-memory cluster with linkage to Hadoop Datalake inching up on 1Pb of data.
> Exploring machine learning and big data. We work with Tb not Gb of data in a high
> security environment.

**Resume summary (paste this):**
> Administered a 25-node SAS Viya in-memory analytics cluster (26TB RAM) with connectivity
> to a 50+ node Hadoop data lake approaching 1PB, operating on a closed network under NIST
> 800-53 high security controls with DEA data hosted. Worked directly with the USPS Chief
> Data Scientist and his team of data scientists, providing platform engineering, data
> engineering, and machine learning infrastructure support — including building custom data
> acquisition modules that gave the data science team access to production-quality geospatial
> and operational datasets they couldn't obtain from existing sources. Stabilized platform
> operations, built CISO-compliant administration automation (Python Fabric, Ansible), and
> constructed a complete Hadoop development platform replicating production for upgrade
> planning.

#### AKC — High Priority

**Current LinkedIn:**
> Oversee the design and execution of the cloud computing strategy including the cloud
> adoption plans, cloud application design, and cloud management and monitoring. Provide
> expertise in the definition, design, implementation, adoption and adherence to enterprise
> architecture strategies, processes and standards. Focused on Amazon cloud technologies.

**Resume summary (paste this):**
> Served as cloud evangelist bringing AWS into an organization that was entirely data-center
> and vendor-hosted, overcoming significant resistance from data center engineers who feared
> cloud adoption would eliminate their roles. Coached the existing engineering team through
> the transition — demonstrating that cloud is infrastructure with automation built in, not a
> replacement for engineers, and that upskilling into scripting, IaC, and automation was the
> path to staying relevant. That investment in people was as critical to the migration's
> success as the technical architecture. Built the AWS platform from nothing to a fully
> functional managed environment hosting AKC's primary website and marketplace. Completed
> zero-downtime migration of akc.org in six weeks and marketplace.akc.org in two weeks,
> reducing hosting costs from $30,000/month to under $5,000/month while improving uptime and
> response times. Designed and implemented a complex three-way Active Directory synchronization
> across AWS, the on-premises AKC data center, and Office 365. Led application modernization
> from legacy ColdFusion and Perl to a MEAN stack with end-to-end CI/CD.

**Condensed version (if LinkedIn truncates):**
> Cloud evangelist who brought AWS into a data-center-only organization. Built the AWS
> platform from scratch, completed zero-downtime migration of akc.org (6 weeks) and
> marketplace.akc.org (2 weeks), reducing hosting costs from $30K/month to under $5K/month.
> Coached the engineering team through the cloud transition. Designed three-way AD sync
> (AWS + on-prem + O365). Led application modernization from ColdFusion/Perl to MEAN stack
> with end-to-end CI/CD. Implemented MongoDB Atlas managed service.

#### NC DIT — Medium Priority

**Current LinkedIn:**
> Accountable for developing, maintaining and overseeing the execution of formalized
> technology, application, platform, and systems integration strategies...

**Resume summary (paste this):**
> Led enterprise-wide technology strategy for North Carolina state government in a dynamic
> environment with four direct-manager transitions, including a period of six months reporting
> directly to the State CIO (future Secretary of IT). Authored the Request for Information
> (RFI) for statewide data center network modernization and co-authored the Request for
> Proposals (RFP) with the State Risk Officer for a security standards rewrite based on NIST
> and DoD frameworks. Evaluated and responded to RFCs, policy and controls requests, and led
> program management for cloud technology adoption across Azure, OpenShift, and direct AWS
> engagement. Leveraged deep cross-agency relationships built over years as a state employee
> (NC DOR, UNC System, Community Colleges) and worked closely with the CISO on compliance and
> security initiatives — cross-domain knowledge from IRS audit and security background proved
> essential for moving programs and projects forward across organizational boundaries.

#### Measurement Inc — Medium Priority

**Current LinkedIn:**
> Systems Administration for Linux and Windows on Cloud platforms...

**Resume summary (paste this):**
> Originally hired to build data center infrastructure for an ML moonshot project — automated
> essay assessment for school system end-of-year exams — and rapidly pivoted to an AWS-hosted
> solution. Built a custom scalable compute and monitoring platform with a team of engineers
> that scaled to thousands of first-generation spot EC2 instances for ML scoring workloads,
> then scaled down. Owned all costs and cost controls across the platform (FinOps before the
> term existed). Scope expanded from systems administrator to systems programmer to cloud
> architect to machine learning engineer: optimized low-level ML libraries (CBlas, LPSolve,
> Shogun), ported the ML Toolkit to native Windows, and contributed patches back to open
> source communities. Also built a private cloud platform (Eucalyptus 3.4 replicating AWS
> services) with iSCSI shared storage for on-premises workloads. Concurrent with Georgia Tech
> MS coursework in machine learning — SVP Dr. Kirk Ridge provided the recommendation letter
> and support that enabled entry into the OMSCS program.

#### SAS Institute — Medium Priority

**Current LinkedIn:**
> Systems administration for Windows, Solaris, AIX and Linux for SAS Solutions OnDemand...

**Resume summary (paste this):**
> Administered validated systems for the pharmaceutical industry under FDA CFR Part 11
> compliance — not standard systems administration but validated systems administration where
> every action is auditable, every installation documented, and every change request traceable
> for federal audit. Designed multi-tier SAS architectures for 80+ customers in unique
> configurations, including the first production Disaster Recovery capable multi-tier SSO
> system for a clinical trial customer (7 servers + 8 load-balanced terminal servers).
> Automation-first approach using Puppet, scripting, and SAS product customization to ensure
> consistency across validated environments. Completed all six available SAS certifications in
> six consecutive months — one per month, the fastest anyone had accomplished this in any
> division at SAS: Platform Administrator, Base Programmer, Clinical Trials, Data Integration,
> BI Content Developer, and Statistical Business Analyst.

#### NC DOR — Medium Priority

**Current LinkedIn:**
> Review compliance to required state and federal policies...

**Resume summary (paste this):**
> Grew from firewall administrator to policy and controls leader over four years, rapidly
> expanding security scope from IC work to contributor on nationwide projects and multi-state
> initiatives. Skip-level reported to the Secretary of Revenue for half the tenure, taking
> direction from the top tier of the organization. Part of the five-person team that passed
> the IRS SafeGuard audit — a seven-month preparation producing a 1,300-page report covering
> all IT infrastructure, with no noteworthy findings (acknowledged by IRS auditors as a
> significant achievement). Loaned to the IRS for Congressional subcommittee work (ETAAC)
> developing third-party tax preparer security standards based on NIST 800-53 controls
> adapted to IRS Publication 1075. Integrated security reviews into every step of the SDLC,
> reducing rework costs and improving PCI and IRS compliance. Applied NIST 800-53, FISMA,
> FIPS 140-2, PCI-DSS, and ISO/IEC 27002 frameworks.

#### BD Biosciences — Medium Priority

**Current LinkedIn:**
> Provide for all IT services at the BD Treyburn manufacturing plant...

**Resume summary (paste this):**
> IT Director for the BD Treyburn manufacturing plant — sole IT leader managing all IT
> services, budgets, and one direct report with dotted-line reporting to the BD CIO and direct
> reporting to the plant manager. Owned costs and financials for all IT operations. Navigated
> a complex environment spanning an Apriso MES implementation with custom Oracle/SAP
> integrations, Genesis SAP deployment, phone system and network replacement, and medical
> device standards compliance. Led the Windows NT domain to Active Directory migration and SMS
> 2003 deployment. Integrated Allen & Bradley ControlLogix PLCs with manufacturing floor
> automation systems. Leveraged Lotus Notes and Domino experience from Ziff-Davis to manage
> BD's email and collaboration platform for 200+ users. Trained in BD Project Management
> Mastery (PMM) and Six Sigma. Built on the multi-site management experience from NC LIVE to
> lead a manufacturing plant IT operation in a regulated industry.

#### Earlier Roles (Lower Priority)

The resume now has leadership-voiced summaries for every role back to 1990. The most
impactful LinkedIn updates for earlier roles:

| Role | Key Resume Upgrade | LinkedIn Priority |
|------|-------------------|-------------------|
| NC Community Colleges | "Administered for all 58 colleges, led Solaris 9 upgrade, built automation" | Medium — shows statewide scope |
| Hosted Solutions | "Senior off-shift supervisor across three operation centers" | Low |
| NetIQ | "Built cloud-like lab automation before cloud existed, LabManager API-driven VM provisioning" | Medium — shows early cloud thinking |
| NCSU Systems Programmer II | "Returned to College of Engineering, RHCE, open source initiatives" | Low |
| NCSU Dev/Ops Manager | "NC LIVE statewide platform, EDUCAUSE presentation, Cisco 4700 first deployment, tripled providers" | Medium — leadership scope |
| NCSU Application Analyst | "First professional role at NCSU after work-study, NIOSH study" | Low |
| Ziff-Davis | "Grew across every product area, NDA with Microsoft/Intel, JMark cross-platform, Editorial Excellence Award" | Low — but keep for networking |
| Interpath 1998 | "Held concurrently with Ziff-Davis, learned Internet from ground floor" | Low |
| Pioneer Software | "First professional role, 130+ OEM customers, 50%+ of revenue, 15 international staff" | Medium — first management role |

### Certifications to Add to LinkedIn

| Certification | Status on Resume | Status on LinkedIn | Action |
|--------------|-----------------|-------------------|--------|
| ISC2 Certified in Cybersecurity (CC) | ✅ Nov 2024 – Nov 2027 | ❌ Missing | Add — current, security positioning |
| AWS SysOps Administrator – Associate | ✅ 2017-2020 (expired) | ❌ Missing | Add with dates — shows AWS depth |
| AWS Solutions Architect – Associate | ✅ 2017-2020 (expired) | ❌ Missing | Add with dates — shows AWS depth |
| SAS Base Programmer for SAS 9 | ✅ 2012 | ❌ Missing | Add — data science narrative |
| SAS Clinical Trials Programming | ✅ 2012 | ❌ Missing | Add — pharma/compliance narrative |
| SAS Data Integration Developer | ✅ 2012 | ❌ Missing | Add — data engineering narrative |
| SAS Statistical Business Analyst | ✅ 2013 | ❌ Missing | Add — analytics narrative |
| ITIL Foundation v2011 | ✅ 2016 | ✅ On LinkedIn (2006 version) | Verify — resume shows both 2006 and 2016 versions |
| RHCE | ✅ 2001-2006 | ❌ Missing | Add — early Linux depth |
| Solaris Certified Systems Admin | ✅ 2003-2005 | ❌ Missing | Low priority — dated |
| USPS Analytics University Bronze | ✅ 2018 | ❌ Missing | Low priority — niche |
| OWASP Top 10 (LinkedIn Learning) | ✅ 2022 | ❌ Missing | Low priority |

### Honors & Awards to Add to LinkedIn

| Award | Details | Action |
|-------|---------|--------|
| ISSIP Excellence in Service Innovation Award | CarePath CCM model at Blue Cross NC | Add to Honors & Awards |
| Healthcare Innovation Innovator Award | CarePath H2H model at Blue Cross NC | Add to Honors & Awards |
| Ziff-Davis Editorial Excellence Award | 1996 | Already on LinkedIn ✅ |
| Upsilon Pi Epsilon (UPE) | CS honor society | Already on LinkedIn ✅ |

### Education Updates

| Degree | Resume Highlights to Verify on LinkedIn |
|--------|----------------------------------------|
| EMBA at UNCW | "EMBA Candidate, Corporate Entrepreneurship focus, 4.00 GPA, Expected Graduation: Spring 2027" |
| MS at Georgia Tech | "Five-year program while working full-time, Interactive Intelligence, NJL publication, NWAV 46 presentation" |
| BS at NC State | "Completed while working full-time, graduated with Honors, 3.42 GPA" |

---

## Early Career Roles — Keep on LinkedIn

Per original assessment: the old companies help find former colleagues, and the old certs
show certification depth before the BS and MS. These serve a networking purpose on LinkedIn
that they don't serve on a resume. Keep them on LinkedIn. The resume now has richer
summaries for all of them if you want to update LinkedIn descriptions.

---

## Priority Actions (LinkedIn Only)

All resume work is complete. These are LinkedIn-only actions.

| # | Action | Effort |
|---|--------|--------|
| 1 | Rewrite Envestnet description (paste resume summary) | 5 min |
| 2 | Rewrite Blue Cross NC description (paste resume summary) + add ISSIP to Honors | 5 min |
| 3 | Rewrite USPS description (paste resume summary) | 5 min |
| 4 | Rewrite AKC description (paste resume summary or condensed version) | 5 min |
| 5 | Change BD Biosciences title to "IT Director" + rewrite description | 5 min |
| 6 | Change NC DOR title to "Application and Network Security Specialist" + rewrite | 5 min |
| 7 | Change NCSU 1999-2000 title to "Development Manager / Operations Manager" | 2 min |
| 8 | Change Envestnet title to add "ML Focus" | 2 min |
| 9 | Rewrite NC DIT description (paste resume summary) | 5 min |
| 10 | Rewrite Measurement Inc description (paste resume summary) | 5 min |
| 11 | Rewrite SAS Institute description (paste resume summary) | 5 min |
| 12 | Rewrite NC DOR description (paste resume summary) | 5 min |
| 13 | Rewrite BD Biosciences description (paste resume summary) | 5 min |
| 14 | Add ISC2 CC certification | 3 min |
| 15 | Add expired AWS certs (2) | 3 min |
| 16 | Add missing SAS certs (4) | 5 min |
| 17 | Add RHCE certification | 2 min |
| 18 | Add ISSIP + Healthcare Innovation awards to Honors & Awards | 3 min |
| 19 | Update EMBA to "EMBA Candidate — Expected Graduation: Spring 2027" | 2 min |
| 20 | Update earlier role descriptions (NetIQ, NC Community Colleges, Pioneer, etc.) | 20 min |
| 21 | Verify education descriptions match resume | 5 min |

**Total: ~105 minutes for all LinkedIn updates.**

**Quick wins (items 1-6):** The top six roles are the ones recruiters and hiring committees
actually read. Updating these six descriptions takes ~30 minutes and covers 90% of the
SVP positioning impact.

---

## Reference

- **LinkedIn profile snapshot:** `_drafts/PERSONA-LINKEDIN.md`
- **SVP positioning plan:** `_drafts/PERSONA-SVP.md`
- **Persona voice guide:** `_drafts/PERSONA.md`
- **Resume data:** `../resume/_data/data.yml`
- **Resume URL:** https://mcgarrah.org/resume/print
- **LinkedIn profile:** https://www.linkedin.com/in/michaelmcgarrah/
