"""Generate the AI Governance Atlas academic paper (about 4,000 words) as a PDF.

The paper is assembled deterministically from the coded dataset and the
analysis tables (see atlas_data.py). Every count, percentage, list of
provisions and pattern-dependent claim is computed from the data; the framing
prose is fixed. Re-running after the data changes therefore updates the
findings, figures and tables together. No AI service or network access is
used.

Outputs (results/paper/):
    AI_Governance_Atlas_Paper.pdf     typeset paper
    AI_Governance_Atlas_Paper.md      the same text in Markdown, for editing
    figures/fig*.png                  figures embedded in the paper
    paper_word_count.txt              word count of the main text

Usage:
    python src/publish/generate_paper.py
    python src/publish/generate_paper.py --author "Your Name" --affiliation "Your University"

The generated paper is a data-driven manuscript draft. The author is
responsible for reviewing it, extending the literature review and checking
every legal statement against the primary sources before submission.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

import atlas_data as ad  # noqa: E402

OUT_DIR = ad.ROOT / "results" / "paper"
FIG_DIR = OUT_DIR / "figures"
PDF_PATH = OUT_DIR / "AI_Governance_Atlas_Paper.pdf"
MD_PATH = OUT_DIR / "AI_Governance_Atlas_Paper.md"
COUNT_PATH = OUT_DIR / "paper_word_count.txt"

TARGET_WORDS = 4000
TOLERANCE = 0.10  # the main text must fall within ±10% of the target

TITLE = (
    "From Principles to Enforceable Obligations: A Provision-Level Comparison "
    "of AI Governance in the European Union, India and the United Kingdom"
)

# ---------------------------------------------------------------------------
# Colour roles (validated with the dataviz palette validator, light mode)
# ---------------------------------------------------------------------------
FRAMEWORK_COLOURS = {
    "EU": "#257de0",
    "India": "#f47230",
    "UK": "#00b894",
    "OECD (international benchmark)": "#f2a600",
}
ENFORCEMENT_COLOURS = {
    "Cross-referenced": "#6a4ce2",
    "System-level only": "#ee7fac",
    "Direct": "#008a17",
    "None identified": "#9c9c9c",
    "Not applicable": "#ffffff",  # drawn as an outlined, hatched segment
}
IMPLEMENTATION_COLOURS = {
    "Implemented": "#262626",
    "Partially implemented": "#4f4f4f",
    "Not yet implemented": "#787878",
    "No evidence of implementation found": "#a3a3a3",
    "Not assessed": "#ffffff",  # drawn as an outlined segment
}
TEXT = "#191919"
TEXT_2 = "#666666"
GRID = "#e5e5e5"

PRIVATE_ACTORS = {"AI Provider", "AI Deployer", "Developer", "Intermediary", "End User", "AI Lifecycle Actors", "Multiple Stakeholders"}
PUBLIC_ACTORS = {"Government", "Regulator", "Institution"}

# Scholarly works cited in the framing sections. Publication details were
# checked against the publishers' records; keep this list accurate if edited.
LITERATURE = [
    "Jobin, A., Ienca, M. and Vayena, E. (2019) 'The global landscape of AI ethics guidelines', "
    "Nature Machine Intelligence, 1(9), pp. 389-399. doi:10.1038/s42256-019-0088-2.",
    "Mittelstadt, B. (2019) 'Principles alone cannot guarantee ethical AI', "
    "Nature Machine Intelligence, 1(11). doi:10.1038/s42256-019-0114-4.",
    "Veale, M. and Zuiderveen Borgesius, F. (2021) 'Demystifying the Draft EU Artificial "
    "Intelligence Act', Computer Law Review International, 22(4), pp. 97-112. doi:10.9785/cri-2021-220402.",
]

# Instruments that post-date the coded versions and are not in the sample.
# Listed so the limitations section stays honest about scope.
OUT_OF_SAMPLE = [
    "India's Second Amendment Rules of 2026, prepared in April 2026 to require continuous display of "
    "synthetic-content labels, whose gazette status could not be confirmed",
    "the strategic approaches published by individual UK regulators in 2024, which are recorded as "
    "implementation evidence rather than coded as provisions",
    "sector-specific AI guidance issued under each framework",
]


# ---------------------------------------------------------------------------
# Small text helpers
# ---------------------------------------------------------------------------
NUM_WORDS = {0: "none", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
             6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


PROSE_NAME = {"EU": "the EU", "India": "India", "UK": "the UK", "OECD (international benchmark)": "the OECD benchmark"}


def name(framework: str, capital: bool = False) -> str:
    """Framework name for running text, with its article ('the EU', 'India')."""
    n = PROSE_NAME[framework]
    return n[0].upper() + n[1:] if capital else n


def names(frameworks) -> str:
    return join([name(f) for f in frameworks])


def num(n: int) -> str:
    return NUM_WORDS.get(n, str(n))


def Num(n: int) -> str:
    return num(n).capitalize()


def of(k: int, total: int) -> str:
    """'all five', 'none of the five', 'three of five'."""
    if total == 2 and k == 2:
        return "both"
    if total and k == total:
        return f"all {num(total)}"
    if k == 0:
        return f"none of the {num(total)}"
    return f"{num(k)} of {num(total)}"


def pct(part: int, whole: int) -> str:
    return f"{round(100 * part / whole)}%" if whole else "0%"


def plural(n: int, one: str, many: str | None = None) -> str:
    return one if n == 1 else (many or one + "s")


def join(items: list[str]) -> str:
    items = [i for i in items if i]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def first_sentence(text: str) -> str:
    """First sentence of a coded summary, ready to follow 'In <framework> (<id>), '."""
    sent = re.split(r"(?<=[a-z0-9)])\.\s", text.strip(), maxsplit=1)[0].rstrip(".")
    # Lower-case the first letter unless the word is an acronym (e.g. "AI", "OECD")
    if len(sent) > 1 and sent[0].isupper() and not sent[1].isupper():
        sent = sent[0].lower() + sent[1:]
    return sent


def ids(records: list[dict]) -> str:
    return ", ".join(r["id"] for r in records)


CLASSIFICATION_FIELDS = {"legal_status", "obligation_type", "governance_dimension", "secondary_dimension",
                         "implementation_status", "applicability_status", "document_type"}


def corrections_scope_sentence(meta: dict) -> str:
    by_field = meta.get("corrections_by_field", {})
    if not by_field:
        return ""
    classification = sum(v for k, v in by_field.items() if k in CLASSIFICATION_FIELDS)
    top = sorted(((v, k) for k, v in by_field.items() if k not in CLASSIFICATION_FIELDS), reverse=True)[:3]
    top_txt = join([f"{k.replace('_', ' ')} ({v})" for v, k in top])
    if classification == 0:
        return (f"None of the corrections changes a classification category used in the analysis; they "
                f"concern descriptive and referencing fields, chiefly {top_txt}.")
    return (f"{Num(classification)} {plural(classification, 'correction concerns', 'corrections concern')} "
            f"a classification category used in the analysis; the remainder concern {top_txt}.")


def word_count(text: str) -> int:
    text = re.sub(r"<[^>]+>", " ", text)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-.%/()]*", text))


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
def _style(ax):
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=TEXT_2, labelsize=8, length=0)
    ax.xaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def _stacked_hbar(ax, data, levels, colours, outlined, hatched=()):
    frameworks = list(data)
    y = list(range(len(frameworks)))[::-1]
    left = [0] * len(frameworks)
    for lvl in levels:
        vals = [data[fw][lvl] for fw in frameworks]
        face = colours[lvl]
        edge = TEXT_2 if lvl in outlined else "white"
        for yi, v, l in zip(y, vals, left):
            if not v:  # skip empty segments (avoids stray outline slivers)
                continue
            ax.barh(yi, v, left=l, height=0.56, color=face, edgecolor=edge,
                    linewidth=0.8 if lvl in outlined else 1.5,
                    hatch="////" if lvl in hatched else None)
            dark_fill = face.lower() in {"#262626", "#4f4f4f", "#787878", "#6a4ce2", "#008a17"}
            ax.text(l + v / 2, yi, str(v), ha="center", va="center", fontsize=8,
                    color="white" if dark_fill else TEXT, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none")
                    if lvl in hatched else None)
        left = [a + b for a, b in zip(left, vals)]
    ax.set_yticks(y)
    ax.set_yticklabels([ad.SHORT[f] for f in frameworks], fontsize=9, color=TEXT)
    ax.set_xlim(0, max(left) if max(left) else 1)
    ax.set_xlabel("Number of coded provisions", fontsize=8, color=TEXT_2)
    _style(ax)


def fig_enforcement(atlas, path):
    data = atlas.crosstab("enforcement_level", ad.ENFORCEMENT_LEVELS)
    fig, ax = plt.subplots(figsize=(6.4, 2.7))
    _stacked_hbar(ax, data, ad.ENFORCEMENT_LEVELS, ENFORCEMENT_COLOURS,
                  outlined={"Not applicable"}, hatched={"Not applicable"})
    handles = [Patch(facecolor=ENFORCEMENT_COLOURS[l], edgecolor=TEXT_2 if l == "Not applicable" else "white",
                     hatch="////" if l == "Not applicable" else None, label=l) for l in ad.ENFORCEMENT_LEVELS]
    ax.legend(handles=handles, ncol=5, fontsize=7, frameon=False, loc="lower left", columnspacing=1.0,
              bbox_to_anchor=(0, 1.02), handlelength=1.2, labelcolor=TEXT)
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


def fig_implementation(atlas, path):
    data = atlas.crosstab("implementation_status", ad.IMPLEMENTATION_LEVELS)
    fig, ax = plt.subplots(figsize=(6.4, 2.7))
    _stacked_hbar(ax, data, ad.IMPLEMENTATION_LEVELS, IMPLEMENTATION_COLOURS, outlined={"Not assessed"})
    handles = [Patch(facecolor=IMPLEMENTATION_COLOURS[l], edgecolor=TEXT_2 if l == "Not assessed" else "white",
                     label=l.replace("No evidence of implementation found", "No evidence found")) for l in ad.IMPLEMENTATION_LEVELS]
    ax.legend(handles=handles, ncol=5, fontsize=7, frameon=False, loc="lower left", columnspacing=1.0,
              bbox_to_anchor=(0, 1.02), handlelength=1.2, labelcolor=TEXT)
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


def fig_addressees(atlas, path):
    cats, table = atlas.multi_crosstab("responsibility_categories")
    order = [c for c in cats if c in PRIVATE_ACTORS] + [c for c in cats if c in PUBLIC_ACTORS] + \
            [c for c in cats if c not in PRIVATE_ACTORS | PUBLIC_ACTORS]
    ramp = ["#ffffff", "#cce3fd", "#84b9f3", "#338ced", "#2370cd", "#0f4a96"]
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    for i, fw in enumerate(ad.FRAMEWORKS):
        for j, cat in enumerate(order):
            v = table[fw].get(cat, 0)
            face = ramp[min(v, len(ramp) - 1)]
            ax.add_patch(plt.Rectangle((j, len(ad.FRAMEWORKS) - 1 - i), 0.94, 0.9, facecolor=face,
                                       edgecolor=GRID if v == 0 else "white", linewidth=0.8))
            if v:
                ax.text(j + 0.47, len(ad.FRAMEWORKS) - 1 - i + 0.45, str(v), ha="center", va="center",
                        fontsize=8, color="white" if v >= 3 else TEXT, fontweight="bold")
    n_private = sum(c in PRIVATE_ACTORS for c in order)
    ax.axvline(n_private - 0.03, color=TEXT_2, linewidth=0.8, linestyle=(0, (2, 2)))
    ax.text(n_private / 2, len(ad.FRAMEWORKS) + 0.15, "Private actors", ha="center", fontsize=8, color=TEXT_2)
    ax.text(n_private + (len(order) - n_private) / 2, len(ad.FRAMEWORKS) + 0.15, "Public bodies",
            ha="center", fontsize=8, color=TEXT_2)
    ax.set_xlim(0, len(order))
    ax.set_ylim(0, len(ad.FRAMEWORKS) + 0.6)
    ax.set_xticks([j + 0.47 for j in range(len(order))])
    ax.set_xticklabels([c.replace("AI Lifecycle Actors", "Lifecycle actors").replace("Multiple Stakeholders", "Multiple")
                        .replace("AI ", "") for c in order], fontsize=7.5, color=TEXT, rotation=30, ha="right")
    ax.set_yticks([len(ad.FRAMEWORKS) - 1 - i + 0.45 for i in range(len(ad.FRAMEWORKS))])
    ax.set_yticklabels([ad.SHORT[f] for f in ad.FRAMEWORKS], fontsize=9, color=TEXT)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


def fig_keywords(atlas, path):
    kw = atlas.keywords
    dims = ad.DIMENSIONS
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    h = 0.19
    for k, fw in enumerate(ad.FRAMEWORKS):
        vals = [float(kw[(kw.framework == fw) & (kw.dimension == d)]["frequency_per_1000_words"].sum()) for d in dims]
        ys = [len(dims) - 1 - i + (1.5 - k) * h for i in range(len(dims))]
        ax.barh(ys, vals, height=h - 0.02, color=FRAMEWORK_COLOURS[fw], edgecolor="white", linewidth=1, label=ad.SHORT[fw])
        for yv, v in zip(ys, vals):
            ax.text(v + 0.06, yv, f"{v:.1f}", va="center", fontsize=6.5, color=TEXT_2)
    ax.set_yticks(range(len(dims)))
    ax.set_yticklabels(dims[::-1], fontsize=8.5, color=TEXT)
    ax.set_xlabel("Keyword occurrences per 1,000 words", fontsize=8, color=TEXT_2)
    _style(ax)
    ax.legend(ncol=4, fontsize=7.5, frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0),
              handlelength=1.2, labelcolor=TEXT)
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------
def build_content(atlas: ad.Atlas, author: str, affiliation: str, figs: dict) -> list[tuple]:
    R = atlas.records
    n = atlas.n
    FW = ad.FRAMEWORKS
    juris = [f for f in FW if not f.startswith("OECD")]
    by = {f: atlas.by_framework(f) for f in FW}
    per_fw = {f: len(by[f]) for f in FW}

    obl = atlas.crosstab("obligation_type", ad.OBLIGATION_TYPES)
    enf = atlas.crosstab("enforcement_level", ad.ENFORCEMENT_LEVELS)
    imp = atlas.crosstab("implementation_status", ad.IMPLEMENTATION_LEVELS)
    dims = atlas.crosstab("governance_dimension", ad.DIMENSIONS)

    mandatory = [r for r in R if r["obligation_type"] == "Mandatory"]
    mand_fw = sorted({r["country"] for r in mandatory}, key=FW.index)
    recommended = [r for r in R if r["obligation_type"] == "Recommended"]
    voluntary = [r for r in R if r["obligation_type"] == "Voluntary"]
    unspecified = [r for r in R if r["obligation_type"] == "Not specified"]
    binding = [r for r in R if r["legal_status"].startswith("Binding")]
    binding_fw = sorted({r["country"] for r in binding}, key=FW.index)
    nonbinding = [r for r in R if not r["legal_status"].startswith("Binding")]
    # Mandatory wording inside a non-binding instrument (e.g. an internal OECD instruction)
    mand_nonbinding = [r for r in mandatory if not r["legal_status"].startswith("Binding")]
    later = [r for r in R if not r["principal_instrument"]]
    later_fw = sorted({r["country"] for r in later}, key=FW.index)
    later_docs = [d for d, src in atlas.sources.items() if not src["principal"]]
    core_per_fw = {f: sum(r["principal_instrument"] for r in by[f]) for f in FW}
    india_binding = [r for r in by["India"] if r["legal_status"].startswith("Binding")]
    india_in_force = [r for r in india_binding if r["applicability_status"].startswith("In force")]

    linked = [r for r in R if r["enforcement_level"] in ("Cross-referenced", "Direct")]
    crossref = [r for r in R if r["enforcement_level"] == "Cross-referenced"]
    direct = [r for r in R if r["enforcement_level"] == "Direct"]
    system = [r for r in R if r["enforcement_level"] == "System-level only"]
    none_ = [r for r in R if r["enforcement_level"] == "None identified"]
    na = [r for r in R if r["enforcement_level"] == "Not applicable"]
    statutory_sanction = [r for r in R if r["mechanism_character"] == "Statutory enforcement"]
    sanction_fw = sorted({r["country"] for r in statutory_sanction}, key=FW.index)

    def addressed_private(r):
        return any(c in PRIVATE_ACTORS for c in r["responsibility_categories"])

    def addressed_public(r):
        return any(c in PUBLIC_ACTORS for c in r["responsibility_categories"])

    priv = {f: sum(addressed_private(r) for r in by[f]) for f in FW}
    binding_private = sum(addressed_private(r) for r in binding)
    nonbinding_public = sum(addressed_public(r) for r in nonbinding)
    pub = {f: sum(addressed_public(r) for r in by[f]) for f in FW}
    public_only = {f: sum(addressed_public(r) and not addressed_private(r) for r in by[f]) for f in FW}

    assessed = {f: [r for r in by[f] if r["implementation_status"] != "Not assessed"] for f in FW}
    evidenced = {f: [r for r in by[f] if r["implementation_status"] in ("Implemented", "Partially implemented")] for f in FW}
    not_yet_applicable = [r for r in R if r["applicability_status"].startswith("Legally adopted but not yet applicable")]

    kw = atlas.keywords

    def kwv(fw, dim):
        s = kw[(kw.framework == fw) & (kw.dimension == dim)]["frequency_per_1000_words"]
        return float(s.sum()) if len(s) else 0.0

    def kw_words(fw):
        s = kw[kw.framework == fw]["total_words"]
        return int(s.iloc[0]) if len(s) else 0

    top_dim = {f: max(ad.DIMENSIONS, key=lambda d: kwv(f, d)) for f in FW}
    eu_enf_kw = kwv("EU", "Enforcement")
    max_enf_fw = max(FW, key=lambda f: kwv(f, "Enforcement"))

    eu_sanction_mechs = sorted({m for r in by["EU"] for m in r["enforcement_mechanisms"]})
    india_direct = [r for r in by["India"] if r["enforcement_level"] == "Direct"]
    uk_direct = [r for r in by["UK"] if r["enforcement_level"] == "Direct"]

    fig_n = {"addr": 1, "enf": 2, "imp": 3, "kw": 4}

    blocks: list[tuple] = []
    P = lambda t: blocks.append(("p", t))  # noqa: E731
    H1 = lambda t: blocks.append(("h1", t))  # noqa: E731
    H2 = lambda t: blocks.append(("h2", t))  # noqa: E731

    blocks.append(("title", TITLE))
    blocks.append(("byline", f"{author}" + (f" · {affiliation}" if affiliation else "")))
    blocks.append(("date", f"Manuscript generated {date.today().strftime('%d %B %Y')} from the AI Governance Atlas dataset"))

    # ---------------- Abstract ----------------
    blocks.append(("abstract",
        "Artificial intelligence governance has produced a broad consensus on principles such as transparency, "
        "accountability and safety, but far less agreement on how those principles become duties that someone must "
        f"perform and that someone else can enforce. This paper compares {n} purposively selected provisions from the "
        "European Union's AI Act, India's AI Governance Guidelines"
        + (" and its 2026 intermediary rules on synthetically generated information" if india_binding else "")
        + ", and the United Kingdom's pro-innovation White Paper"
        + (" and the government's 2024 response" if any(r["country"] == "UK" for r in later) else "")
        + ", using the OECD Recommendation on Artificial Intelligence as an international benchmark. Each provision is "
        "coded for legal force, obligation force and nature, duty-holder, enforcement linkage and implementation evidence, "
        "and the manual coding is complemented by keyword analysis and an AI-assisted blind second coding. "
        f"{Num(len(binding))} of the {n} provisions come from binding instruments, in {names(binding_fw)}, and "
        f"{num(len(statutory_sanction))} are linked to statutory sanctions. The frameworks differ less in the principles "
        "they recognise than in where they place responsibility: "
        f"{'every' if binding_private == len(binding) else f'{binding_private} of the {len(binding)}'} binding "
        "provision addresses private providers, deployers or intermediaries, whereas non-binding provisions mainly "
        "address governments and regulators. The paper calls this a difference in the translation chain between principle "
        "and enforcement. It also finds that enforceability and implementation diverge: "
        + ("the EU's statutory duties were not yet applicable during the research period, while India's targeted "
           "intermediary duties took effect within days by building on an existing due-diligence regime. "
           if india_in_force and not_yet_applicable else
           "the framework with the most enforceable duties is the one whose duties were not yet applicable during the "
           "research period. ")
        + "The findings describe a small structured sample and do not rank the frameworks."))
    blocks.append(("keywords", "Keywords: AI governance; AI Act; comparative regulation; enforcement; India; United Kingdom; OECD"))

    # ---------------- 1 Introduction ----------------
    H1("1. Introduction")
    P("The last decade produced an abundance of AI principles. Governments, companies, standard-setting bodies and "
      "international organisations have published statements committing to transparent, fair, accountable and safe "
      "artificial intelligence. Mapping studies found that these documents converge on a small set of recurring values "
      "while diverging on what the values mean and how they should be implemented (Jobin, Ienca and Vayena, 2019). "
      "Critics have argued that principles alone cannot secure ethical outcomes, because AI development lacks the "
      "professional norms, proven methods and robust accountability mechanisms that make principles operative in fields "
      "such as medicine (Mittelstadt, 2019).")
    P("That critique raises an empirical question for regulators rather than ethicists. When a jurisdiction moves from "
      "endorsing a principle to governing AI, what exactly changes? A principle may become a statutory duty with a named "
      "duty-holder and a sanction; it may become guidance that existing regulators are invited to apply; or it may remain "
      "a recommendation whose only follow-up is periodic reporting. These are different regulatory techniques, and they "
      "carry different implications for whether the principle will shape conduct.")
    P("This paper examines that translation in three jurisdictions that have taken visibly different routes. The European "
      "Union adopted a horizontal, risk-based regulation, the AI Act, and amended it in 2026 through the Digital Omnibus "
      "on AI. The United Kingdom chose a principles-based framework applied by existing sectoral regulators without new "
      "primary legislation, and confirmed that approach in its February 2024 response to consultation. India issued "
      "national AI Governance Guidelines in November 2025 that favour voluntary measures, existing law and new "
      "coordinating institutions"
      + (", and three months later brought synthetically generated content within its binding rules for online "
         "intermediaries" if india_binding else "") + ". The OECD Recommendation on Artificial Intelligence, to which all "
      "three relate, serves as an international benchmark rather than as a fourth jurisdiction.")
    P("The three cases were chosen because they vary the variable of interest while holding the underlying principles "
      "roughly constant. All three jurisdictions adhere to, or draw explicitly on, the OECD principles, so differences "
      "between them are unlikely to reflect disagreement about values. They differ instead in regulatory technique: a "
      "dedicated statute with product-safety style compliance machinery, a non-statutory principles regime delivered "
      "through existing regulators, and a guidelines-led approach that combines voluntary measures with institution "
      "building and reliance on existing legislation. India also extends the comparison beyond the EU-UK pairing that "
      "dominates much commentary, adding a large jurisdiction whose approach is explicitly framed around enabling "
      "innovation and adoption.")
    P("The central research question is: to what extent do the EU, India and the UK translate AI governance principles into "
      "specific, measurable and enforceable regulatory obligations? The paper contributes in three ways. First, it offers "
      "a provision-level coding scheme that separates the legal force of an instrument from the force of an individual "
      "duty, the duty-holder, the enforcement route and the evidence of implementation. Second, it applies that scheme to a "
      "transparent and reproducible evidence base in which every coded record carries its exact text, page reference and "
      "source version. Third, it uses the comparison to identify two patterns, concerning the addressees of obligations and "
      "the timing of implementation, that a principle-by-principle comparison would miss.")

    # ---------------- 2 Framework ----------------
    H1("2. Analytical framework: the translation chain")
    P("The analysis treats the movement from principle to practice as a chain of five links. A break at any link limits "
      "how far a principle can be relied upon to change behaviour, and the links are deliberately coded separately so "
      "that strength at one point is not mistaken for strength throughout.")
    P("<b>Legal force</b> concerns the instrument: whether it is binding legislation, government policy, non-binding "
      "guidance or an international recommendation. <b>Obligation force</b> concerns the individual provision: whether it "
      "imposes a mandatory requirement, makes a recommendation, or assigns a function to an institution. A binding "
      "instrument can contain recommendations, and a policy document can describe obligations that already exist "
      "elsewhere in law, so the two must be distinguished.")
    P("The <b>duty-holder</b> link identifies who is expected to act. A provision addressed to an AI provider creates a "
      "different regulatory relationship from one addressed to a ministry or a sectoral regulator, even where both concern "
      "the same principle. The <b>enforcement linkage</b> link asks whether a compliance route attaches to the duty. The "
      "coding distinguishes five situations: a route named in the provision itself (direct); a route attached by "
      "cross-reference to sanctions elsewhere in the instrument (cross-referenced); reliance on the general powers of "
      "existing bodies without a provision-specific route (system-level only); no identified route; and provisions that "
      "build institutions rather than impose compliance duties (not applicable).")
    P("The final link, <b>implementation evidence</b>, records whether dated and attributable sources show that the measure "
      "has been put into operation. It is coded on a five-point scale from implemented to not assessed, and absence of "
      "located evidence is never treated as proof of non-implementation. Effectiveness, meaning whether a measure changed "
      "conduct or reduced harm, lies outside the chain and outside this study.")

    # ---------------- 3 Data and methods ----------------
    H1("3. Data and methods")
    H2("3.1 Sources and versions")
    P(f"The corpus consists of a principal instrument for each framework"
      + (f", supplemented by {num(len(later_docs))} later {plural(len(later_docs), 'instrument')} for "
         f"{names(later_fw)}" if later_docs else "")
      + ", listed with the version coded in Table 1. For the EU, "
      f"the coding uses the consolidated text that incorporates Regulation (EU) 2026/1744; because several high-risk "
      f"obligations were deferred by that amendment, {of(len(not_yet_applicable), per_fw['EU'])} EU provisions are "
      "recorded as legally adopted but not yet applicable. The UK White Paper and the India Guidelines are coded in the "
      "versions published by their issuing departments, and the OECD Recommendation as revised in May 2024."
      + (" The later instruments were added so that the sample reflects how each framework developed after its principal "
         "instrument: India's 2026 amendment of the intermediary rules, which created the country's first binding "
         "obligations aimed at AI-generated content, and the UK government's 2024 consultation response." if later_docs else ""))
    blocks.append(("table_sources", None))
    H2("3.2 Sample and coding")
    P(f"The evidence base contains {n} provisions, {join([f'{num(per_fw[f])} from {name(f)}' for f in FW])}. "
      "Provisions were selected purposively for their relevance to five governance dimensions: transparency, "
      "accountability, risk assessment, safety and testing, and enforcement. Each record contains the verbatim text, the "
      "article or section, PDF and printed page references, the duty-holder in the source's own terminology, the "
      "enforcement route with cross-references, and dated implementation evidence. "
      + (f"The principal instruments contribute {num(core_per_fw['EU'])} provisions each; the later instruments add "
         f"{num(len(later))} more. " if len(set(core_per_fw.values())) == 1 and later else "")
      + "The counts support structured description but do not imply that the frameworks are of equal scope or that the "
      "sample represents each framework as a whole.")
    P("Coding followed a written framework that defines each category and its decision rules, including the rule that "
      "aspirational language is not coded as a mandatory obligation and that a sanction located elsewhere in an "
      "instrument is recorded as cross-referenced rather than direct. Obligation force (mandatory, recommended, voluntary "
      "or not specified) is coded separately from obligation nature (institutional, procedural, substantive, reporting "
      "or other), so that a provision assigning a task to an institution is not mistaken for a weaker form of duty. "
      "Duty-holders and enforcement mechanisms were then "
      "normalised into standard categories, allowing a provision to belong to more than one. A structured audit checked "
      "identifiers, missing values and category distributions, and a source-validation register links every record to "
      "its official publication.")
    meta = atlas.meta
    if meta.get("audit_checks"):
        v = meta["audit_verdicts"]
        corrected = v.get("Corrected", 0)
        caveat = v.get("Verified with caveat", 0)
        signed = meta["corrections_decided"]
        total = meta["corrections"]
        in_data = meta["corrections_in_dataset"]
        if total and in_data == total:
            applied = (f"; all {total} corrections have been made in the dataset analysed here and are logged in a "
                       "correction register so that each can be formally signed off with a recorded reason")
        elif total:
            applied = (f"; {in_data} of the {total} logged corrections match the dataset analysed here, and the "
                       "correction register records each for formal sign-off")
        else:
            applied = ""
        if total and signed < total:
            signoff = (f". At the time of generation, {'none' if signed == 0 else f'{signed} of the {total}'} "
                       "had been signed off by a reviewer")
        elif total:
            signoff = ". All corrections had been signed off at the time of generation"
        else:
            signoff = ""
        P(f"Every record was then checked against its primary source. The verification audit comprises "
          f"{meta['audit_checks']} field-level checks across {meta['audit_fields']} coded fields: "
          f"{v.get('Verified', 0)} were verified as recorded, {corrected} led to a correction"
          + (f" and {caveat} were verified with a caveat" if caveat else "") +
          applied + signoff + ". " + corrections_scope_sentence(meta))
    rel = {r["field"]: r for r in meta.get("reliability", [])}
    if rel:
        def kfmt(field):
            r = rel.get(field, {})
            return f"κ = {float(r['cohens_kappa']):.2f}" if r.get("cohens_kappa") else "n/a"
        weakest = min((r for r in rel.values() if r.get("cohens_kappa")), key=lambda r: float(r["cohens_kappa"]))
        coder = rel[next(iter(rel))]["second_coder"]
        nat = rel.get("obligation_nature", {})
        P(f"Coding reliability was checked with a blind second coding of all {rel[next(iter(rel))]['n']} provisions. "
          + ("The second coder was an AI agent that saw only each provision's text, location and instrument together with "
             "the written coding framework, and never the primary codes; the check is therefore reported as AI-assisted and "
             "is not a substitute for an independent human coder. " if coder != "human" else
             "The second coder worked from the written framework without access to the primary codes. ") +
          f"Agreement was {kfmt('legal_status')} for legal force, {kfmt('governance_dimension')} for the primary "
          f"dimension, {kfmt('obligation_force')} for obligation force and {kfmt('enforcement_linkage')} for enforcement "
          f"linkage (Cohen's kappa), with {nat.get('percent_agreement', 'n/a')}% exact agreement on the multi-label "
          f"obligation nature. The weakest agreement, on {weakest['variable'].lower()}, concentrated on the boundary "
          "between provisions that organise enforcement through existing bodies and provisions that create no compliance "
          "duty at all, which the framework's definitions do not fully separate.")
    H2("3.3 Computational indicators")
    P("To complement the manual coding, the full text of each instrument was extracted page by page and searched for "
      "dimension-related keyword families, with counts normalised per 1,000 words. The extracted EU text is the "
      f"consolidated version without recitals ({kw_words('EU'):,} words), compared with {kw_words('India'):,} words for "
      f"India, {kw_words('UK'):,} for the UK and {kw_words('OECD (international benchmark)'):,} for the OECD. Keyword "
      "frequencies are treated strictly as descriptive indicators of emphasis in drafting. They cannot show whether a "
      "term creates an obligation, and they are sensitive to vocabulary that is specific to one instrument.")

    # ---------------- 4 Findings ----------------
    H1("4. Findings")
    H2("4.1 Legal force and obligation force")
    nonmand_parts = [f"recommendations ({len(recommended)})"]
    if voluntary:
        nonmand_parts.append(f"voluntary undertakings by the issuing government ({len(voluntary)})")
    if unspecified:
        nonmand_parts.append(f"statements of no specified force ({len(unspecified)})")
    bind_mand = [r for r in mandatory if r["legal_status"].startswith("Binding")]
    P(f"Table 2 summarises the translation profile of each framework. The sharpest division is in obligation force. "
      f"{Num(len(bind_mand))} of the {num(len(mandatory))} mandatory provisions come from binding instruments: "
      + join([f"{of(sum(r['country'] == f for r in bind_mand), per_fw[f] if f != 'India' else len(india_binding))} "
              + ("EU provisions" if f == "EU" else "of India's 2026 intermediary-rule provisions" if f == "India" else f"{ad.SHORT[f]} provisions")
              for f in sorted({r['country'] for r in bind_mand}, key=FW.index)])
      + ". "
      + (f"{Num(len(mand_nonbinding))} {plural(len(mand_nonbinding), 'is', 'are')} mandatory only within a non-binding "
         f"instrument ({ids(mand_nonbinding)}): "
         + " ".join(first_sentence(r['provision_summary'])[0].upper() + first_sentence(r['provision_summary'])[1:] + "."
                    for r in mand_nonbinding)
         + f" {plural(len(mand_nonbinding), 'It binds', 'They bind')} no state or AI actor. " if mand_nonbinding else "")
      + f"The remaining {n - len(mandatory)} provisions are " + join(nonmand_parts) + ".")
    blocks.append(("table_profile", None))
    P("The difference is not simply that some instruments are statutes. The UK and Indian guideline provisions are "
      "frequently precise about what good practice looks like: the UK transparency principle (UK001) describes "
      "proportionate explainability in some detail, and the India Guidelines recommend transparency reports assessing "
      "risks of harm in the Indian context (IND001). What they lack is the grammar of obligation: an addressee who must "
      "act and a consequence if it does not. Conversely, the EU provisions are written in the passive voice, and their "
      "duty-holder is established only by reading them with Article 16, which obliges providers to ensure compliance with "
      "the requirements of Chapter III, Section 2."
      + (" India's 2026 rules supply the grammar of obligation in a narrower field: intermediaries 'shall' label synthetic "
         "content and preserve its provenance metadata, and the consequence of non-observance is stated in the rules "
         "themselves." if india_binding else "")
      + " Obligation force therefore depends on the architecture of the instrument as well as on the wording of a single "
      "provision.")

    H2("4.2 Who is obliged? The addressees of governance")
    ind_guid = [r for r in by["India"] if not r["legal_status"].startswith("Binding")]
    ind_guid_pub = sum(addressed_public(r) for r in ind_guid)
    P(f"Figure {fig_n['addr']} shows the actors to whom each framework's provisions are addressed. In the EU sample, "
      f"{of(priv['EU'], per_fw['EU'])} provisions place duties on private actors (providers, and in EU004 also "
      f"deployers) and {num(pub['EU'])} address public bodies. The UK pattern is close to the reverse: regulators appear "
      f"in {of(sum('Regulator' in r['responsibility_categories'] for r in by['UK']), per_fw['UK'])} UK provisions, "
      f"and {num(public_only['UK'])} {plural(public_only['UK'], 'provision is', 'provisions are')} addressed to public "
      "bodies alone. "
      + (f"India's sample contains both patterns. {Num(ind_guid_pub)} of its {num(len(ind_guid))} Guidelines provisions "
         "are addressed to government, regulators or new institutions such as the AI Safety Institute and the AI "
         f"Governance Group, whereas its {num(len(india_binding))} intermediary-rule provisions place duties on online "
         "intermediaries." if india_binding else
         f"India's sample is the most institutionally oriented, with {of(pub['India'], per_fw['India'])} provisions "
         "addressed to government, regulators or new institutions such as the AI Safety Institute and the AI Governance "
         "Group.")
      + f" Across the whole sample, {of(binding_private, len(binding))} binding provisions address private actors, while "
      f"{num(nonbinding_public)} of the {num(len(nonbinding))} non-binding provisions address public bodies.")
    blocks.append(("figure", figs["addr"],
                   f"Figure {fig_n['addr']}. Duty-holders named in the coded provisions, by framework. Cells show the "
                   "number of provisions that address each actor category; a provision can address more than one. "
                   "Darker cells indicate more provisions."))
    P("This difference matters for the translation chain. A principle addressed to a regulator is translated into conduct "
      "only after a second step, when the regulator issues guidance, rules or decisions of its own. A principle addressed "
      "to a provider or an intermediary skips that step. Non-statutory provisions are therefore not merely softer "
      "versions of statutory ones; they are structured as instructions to the state about how to govern, with obligations "
      "on industry left to existing sectoral law or to a later stage. The OECD benchmark sits between the two: it "
      f"addresses AI actors generally in {num(priv['OECD (international benchmark)'])} of its "
      f"{num(per_fw['OECD (international benchmark)'])} provisions, but only through recommendations to adhering "
      "governments.")

    H2("4.3 Enforcement linkage")
    eu_cross = [r for r in crossref if r["country"] == "EU"]
    other_linked = [r for r in linked if r["country"] != "EU"]
    P(f"Figure {fig_n['enf']} reports the enforcement linkage of each provision. {Num(len(linked))} of the {n} provisions "
      f"have a compliance route that is either named in the provision or attached to it by cross-reference. "
      f"{Num(len(eu_cross))} of these are EU provisions, each linked through Article 16 to administrative fines under "
      f"Article 99, supported by conformity assessment and market surveillance"
      + (f"; EU004 additionally links deployer duties to fines through Article 26" if any(r['id'] == 'EU004' and len(r['enforcement_mechanisms']) > 1 for r in by['EU']) else "")
      + ".")
    blocks.append(("figure", figs["enf"],
                   f"Figure {fig_n['enf']}. Enforcement linkage of coded provisions, by framework. Cross-referenced: "
                   "duty linked to statutory sanctions elsewhere in the instrument. System-level only: reliance on the "
                   "general powers of existing bodies. Direct: mechanism named in the provision. Not applicable "
                   "(hatched): institution-building rather than a compliance duty."))
    statutory_other = [r for r in other_linked if r["mechanism_character"] == "Statutory enforcement"]
    soft_other = [r for r in other_linked if r["mechanism_character"] != "Statutory enforcement"]
    P("Outside the EU, the compliance routes differ in kind. "
      + (f"India's 2026 intermediary rules create a statutory route ({ids(statutory_other)}): an intermediary that fails "
         "to observe the rules loses its exemption from liability for third-party content under section 79(1) of the "
         "Information Technology Act, 2000. The sanction is the withdrawal of a legal protection rather than a fine, which "
         "makes compliance a condition of the intermediary's business model. " if statutory_other else "")
      + (" ".join(f"{r['id']} ({ad.SHORT[r['country']]}) relies on {join([m.lower() for m in r['enforcement_mechanisms']])}"
                  + (", a soft-accountability route with no sanction" if r["mechanism_character"] == "Soft accountability" else "")
                  + "." for r in soft_other) + " " if soft_other else "")
      + f"Elsewhere outside the EU, the most common outcome is reliance on system-level powers "
      f"({num(sum(r['country'] != 'EU' for r in system))} {plural(sum(r['country'] != 'EU' for r in system), 'provision')}) "
      f"or no identified route ({num(sum(r['country'] != 'EU' for r in none_))}). "
      f"{Num(len(na))} {plural(len(na), 'provision is', 'provisions are')} coded as not applicable because "
      f"{plural(len(na), 'it creates', 'they create')} institutional functions, such as the UK's cross-sectoral risk "
      "assessment function and India's planned risk classification framework, rather than compliance duties.")
    P("System-level reliance should not be read as an absence of enforcement. The UK model deliberately routes enforcement "
      "through regulators that already hold statutory powers, and India's Guidelines assign enforcement to sectoral bodies "
      "such as financial and telecommunications regulators. The point is that the link between a specific AI principle and "
      "a specific sanction is indirect: it depends on whether a sector regulator's existing mandate covers the conduct, "
      "and on that regulator choosing to act. For the OECD benchmark, the only follow-up mechanism in the sample is "
      "reporting by the Digital Policy Committee to the OECD Council, which monitors implementation but does not enforce it.")

    H2("4.4 Implementation evidence")
    implemented = [r for r in R if r["implementation_status"] == "Implemented"]
    P(f"Figure {fig_n['imp']} reports the implementation evidence recorded for each provision. "
      f"{of(per_fw['EU'] - imp['EU']['Not assessed'], per_fw['EU']).capitalize()} EU provisions "
      "has an implementation assessment, because their obligations were adopted but not yet applicable during the "
      "research period; harmonised standards and the deferred application dates mean that compliance cannot yet be "
      f"observed. By contrast, {of(len(evidenced['UK']), per_fw['UK'])} UK provisions show at least partial "
      "implementation, documented mainly through the government's 2024 response and regulators' published strategic "
      f"approaches, and {of(len(evidenced['India']), per_fw['India'])} Indian provisions show at least partial "
      "implementation, chiefly through institutional steps such as the creation of the IndiaAI Safety Institute"
      + (f" and, for {ids([r for r in india_in_force if r in evidenced['India']])}, the entry into force of the "
         "intermediary rules on 20 February 2026"
         if any(r in evidenced['India'] for r in india_in_force) else "")
      + "." + (f" {Num(len(implemented))} {plural(len(implemented), 'provision is', 'provisions are')} coded as fully "
               f"implemented ({ids(implemented)})." if implemented else ""))
    blocks.append(("figure", figs["imp"],
                   f"Figure {fig_n['imp']}. Implementation evidence recorded for coded provisions, by framework. "
                   "Outlined segments are provisions not assessed, which is not a finding of non-implementation."))
    ind_gap = [r for r in ind_guid if r["implementation_status"] in ("Not yet implemented", "No evidence of implementation found")]
    P("Measures addressed to the state, such as creating an institution or publishing guidance, can be implemented quickly "
      "and documented in official sources. The EU shows that measures addressed to industry under a new horizontal statute "
      "may need standards, designated authorities and transition periods before they bite. "
      + ("India's intermediary rules show the opposite case: a targeted duty attached to an existing due-diligence regime, "
         "with an established sanction, took effect ten days after notification. The speed of implementation therefore "
         "depends less on whether a duty is binding than on whether it can be attached to legal machinery that already "
         "exists. " if india_in_force else "")
      + (f"Where Indian Guidelines measures depend on industry or on new legal obligations ({ids(ind_gap)}), the recorded "
         "evidence is weakest. " if ind_gap else "")
      + "Implementation evidence also needs to be read alongside the addressee of each duty: early implementation of "
      "institution-building provisions does not show that private conduct has changed, and entry into force does not show "
      "compliance.")

    H2("4.5 Principle by principle")
    P("Reading the sample by governance dimension shows how the same principle takes different regulatory forms. For each "
      "dimension, the provisions are grouped below by obligation force, with an example of its strongest form.")
    force_rank = {"Mandatory": 0, "Recommended": 1, "Voluntary": 2, "Not specified": 3}
    for dim in ad.DIMENSIONS:
        recs = [r for r in R if r["governance_dimension"] == dim]
        if not recs:
            continue
        groups = []
        for force in ad.OBLIGATION_TYPES:
            members = [r for r in recs if r["obligation_type"] == force]
            if members:
                fws = sorted({r["country"] for r in members}, key=FW.index)
                groups.append(f"{force.lower()} in {names(fws)} ({ids(members)})")
        ranked = sorted(recs, key=lambda r: force_rank.get(r["obligation_type"], 9))
        strong = ranked[0]
        text = (f"<i>{dim}</i> ({num(len(recs))} {plural(len(recs), 'provision')}) is " + "; ".join(groups) + ". ")
        text += f"In its strongest form, in {name(strong['country'])} ({strong['id']}), {first_sentence(strong['provision_summary'])}."
        missing = [f for f in FW if f not in {r["country"] for r in recs}]
        if missing:
            text += (f" No provision from {names(missing)} is coded primarily under this dimension"
                     + (", because EU enforcement attaches to duties by cross-reference" if dim == "Enforcement" and "EU" in missing else "")
                     + "; this reflects the selection of provisions, not the content of the framework.")
        P(text)

    H2("4.6 Computational indicators")
    P(f"Figure {fig_n['kw']} reports keyword frequencies. The EU text has the highest density of risk-assessment vocabulary "
      f"({kwv('EU', 'Risk Assessment'):.1f} occurrences per 1,000 words) and of enforcement vocabulary ({eu_enf_kw:.1f}), "
      f"consistent with its compliance architecture"
      + ("" if max_enf_fw == "EU" else f", although {name(max_enf_fw)} has a higher enforcement-term density") +
      ". "
      + (f"Both the India and UK texts are dominated by {top_dim['India'].lower()} vocabulary"
         if top_dim['India'] == top_dim['UK'] else
         f"The India and UK texts are dominated by {top_dim['India'].lower()} and {top_dim['UK'].lower()} vocabulary respectively")
      + ", and the OECD Recommendation contains no enforcement terms at all.")
    blocks.append(("figure", figs["kw"],
                   f"Figure {fig_n['kw']}. Frequency of dimension-related keyword families per 1,000 words in the full "
                   "text of each instrument. The EU figure uses the consolidated text without recitals. Frequencies "
                   "indicate drafting emphasis, not legal effect."))
    P("These indicators agree with the manual coding at the level of broad emphasis, but they also show the limits of "
      "lexical methods. Part of the EU's risk-assessment score reflects the term 'high-risk', which is a defined category "
      "in the Act rather than evidence of a risk-assessment duty, and the accountability scores for India and the UK are "
      "inflated by general uses of 'responsible'. Keyword density measures how often a framework talks about a principle; "
      "only provision-level reading establishes whether it turns that principle into a duty."
      + (" The keyword corpus covers the principal instrument of each framework only; the later instruments are analysed "
         "through provision-level coding alone." if later_docs else ""))

    # ---------------- 5 Discussion ----------------
    H1("5. Discussion")
    P("The comparison supports three observations about how AI principles are translated into governance.")
    P("First, the frameworks share principles but differ in where the chain of translation runs. The OECD benchmark, the UK "
      "principles and the India sutras all recognise transparency, accountability and safety, and the EU requirements "
      "operationalise the same values. The decisive differences lie further down the chain: in obligation force, in the "
      "addressee of the duty and in the presence of a provision-specific route to a sanction. Comparisons that stop at the "
      "level of principles will therefore overstate convergence, a point consistent with the observation that consensus on "
      "high-level values can conceal deep disagreement about implementation (Mittelstadt, 2019).")
    P("Second, the non-statutory frameworks are best understood as delegations of translation rather than as weaker "
      "statements of obligation. The UK framework asks regulators to interpret and apply cross-cutting principles within "
      "their remits; the India Guidelines ask ministries, sectoral regulators and new coordinating bodies to clarify how "
      "existing law applies to actors in the AI value chain and to develop risk frameworks. In both, the step that turns a "
      "principle into a duty on industry is postponed and distributed. This preserves flexibility and avoids premature "
      "rules for a fast-moving technology, but it makes outcomes depend on regulators' capacity, mandates and willingness "
      "to act, and it can leave gaps where conduct falls between sectors."
      + (" India's 2026 rules show what can follow such delegation: when a specific harm, synthetic media, became "
         "salient, binding duties were attached to an existing legal hook, intermediary due diligence, rather than enacted "
         "in a horizontal AI statute." if india_binding else "")
      + (" The UK's 2024 response points the same way, anticipating targeted mandatory interventions for highly capable "
         "general-purpose systems while relying on voluntary measures for now." if any(r["id"] == "UK007" for r in R) else ""))
    P("Third, legal enforceability and early implementation pulled in opposite directions during the research period. The "
      "EU has the most complete chain on paper, with mandatory duties, named duty-holders and cross-referenced sanctions, but "
      "its high-risk obligations had not yet become applicable, and their entry into application was deferred by the "
      "2026 amendment. Commentators had already questioned whether parts of the Act's enforcement design would achieve their "
      "aims (Veale and Zuiderveen Borgesius, 2021). The UK and India show more documented implementation, but mostly of "
      "measures addressed to the state"
      + ("; the exception, India's intermediary rules, combines binding force with rapid entry into force because it "
         "extends an existing regime" if india_in_force else "") + ". Neither pattern establishes which approach will better protect people affected by AI; "
      "they show that enforceability and implementation must be assessed separately and over time.")
    weak_link = []
    for f in juris:
        # Where a framework mixes binding and non-binding instruments, judge the
        # weakest link on its non-binding (guidance or policy) provisions.
        recs_f = by[f]
        mixed = any(r["legal_status"].startswith("Binding") for r in recs_f) and any(
            not r["legal_status"].startswith("Binding") for r in recs_f)
        if mixed:
            recs_f = [r for r in recs_f if not r["legal_status"].startswith("Binding")]
        e = {lvl: sum(r["enforcement_level"] == lvl for r in recs_f) for lvl in ad.ENFORCEMENT_LEVELS}
        i = {lvl: sum(r["implementation_status"] == lvl for r in recs_f) for lvl in ad.IMPLEMENTATION_LEVELS}
        label = (f"{name(f)}'s Guidelines" if f == "India" else f"{name(f)}'s non-statutory provisions") if mixed else name(f)
        if e["Cross-referenced"] + e["Direct"] == len(recs_f) and i["Not assessed"] == len(recs_f):
            weak_link.append(f"For {label}, whose sampled duties are fully linked to enforcement but not yet "
                             "applicable, the weakest link is implementation: the priority is timely harmonised standards, "
                             "designated authorities and early reporting on conformity assessment and market surveillance.")
        elif e["System-level only"] >= max(e["None identified"], 1):
            weak_link.append(f"For {label}, where most sampled provisions rely on the general powers of existing "
                             "regulators, the weakest link is the connection between principle and sanction: a public map "
                             "of which regulator's powers cover which principle, and a statement of how gaps between "
                             "sectors are handled, would make that link visible.")
        else:
            weak_link.append(f"For {label}, where several sampled provisions have no identified enforcement route, "
                             "the weakest link is the duty-holder: the recommended clarification of obligations across the "
                             "AI value chain is the step on which the rest of the chain depends, and a published timetable "
                             "for it would allow progress to be tracked.")
    P("The coding also indicates where each framework's chain is weakest. " + " ".join(weak_link) +
      " These are inferences from a small sample and are offered as hypotheses for fuller study rather than as "
      "evaluations of the frameworks.")
    P("For researchers, the implication is methodological. Coding legal force, obligation force, duty-holder, enforcement "
      "linkage and implementation as separate variables reveals patterns that a single measure of regulatory strength "
      "would hide. For policymakers, the comparison suggests that the credibility of a principles-based approach depends on "
      "the second step of translation, which deserves the same transparency and monitoring as the principles themselves.")

    # ---------------- 6 Limitations ----------------
    H1("6. Limitations")
    rel_note = ("The coding was carried out by a single researcher under a written framework, and the reliability check "
                "used an AI second coder rather than a trained human coder; agreement with a human second coder remains to "
                "be measured." if rel and rel[next(iter(rel))]["second_coder"] != "human" else
                "The coding was carried out by a single researcher under a written framework"
                + ("." if rel else "; inter-coder reliability has not yet been measured."))
    P(f"The study has important limitations. The sample of {n} provisions is purposive"
      + (f", with {num(core_per_fw['EU'])} provisions from each principal instrument" if len(set(core_per_fw.values())) == 1 else "")
      + ", and supports structured comparison, not statistical generalisation. A provision absent from the sample may exist "
      "elsewhere in a framework, and a fuller sample could change the patterns observed. " + rel_note)
    P("The instruments also differ in date, length, legal character and purpose. Later developments are outside the coded "
      "versions or the sample, including " + "; ".join(OUT_OF_SAMPLE[:-1]) + "; and " + OUT_OF_SAMPLE[-1] + ". Such developments may change the binding status "
      "or practical effect of parts of a framework. Implementation evidence depends on what official sources publish "
      "and was assessed at a single point in time."
      + (f" The provisions added from later instruments ({ids(later)}) were checked against the official texts at rule "
         "or paragraph level, but their page references and quotations have yet to be re-checked against downloaded copies."
         if later else "")
      + " Finally, the computational indicators are sensitive to extraction "
      "quality and instrument-specific vocabulary and should be read only as descriptive context.")

    # ---------------- 7 Conclusion ----------------
    H1("7. Conclusion")
    P("AI governance principles are widely shared; their translation into enforceable obligations is not. In this "
      f"provision-level comparison, binding duties and statutory sanctions were confined to {names(sanction_fw) or 'none of the frameworks'}"
      + (", and in India to targeted intermediary rules on synthetic content; India's Guidelines and the UK framework relied "
         "on regulators, institutions and existing law to complete the translation, and the OECD benchmark relied on "
         "reporting." if india_binding else
         ", while the UK and India relied on regulators, institutions and existing law to complete the translation, and the "
         "OECD benchmark relied on reporting.")
      + " The most informative differences lay not in which principles each framework "
      "endorses but in who is obliged to act, whether a route to enforcement attaches to the duty, and whether evidence "
      "shows the measure in operation. Tracing those links, provision by provision, offers a more precise basis for "
      "comparing AI governance than counting principles, and a clearer view of where the gap between principle and "
      "practice actually lies.")

    # ---------------- Data availability ----------------
    H1("Data and code availability")
    P("The coded dataset, source PDFs, analysis scripts and the generator for this manuscript are available in the AI "
      "Governance Atlas repository. All figures and counts in this paper are produced from the dataset by "
      "<i>run_pipeline.py</i>; re-running the pipeline regenerates the manuscript. The generated text is a data-driven "
      "draft: legal statements should be checked against the primary sources cited below before publication.")

    blocks.append(("references", None))
    blocks.append(("appendix", None))
    return blocks


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------
def table_sources(atlas):
    rows = [["Framework", "Instrument", "Version coded", "Legal status", "Provisions"]]
    for doc, src in atlas.sources.items():
        version = src["version_used"]
        if len(version) > 160:  # keep long version notes readable in the table
            version = version[:157].rsplit(" ", 1)[0] + " …"
        rows.append([ad.SHORT[src["framework"]], doc, version, src["legal_status"], str(src["n_provisions"])])
    return rows, "Table 1. Instruments and versions coded. The first instrument listed for each framework is its principal instrument."


def table_profile(atlas):
    obl = atlas.crosstab("obligation_type", ad.OBLIGATION_TYPES)
    enf = atlas.crosstab("enforcement_level", ad.ENFORCEMENT_LEVELS)
    rows = [["", "Total", "Binding", "Mand.", "Rec.", "Vol. or n.s.", "Route †", "System level", "Evidence ‡"]]
    for fw in ad.FRAMEWORKS:
        recs = atlas.by_framework(fw)
        ev = sum(r["implementation_status"] in ("Implemented", "Partially implemented") for r in recs)
        bind = sum(r["legal_status"].startswith("Binding") for r in recs)
        rows.append([ad.SHORT[fw], str(len(recs)), str(bind), str(obl[fw]["Mandatory"]), str(obl[fw]["Recommended"]),
                     str(obl[fw]["Voluntary"] + obl[fw]["Not specified"]),
                     str(enf[fw]["Cross-referenced"] + enf[fw]["Direct"]),
                     str(enf[fw]["System-level only"]), str(ev)])
    note = ("Table 2. Translation profile by framework (number of coded provisions). Binding: from a binding instrument. "
            "Mand., Rec., Vol. or n.s.: obligation force mandatory, recommended, voluntary or not specified. "
            "† Direct or cross-referenced enforcement linkage. System level: system-level enforcement only. "
            "‡ Implemented or partially implemented.")
    return rows, note


def table_appendix(atlas):
    rows = [["ID", "Provision", "Dimension", "Obligation", "Enforcement linkage", "Implementation"]]
    for r in atlas.records:
        rows.append([r["id"], r["article_or_section"], r["governance_dimension"], r["obligation_type"],
                     r["enforcement_level"], r["implementation_status"].replace("No evidence of implementation found", "No evidence found")])
    return rows, "Table A1. The coded provisions."


def primary_references(atlas):
    refs = []
    for doc, src in atlas.sources.items():
        url = re.search(r"https?://\S+", src["source_reference"])
        refs.append(f"{doc}. Version coded: {src['version_used']}" + ("" if src["version_used"].endswith(".") else ".")
                    + (f" Available at: {url.group(0).rstrip(';,')}" if url else ""))
    return refs


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------
def render_markdown(blocks, atlas) -> str:
    out = []
    for b in blocks:
        kind = b[0]
        if kind == "title":
            out.append(f"# {b[1]}\n")
        elif kind in ("byline", "date"):
            out.append(f"*{b[1]}*\n")
        elif kind == "abstract":
            out.append(f"**Abstract.** {b[1]}\n")
        elif kind == "keywords":
            out.append(f"*{b[1]}*\n")
        elif kind == "h1":
            out.append(f"## {b[1]}\n")
        elif kind == "h2":
            out.append(f"### {b[1]}\n")
        elif kind == "p":
            out.append(re.sub(r"</?b>", "**", re.sub(r"</?i>", "*", b[1])) + "\n")
        elif kind == "figure":
            out.append(f"![{b[2]}](figures/{Path(b[1]).name})\n\n*{b[2]}*\n")
        elif kind in ("table_sources", "table_profile"):
            rows, cap = (table_sources if kind == "table_sources" else table_profile)(atlas)
            out.append(f"*{cap}*\n")
            out.append(_md_table(rows))
        elif kind == "references":
            out.append("## References\n")
            out.append("### Primary sources\n")
            out += [f"- {r}" for r in primary_references(atlas)]
            out.append("\n### Literature\n")
            out += [f"- {r}" for r in LITERATURE]
            out.append("")
        elif kind == "appendix":
            rows, cap = table_appendix(atlas)
            out.append("## Appendix\n")
            out.append(f"*{cap}*\n")
            out.append(_md_table(rows))
    return "\n".join(out)


def _md_table(rows):
    lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * len(rows[0])]
    lines += ["| " + " | ".join(c.replace("|", "/") for c in r) + " |" for r in rows[1:]]
    return "\n".join(lines) + "\n"


def render_pdf(blocks, atlas, path: Path, author: str):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,
                                    SimpleDocTemplate, Spacer, Table, TableStyle)

    base = dict(fontName="Times-Roman", fontSize=10.5, leading=14.2, textColor=colors.HexColor(TEXT))
    S = {
        "title": ParagraphStyle("title", fontName="Times-Bold", fontSize=16, leading=20, alignment=TA_CENTER,
                                spaceAfter=10, textColor=colors.HexColor(TEXT)),
        "byline": ParagraphStyle("byline", **{**base, "alignment": TA_CENTER, "fontSize": 11}),
        "date": ParagraphStyle("date", **{**base, "alignment": TA_CENTER, "fontSize": 8.5,
                                          "textColor": colors.HexColor(TEXT_2), "spaceAfter": 14}),
        "abstract": ParagraphStyle("abstract", **{**base, "fontSize": 9.5, "leading": 12.8, "alignment": TA_JUSTIFY,
                                                  "leftIndent": 1.0 * cm, "rightIndent": 1.0 * cm, "spaceAfter": 6}),
        "keywords": ParagraphStyle("keywords", **{**base, "fontName": "Times-Italic", "fontSize": 9,
                                                  "leftIndent": 1.0 * cm, "rightIndent": 1.0 * cm, "spaceAfter": 12}),
        "h1": ParagraphStyle("h1", fontName="Times-Bold", fontSize=12.5, leading=16, spaceBefore=12, spaceAfter=5,
                             textColor=colors.HexColor(TEXT)),
        "h2": ParagraphStyle("h2", fontName="Times-BoldItalic", fontSize=11, leading=14, spaceBefore=8, spaceAfter=3,
                             textColor=colors.HexColor(TEXT)),
        "p": ParagraphStyle("p", **{**base, "alignment": TA_JUSTIFY, "spaceAfter": 6, "firstLineIndent": 0.5 * cm}),
        "cap": ParagraphStyle("cap", **{**base, "fontSize": 8.5, "leading": 11, "textColor": colors.HexColor(TEXT_2),
                                        "spaceBefore": 3, "spaceAfter": 10}),
        "cell": ParagraphStyle("cell", **{**base, "fontSize": 7.8, "leading": 9.6}),
        "cellh": ParagraphStyle("cellh", **{**base, "fontName": "Times-Bold", "fontSize": 7.8, "leading": 9.6}),
        "ref": ParagraphStyle("ref", **{**base, "fontSize": 9, "leading": 11.8, "leftIndent": 0.6 * cm,
                                        "firstLineIndent": -0.6 * cm, "spaceAfter": 4}),
    }
    width = A4[0] - 5.0 * cm

    def tbl(rows, col_fracs, caption, keep=True, pad=2.5):
        data = [[Paragraph(escape(c), S["cellh" if i == 0 else "cell"]) for c in row] for i, row in enumerate(rows)]
        t = Table(data, colWidths=[f * width for f in col_fracs], repeatRows=1)
        t.setStyle(TableStyle([
            ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.HexColor(TEXT)),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor(TEXT)),
            ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.HexColor(TEXT)),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), pad),
            ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f6f6")]),
        ]))
        if keep:
            return [KeepTogether([Paragraph(escape(caption), S["cap"]), t]), Spacer(1, 10)]
        return [Paragraph(escape(caption), S["cap"]), t, Spacer(1, 10)]

    story = []
    for b in blocks:
        kind = b[0]
        if kind in ("title", "byline", "date", "h1", "h2", "keywords"):
            story.append(Paragraph(escape(b[1]), S[kind]))
        elif kind == "abstract":
            story.append(Paragraph("<b>Abstract.</b> " + escape(b[1]), S["abstract"]))
        elif kind == "p":
            # Allow only <b> and <i> markup from the content builder
            safe = escape(b[1]).replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>") \
                               .replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
            story.append(Paragraph(safe, S["p"]))
        elif kind == "figure":
            img = Image(str(b[1]))
            scale = width / img.imageWidth
            img.drawWidth, img.drawHeight = width, img.imageHeight * scale
            story.append(KeepTogether([img, Paragraph(escape(b[2]), S["cap"])]))
        elif kind == "table_sources":
            rows, cap = table_sources(atlas)
            story += tbl(rows, [0.09, 0.36, 0.30, 0.15, 0.10], cap)
        elif kind == "table_profile":
            rows, cap = table_profile(atlas)
            story += tbl(rows, [0.10, 0.10, 0.10, 0.10, 0.12, 0.12, 0.12, 0.11, 0.13], cap)
        elif kind == "references":
            story.append(Paragraph("References", S["h1"]))
            story.append(Paragraph("<i>Primary sources</i>", S["h2"]))
            story += [Paragraph(escape(r), S["ref"]) for r in primary_references(atlas)]
            story.append(Paragraph("<i>Literature</i>", S["h2"]))
            story += [Paragraph(escape(r), S["ref"]) for r in LITERATURE]
        elif kind == "appendix":
            story.append(PageBreak())
            story.append(Paragraph("Appendix", S["h1"]))
            rows, cap = table_appendix(atlas)
            story += tbl(rows, [0.10, 0.35, 0.13, 0.12, 0.16, 0.14], cap, keep=False, pad=1.6)

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Times-Roman", 8)
        canvas.setFillColor(colors.HexColor(TEXT_2))
        canvas.drawString(2.5 * cm, 1.3 * cm, "AI Governance Atlas")
        canvas.drawRightString(A4[0] - 2.5 * cm, 1.3 * cm, str(doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=2.5 * cm, rightMargin=2.5 * cm,
                            topMargin=2.3 * cm, bottomMargin=2.2 * cm, title=TITLE, author=author,
                            subject="AI governance comparative analysis", creator="AI Governance Atlas paper generator")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the AI Governance Atlas paper as PDF.")
    parser.add_argument("--author", default="Suzzan Patel", help="Author name for the title page")
    parser.add_argument("--affiliation", default="", help="Author affiliation (optional)")
    parser.add_argument("--no-word-check", action="store_true",
                        help="Do not fail when the main text falls outside the target word range")
    args = parser.parse_args()

    atlas = ad.load()
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    figs = {
        "addr": FIG_DIR / "fig1_duty_holders.png",
        "enf": FIG_DIR / "fig2_enforcement_linkage.png",
        "imp": FIG_DIR / "fig3_implementation_evidence.png",
        "kw": FIG_DIR / "fig4_keyword_frequencies.png",
    }
    fig_enforcement(atlas, figs["enf"])
    fig_addressees(atlas, figs["addr"])
    fig_implementation(atlas, figs["imp"])
    fig_keywords(atlas, figs["kw"])

    blocks = build_content(atlas, args.author, args.affiliation, figs)

    # Main text = abstract through conclusion (excludes title page, captions,
    # tables, data statement, references and appendix), as journals count it.
    main_words, in_main = 0, False
    for b in blocks:
        if b[0] == "abstract":
            in_main = True
        if b[0] == "h1" and b[1].startswith("Data and code"):
            in_main = False
        if in_main and b[0] in ("abstract", "h1", "h2", "p"):
            main_words += word_count(b[1])

    md = render_markdown(blocks, atlas)
    total_words = word_count(md)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MD_PATH.write_text(md, encoding="utf-8")
    render_pdf(blocks, atlas, PDF_PATH, args.author)

    lo, hi = int(TARGET_WORDS * (1 - TOLERANCE)), int(TARGET_WORDS * (1 + TOLERANCE))
    COUNT_PATH.write_text(
        f"Main text (abstract to conclusion): {main_words} words\n"
        f"Whole document incl. tables, captions, references, appendix: {total_words} words\n"
        f"Target: {TARGET_WORDS} words (accepted range {lo}-{hi})\n", encoding="utf-8")

    print("PAPER GENERATED")
    print(f"  PDF:      {PDF_PATH.relative_to(ad.ROOT)}")
    print(f"  Markdown: {MD_PATH.relative_to(ad.ROOT)}")
    print(f"  Main text: {main_words} words (target {TARGET_WORDS}, range {lo}-{hi}); whole document {total_words}")
    if not (lo <= main_words <= hi) and not args.no_word_check:
        raise SystemExit(f"Main text is {main_words} words, outside {lo}-{hi}. "
                         "Adjust the content or run with --no-word-check.")


if __name__ == "__main__":
    main()
