#!/usr/bin/env python3
"""
Hobby Popularity Explorer
- Cleans a hobby list dataset (one hobby per row)
- Creates summary tables
- Rule-based categorization into broad hobby categories
- Produces matplotlib plots (no seaborn)

Run:
  python hobby_analysis.py --input hobbies.csv --out_dir outputs --top_n 25
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Tuple

import pandas as pd
import matplotlib.pyplot as plt


# ----------------------------
# Cleaning helpers
# ----------------------------

_SPLIT_RE = re.compile(r"\s{2,}")  # split when 2+ spaces separate multiple hobbies in one row


def _drop_trailing_single_letter(text: str) -> str:
    parts = text.split(" ")
    if len(parts) >= 2 and len(parts[-1]) == 1 and parts[-1].isalpha() and parts[-1].isupper():
        return " ".join(parts[:-1])
    return text


def clean_hobby_series(raw: pd.Series) -> pd.Series:
    """Return a cleaned, exploded Series of hobbies (one hobby per row)."""
    s = raw.astype(str).str.strip()

    # explode rows containing multiple hobbies separated by 2+ spaces
    expanded: List[str] = []
    for val in s.tolist():
        if _SPLIT_RE.search(val):
            expanded.extend([p.strip() for p in _SPLIT_RE.split(val) if p.strip()])
        else:
            expanded.append(val)

    s2 = pd.Series(expanded, name="HOBBIES")
    s2 = s2.str.replace(r"\s+", " ", regex=True).str.strip()
    s2 = s2.apply(_drop_trailing_single_letter)

    s2 = s2[s2.str.len() > 0].reset_index(drop=True)
    return s2


# ----------------------------
# Categorization (rule-based)
# ----------------------------

Rule = Tuple[str, str]  # (category, regex)

CATEGORY_RULES: List[Rule] = [
    ("Sports & Fitness", r"\b(aerobics|running|jog|fitness|gym|yoga|pilates|boxing|martial|self defense|swim|swimming|tennis|badminton|squash|bowling|golf|soccer|football|basketball|volleyball|skate|skating|inline skating|speed skating|ski|skiing|surf|surfing|hockey|air hockey|table tennis|racquet|tai chi|bodybuilding|cycling|bicycl|water ski|windsurf)\b"),
    ("Outdoors & Nature", r"\b(hiking|camp|climb|tree climbing|fishing|shark fishing|bird|wildlife|safari|snorkel|scuba|astronomy|stargaz|cloud watching|travel|kayak|canoe|rafting|park|sailing|boating|hang gliding|gliding|paragliding|hunting|aquarium|aquariums|ghost hunting)\b"),
    ("Arts, Music & Performance", r"\b(acting|theat|dance|choir|show choir|band|worship team|sing|singing|music|guitar|piano|photograph|artwork|painting|drawing|sketch|sculpture|poetr|writing|worldbuilding|journal|calligraphy)\b"),
    ("Crafts & DIY", r"\b(knit|crochet|sew|sewing|quil|bead|beadwork|tie dye|tie dying|origami|papermaking|wood|carpentry|model|soap|candle|jewel|pottery|ceramic|knapping|weaving)\b"),
    ("Games & Tech", r"\b(video gaming|videophilia|arcade|games|chess|puzzle|crossword|tetris|computer|coding|programming|robot|drone|skype)\b"),
    ("Collecting", r"\b(collect|collection|stamp|coin|antique|action figures|cards|comic|vinyl|swords|autographs|sea glass)\b"),
    ("Food & Drink", r"\b(cook|cooking|baking|bbq|grill|wine|wines|beer|coffee|tea|eating out)\b"),
    ("Learning & Culture", r"\b(courses|language|architecture|meteorology|tarot|history|reading|book|chemistry|science)\b"),
]


def categorize_hobby(hobby: str) -> str:
    for cat, pattern in CATEGORY_RULES:
        if re.search(pattern, hobby, flags=re.IGNORECASE):
            return cat
    return "Other"


# ----------------------------
# Plotting
# ----------------------------

def save_bar_chart(series: pd.Series, title: str, xlabel: str, ylabel: str, out_path: Path, top_n: int = 20) -> None:
    data = series.head(top_n)
    plt.figure(figsize=(12, 6))
    plt.bar(data.index.astype(str), data.values)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=60, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def save_pie_chart(series: pd.Series, title: str, out_path: Path, top_n: int = 10) -> None:
    data = series.copy()
    if len(data) > top_n:
        rest = data.iloc[top_n:].sum()
        data = pd.concat([data.iloc[:top_n], pd.Series({"Other categories": rest})])
    plt.figure(figsize=(8, 8))
    plt.pie(data.values, labels=data.index.astype(str), autopct="%1.1f%%")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


# ----------------------------
# Main
# ----------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze and visualize a hobbies dataset.")
    parser.add_argument("--input", required=True, help="Path to hobbies.csv")
    parser.add_argument("--out_dir", default="outputs", help="Directory for outputs (tables + plots).")
    parser.add_argument("--top_n", type=int, default=25, help="Top N items to show in plots/tables.")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)
    if "HOBBIES" not in df.columns:
        raise ValueError("Expected a column named 'HOBBIES' in the CSV.")

    hobbies = clean_hobby_series(df["HOBBIES"])

    total_rows = len(hobbies)
    unique_hobbies = hobbies.nunique()
    dup_rows = total_rows - unique_hobbies

    print("=== Hobby Popularity Explorer ===")
    print(f"Rows (after cleaning/exploding): {total_rows}")
    print(f"Unique hobbies: {unique_hobbies}")
    print(f"Duplicate entries: {dup_rows}")

    hobby_counts = hobbies.value_counts()
    hobby_counts.to_csv(out_dir / "hobby_counts.csv", header=["count"])

    categories = hobbies.apply(categorize_hobby)
    cat_counts = categories.value_counts()
    cat_counts.to_csv(out_dir / "category_counts.csv", header=["count"])

    pd.DataFrame({"HOBBIES": hobbies, "CATEGORY": categories}).to_csv(out_dir / "hobbies_cleaned.csv", index=False)

    save_bar_chart(
        hobby_counts,
        title=f"Top {min(args.top_n, len(hobby_counts))} Most Frequent Hobbies (by duplicates in list)",
        xlabel="Hobby",
        ylabel="Count",
        out_path=out_dir / "top_hobbies.png",
        top_n=args.top_n,
    )

    save_bar_chart(
        cat_counts,
        title="Hobby Categories (rule-based)",
        xlabel="Category",
        ylabel="Count",
        out_path=out_dir / "category_counts.png",
        top_n=len(cat_counts),
    )

    save_pie_chart(
        cat_counts,
        title="Category Share (Top categories)",
        out_path=out_dir / "category_share.png",
        top_n=8,
    )

    print("\nSaved outputs to:", out_dir.resolve())


if __name__ == "__main__":
    main()