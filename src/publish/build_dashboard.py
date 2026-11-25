"""Build the AI Governance Atlas interactive dashboard as one self-contained HTML file.

The dashboard reads the same data layer as the paper (atlas_data.py), so its
figures always agree with the manuscript. The output is a single HTML file
with the data embedded: no server, internet connection or external library is
needed. Open it in any modern browser.

Output: results/dashboard/index.html

Views
    Overview      headline figures, enforcement linkage, implementation evidence, duty-holders
    Explorer      every coded provision, with filters and a full detail panel
    Indicators    keyword frequencies per 1,000 words (descriptive only)

Usage:
    python src/publish/build_dashboard.py
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import atlas_data as ad  # noqa: E402

OUT_DIR = ad.ROOT / "results" / "dashboard"
OUT_FILE = OUT_DIR / "index.html"

RECORD_FIELDS = [
    "id", "country", "framework_short", "document", "legal_status", "article_or_section", "page_number",
    "governance_dimension", "secondary_dimension", "exact_text", "provision_summary", "obligation_type",
    "responsible_party", "applicability", "enforcement_mechanism", "enforcement_level", "enforcement_mechanisms",
    "mechanism_character", "responsibility_categories", "source_reference", "version_used",
    "applicability_status", "implementation_status", "implementation_notes", "verification_notes",
]


def payload(atlas: ad.Atlas) -> dict:
    kw = [
        {"framework": r["framework"], "dimension": r["dimension"],
         "value": round(float(r["frequency_per_1000_words"]), 3), "words": int(r["total_words"])}
        for _, r in atlas.keywords.iterrows() if isinstance(r["framework"], str)
    ]
    return {
        "generated": date.today().isoformat(),
        "frameworks": ad.FRAMEWORKS,
        "short": ad.SHORT,
        "dimensions": ad.DIMENSIONS,
        "enforcementLevels": ad.ENFORCEMENT_LEVELS,
        "enforcementDesc": ad.ENFORCEMENT_LEVEL_DESC,
        "implementationLevels": ad.IMPLEMENTATION_LEVELS,
        "obligationTypes": ad.OBLIGATION_TYPES,
        "records": [{k: r.get(k, "") for k in RECORD_FIELDS} for r in atlas.records],
        "keywords": kw,
        "sources": atlas.sources,
        "meta": atlas.meta,
    }


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Governance Atlas — Dashboard</title>
<style>
.viz-root {
  color-scheme: light;
  --surface-0: #f7f7f5; --surface-1: #ffffff; --surface-2: #f1f1ef; --border: #e3e3e0;
  --text-primary: #191919; --text-secondary: #666666; --grid: #ececec; --focus: #257de0;
  --fw-eu: #257de0; --fw-india: #f47230; --fw-uk: #00b894; --fw-oecd: #f2a600;
  --enf-cross: #6a4ce2; --enf-system: #ee7fac; --enf-direct: #008a17; --enf-none: #9c9c9c; --enf-na: #ffffff;
  --imp-1: #262626; --imp-2: #4f4f4f; --imp-3: #787878; --imp-4: #a3a3a3; --imp-5: #ffffff;
  --seq-0: #f4f4f2; --seq-1: #cce3fd; --seq-2: #84b9f3; --seq-3: #338ced; --seq-4: #2370cd; --seq-5: #0f4a96;
  --hatch: #8a8a8a;
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) .viz-root {
    color-scheme: dark;
    --surface-0: #111111; --surface-1: #191919; --surface-2: #222222; --border: #333333;
    --text-primary: #efefef; --text-secondary: #9c9c9c; --grid: #2c2c2c; --focus: #338ced;
    --fw-eu: #338ced; --fw-india: #e76624; --fw-uk: #00a888; --fw-oecd: #d28e05;
    --enf-cross: #9887ef; --enf-system: #e24d8b; --enf-direct: #0aac23; --enf-none: #7a7a7a; --enf-na: #191919;
    --imp-1: #e6e6e6; --imp-2: #b0b0b0; --imp-3: #868686; --imp-4: #5c5c5c; --imp-5: #191919;
    --seq-0: #222222; --seq-1: #0e3d7e; --seq-2: #1757ac; --seq-3: #2370cd; --seq-4: #519ced; --seq-5: #9dc8f7;
    --hatch: #8a8a8a;
  }
}
:root[data-theme="dark"] .viz-root {
  color-scheme: dark;
  --surface-0: #111111; --surface-1: #191919; --surface-2: #222222; --border: #333333;
  --text-primary: #efefef; --text-secondary: #9c9c9c; --grid: #2c2c2c; --focus: #338ced;
  --fw-eu: #338ced; --fw-india: #e76624; --fw-uk: #00a888; --fw-oecd: #d28e05;
  --enf-cross: #9887ef; --enf-system: #e24d8b; --enf-direct: #0aac23; --enf-none: #7a7a7a; --enf-na: #191919;
  --imp-1: #e6e6e6; --imp-2: #b0b0b0; --imp-3: #868686; --imp-4: #5c5c5c; --imp-5: #191919;
  --seq-0: #222222; --seq-1: #0e3d7e; --seq-2: #1757ac; --seq-3: #2370cd; --seq-4: #519ced; --seq-5: #9dc8f7;
  --hatch: #8a8a8a;
}
* { box-sizing: border-box; }
body { margin: 0; }
.viz-root { background: var(--surface-0); color: var(--text-primary); min-height: 100vh;
  font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, sans-serif; }
.wrap { max-width: 1180px; margin: 0 auto; padding: 24px 20px 48px; }
header { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; }
h1 { font-size: 22px; margin: 0 0 4px; letter-spacing: -0.01em; }
.sub { color: var(--text-secondary); margin: 0; max-width: 720px; }
.theme-btn, .tab, .chip, .linkbtn, select, input[type=search] {
  font: inherit; color: var(--text-primary); background: var(--surface-1); border: 1px solid var(--border);
  border-radius: 8px; padding: 6px 10px; }
.theme-btn, .tab, .chip, .linkbtn { cursor: pointer; }
:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
nav.tabs { display: flex; gap: 6px; margin: 20px 0 12px; border-bottom: 1px solid var(--border); padding-bottom: 10px; }
.tab[aria-selected="true"] { background: var(--text-primary); color: var(--surface-1); border-color: var(--text-primary); }
.filters { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin: 0 0 16px; }
.filters .label { color: var(--text-secondary); font-size: 12px; margin-right: 2px; }
.chip { display: inline-flex; align-items: center; gap: 6px; padding: 5px 10px; font-size: 13px; }
.chip[aria-pressed="false"] { color: var(--text-secondary); background: transparent; }
.chip[aria-pressed="false"] .sw { opacity: .3; }
.sw { width: 10px; height: 10px; border-radius: 2px; display: inline-block; flex: none; }
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
.kpi, .card { background: var(--surface-1); border: 1px solid var(--border); border-radius: 12px; }
.kpi { padding: 14px 16px; }
.kpi .v { font-size: 30px; font-weight: 650; line-height: 1.1; font-variant-numeric: tabular-nums; }
.kpi .l { color: var(--text-secondary); font-size: 12.5px; margin-top: 4px; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.card { padding: 16px; margin-bottom: 16px; }
.card h2 { font-size: 15px; margin: 0 0 2px; }
.card .desc { color: var(--text-secondary); font-size: 12.5px; margin: 0 0 12px; }
.card-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.linkbtn { font-size: 12px; padding: 3px 8px; white-space: nowrap; flex: none; }
.legend { display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: 12px; color: var(--text-primary); margin-bottom: 8px; }
.legend span { display: inline-flex; align-items: center; gap: 6px; }
svg text { fill: var(--text-primary); font-size: 12px; }
svg .muted { fill: var(--text-secondary); font-size: 11px; }
svg .mark { cursor: pointer; transition: opacity .1s; }
svg .mark:hover, svg .mark:focus { opacity: .82; outline: none; }
svg .mark:focus-visible { stroke: var(--focus); stroke-width: 2px; }
table.data { width: 100%; border-collapse: collapse; font-size: 12.5px; }
table.data th, table.data td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--border); vertical-align: top; }
table.data th { color: var(--text-secondary); font-weight: 600; }
table.data td.num, table.data th.num { text-align: right; font-variant-numeric: tabular-nums; }
.explorer { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr); gap: 16px; }
.plist { max-height: 640px; overflow: auto; }
.plist tr { cursor: pointer; }
.plist tr:hover td { background: var(--surface-2); }
.plist tr[aria-selected="true"] td { background: var(--surface-2); }
.plist tr[aria-selected="true"] td:first-child { box-shadow: inset 3px 0 0 var(--focus); }
.detail { position: sticky; top: 12px; align-self: start; max-height: calc(100vh - 24px); overflow: auto; }
.tag { display: inline-flex; align-items: center; gap: 5px; font-size: 11.5px; padding: 1px 7px; border-radius: 999px;
  border: 1px solid var(--border); white-space: nowrap; }
.detail h3 { margin: 0 0 4px; font-size: 16px; }
.detail dl { display: grid; grid-template-columns: 150px 1fr; gap: 6px 12px; margin: 12px 0 0; font-size: 13px; }
.detail dt { color: var(--text-secondary); }
.detail dd { margin: 0; overflow-wrap: anywhere; }
.detail blockquote { margin: 10px 0; padding: 8px 12px; border-left: 3px solid var(--border); background: var(--surface-2);
  border-radius: 0 8px 8px 0; font-size: 13px; }
.chain { display: flex; flex-wrap: wrap; align-items: stretch; gap: 6px; margin-top: 12px; }
.chain .step { flex: 1 1 120px; border: 1px solid var(--border); border-radius: 8px; padding: 8px; font-size: 12px; }
.chain .step b { display: block; font-size: 11px; color: var(--text-secondary); font-weight: 600; margin-bottom: 2px; }
.note { color: var(--text-secondary); font-size: 12px; }
.empty { color: var(--text-secondary); padding: 24px; text-align: center; }
#tip { position: fixed; pointer-events: none; z-index: 10; background: var(--surface-1); color: var(--text-primary);
  border: 1px solid var(--border); border-radius: 8px; padding: 8px 10px; font-size: 12px; box-shadow: 0 4px 14px rgba(0,0,0,.12);
  max-width: 280px; display: none; }
#tip .tv { font-size: 15px; font-weight: 650; }
#tip .tk { display: inline-block; width: 12px; height: 3px; border-radius: 2px; margin-right: 6px; vertical-align: middle; }
footer { margin-top: 24px; color: var(--text-secondary); font-size: 12px; }
@media (max-width: 860px) { .kpis { grid-template-columns: repeat(2, 1fr); } .grid2, .explorer { grid-template-columns: 1fr; } }
@media (forced-colors: active) { .sw, .mark { forced-color-adjust: none; } }
</style>
</head>
<body>
<div class="viz-root">
<div class="wrap">
  <header>
    <div>
      <h1>AI Governance Atlas</h1>
      <p class="sub">How the EU, India and the UK turn AI governance principles into obligations, measured against the OECD
        benchmark. Every figure comes from the coded provisions in the project dataset.</p>
    </div>
    <button class="theme-btn" id="themeBtn" type="button" aria-label="Switch colour theme">Theme: auto</button>
  </header>

  <nav class="tabs" role="tablist" aria-label="Dashboard views">
    <button class="tab" role="tab" id="tab-overview" aria-controls="view-overview" aria-selected="true">Overview</button>
    <button class="tab" role="tab" id="tab-explorer" aria-controls="view-explorer" aria-selected="false">Provision explorer</button>
    <button class="tab" role="tab" id="tab-indicators" aria-controls="view-indicators" aria-selected="false">Text indicators</button>
  </nav>

  <div class="filters" role="group" aria-label="Filters">
    <span class="label">Frameworks</span><span id="fwChips"></span>
    <span class="label" style="margin-left:8px">Dimension</span>
    <select id="dimSel" aria-label="Governance dimension"></select>
    <input type="search" id="q" placeholder="Search provisions…" aria-label="Search provisions" size="24">
    <button class="linkbtn" id="resetBtn" type="button">Reset</button>
  </div>

  <section id="view-overview" role="tabpanel" aria-labelledby="tab-overview">
    <div class="kpis" id="kpis"></div>
    <div class="card">
      <div class="card-head"><div><h2>Enforcement linkage</h2>
        <p class="desc">How each provision connects to a route for securing compliance.</p></div>
        <button class="linkbtn" data-table="enf">Show table</button></div>
      <div class="legend" id="enfLegend"></div>
      <div id="enfChart"></div><div id="enfTable" hidden></div>
    </div>
    <div class="grid2">
      <div class="card">
        <div class="card-head"><div><h2>Implementation evidence</h2>
          <p class="desc">“Not assessed” means no assessment was made, not that implementation failed.</p></div>
          <button class="linkbtn" data-table="imp">Show table</button></div>
        <div class="legend" id="impLegend"></div>
        <div id="impChart"></div><div id="impTable" hidden></div>
      </div>
      <div class="card">
        <div class="card-head"><div><h2>Who is obliged?</h2>
          <p class="desc">Provisions addressing each type of duty-holder. A provision can address several.</p></div>
          <button class="linkbtn" data-table="addr">Show table</button></div>
        <div id="addrChart"></div><div id="addrTable" hidden></div>
      </div>
    </div>
    <div class="card">
      <h2>Translation profile</h2>
      <p class="desc">Number of coded provisions at each link of the chain from principle to practice.</p>
      <div id="oblTable"></div>
    </div>
  </section>

  <section id="view-explorer" role="tabpanel" aria-labelledby="tab-explorer" hidden>
    <div class="explorer">
      <div class="card plist"><table class="data" id="plist" aria-label="Coded provisions"></table></div>
      <div class="card detail" id="detail" aria-live="polite"></div>
    </div>
  </section>

  <section id="view-indicators" role="tabpanel" aria-labelledby="tab-indicators" hidden>
    <div class="card">
      <div class="card-head"><div><h2>Keyword frequency per 1,000 words</h2>
        <p class="desc">Full text of each instrument. These are descriptive indicators of drafting emphasis: a keyword
          does not show that an obligation exists. The EU figure uses the consolidated text without recitals. The
          dimension filter does not apply here.</p></div>
        <button class="linkbtn" data-table="kw">Show table</button></div>
      <div class="legend" id="kwLegend"></div>
      <div id="kwChart"></div><div id="kwTable" hidden></div>
    </div>
  </section>

  <footer id="foot"></footer>
</div>
<div id="tip" role="tooltip"></div>
</div>

<script id="atlas-data" type="application/json">__DATA__</script>
<script>
(() => {
"use strict";
const D = JSON.parse(document.getElementById("atlas-data").textContent);
const SVGNS = "http://www.w3.org/2000/svg";
const FW_VAR = {"EU": "--fw-eu", "India": "--fw-india", "UK": "--fw-uk", "OECD (international benchmark)": "--fw-oecd"};
const ENF_VAR = {"Cross-referenced": "--enf-cross", "System-level only": "--enf-system", "Direct": "--enf-direct",
                 "None identified": "--enf-none", "Not applicable": "--enf-na"};
const IMP_VAR = {"Implemented": "--imp-1", "Partially implemented": "--imp-2", "Not yet implemented": "--imp-3",
                 "No evidence of implementation found": "--imp-4", "Not assessed": "--imp-5"};
const OUTLINED = new Set(["Not applicable", "Not assessed"]);
const HATCHED = new Set(["Not applicable"]);
const PRIVATE = new Set(["AI Provider", "AI Deployer", "Developer", "End User", "AI Lifecycle Actors", "Multiple Stakeholders"]);
const PUBLIC = new Set(["Government", "Regulator", "Institution"]);
const css = v => getComputedStyle(document.querySelector(".viz-root")).getPropertyValue(v).trim();
const short = f => D.short[f] || f;

// ---------- state ----------
const state = { fws: new Set(D.frameworks), dim: "", q: "", selected: null, view: "overview" };
function filtered() {
  const q = state.q.toLowerCase();
  return D.records.filter(r => state.fws.has(r.country)
    && (!state.dim || r.governance_dimension === state.dim)
    && (!q || [r.id, r.article_or_section, r.provision_summary, r.exact_text, r.responsible_party, r.enforcement_mechanism]
              .join(" ").toLowerCase().includes(q)));
}
const activeFws = () => D.frameworks.filter(f => state.fws.has(f));

// ---------- helpers ----------
function el(tag, attrs = {}, text) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (text !== undefined) n.textContent = text;
  return n;
}
function s(tag, attrs = {}) { const n = document.createElementNS(SVGNS, tag); for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v); return n; }
function swatch(varName, outlined, hatched) {
  const sp = el("span", {class: "sw"});
  sp.style.background = hatched ? `repeating-linear-gradient(45deg, var(--hatch) 0 1.5px, transparent 1.5px 4px)` : `var(${varName})`;
  if (outlined) sp.style.border = "1px solid var(--text-secondary)";
  return sp;
}
function legend(id, levels, map, label = x => x) {
  const box = document.getElementById(id); box.replaceChildren();
  levels.forEach(l => { const sp = el("span"); sp.append(swatch(map[l], OUTLINED.has(l), HATCHED.has(l)), document.createTextNode(label(l))); box.append(sp); });
}
const tip = document.getElementById("tip");
function showTip(evt, value, label, sub, colorVar) {
  tip.replaceChildren();
  const v = el("div", {class: "tv"}, String(value));
  const l = el("div"); const k = el("span", {class: "tk"}); k.style.background = `var(${colorVar})`;
  if (colorVar) l.append(k); l.append(document.createTextNode(label));
  tip.append(v, l);
  if (sub) tip.append(el("div", {class: "note"}, sub));
  tip.style.display = "block";
  let x, y;
  if (evt.type === "focus") { const b = evt.target.getBoundingClientRect(); x = b.right; y = b.top; }
  else { x = evt.clientX; y = evt.clientY; }
  const w = tip.offsetWidth, h = tip.offsetHeight;
  tip.style.left = Math.min(window.innerWidth - w - 8, x + 12) + "px";
  tip.style.top = Math.max(8, y - h - 10) + "px";
}
const hideTip = () => { tip.style.display = "none"; };
function bindTip(node, value, label, sub, colorVar) {
  node.setAttribute("tabindex", "0"); node.setAttribute("class", "mark");
  node.setAttribute("aria-label", `${label}: ${value}${sub ? ", " + sub : ""}`);
  ["pointermove", "focus"].forEach(e => node.addEventListener(e, ev => showTip(ev, value, label, sub, colorVar)));
  ["pointerleave", "blur"].forEach(e => node.addEventListener(e, hideTip));
}
function tableView(id, head, rows) {
  const box = document.getElementById(id); box.replaceChildren();
  const t = el("table", {class: "data"}); const tr = el("tr");
  head.forEach((h, i) => tr.append(el("th", i ? {class: "num"} : {}, h))); t.append(tr);
  rows.forEach(r => { const row = el("tr"); r.forEach((c, i) => row.append(el("td", i ? {class: "num"} : {}, String(c)))); t.append(row); });
  box.append(t);
}
function countBy(records, field, levels) {
  const out = {};
  activeFws().forEach(f => { out[f] = Object.fromEntries(levels.map(l => [l, 0])); });
  records.forEach(r => { if (out[r.country] && r[field] in out[r.country]) out[r.country][r[field]]++; });
  return out;
}

// ---------- stacked horizontal bar ----------
function stacked(containerId, data, levels, map, labelFn = x => x) {
  const box = document.getElementById(containerId); box.replaceChildren();
  const fws = Object.keys(data);
  if (!fws.length) { box.append(el("div", {class: "empty"}, "No frameworks selected.")); return; }
  const totals = fws.map(f => levels.reduce((a, l) => a + data[f][l], 0));
  const max = Math.max(1, ...totals);
  const W = Math.max(320, box.clientWidth || 1000), rowH = 34, barH = 22, left = 56, right = 12, top = 6, axisH = 26;
  const H = top + fws.length * rowH + axisH;
  const svg = s("svg", {viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: "img",
    "aria-label": "Stacked bar chart; use Show table for values"});
  const x = v => left + (W - left - right) * v / max;
  for (let t = 0; t <= max; t++) {
    svg.append(s("line", {x1: x(t), x2: x(t), y1: top, y2: H - axisH + 2, stroke: css("--grid")}));
    const tx = s("text", {x: x(t), y: H - 8, "text-anchor": "middle", class: "muted"}); tx.textContent = t; svg.append(tx);
  }
  const defs = s("defs");
  const pat = s("pattern", {id: containerId + "-hatch", width: 6, height: 6, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)"});
  pat.append(s("rect", {width: 6, height: 6, fill: css("--surface-1")}), s("line", {x1: 0, y1: 0, x2: 0, y2: 6, stroke: css("--hatch"), "stroke-width": 2}));
  defs.append(pat); svg.append(defs);
  fws.forEach((f, i) => {
    const y = top + i * rowH + (rowH - barH) / 2;
    const lab = s("text", {x: left - 10, y: y + barH / 2 + 4, "text-anchor": "end"}); lab.textContent = short(f); svg.append(lab);
    let acc = 0;
    levels.forEach(l => {
      const v = data[f][l]; if (!v) return;
      const x0 = x(acc), x1 = x(acc + v), w = Math.max(0, x1 - x0 - 2);
      const outlined = OUTLINED.has(l), hatched = HATCHED.has(l);
      const rect = s("rect", {x: x0 + 1, y, width: w, height: barH, rx: 3,
        fill: hatched ? `url(#${containerId}-hatch)` : css(map[l]),
        stroke: outlined ? css("--text-secondary") : "none", "stroke-width": outlined ? 1 : 0});
      bindTip(rect, v, labelFn(l), `${short(f)} · ${v === 1 ? "1 provision" : v + " provisions"}`, map[l]);
      svg.append(rect);
      if (w > 18) {
        const dark = ["--imp-1", "--imp-2", "--imp-3", "--enf-cross", "--enf-direct"].includes(map[l]);
        const isDarkTheme = document.querySelector(".viz-root") && css("--surface-1") !== "#ffffff";
        const t = s("text", {x: x0 + 1 + w / 2, y: y + barH / 2 + 4, "text-anchor": "middle", "font-weight": 600, "pointer-events": "none"});
        t.style.fill = (dark && !isDarkTheme) || (isDarkTheme && ["--enf-cross","--enf-direct"].includes(map[l])) ? "#ffffff"
                     : (isDarkTheme && ["--imp-1","--imp-2"].includes(map[l]) ? "#111111" : "var(--text-primary)");
        if (hatched) { const bg = s("rect", {x: x0 + 1 + w / 2 - 9, y: y + barH / 2 - 8, width: 18, height: 16, rx: 3, fill: css("--surface-1"), "pointer-events": "none"}); svg.append(bg); }
        t.textContent = v; svg.append(t);
      }
      acc += v;
    });
  });
  box.append(svg);
}

// ---------- views ----------
function renderKpis(recs) {
  const box = document.getElementById("kpis"); box.replaceChildren();
  const items = [
    [recs.length, "provisions in view"],
    [recs.filter(r => r.obligation_type === "Mandatory").length, "mandatory duties"],
    [recs.filter(r => ["Cross-referenced", "Direct"].includes(r.enforcement_level)).length, "with a direct or cross-referenced compliance route"],
    [recs.filter(r => ["Implemented", "Partially implemented"].includes(r.implementation_status)).length, "with implementation evidence"],
  ];
  items.forEach(([v, l]) => { const k = el("div", {class: "kpi"}); k.append(el("div", {class: "v"}, String(v)), el("div", {class: "l"}, l)); box.append(k); });
}

function renderOverview() {
  const recs = filtered();
  renderKpis(recs);
  const enf = countBy(recs, "enforcement_level", D.enforcementLevels);
  stacked("enfChart", enf, D.enforcementLevels, ENF_VAR, l => `${l} — ${D.enforcementDesc[l]}`);
  tableView("enfTable", ["Framework", ...D.enforcementLevels], Object.entries(enf).map(([f, c]) => [short(f), ...D.enforcementLevels.map(l => c[l])]));
  const imp = countBy(recs, "implementation_status", D.implementationLevels);
  stacked("impChart", imp, D.implementationLevels, IMP_VAR);
  tableView("impTable", ["Framework", ...D.implementationLevels], Object.entries(imp).map(([f, c]) => [short(f), ...D.implementationLevels.map(l => c[l])]));
  const obl = countBy(recs, "obligation_type", D.obligationTypes);
  tableView("oblTable", ["Framework", "Provisions", "Mandatory", "Recommended", "Institutional", "Compliance route", "Implementation evidence"],
    Object.entries(obl).map(([f, c]) => {
      const rs = recs.filter(r => r.country === f);
      return [short(f), rs.length, c.Mandatory, c.Recommended, c.Institutional,
        rs.filter(r => ["Cross-referenced", "Direct"].includes(r.enforcement_level)).length,
        rs.filter(r => ["Implemented", "Partially implemented"].includes(r.implementation_status)).length];
    }));
  renderAddressees(recs);
}

function renderAddressees(recs) {
  const box = document.getElementById("addrChart"); box.replaceChildren();
  const fws = activeFws();
  const cats = [...new Set(D.records.flatMap(r => r.responsibility_categories))];
  const order = [...cats.filter(c => PRIVATE.has(c)).sort(), ...cats.filter(c => PUBLIC.has(c)).sort(), ...cats.filter(c => !PRIVATE.has(c) && !PUBLIC.has(c))];
  const counts = {}; fws.forEach(f => counts[f] = Object.fromEntries(order.map(c => [c, 0])));
  recs.forEach(r => r.responsibility_categories.forEach(c => { if (counts[r.country]) counts[r.country][c]++; }));
  if (!fws.length) { box.append(el("div", {class: "empty"}, "No frameworks selected.")); return; }
  const cw = 52, ch = 30, left = 56, top = 22, bottom = 74;
  const W = left + order.length * cw + 44, H = top + fws.length * ch + bottom;
  const svg = s("svg", {viewBox: `0 0 ${W} ${H}`, width: "100%", role: "img", "aria-label": "Heatmap of duty-holders; use Show table for values"});
  const nPriv = order.filter(c => PRIVATE.has(c)).length;
  [["Private actors", 0, nPriv], ["Public bodies", nPriv, order.length]].forEach(([t, a, b]) => {
    if (b > a) { const tx = s("text", {x: left + (a + b) / 2 * cw, y: 12, "text-anchor": "middle", class: "muted"}); tx.textContent = t; svg.append(tx); }
  });
  svg.append(s("line", {x1: left + nPriv * cw - 1, x2: left + nPriv * cw - 1, y1: top - 4, y2: top + fws.length * ch, stroke: css("--text-secondary"), "stroke-dasharray": "3 3"}));
  const ramp = ["--seq-0", "--seq-1", "--seq-2", "--seq-3", "--seq-4", "--seq-5"];
  fws.forEach((f, i) => {
    const lab = s("text", {x: left - 8, y: top + i * ch + ch / 2 + 4, "text-anchor": "end"}); lab.textContent = short(f); svg.append(lab);
    order.forEach((c, j) => {
      const v = counts[f][c], fillVar = ramp[Math.min(v, ramp.length - 1)];
      const r = s("rect", {x: left + j * cw + 1, y: top + i * ch + 1, width: cw - 2, height: ch - 2, rx: 3, fill: css(fillVar)});
      bindTip(r, v, c, `${short(f)} · provisions addressing this actor`, fillVar);
      svg.append(r);
      if (v) { const t = s("text", {x: left + j * cw + cw / 2, y: top + i * ch + ch / 2 + 4, "text-anchor": "middle", "font-weight": 600, "pointer-events": "none"});
        t.style.fill = v >= 3 ? (css("--surface-1") === "#ffffff" ? "#ffffff" : "#111111") : "var(--text-primary)"; t.textContent = v; svg.append(t); }
    });
  });
  order.forEach((c, j) => {
    const t = s("text", {transform: `translate(${left + j * cw + cw / 2},${top + fws.length * ch + 10}) rotate(35)`, class: "muted"});
    t.textContent = c.replace("AI Lifecycle Actors", "Lifecycle actors").replace("Multiple Stakeholders", "Multiple").replace(/^AI /, ""); svg.append(t);
  });
  box.append(svg);
  tableView("addrTable", ["Framework", ...order], fws.map(f => [short(f), ...order.map(c => counts[f][c])]));
}

function tag(text, varName, outlined, hatched) { const t = el("span", {class: "tag"}); t.append(swatch(varName, outlined, hatched), document.createTextNode(text)); return t; }

function renderExplorer() {
  const recs = filtered();
  const t = document.getElementById("plist"); t.replaceChildren();
  const hr = el("tr"); ["ID", "Provision", "Obligation", "Enforcement"].forEach(h => hr.append(el("th", {}, h))); t.append(hr);
  if (!recs.length) { const tr = el("tr"); const td = el("td", {colspan: 4, class: "empty"}, "No provisions match the filters."); tr.append(td); t.append(tr); }
  if (!recs.find(r => r.id === state.selected)) state.selected = recs.length ? recs[0].id : null;
  recs.forEach(r => {
    const tr = el("tr", {tabindex: "0", "aria-selected": String(r.id === state.selected)});
    const idc = el("td"); idc.append(tag(r.id, FW_VAR[r.country]));
    const pc = el("td"); pc.append(el("div", {}, r.article_or_section)); pc.append(el("div", {class: "note"}, short(r.country) + " · " + r.legal_status));
    pc.append(el("div", {class: "note"}, r.governance_dimension));
    tr.append(idc, pc, el("td", {}, r.obligation_type));
    const ec = el("td"); ec.append(tag(r.enforcement_level, ENF_VAR[r.enforcement_level], OUTLINED.has(r.enforcement_level), HATCHED.has(r.enforcement_level))); tr.append(ec);
    const pick = () => { state.selected = r.id; renderExplorer(); };
    tr.addEventListener("click", pick);
    tr.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); } });
    t.append(tr);
  });
  renderDetail(D.records.find(r => r.id === state.selected));
}

function renderDetail(r) {
  const box = document.getElementById("detail"); box.replaceChildren();
  if (!r) { box.append(el("div", {class: "empty"}, "Select a provision to see its details.")); return; }
  const head = el("div"); head.append(tag(r.id, FW_VAR[r.country]), document.createTextNode(" "), el("span", {class: "note"}, r.document));
  box.append(head, el("h3", {}, r.article_or_section));
  box.append(el("p", {}, r.provision_summary));
  if (r.exact_text) box.append(el("blockquote", {}, r.exact_text));
  const chain = el("div", {class: "chain", "aria-label": "Translation chain"});
  [["Legal force", r.legal_status], ["Obligation", r.obligation_type], ["Duty-holder", r.responsible_party],
   ["Enforcement linkage", r.enforcement_level + (r.enforcement_mechanisms.length ? " — " + r.enforcement_mechanisms.join("; ") : "")],
   ["Implementation", r.implementation_status]].forEach(([k, v]) => { const st = el("div", {class: "step"}); st.append(el("b", {}, k), document.createTextNode(v)); chain.append(st); });
  box.append(chain);
  const dl = el("dl");
  const add = (k, v, link) => { if (!v) return; dl.append(el("dt", {}, k)); const dd = el("dd");
    if (link) { const m = v.match(/https?:\/\/[^\s;,)]+/); if (m) { const a = el("a", {href: m[0], target: "_blank", rel: "noopener noreferrer"}, m[0]); dd.append(a); dl.append(dd); return; } }
    dd.textContent = v; dl.append(dd); };
  add("Dimension", r.governance_dimension + (r.secondary_dimension ? " (secondary: " + r.secondary_dimension + ")" : ""));
  add("Applicability", r.applicability);
  add("Applicability status", r.applicability_status);
  add("Enforcement detail", r.enforcement_mechanism);
  add("Implementation notes", r.implementation_notes);
  add("Page", r.page_number);
  add("Version coded", r.version_used);
  add("Source", r.source_reference, true);
  add("Verification notes", r.verification_notes);
  box.append(dl);
}

function renderIndicators() {
  const fws = activeFws(), dims = D.dimensions;
  legend("kwLegend", fws, FW_VAR, short);
  const box = document.getElementById("kwChart"); box.replaceChildren();
  if (!fws.length) { box.append(el("div", {class: "empty"}, "No frameworks selected.")); return; }
  const val = (f, d) => (D.keywords.find(k => k.framework === f && k.dimension === d) || {value: 0}).value;
  const max = Math.max(1, ...fws.flatMap(f => dims.map(d => val(f, d))));
  const W = Math.max(320, box.clientWidth || 1000), left = 130, right = 40, bh = 12, gap = 3, groupGap = 18, top = 6, axisH = 26;
  const groupH = fws.length * (bh + gap) + groupGap;
  const H = top + dims.length * groupH + axisH;
  const svg = s("svg", {viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: "img", "aria-label": "Grouped bar chart of keyword frequencies; use Show table for values"});
  const nice = Math.ceil(max);
  const x = v => left + (W - left - right) * v / nice;
  for (let t = 0; t <= nice; t++) {
    svg.append(s("line", {x1: x(t), x2: x(t), y1: top, y2: H - axisH + 2, stroke: css("--grid")}));
    const tx = s("text", {x: x(t), y: H - 8, "text-anchor": "middle", class: "muted"}); tx.textContent = t; svg.append(tx);
  }
  dims.forEach((d, i) => {
    const gy = top + i * groupH;
    const lab = s("text", {x: left - 10, y: gy + (fws.length * (bh + gap)) / 2 + 4, "text-anchor": "end"}); lab.textContent = d; svg.append(lab);
    fws.forEach((f, k) => {
      const v = val(f, d), y = gy + k * (bh + gap);
      const r = s("rect", {x: left, y, width: Math.max(1.5, x(v) - left), height: bh, rx: 3, fill: css(FW_VAR[f])});
      bindTip(r, v.toFixed(2), short(f), `${d} · per 1,000 words`, FW_VAR[f]); svg.append(r);
      const t = s("text", {x: x(v) + 5, y: y + bh - 2, class: "muted"}); t.textContent = v.toFixed(1); svg.append(t);
    });
  });
  box.append(svg);
  tableView("kwTable", ["Dimension", ...fws.map(short)], dims.map(d => [d, ...fws.map(f => val(f, d).toFixed(2))]));
}

function render() {
  if (state.view === "overview") renderOverview();
  if (state.view === "explorer") renderExplorer();
  if (state.view === "indicators") renderIndicators();
}

// ---------- controls ----------
const chips = document.getElementById("fwChips");
D.frameworks.forEach(f => {
  const b = el("button", {class: "chip", type: "button", "aria-pressed": "true"});
  b.append(swatch(FW_VAR[f]), document.createTextNode(short(f)));
  b.addEventListener("click", () => { state.fws.has(f) ? state.fws.delete(f) : state.fws.add(f); b.setAttribute("aria-pressed", String(state.fws.has(f))); render(); });
  chips.append(b);
});
const dimSel = document.getElementById("dimSel");
dimSel.append(el("option", {value: ""}, "All dimensions"));
D.dimensions.forEach(d => dimSel.append(el("option", {value: d}, d)));
dimSel.addEventListener("change", () => { state.dim = dimSel.value; render(); });
document.getElementById("q").addEventListener("input", e => { state.q = e.target.value; render(); });
document.getElementById("resetBtn").addEventListener("click", () => {
  state.fws = new Set(D.frameworks); state.dim = ""; state.q = "";
  dimSel.value = ""; document.getElementById("q").value = "";
  chips.querySelectorAll(".chip").forEach(c => c.setAttribute("aria-pressed", "true")); render();
});
document.querySelectorAll("[data-table]").forEach(b => b.addEventListener("click", () => {
  const t = document.getElementById(b.dataset.table + "Table"); const c = document.getElementById(b.dataset.table + "Chart");
  const show = t.hidden; t.hidden = !show; c.hidden = show; b.textContent = show ? "Show chart" : "Show table";
}));
const tabs = ["overview", "explorer", "indicators"];
tabs.forEach(v => document.getElementById("tab-" + v).addEventListener("click", () => {
  state.view = v;
  tabs.forEach(o => { document.getElementById("tab-" + o).setAttribute("aria-selected", String(o === v)); document.getElementById("view-" + o).hidden = o !== v; });
  render();
}));
const root = document.documentElement, themes = ["auto", "light", "dark"]; let ti = 0;
document.getElementById("themeBtn").addEventListener("click", e => {
  ti = (ti + 1) % 3; const t = themes[ti];
  if (t === "auto") root.removeAttribute("data-theme"); else root.setAttribute("data-theme", t);
  e.target.textContent = "Theme: " + t; render();
});
let rz; window.addEventListener("resize", () => { clearTimeout(rz); rz = setTimeout(render, 150); });
if (window.matchMedia) window.matchMedia("(prefers-color-scheme: dark)").addEventListener?.("change", render);

legend("enfLegend", D.enforcementLevels, ENF_VAR);
legend("impLegend", D.implementationLevels, IMP_VAR, l => l.replace("No evidence of implementation found", "No evidence found"));
const foot = document.getElementById("foot");
const m = D.meta || {};
foot.textContent = `Generated ${D.generated} from data/annotated/governance_dataset.csv (${D.records.length} coded provisions). `
  + (m.audit_checks ? `Source verification: ${m.audit_checks} field-level checks; ${m.corrections - m.corrections_decided} proposed corrections pending review. ` : "")
  + "The sample is purposive and does not rank the frameworks. Not legal advice.";
render();
})();
</script>
</body>
</html>
"""


def main() -> None:
    atlas = ad.load()
    data = json.dumps(payload(atlas), ensure_ascii=False)
    # Prevent the embedded JSON from closing the <script> element early
    data = data.replace("</", "<\\/")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(TEMPLATE.replace("__DATA__", data), encoding="utf-8")
    print("DASHBOARD GENERATED")
    print(f"  {OUT_FILE.relative_to(ad.ROOT)}  ({OUT_FILE.stat().st_size // 1024} KB, {atlas.n} provisions)")


if __name__ == "__main__":
    main()
