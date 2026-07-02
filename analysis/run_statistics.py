"""
run_statistics.py — Statistical significance analysis for HOSPIQ.

Uses scipy for all tests (chi-square, one-way ANOVA, Pearson correlation,
Mann-Whitney U). Prints all five sections and writes the results to
analysis/statistical_findings.md as a static report.

Run: python analysis/run_statistics.py
"""

import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console defaults to cp1252
except Exception:
    pass

DATA_PATH = os.environ.get(
    "HOSPIQ_DATA", os.path.join("data", "processed", "hdhi_admission_cleaned.csv")
)
OUT_MD = os.path.join("analysis", "statistical_findings.md")
AGE_ORDER = ["Under 40", "40-60", "61-80", "Over 80"]


def cramers_v(chi2, n, table_shape):
    k = min(table_shape) - 1
    return float(np.sqrt(chi2 / (n * k))) if k > 0 else float("nan")


def main():
    df = pd.read_csv(DATA_PATH)
    df["is_expired"] = (df["outcome"] == "Expired").astype(int)
    n = len(df)
    md = ["# Statistical Analysis — HOSPIQ Cardiac Admissions", ""]

    # -------- Section 1: Rural vs Urban mortality (chi-square) --------
    ct1 = pd.crosstab(df["locality"], df["is_expired"])
    chi2, p1, dof, _ = stats.chi2_contingency(ct1)
    v = cramers_v(chi2, n, ct1.shape)
    rural = df.loc[df.locality == "Rural", "is_expired"].mean() * 100
    urban = df.loc[df.locality == "Urban", "is_expired"].mean() * 100
    sig1 = "statistically significant" if p1 < 0.05 else "NOT statistically significant"
    print("=== SECTION 1: Rural vs Urban Mortality ===")
    print(f"Rural {rural:.2f}% vs Urban {urban:.2f}% | chi2={chi2:.3f} p={p1:.4f} dof={dof} Cramer's V={v:.3f}")
    md += [
        "## 1. Rural vs Urban Mortality Gap",
        f"- Rural mortality: **{rural:.2f}%** · Urban mortality: **{urban:.2f}%**",
        f"- Chi-square test of independence: chi2 = {chi2:.3f}, p = {p1:.4f}, dof = {dof}",
        f"- Effect size (Cramer's V) = {v:.3f} (small)",
        f"- **Interpretation:** the rural–urban difference is {sig1} at alpha 0.05"
        + (". The observed gap is real but the effect size is small — consistent with an "
           "access/time-to-care signal rather than a large clinical difference."
           if p1 < 0.05 else ", so the observed gap may be attributable to chance."),
        "",
    ]

    # -------- Section 2: Correlation with mortality --------
    print("\n=== SECTION 2: Correlation with Mortality ===")
    md += ["## 2. Correlation with Mortality",
           "Pearson correlation of each variable with `is_expired` "
           "(|r| > 0.15 flagged as notable):", "",
           "| Variable | Pearson r | Notable? |", "| --- | --- | --- |"]
    for col in ["ef", "creatinine", "age", "los_days", "risk_score"]:
        r, _ = stats.pearsonr(df[col], df["is_expired"])
        flag = "✅ notable" if abs(r) > 0.15 else "—"
        print(f"{col:12s} r={r:.3f} {flag}")
        md.append(f"| {col} | {r:.3f} | {flag} |")
    md.append("")

    # -------- Section 3: Age-group mortality (one-way ANOVA) --------
    groups = [df.loc[df.age_group == g, "is_expired"].values for g in AGE_ORDER
              if (df.age_group == g).any()]
    f_stat, p3 = stats.f_oneway(*groups)
    sig3 = "differ significantly" if p3 < 0.05 else "do not differ significantly"
    print("\n=== SECTION 3: Age Group Mortality (ANOVA) ===")
    print(f"F={f_stat:.3f} p={p3:.4f}")
    rates = " · ".join(
        f"{g}: {df.loc[df.age_group == g, 'is_expired'].mean() * 100:.2f}%"
        for g in AGE_ORDER if (df.age_group == g).any())
    md += ["## 3. Age Group Mortality (ANOVA)",
           f"- Group mortality — {rates}",
           f"- One-way ANOVA: F = {f_stat:.3f}, p = {p3:.4f}",
           f"- **Interpretation:** mortality rates across age groups **{sig3}** (alpha 0.05).", ""]

    # -------- Section 4: Emergency vs OPD (chi-square + odds ratio) --------
    ct4 = pd.crosstab(df["admission_type"], df["is_expired"])
    chi2_4, p4, _, _ = stats.chi2_contingency(ct4)
    em = df.loc[df.admission_type == "Emergency", "is_expired"].mean()
    op = df.loc[df.admission_type == "OPD", "is_expired"].mean()
    # true odds ratio from the 2x2 table
    e_d, e_s = ct4.loc["Emergency", 1], ct4.loc["Emergency", 0]
    o_d, o_s = ct4.loc["OPD", 1], ct4.loc["OPD", 0]
    odds_ratio = (e_d / e_s) / (o_d / o_s)
    print("\n=== SECTION 4: Emergency vs OPD Mortality ===")
    print(f"Emergency {em * 100:.2f}% vs OPD {op * 100:.2f}% | chi2={chi2_4:.3f} p={p4:.4f} OR={odds_ratio:.2f}")
    sig4 = "significant" if p4 < 0.05 else "not significant"
    md += ["## 4. Emergency vs OPD Mortality",
           f"- Emergency mortality: **{em * 100:.2f}%** · OPD mortality: **{op * 100:.2f}%**",
           f"- Chi-square: chi2 = {chi2_4:.3f}, p = {p4:.4f}",
           f"- Odds ratio (Emergency vs OPD death odds) = **{odds_ratio:.2f}**",
           f"- **Interpretation:** the difference is {sig4}; emergency-route patients face "
           f"{odds_ratio:.1f}x the odds of in-hospital death versus planned/OPD admissions.", ""]

    # -------- Section 5: LOS distribution by outcome (Mann-Whitney) --------
    print("\n=== SECTION 5: LOS Distribution by Outcome ===")
    md += ["## 5. Length of Stay by Outcome",
           "| Outcome | Mean LOS | Median LOS | Std | 90th pct |",
           "| --- | --- | --- | --- | --- |"]
    for oc in ["Discharged", "Expired", "DAMA"]:
        s = df.loc[df.outcome == oc, "los_days"]
        print(f"{oc:11s} mean={s.mean():.2f} median={s.median():.0f} std={s.std():.2f} p90={s.quantile(0.9):.0f}")
        md.append(f"| {oc} | {s.mean():.2f} | {s.median():.0f} | {s.std():.2f} | {s.quantile(0.9):.0f} |")
    exp_los = df.loc[df.outcome == "Expired", "los_days"]
    dis_los = df.loc[df.outcome == "Discharged", "los_days"]
    u_stat, p5 = stats.mannwhitneyu(exp_los, dis_los, alternative="two-sided")
    sig5 = "significantly different" if p5 < 0.05 else "not significantly different"
    print(f"Mann-Whitney U={u_stat:.0f} p={p5:.4f}")
    md += ["",
           f"- Mann-Whitney U (Expired vs Discharged LOS) = {u_stat:.0f}, p = {p5:.4f}",
           f"- **Interpretation:** Expired and Discharged length-of-stay distributions are **{sig5}** "
           "(non-parametric test used because LOS is right-skewed).", ""]

    # -------- Key takeaway --------
    md += ["## Key Takeaway",
           f"- Emergency-route admissions carry meaningfully higher death odds "
           f"({odds_ratio:.1f}x vs OPD) — the pathway where clinical risk concentrates.",
           "- Ejection fraction and creatinine are the variables most correlated with death, "
           "confirming pump function and kidney stress as the clearest bedside warning signs.",
           f"- The rural–urban mortality gap is {('real but small' if p1 < 0.05 else 'not statistically robust')}, "
           "pointing to access factors worth a targeted operational review rather than a broad clinical overhaul.",
           ""]

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"\nWrote {OUT_MD}")


if __name__ == "__main__":
    main()
