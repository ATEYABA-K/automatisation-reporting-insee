"""
Pipeline de rafraichissement automatique : donnees Insee (adoption IA en entreprise)
-> nettoyage -> format tidy -> graphiques.

Concu pour tourner seul (CLI ou CI), sans intervention manuelle :
- re-telecharge le fichier source a chaque execution
- regenere le CSV tidy et les graphiques a l'identique
- n'echoue pas silencieusement : leve une erreur claire si une etape rate

Usage : python3 scripts/refresh_pipeline.py
"""

import sys
from pathlib import Path

import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SOURCE_URL = "https://www.insee.fr/fr/statistiques/fichier/9025878/IP2120.xlsx"
RAW_FILE = DATA_DIR / "IP2120.xlsx"
TIDY_FILE = DATA_DIR / "insee_ia_pour_powerbi.csv"

TAILLE_ORDER = ["De 10 à 49 salariés", "De 50 à 249 salariés", "250 salariés ou plus"]
COLORS = ["#4C78A8", "#F58518", "#54A24B"]


def download_source() -> None:
    print(f"Téléchargement de {SOURCE_URL} ...")
    response = requests.get(SOURCE_URL, timeout=30)
    response.raise_for_status()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RAW_FILE.write_bytes(response.content)
    print(f"OK — {len(response.content) / 1024:.0f} Ko écrits dans {RAW_FILE}")


def clean_to_tidy() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, sheet_name="Figure 1", skiprows=3)
    df = df.rename(columns={"Unnamed: 0": "categorie"})

    taille = df.iloc[1:4].copy()
    taille["type"] = "Taille de l'entreprise"
    secteur = df.iloc[5:15].copy()
    secteur["type"] = "Secteur d'activité"

    df_clean = pd.concat([taille, secteur], ignore_index=True)
    df_clean = df_clean.rename(columns={
        2023: "France_2023", 2024: "France_2024", 2025: "France_2025",
        "2023.1": "UE_2023", "2024.1": "UE_2024", "2025.1": "UE_2025",
    })

    df_tidy = df_clean.melt(
        id_vars=["categorie", "type"],
        value_vars=["France_2023", "France_2024", "France_2025", "UE_2023", "UE_2024", "UE_2025"],
        var_name="zone_annee",
        value_name="part_entreprises_ia_pct",
    )
    df_tidy[["zone", "annee"]] = df_tidy["zone_annee"].str.split("_", expand=True)
    df_tidy = df_tidy.drop(columns=["zone_annee"])
    df_tidy["annee"] = df_tidy["annee"].astype(int)

    expected_rows = 13 * 6
    if len(df_tidy) != expected_rows:
        raise ValueError(f"Nombre de lignes inattendu après nettoyage : {len(df_tidy)} (attendu {expected_rows})")

    df_tidy.to_csv(TIDY_FILE, index=False, encoding="utf-8-sig")
    print(f"OK — {len(df_tidy)} lignes écrites dans {TIDY_FILE}")
    return df_tidy


def make_charts(df: pd.DataFrame) -> None:
    d1 = df[(df["type"] == "Taille de l'entreprise") & (df["zone"] == "France") & (df["annee"] == 2025)]
    d1 = d1.set_index("categorie").loc[TAILLE_ORDER].reset_index()

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(d1["categorie"], d1["part_entreprises_ia_pct"], color=COLORS)
    ax.set_title("Adoption de l'IA par taille d'entreprise (France, 2025)", fontsize=13, fontweight="bold")
    ax.set_ylabel("% d'entreprises utilisant l'IA")
    ax.set_ylim(0, 65)
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.0f} %", (bar.get_x() + bar.get_width() / 2, h), textcoords="offset points",
                    xytext=(0, 5), ha="center", fontsize=11, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig(ROOT / "chart_ia_par_taille_2025.png", dpi=150)
    plt.close()

    d2 = df[(df["type"] == "Taille de l'entreprise") & (df["zone"] == "France")]
    fig, ax = plt.subplots(figsize=(8, 5))
    for cat, color in zip(TAILLE_ORDER, COLORS):
        sub = d2[d2["categorie"] == cat].sort_values("annee")
        ax.plot(sub["annee"], sub["part_entreprises_ia_pct"], marker="o", label=cat, color=color, linewidth=2.5)
        last = sub.iloc[-1]
        ax.annotate(f"{last['part_entreprises_ia_pct']:.0f} %", (last["annee"], last["part_entreprises_ia_pct"]),
                    textcoords="offset points", xytext=(8, 0), va="center", fontsize=10, fontweight="bold", color=color)
    ax.set_title("Évolution de l'adoption de l'IA par taille d'entreprise (France, 2023-2025)", fontsize=13, fontweight="bold")
    ax.set_ylabel("% d'entreprises utilisant l'IA")
    ax.set_xticks(sorted(d2["annee"].unique()))
    ax.set_ylim(0, 65)
    ax.legend(loc="upper left", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig(ROOT / "chart_evolution_ia_2023_2025.png", dpi=150)
    plt.close()
    print("OK — graphiques régénérés")


def main() -> None:
    try:
        download_source()
        df_tidy = clean_to_tidy()
        make_charts(df_tidy)
    except Exception as exc:
        print(f"ÉCHEC du pipeline : {exc}", file=sys.stderr)
        sys.exit(1)
    print("Pipeline terminé avec succès.")


if __name__ == "__main__":
    main()
