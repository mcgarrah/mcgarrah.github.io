---
title:  "Five Stages of a Successful Cloud Data Science Platform"
layout: post
published: false
---

Data Science promotion process in five stages (with maybe three in a startup): it is always about the data

<!-- excerpt-end -->

Develop, productize and maintain ML pipelines for model training, evaluation, deployment are the MLOps... look at SageMaker and DataIKU are examples of ML Operational promotion processes.

First, a **Cloud Data Science Platform** is not the same as a standard Software Development Platform. The standard SDLC does not map to Data Science. The most obvious way to see this difference is where your production data, that includes things like PII, HIPAA, and PCI-DSS content, resides.

In typical SDLC, you have fake or synthetic data in your lower non-production environments that is just barely good enough to test and release your software. Often, special processes will sanitize your production data to be brought down to lower non-production environments so as to protect you customer data. Sometimes, you have external contractors in foreign countries... with different laws limiting access to production data. Sometimes you work in a highly regulated industry. But in the end, you have to protect your prod data.

To frame the discussion, here is a simplistic view of classic SDLC with a list of some of the classic environments. The middle environments are different in almost every enterprise I've worked in over the years. And those middle ones can be hotly debated. For the purposes on this discussion, we don't care about the middle. We care that some form of "Development" is the starting point without production data and at the end some form of a final "Production" environment exists with the real enterprise data.

1. Development (greatest flex / least secure)
1. SIT / STG Staging / SI / QA / Pre-Prod / UAT User Acceptance / etc...
1. Production (least flex / most secure)

What you classically call a development environment here would typically never have production data. The middle environments slosh back and forth with what kind of data but generally they are non-prod and don't have full production data copies. With this lack of real data carries a great deal more flexibility in how you manage those environment and peoples access to them as far as security and compliance are concerned. So you go from least secured and monitored to greatest security and auditing in the above environments.

This wholly successful and venerable pattern in classic SDLC falls flat when doing Data Science. But why!?! Because, doing DS on synthetic or sanitized data means not training with the real data that leads to good machine learning models. Bad, synthetic, and sanitized data fed into machine learning equates to bad training and resulting models. Model training requires real production data. I've had this argument with several Development and Project Managers over the last decade.

So you can now see "***The Conflict***..."

A Data Scientist, Data Engineer, or AI/ML Engineer are all going to need the flexibility of an interactive "Development" environment but access to the "Production" data that requires higher levels of controls limiting access and capabilities or adding extensive monitoring and auditing.

With that, here is a proposal for a set of promotion environments for Data Science and Machine Learning:

* Infrastructure Development
* Infrastructure Pre-Production
* **Prod Discovery** (DS Dev / interactive)
* **Prod Integration** (DS Pre-Prod / automation)
* **Production Production** (Final Prod)

Infra Dev/Pre-Prod are where you develop your infrastructure and test new tools before releasing to your DS Production environments. This protects the DS users from infra dev/test cycles. All changes in Infra Pre-Prod are released to all Prod closely together.

Everything with "Prod" on the front means *real* production customer data... so everything below is held to a higher standard for security and compliance. Also, in compliance and security reviews, removing the term "Development" from the name of the Discovery simplifies working with standard compliance frameworks. The highly interactive discovery environment carries the Prod designation, but also has to have exceptions for the interactive work done that is similar to some Development like patterns.

Discovery is DS interactive (development like) work which allows the DS developers lots of access to do things in there. Lots of auditing and monitoring is required as we grant high levels of access to critical and highly valued data. Discovery also will have Data Engineering happening as well which means lots of extra copies of the data. Feature Engineering will likely have you making copies of content making this a very storage heavy location. Likely, you will want to reach from Discovery to Final Prod datasets when working on ML models. You may also use datasets that are in active development by Data Engineers in Discovery as well.

Integration is for automation release of DS development work. No interactive work is done here. Automation based promotions of DS and DE work is pushed here before going to Final Prod for testing. This protects Final Prod from bad promotions.

Final Prod is where your customers use the AI/ML insights. It hosts the final copies of Data Engineering (DE) datasets and their data pipelines. It also hosts the final models and training from the Data Scientists (DS) to be used by the customers.

Reaching between the three "Prod" designated environments that each have production data in them can be done as each will have controls in place to manage and monitor access. Those controls become more and more restrictive as you move up from Discovery -> Integration -> Final Prod.

This pattern ccould be reduced to just three environments as shown with two or three having production data.

This one likely has lots of new tooling or infrastructure development happening...

* Infrastructure Development
* **Prod Discovery** (DS Dev / interactive)
* **Production Production** (Final Prod)

This one could have less and more focus on protecting the Final Prod.

* **Prod Discovery** (DS Dev / interactive)
* **Prod Integration** (DS Pre-Prod / automation)
* **Production Production** (Final Prod)

There is no one size fits all, but the basic idea that you need an interactive DS environment with production data influences everything you do. Add in your compliance and security requirements, and you can see why this is a challenging space.
