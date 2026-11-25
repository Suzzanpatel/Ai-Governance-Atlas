# Research Methodology

## 1. Research Design

AI Governance Atlas uses a comparative, document-based research design
to examine how selected AI governance frameworks express principles
through regulatory or policy provisions.

The project combines qualitative legal and policy analysis with
computational text analysis. The computational component helps organise
and identify patterns in documentary material; it does not replace
interpretation of legal meaning, legal force or implementation.

The comparison covers three jurisdictions---India, the European Union
(EU) and the United Kingdom (UK)---and uses the OECD AI Principles as an
international benchmark. The OECD is treated as an international
reference framework, not as a fourth national jurisdiction.

## 2. Research Question and Objectives

The central research question is:

> To what extent do India, the European Union and the United Kingdom
> translate AI governance principles into specific, measurable and
> enforceable regulatory obligations?

The project examines differences in approaches to transparency,
accountability, risk assessment, safety and testing, and enforcement. It
also considers the distinction between voluntary governance principles
and legally binding obligations, and the limitations of computational
methods in assessing regulatory effectiveness.

## 3. Case Selection

The project selects India, the EU and the UK to enable comparison across
different legal and policy approaches to AI governance. The OECD AI
Principles provide an international benchmark against which selected
themes and approaches can be considered.

The case selection is purposive. The project does not claim that the
selected materials represent every AI-related law, policy or institution
in any of the frameworks.

## 4. Documentary Evidence and Sources

The research uses official legal and policy documents as its primary
documentary material. The project repository organises raw source
documents by framework and stores extracted and cleaned documentary text
separately.

Primary sources should be cited by their issuing institution, title,
date, provision or section, and an official URL or stable reference
where available. Secondary literature may be used to contextualise or
critically assess the primary material, but should not substitute for
the text of a legal or policy instrument when classifying a provision.

For each provision included in the evidence pack, the project records
its identifier, framework or country, relevant text, summary, legal
status, obligation type, governance dimension, responsible actor,
enforcement information, implementation status and source reference,
where those fields are available.

## 5. Selection of Provisions

The current annotated evidence dataset contains 20 selected provisions:
five each for the EU, India, the UK and the OECD benchmark.

The sample is purposive rather than statistically representative. It is
designed to support a structured, manageable comparison across five
governance dimensions:

1.  Risk Assessment
2.  Transparency
3.  Accountability
4.  Safety and Testing
5.  Enforcement

The selected provisions are units of analysis. Findings should therefore
be described as findings about the selected provisions and documentary
sample, not as exhaustive conclusions about each entire governance
framework.

## 6. Document Processing and Computational Analysis

The computational workflow uses Python to support document processing
and analysis. The project includes source PDFs, extracted document text
and cleaned-document data.

The workflow includes:

1.  Collecting and organising source documents.
2.  Extracting text from PDF documents.
3.  Cleaning and preparing extracted text for analysis.
4.  Conducting keyword-based and text-based analysis to identify
    recurring governance themes.
5.  Producing tables and visualisations to support comparison.

Keyword frequencies and other text patterns are descriptive indicators.
They do not, by themselves, establish the legal force, practical
effectiveness or implementation of a regulatory requirement. Document
length, drafting style, publication date and document type can affect
computational results and must be considered when interpreting
comparisons.

Where automated processing is used, relevant classifications and
interpretations require human review.

## 7. Manual Legal and Policy Coding

The project applies a coding framework to classify selected provisions.
The framework keeps distinct the following analytical categories:

-   **Legal force:** whether the instrument is binding legislation,
    non-binding guidance, government policy or an international
    recommendation.
-   **Obligation force:** whether the specific provision is mandatory,
    recommended, voluntary or not specified.
-   **Obligation nature:** whether the requirement is institutional,
    procedural, substantive, reporting-related or another type.
-   **Governance dimension:** the provision's primary governance
    dimension, with a secondary dimension where justified.
-   **Responsible actor:** the actor assigned responsibility by the
    source.
-   **Enforcement mechanism:** the mechanism established by the
    provision or connected provisions, distinguishing direct from wider
    framework mechanisms.
-   **Implementation status:** the status supported by documented
    implementation evidence, or "Not assessed" where no assessment has
    been made.

Coding decisions should be grounded in the relevant primary-source text.
The rationale and source reference should be recorded, particularly
where a classification is contestable. Legal force and obligation force
must not be treated as interchangeable.

## 8. Implementation Evidence Assessment

The existence of a law, policy or recommendation does not by itself
demonstrate implementation. Implementation classifications require
documentary evidence and should identify the issuing organisation,
publication date, relevant page or paragraph, and the specific passage
supporting the assessment.

The project uses the categories Implemented, Partially implemented, Not
yet implemented, No evidence of implementation found and Not assessed.

"Not assessed" means that implementation has not been evaluated. "No
evidence of implementation found" means that a documented search did not
locate adequate evidence; it does not prove that implementation has not
occurred. Where the evidence is insufficient, the project should avoid
unsupported conclusions.

## 9. Comparative Analysis

The comparative analysis examines how the selected provisions address
the five governance dimensions and how their legal status, obligation
force, responsible actors and enforcement mechanisms differ.

The analysis should account for differences between binding legislation,
government policy, non-binding guidance and international
recommendations. Counts and matrices are used to describe the selected
sample, not to rank entire frameworks or establish regulatory
effectiveness on their own.

The OECD benchmark is used to contextualise international principles and
recommendations alongside the three jurisdictional approaches.

## 10. Reliability, Transparency and Reproducibility

To support reproducibility, the project retains source documents,
extracted and cleaned data, annotated records, coding rules, source
references, audit outputs and analysis scripts within the repository.

Material coding changes should preserve the original decision and record
the revised classification, reason for change, source reference,
reviewer decision and review date. Uncertainty should be recorded rather
than concealed through unsupported classifications.

A structural audit can identify issues such as duplicate identifiers,
missing values and category distributions. Such an audit checks dataset
structure and consistency; it does not independently verify the legal
accuracy of every coded record.

## 11. Limitations

The evidence pack contains 20 purposively selected provisions, five from
each framework. It is not necessarily representative of the full body of
AI law and policy in any framework.

The documents differ in legal status, institutional context, scope,
length, drafting style and publication date. These differences limit
direct comparison.

Keyword analysis and other computational text methods can identify
patterns but may miss context, nuance, legal qualifications and
differences in terminology. Manual legal interpretation is therefore
necessary.

Implementation evidence may be uneven across frameworks. A lack of
located evidence should not be treated as proof of non-implementation,
and "Not assessed" should not be interpreted as failure.

Finally, the selected sample and descriptive computational analysis
cannot, by themselves, establish the real-world effectiveness of an
entire AI governance system. Conclusions must remain proportionate to
the documentary evidence examined.

## 12. Methodological Status

This document describes the research design and workflow of AI
Governance Atlas. It should be updated when the project adds or removes
source materials, changes the selection of provisions, modifies the
coding framework or completes further verification.

Claims that a source has been verified, a classification has been
validated or an implementation status has been established should only
be made after the relevant source check and evidence review have been
completed.
