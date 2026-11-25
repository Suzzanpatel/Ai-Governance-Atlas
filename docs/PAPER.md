# The academic paper

**Title:** *From Principles to Enforceable Obligations: A Provision-Level Comparison of AI Governance in the European Union, India and the United Kingdom*

**Files:** `results/paper/AI_Governance_Atlas_Paper.pdf` (typeset) and `AI_Governance_Atlas_Paper.md` (the same text in Markdown, for editing)

## Generate it

```bash
python run_pipeline.py --stage publish
# or, with your name on the title page:
python src/publish/generate_paper.py --author "Your Name" --affiliation "Your University"
```

The script works offline and calls no AI or web service. For the same data it always produces the same text.

## Structure

Abstract · 1 Introduction · 2 Analytical framework (the translation chain) · 3 Data and methods · 4 Findings (4.1 legal and obligation force, 4.2 duty-holders, 4.3 enforcement linkage, 4.4 implementation evidence, 4.5 principle by principle, 4.6 computational indicators) · 5 Discussion · 6 Limitations · 7 Conclusion · Data and code availability · References · Appendix (all coded provisions)

Four figures and three tables are drawn from the data on each run.

## What is computed and what is fixed

| Computed from the data on every run | Fixed text in `generate_paper.py` |
|---|---|
| Every count, percentage and list of provision IDs | Framing of the introduction and the translation-chain framework |
| Per-dimension paragraphs, which quote each provision's coded summary | Parts of the discussion and conclusion |
| Pattern-dependent sentences (for example, which framework makes a principle mandatory, or each framework's weakest link) | The three scholarly references (checked against publishers' records) |
| Verification-audit figures and pending corrections | |
| All figures, tables, primary-source references and the appendix | |

If you recode provisions, the findings, figures and tables update automatically. **Re-read the fixed framing paragraphs** after significant data changes to make sure they still fit.

## Word count

The main text (abstract to conclusion, excluding tables, captions, references and appendix) must be within **±10% of 4,000 words** (3,600–4,400). The script reports the count, writes it to `paper_word_count.txt`, and stops with an error if the text falls outside the range. Use `--no-word-check` to override this while drafting.

## Before submitting

The generated paper is a data-driven draft. Before submitting it to a journal or repository:

1. Put your name and affiliation on the title page (`--author`, `--affiliation`).
2. Extend the literature review. The paper cites three works; a journal will expect a fuller review.
3. Check every legal statement against the primary sources listed in the references.
4. Decide on the 37 pending corrections in the Phase 12 correction register; the paper reports them as pending.
5. Consider adding later instruments (see section 6) and an inter-coder reliability check.

To edit the prose by hand, work from the Markdown file. Note that re-running the pipeline overwrites both the PDF and the Markdown.
