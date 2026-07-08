# Power BI Desktop — Manual Fix List

`hospiq_cardiac.pbix` is git-ignored and not present in this repo (see `.gitignore`).
There is no CLI or API for editing a Power BI Desktop report's pages, visuals, or DAX —
these two issues can only be fixed by opening the actual `.pbix` file in Power BI Desktop.
This document is the exact, actionable checklist for doing that. Nothing here has been
faked or worked around in the committed screenshots; the known-bad screenshots stay as
they are until you re-export the real fix.

---

## A. Page 4 — Patient Cohort Detail: missing page styling

**Symptom:** `screenshots/04_patient_cohort_detail.png` shows a bare, unstyled table
floating top-left on an empty white canvas. Pages 1–3 all share a consistent theme: a
dark navy header bar with the page title, a filter-slicer row, and card-style visuals
with rounded borders and subtle shadows. Page 4 has none of this — it reads as an
unfinished page next to the other four.

**Fix steps in Power BI Desktop:**

1. Open the **Patient Cohort Detail** page.
2. **Add the matching header bar.**
   - Insert → Shapes → Rectangle, spanning the full page width, ~60–80px tall, docked
     to the top (match the exact height used on pages 1–3 — select the header rectangle
     on page 1, note its **Size and properties** in the Format pane, and enter the same
     values here for pixel-exact consistency).
   - Format the rectangle: **Fill** → same navy hex used on pages 1–3 (sample it with
     the eyedropper tool on an existing header if you don't have the hex saved).
   - Add a text box on top: `HOSPIQ — Patient Cohort Detail`, same font/size/weight and
     white color as the other page titles, plus a subtitle line
     (`Hero DMC Heart Institute | Cohort Drill-Through`) matching the subtitle style
     used elsewhere.
3. **Set the canvas/page background** (Format page → Canvas background) to the same
   off-white/light-gray used on pages 1–3, not the default stark white.
4. **Wrap the table visual in a card.**
   - Select the table visual → Format your visual → **Effects** → turn on **Shadow**
     (match the shadow settings from a KPI card on page 1) and **Border** (rounded
     corners, same radius and hairline color as the other cards).
   - Alternatively, place a background Rectangle behind the table sized with ~16px
     padding on all sides, styled identically to the card rectangles on pages 1–3, then
     send the table to front — visually identical result, sometimes easier to align.
5. **Reposition the table.** It currently sits flush top-left. Move/resize it to sit
   inside a proper content area with consistent left/right/top margins matching the
   chart cards on pages 1–3 (check pages 1–3's card X/Y/Width/Height in the Format pane
   and reuse the same left margin and top offset below the header).
6. **Decide on the filter slicer row.** This page is a drill-through destination (right-click
   a risk-tier bar on page 2 → Drill through), so it inherits the risk-tier filter context
   automatically — it does not need its own gender/locality/admission_type/season slicers.
   If you want it consistent with pages 1–3 regardless, add the same slicer row; otherwise
   leave it out and note in the page subtitle that it's filtered by the source drill-through
   selection, not by independent slicers.
7. Re-export the screenshot at the same resolution/zoom level as the other four (see the
   capture note in section B — do this at 100% zoom, not the ad-hoc zoom level some of the
   earlier screenshots used).

---

## B. Page 5 — Condition Tooltip: screenshot shows the wrong filter context

**Symptom:** `screenshots/05_condition_tooltip.png` shows:
- **Condition Mortality Rank: 7** — impossible, since the `Conditions` table only has 6
  rows (Cardiogenic Shock, STEMI, AKI, Atrial Fibrillation, Heart Failure, CKD — see
  `dashboard/README.md`).
- **Count of outcome: 15.757K** — this is exactly the total admission count for the
  entire dataset (15,757), not a per-condition count.
- **vs Avg: 0.00%** — a degenerate, self-referential delta.

**Root cause (near-certain):** all three symptoms are consistent with the page having
been screenshotted by clicking directly on the **Condition Tooltip** page tab at the
bottom of Power BI Desktop and capturing it as an ordinary page — which renders it with
**no filter context at all** (a blank/whole-dataset context), because report-page
tooltips only receive a filter context when they're invoked *as a tooltip*, by hovering
over a visual that has this page wired up as its tooltip target. Opening the page
directly bypasses that mechanism entirely.

This is also why `vs Avg: 0.00%` is not evidence of a broken DAX formula — it's exactly
what the math produces under a blank filter. Per the documented measures in
`dashboard/README.md`:

```dax
Cohort Avg Mortality = CALCULATE([Mortality Rate], ALL(hdhi_admission_cleaned))
Mortality vs Cohort  = [Mortality Rate] - [Cohort Avg Mortality]
```

With no condition filter applied, `[Mortality Rate]` and `[Cohort Avg Mortality]`
evaluate over the same (whole-dataset) context, so their difference is trivially 0.00%
— by construction, not by bug. **Don't "fix" this measure — fix the capture method.**

**What to check in Power BI Desktop, in order:**

1. **Confirm the tooltip wiring.** Go to page 2 (Risk Intelligence) → select the
   **Mortality by Clinical Condition** bar chart → Format your visual → **General** →
   **Tooltips** → confirm **Type = Report page** and **Page = Condition Tooltip**. If
   this isn't set (or points at the wrong page), that's the actual bug — fix it here first.
2. **Confirm the relationship/filter propagation.** Open **Model view** → check that the
   `Conditions` calculated table (the `UNION(ROW(...), ...)` table from
   `dashboard/README.md`) has an active relationship — or that the measures behind it use
   a working `TREATAS`/lookup pattern — back to `hdhi_admission_cleaned`, so that hovering
   a specific condition bar actually filters the underlying fact table down to that
   condition before the tooltip page's measures evaluate. If there's no relationship and
   no `TREATAS`, the tooltip page's cards will always show the unfiltered whole-dataset
   numbers regardless of what's hovered — same symptom, different root cause than #1, so
   check both.
3. **Confirm the Condition Mortality Rank measure isn't returning a stale/impossible
   value independent of context** — with only 6 rows in `Conditions`, no legitimate
   filter context should ever produce rank 7. If it does even after fixing #1 and #2,
   check the `RANKX` formula's `FILTER(ALL(Conditions[Condition]), ...)` argument for an
   off-by-one or a leftover 7th row in the `Conditions` table definition.
4. **Capture it correctly this time:**
   - Go to page 2 (Risk Intelligence), at 100% zoom.
   - Hover the mouse pointer directly over one bar in the **Mortality by Clinical
     Condition** chart — e.g. AKI — and **do not click**.
   - Wait for the tooltip popup to render near the cursor. Confirm the values in the
     popup look condition-specific (e.g. Count ≈ 3,504 for AKI, not 15,757; a rank
     between 1–6; a non-zero `vs Avg`).
   - Screenshot **that popup** (Win+Shift+S / Snipping Tool), not the Condition Tooltip
     page tab.
5. Save the new capture as `screenshots/05_condition_tooltip.png`, replacing the old one.

---

## After you fix these

Once both pages are corrected and re-exported in Power BI Desktop, send me the two new
PNGs and I'll swap them into `screenshots/04_patient_cohort_detail.png` and
`screenshots/05_condition_tooltip.png`, and update any README/docs captions still
referencing the old broken numbers (the `<span class="tag">` flags in
`docs/dashboard_screenshots.html` in particular should come out once the real fixes are in).
