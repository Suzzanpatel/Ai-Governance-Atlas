# Phase 14.3 — Official Source and Version Validation Register

## Purpose

This phase converts the Phase 14.2 source locator results into a structured
register for validating source authority, document identity, version, legal
status, citation accuracy, and quotation context.

## Coverage

- Unique provisions in the annotated dataset: **24**
- Provision IDs with at least one local PDF candidate: **20**
- Candidate source rows in the register: **29**
- Register rows without a candidate PDF path: **4**
- Automatically authenticated official sources: **0**
- Automatically verified legal provisions: **0**

## Main outputs

- `phase14_3_official_source_version_validation_register.csv`
- `phase14_3_source_validation_coverage.csv`

## Validation checklist

For each candidate source, the reviewer should establish:

1. **Official publisher:** identify the legislature, regulator, government,
   international organisation, or other competent issuing body.
2. **Official source location:** confirm the source through the publisher's
   official repository or website.
3. **Instrument identity:** confirm the complete title and instrument number.
4. **Version:** confirm whether the PDF is an original, amended, or consolidated
   version and record its date.
5. **Amendments:** check later amendments, corrigenda, delegated/implementing
   acts, and relevant transitional provisions.
6. **Commencement:** establish whether the provision was in force at the
   relevant date, including phased application where applicable.
7. **Pinpoint citation:** confirm article, paragraph, page, schedule or annex.
8. **Quotation and context:** check exact wording, surrounding text, definitions,
   exceptions, qualifications and cross-references.

## Decision discipline

The register begins with `PENDING_SOURCE_REVIEW`. Do not change this to a
verified outcome solely because a text locator match exists. A candidate PDF
hash identifies the local file reviewed; it does not establish authenticity.

Recommended decision values for a later reviewed register:
- `VERIFIED`: all material source and pinpoint checks are supported by official
  evidence and reviewer notes.
- `DISCREPANCY_FOUND`: a source, version, pinpoint citation or quotation differs.
- `UNRESOLVED`: evidence is insufficient or contradictory.
- `NOT_APPLICABLE`: a specific check genuinely does not apply, with explanation.

## Limitations

This script does not access the internet, resolve URLs, verify official domains,
or determine legal status. URL values are extracted only when already present
in the dataset's source_reference field. Human review and authoritative source
evidence remain necessary.

## Next step

Phase 14.4 should use the completed register and authoritative source material
to document provision-level legal analysis, including legal force, scope,
conditions, responsible actor, enforcement cross-references, and interpretive
uncertainties.
