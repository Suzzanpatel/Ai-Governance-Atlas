# The interactive dashboard

**File:** `results/dashboard/index.html`: a single self-contained page with the data built in. It needs no server, internet connection or installation; double-click it to open it in a browser.

## Generate it

```bash
python run_pipeline.py --stage publish
# or
python src/publish/build_dashboard.py
```

## Views

| View | What it shows |
|---|---|
| **Overview** | Headline figures; enforcement linkage by framework; implementation evidence; a heatmap of who is obliged (private actors vs public bodies); the translation-profile table |
| **Provision explorer** | All coded provisions. Select one to see its exact text, summary, the five links of its translation chain, applicability, enforcement detail, implementation notes, page reference, source link and verification notes |
| **Text indicators** | Keyword frequency per 1,000 words by governance dimension, with the caveat that keywords show drafting emphasis, not legal effect |

The framework chips, dimension menu and search box sit in one row above the views and filter every chart, figure and table together.

## Accessibility and design

- Every chart has a **Show table** button that presents the same values as a table.
- Hovering over or focusing (Tab key) a bar or cell shows its value; all values can also be reached without hovering.
- Colors were checked for color-vision deficiency and contrast in light and dark modes. Framework, enforcement and implementation categories each use their own color family, so a color never means two things.
- Light, dark and automatic themes are available (button at top right).
- All dataset text is inserted as plain text, never as HTML.

## Sharing it

Because it is a single file, you can:
- attach `index.html` to an email or upload it to a course page;
- download it from the GitHub release assets;
- publish it with **GitHub Pages**: in the repository's Settings → Pages, choose to deploy from the `main` branch and the `/ (root)` folder; it will then be available at `https://suzzanpatel.github.io/Ai-Governance-Atlas/results/dashboard/`.
